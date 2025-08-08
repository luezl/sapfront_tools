from PySide6.QtWidgets import QPlainTextEdit, QWidget
from PySide6.QtGui import QTextFormat, QPainter, QColor, QTextOption, QPen, QFont, QTextLayout, QKeyEvent, QTextCursor
from PySide6.QtCore import Qt, QRect, QSize, QPointF

class PreciseWhitespaceRenderer:
    """精确的空白字符渲染器，使用 QTextLayout 确保与文本渲染完全一致"""
    
    def __init__(self, editor):
        """
        初始化精确渲染器
        
        Args:
            editor (CodeEditor): 关联的代码编辑器实例
        """
        self.editor = editor
        self.layout_cache = {}  # 缓存布局对象，提高性能
        self.cache_version = 0  # 缓存版本号，用于失效检测
    
    def clear_cache(self):
        """清除布局缓存"""
        self.layout_cache.clear()
        self.cache_version += 1
    
    def draw_block_whitespace_precise(self, painter, block, block_rect):
        """
        使用QTextDocument的原生绘制功能精确绘制空白字符
        
        Args:
            painter (QPainter): 绘制器
            block (QTextBlock): 文本块
            block_rect (QRectF): 块的矩形区域
        """
        text = block.text()
        if not text:
            return
        
        # 使用最简单直接的方法：创建临时文档并绘制
        try:
            self._draw_whitespace_with_temp_document(painter, text, block_rect)
        except Exception:
            # 如果失败，使用fallback方案
            self._draw_whitespace_fallback(painter, text, block_rect)
    
    def _draw_whitespace_with_temp_document(self, painter, text, block_rect):
        """
        使用临时QTextDocument获取绝对精确的字符位置
        
        Args:
            painter (QPainter): 绘制器
            text (str): 文本内容
            block_rect (QRectF): 块矩形区域
        """
        from PySide6.QtGui import QTextDocument
        
        # 创建临时文档，使用与编辑器完全相同的设置
        temp_doc = QTextDocument()
        temp_doc.setDefaultFont(self.editor.font())
        temp_doc.setPlainText(text)
        
        # 设置文档的默认文本选项
        option = QTextOption()
        option.setTabStopDistance(self.editor.tabStopDistance())
        temp_doc.setDefaultTextOption(option)
        
        # 获取文档的第一个块
        temp_block = temp_doc.firstBlock()
        if not temp_block.isValid():
            return
        
        # 创建临时布局
        layout = temp_block.layout()
        if layout.lineCount() == 0:
            # 如果没有布局，强制创建
            layout.beginLayout()
            line = layout.createLine()
            line.setLineWidth(10000)  # 设置足够大的宽度
            layout.endLayout()
        
        if layout.lineCount() == 0:
            return
            
        line = layout.lineAt(0)
        if not line.isValid():
            return
        
        fm = self.editor.fontMetrics()
        baseline_y = block_rect.top() + fm.ascent()
        
        # 设置画刷和画笔
        painter.setBrush(self.editor.whitespace_color)
        
        # 检查是否有空白字符需要绘制
        has_whitespace = any(c in [' ', '\t'] for c in text)
        drawn_any = False
        
        # 现在获取每个字符的精确位置
        for i, char in enumerate(text):
            if char in [' ', '\t']:
                try:
                    # 使用QTextLine的cursorToX方法获取精确位置
                    char_x = line.cursorToX(i)
                    next_char_x = line.cursorToX(i + 1)
                    
                    if char_x < 0 or next_char_x < 0 or char_x >= next_char_x:
                        continue
                    
                    # 转换为实际屏幕坐标
                    screen_x = block_rect.left() + char_x
                    screen_next_x = block_rect.left() + next_char_x
                    
                    if char == ' ':
                        # 绘制空格点
                        center_x = screen_x + (screen_next_x - screen_x) / 2
                        center_y = baseline_y - fm.height() / 4
                        painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                        drawn_any = True
                    
                    elif char == '\t':
                        # 绘制 tab 箭头，两边留出3px空隙
                        arrow_y = baseline_y - fm.height() / 4
                        arrow_start_x = screen_x + 3
                        arrow_end_x = screen_next_x - 3
                        
                        # 确保箭头有最小长度
                        if arrow_end_x <= arrow_start_x:
                            arrow_end_x = arrow_start_x + 8
                        
                        # 绘制箭头主体
                        painter.drawLine(int(arrow_start_x), int(arrow_y), 
                                       int(arrow_end_x), int(arrow_y))
                        # 绘制箭头头部
                        painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                       int(arrow_end_x - 4), int(arrow_y - 2))
                        painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                       int(arrow_end_x - 4), int(arrow_y + 2))
                        drawn_any = True
                        
                except Exception:
                    continue
        
        # 恢复画刷
        painter.setBrush(Qt.NoBrush)
        
        # 如果有空白字符但没有绘制任何内容，抛出异常使用fallback
        if has_whitespace and not drawn_any:
            raise Exception("Failed to draw any whitespace with temp document")
    
    def _draw_whitespace_using_painter_metrics(self, painter, text, block_rect):
        """
        使用QPainter的文本度量方法获取精确位置
        
        Args:
            painter (QPainter): 绘制器
            text (str): 文本内容
            block_rect (QRectF): 块矩形区域
        """
        # 设置painter的字体与编辑器一致
        painter.setFont(self.editor.font())
        fm = painter.fontMetrics()
        baseline_y = block_rect.top() + fm.ascent()
        
        # 设置画刷和画笔
        painter.setBrush(self.editor.whitespace_color)
        
        # 创建文本选项，设置tab停止距离
        tab_stops = int(self.editor.tabStopDistance() / fm.horizontalAdvance(' '))
        
        drawn_any = False
        for i, char in enumerate(text):
            if char in [' ', '\t']:
                # 获取到当前字符位置的文本
                text_to_char = text[:i]
                text_to_next = text[:i+1]
                
                # 使用boundingRect获取精确宽度，设置tab展开
                rect_to_char = fm.boundingRect(0, 0, 10000, fm.height(), 
                                             Qt.TextExpandTabs, text_to_char, tab_stops)
                rect_to_next = fm.boundingRect(0, 0, 10000, fm.height(), 
                                             Qt.TextExpandTabs, text_to_next, tab_stops)
                
                char_x = block_rect.left() + rect_to_char.width()
                next_char_x = block_rect.left() + rect_to_next.width()
                
                # 验证位置是否有效
                if char_x >= next_char_x or char_x < block_rect.left():
                    continue
                
                if char == ' ':
                    # 绘制空格点
                    center_x = char_x + (next_char_x - char_x) / 2
                    center_y = baseline_y - fm.height() / 4
                    painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                    drawn_any = True
                
                elif char == '\t':
                    # 绘制 tab 箭头，两边留出3px空隙
                    arrow_y = baseline_y - fm.height() / 4
                    arrow_start_x = char_x + 3
                    arrow_end_x = next_char_x - 3
                    
                    # 确保箭头有最小长度
                    if arrow_end_x <= arrow_start_x:
                        arrow_end_x = arrow_start_x + 8
                    
                    # 绘制箭头主体
                    painter.drawLine(int(arrow_start_x), int(arrow_y), 
                                   int(arrow_end_x), int(arrow_y))
                    # 绘制箭头头部
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y - 2))
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y + 2))
                    drawn_any = True
        
        # 恢复画刷
        painter.setBrush(Qt.NoBrush)
        
        # 如果没有成功绘制任何字符，抛出异常使用fallback
        if not drawn_any and any(c in [' ', '\t'] for c in text):
            raise Exception("Failed to draw whitespace using painter metrics")
    
    def _draw_whitespace_using_cursor_positions(self, painter, block, text, block_rect):
        """
        使用编辑器的光标位置获取精确的字符位置
        
        Args:
            painter (QPainter): 绘制器
            block (QTextBlock): 文本块
            text (str): 文本内容
            block_rect (QRectF): 块矩形区域
        """
        fm = self.editor.fontMetrics()
        baseline_y = block_rect.top() + fm.ascent()
        
        # 设置画刷和画笔
        painter.setBrush(self.editor.whitespace_color)
        
        # 获取块的起始位置
        block_start = block.position()
        drawn_any = False
        
        for i, char in enumerate(text):
            if char in [' ', '\t']:
                # 创建光标到当前字符位置
                cursor_at_char = QTextCursor(self.editor.document())
                cursor_at_char.setPosition(block_start + i)
                
                # 创建光标到下一个字符位置
                cursor_at_next = QTextCursor(self.editor.document())
                cursor_at_next.setPosition(block_start + i + 1)
                
                # 获取光标矩形
                char_rect = self.editor.cursorRect(cursor_at_char)
                next_rect = self.editor.cursorRect(cursor_at_next)
                
                # 验证矩形是否有效
                if (char_rect.isNull() or next_rect.isNull() or 
                    char_rect.left() < 0 or next_rect.left() < 0 or
                    char_rect.left() >= next_rect.left()):
                    # 位置无效，跳过这个字符
                    continue
                
                # 计算字符的实际屏幕位置
                char_x = char_rect.left()
                next_char_x = next_rect.left()
                
                if char == ' ':
                    # 绘制空格点
                    center_x = char_x + (next_char_x - char_x) / 2
                    center_y = baseline_y - fm.height() / 4
                    painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                    drawn_any = True
                
                elif char == '\t':
                    # 绘制 tab 箭头，两边留出3px空隙
                    arrow_y = baseline_y - fm.height() / 4
                    arrow_start_x = char_x + 3
                    arrow_end_x = next_char_x - 3
                    
                    # 确保箭头有最小长度
                    if arrow_end_x <= arrow_start_x:
                        arrow_end_x = arrow_start_x + 8
                    
                    # 绘制箭头主体
                    painter.drawLine(int(arrow_start_x), int(arrow_y), 
                                   int(arrow_end_x), int(arrow_y))
                    # 绘制箭头头部
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y - 2))
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y + 2))
                    drawn_any = True
        
        # 恢复画刷
        painter.setBrush(Qt.NoBrush)
        
        # 如果没有成功绘制任何字符，抛出异常使用fallback
        if not drawn_any and any(c in [' ', '\t'] for c in text):
            raise Exception("Failed to draw whitespace using cursor positions")
    
    def _draw_whitespace_fallback(self, painter, text, block_rect):
        """
        回退方案：使用精确的字符测量绘制空白字符
        
        Args:
            painter (QPainter): 绘制器
            text (str): 文本内容
            block_rect (QRectF): 块矩形区域
        """
        fm = self.editor.fontMetrics()
        space_width = fm.horizontalAdvance(' ')
        tab_width = self.editor.tabStopDistance()
        line_height = fm.height()
        
        # 计算基线位置
        baseline_y = block_rect.top() + fm.ascent()
        
        # 使用fontMetrics精确测量文本到每个位置的宽度
        for i, char in enumerate(text):
            if char in [' ', '\t']:
                # 获取到当前字符位置的精确宽度
                text_to_char = text[:i]
                
                # 使用fontMetrics测量文本宽度，这会正确处理tab
                char_x = block_rect.left()
                if text_to_char:
                    # 创建临时的文本选项来处理tab
                    option = QTextOption()
                    option.setTabStopDistance(tab_width)
                    
                    # 使用boundingRect来获取精确的文本宽度
                    temp_rect = fm.boundingRect(QRect(0, 0, 10000, line_height), 
                                              Qt.TextExpandTabs, text_to_char, 
                                              int(tab_width / space_width))
                    char_x = block_rect.left() + temp_rect.width()
                
                # 获取下一个字符的位置
                text_to_next = text[:i+1]
                next_char_x = block_rect.left()
                if text_to_next:
                    temp_rect = fm.boundingRect(QRect(0, 0, 10000, line_height), 
                                              Qt.TextExpandTabs, text_to_next, 
                                              int(tab_width / space_width))
                    next_char_x = block_rect.left() + temp_rect.width()
                else:
                    next_char_x = char_x + (tab_width if char == '\t' else space_width)
                
                if char == ' ':
                    # 绘制空格实心点
                    center_x = char_x + (next_char_x - char_x) / 2
                    center_y = baseline_y - line_height / 4
                    painter.setBrush(self.editor.whitespace_color)
                    painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                    painter.setBrush(Qt.NoBrush)
                
                elif char == '\t':
                    # 绘制Tab箭头，两边增加3px空隙
                    arrow_y = baseline_y - line_height / 4
                    arrow_start_x = char_x + 3
                    arrow_end_x = next_char_x - 3
                    
                    # 确保箭头有最小长度
                    if arrow_end_x <= arrow_start_x:
                        arrow_end_x = arrow_start_x + 8
                    
                    # 绘制箭头
                    painter.drawLine(int(arrow_start_x), int(arrow_y), int(arrow_end_x), int(arrow_y))
                    painter.drawLine(int(arrow_end_x), int(arrow_y), int(arrow_end_x - 4), int(arrow_y - 2))
                    painter.drawLine(int(arrow_end_x), int(arrow_y), int(arrow_end_x - 4), int(arrow_y + 2))
    
    def _get_or_create_layout(self, block):
        """
        获取或创建文本布局对象
        
        Args:
            block (QTextBlock): 文本块
            
        Returns:
            QTextLayout: 文本布局对象
        """
        block_number = block.blockNumber()
        cache_key = (block_number, self.cache_version)
        
        if cache_key not in self.layout_cache:
            self.layout_cache[cache_key] = QTextLayout()
            
        return self.layout_cache[cache_key]
    
    def _draw_whitespace_at_precise_positions(self, painter, text, layout, block_rect):
        """
        在精确位置绘制空白字符
        
        Args:
            painter (QPainter): 绘制器
            text (str): 文本内容
            layout (QTextLayout): 文本布局
            block_rect (QRectF): 块矩形区域
        """
        if layout.lineCount() == 0:
            raise Exception("Layout has no lines")
            
        line = layout.lineAt(0)
        if not line.isValid():
            raise Exception("Layout line is invalid")
            
        fm = self.editor.fontMetrics()
        baseline_y = block_rect.top() + fm.ascent()
        
        # 设置画刷和画笔
        painter.setBrush(self.editor.whitespace_color)
        
        # 验证能否获取位置信息
        drawn_any = False
        for i, char in enumerate(text):
            if char in [' ', '\t']:
                # 获取字符的精确 x 坐标
                char_x = line.cursorToX(i)
                next_char_x = line.cursorToX(i + 1)
                
                # 检查返回值是否有效
                if char_x < 0 or next_char_x < 0 or char_x == next_char_x:
                    continue
                
                # 转换为视口坐标
                screen_x = block_rect.left() + char_x
                screen_next_x = block_rect.left() + next_char_x
                
                if char == ' ':
                    # 绘制空格点
                    center_x = screen_x + (screen_next_x - screen_x) / 2
                    center_y = baseline_y - fm.height() / 4
                    painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                    drawn_any = True
                
                elif char == '\t':
                    # 绘制 tab 箭头，两边留出3px空隙
                    arrow_y = baseline_y - fm.height() / 4
                    arrow_start_x = screen_x + 3
                    arrow_end_x = screen_next_x - 3
                    
                    # 确保箭头有最小长度
                    if arrow_end_x <= arrow_start_x:
                        arrow_end_x = arrow_start_x + 8
                    
                    # 绘制箭头主体
                    painter.drawLine(int(arrow_start_x), int(arrow_y), 
                                   int(arrow_end_x), int(arrow_y))
                    # 绘制箭头头部
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y - 2))
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y + 2))
                    drawn_any = True
        
        # 恢复画刷
        painter.setBrush(Qt.NoBrush)
        
        # 如果没有成功绘制任何空白字符，抛出异常以使用fallback
        if not drawn_any and any(c in [' ', '\t'] for c in text):
            raise Exception("Failed to draw any whitespace characters")


class LineNumberArea(QWidget):
    """行号区域小部件，用于显示代码编辑器的行号"""
    def __init__(self, editor):
        """
        初始化行号区域
        
        Args:
            editor (CodeEditor): 关联的代码编辑器实例
        """
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        """返回推荐的尺寸"""
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        """
        绘制事件处理
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """
    代码编辑器类，继承自 QPlainTextEdit，并增加了行号显示功能
    使用精确的 QTextLayout 方案解决 tab 对齐问题
    """
    def __init__(self, parent=None):
        """
        初始化代码编辑器
        
        Args:
            parent (QWidget): 父组件
        """
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        # 空白字符显示状态 - 默认显示
        self.show_whitespace = True
        
        # 空白字符颜色设置
        self.whitespace_color = QColor("#6A737D")  # 深灰色
        
        # 设置等宽字体（推荐用于代码编辑）
        font = QFont("Consolas", 10)  # Consolas是Windows常见的等宽字体
        if not font.exactMatch():
            font = QFont("Courier New", 10)  # 备选等宽字体
        font.setFixedPitch(True)
        self.setFont(font)
        
        # 创建精确渲染器（必须在setTabStopDistance之前创建）
        self.precise_renderer = PreciseWhitespaceRenderer(self)
        
        # 设置Tab宽度为4个空格
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        
        # 连接信号和槽
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.textChanged.connect(self._on_text_changed)
        
        # 初始化时更新行号区域宽度
        self.update_line_number_area_width()
        
    def _on_text_changed(self):
        """文本变化时的处理"""
        # 清除布局缓存以确保重新计算
        self.precise_renderer.clear_cache()
        
    def set_show_whitespace(self, show):
        """
        设置是否显示空白字符
        
        Args:
            show (bool): True显示空白字符，False隐藏
        """
        self.show_whitespace = show
        # 刷新显示
        self.viewport().update()
    
    def set_whitespace_color(self, color):
        """
        设置空白字符的颜色
        
        Args:
            color (QColor): 空白字符的颜色
        """
        self.whitespace_color = color
        if self.show_whitespace:
            self.viewport().update()
        
    def is_whitespace_visible(self):
        """
        返回当前是否显示空白字符
        
        Returns:
            bool: True表示显示空白字符，False表示隐藏
        """
        return self.show_whitespace
    
    def paintEvent(self, event):
        """
        重写绘制事件，先绘制正常文本，再叠加空白字符
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        # 先调用父类的paintEvent绘制正常文本（包括选择高亮等）
        super().paintEvent(event)
        
        # 如果需要显示空白字符，则在上面叠加绘制
        if self.show_whitespace:
            self._draw_whitespace_overlay(event)
    
    def _draw_whitespace_overlay(self, event):
        """
        在已绘制的文本上叠加空白字符，使用精确的逐字符位置计算
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        painter = QPainter(self.viewport())
        try:
            painter.setPen(self.whitespace_color)
            
            # 获取可见区域的文本块
            block = self.firstVisibleBlock()
            viewport_offset = self.contentOffset()
            
            while block.isValid():
                block_geometry = self.blockBoundingGeometry(block)
                offset = block_geometry.translated(viewport_offset)
                
                # 检查块是否在可见区域内
                if offset.top() > event.rect().bottom():
                    break
                    
                if offset.bottom() >= event.rect().top():
                    self._draw_block_whitespace_overlay(painter, block, offset)
                
                block = block.next()
        finally:
            painter.end()
    
    def _draw_block_whitespace_overlay(self, painter, block, block_rect):
        """
        为单个文本块绘制空白字符叠加，使用与之前完美方案相同的逐字符计算
        
        Args:
            painter (QPainter): 绘制器
            block (QTextBlock): 文本块
            block_rect (QRectF): 块矩形区域
        """
        text = block.text()
        if not text:
            return
        
        # 设置字体（与编辑器保持一致）
        painter.setFont(self.font())
        fm = painter.fontMetrics()
        
        # 计算基线位置
        baseline_y = block_rect.top() + fm.ascent()
        
        # 使用与之前完美方案相同的逐字符位置计算
        x = block_rect.left()
        
        for i, char in enumerate(text):
            if char == ' ':
                # 在空格位置绘制点
                center_x = x + fm.horizontalAdvance(' ') / 2
                center_y = baseline_y - fm.height() / 4
                painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                x += fm.horizontalAdvance(' ')
                
            elif char == '\t':
                # 计算tab的结束位置
                tab_width = self.tabStopDistance()
                current_offset = x - block_rect.left()
                next_tab_stop = ((current_offset // tab_width) + 1) * tab_width
                new_x = block_rect.left() + next_tab_stop
                
                # 绘制tab箭头
                arrow_y = baseline_y - fm.height() / 4
                arrow_start_x = x + 3
                arrow_end_x = new_x - 3
                
                if arrow_end_x > arrow_start_x:
                    # 绘制箭头主体
                    painter.drawLine(int(arrow_start_x), int(arrow_y), 
                                   int(arrow_end_x), int(arrow_y))
                    # 绘制箭头头部
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y - 2))
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y + 2))
                
                x = new_x
                
            else:
                # 普通字符，只计算宽度不绘制
                x += fm.horizontalAdvance(char)
    
    def _draw_block_text_with_whitespace(self, painter, block, block_rect, event):
        """
        绘制文本块，同时在精确位置绘制空白字符
        
        Args:
            painter (QPainter): 绘制器
            block (QTextBlock): 文本块
            block_rect (QRectF): 块矩形区域
            event (QPaintEvent): 绘制事件
        """
        text = block.text()
        if not text:
            return
        
        # 设置字体
        painter.setFont(self.font())
        fm = painter.fontMetrics()
        
        # 计算基线位置
        baseline_y = block_rect.top() + fm.ascent()
        
        # 使用简单但精确的方法：逐字符绘制
        x = block_rect.left()
        
        for i, char in enumerate(text):
            if char == ' ':
                # 绘制空格字符
                painter.setPen(self.palette().color(self.foregroundRole()))
                painter.drawText(int(x), int(baseline_y), char)
                
                # 在空格位置绘制点
                painter.setPen(self.whitespace_color)
                center_x = x + fm.horizontalAdvance(' ') / 2
                center_y = baseline_y - fm.height() / 4
                painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                
                x += fm.horizontalAdvance(' ')
                
            elif char == '\t':
                # 计算tab的结束位置
                tab_width = self.tabStopDistance()
                current_offset = x - block_rect.left()
                next_tab_stop = ((current_offset // tab_width) + 1) * tab_width
                new_x = block_rect.left() + next_tab_stop
                
                # 绘制tab箭头
                painter.setPen(self.whitespace_color)
                arrow_y = baseline_y - fm.height() / 4
                arrow_start_x = x + 3
                arrow_end_x = new_x - 3
                
                if arrow_end_x > arrow_start_x:
                    # 绘制箭头主体
                    painter.drawLine(int(arrow_start_x), int(arrow_y), 
                                   int(arrow_end_x), int(arrow_y))
                    # 绘制箭头头部
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y - 2))
                    painter.drawLine(int(arrow_end_x), int(arrow_y), 
                                   int(arrow_end_x - 4), int(arrow_y + 2))
                
                x = new_x
                
            else:
                # 绘制普通字符
                painter.setPen(self.palette().color(self.foregroundRole()))
                painter.drawText(int(x), int(baseline_y), char)
                x += fm.horizontalAdvance(char)
    
    def draw_whitespace_characters(self, event):
        """
        绘制空白字符（空格和Tab）- 使用精确渲染器
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        painter = QPainter(self.viewport())
        try:
            painter.setPen(QPen(self.whitespace_color))
            
            # 获取可见的文本块
            block = self.firstVisibleBlock()
            viewport_offset = self.contentOffset()
            
            while block.isValid():
                # 获取块的几何信息
                block_geometry = self.blockBoundingGeometry(block)
                offset = block_geometry.translated(viewport_offset)
                
                # 检查块是否在可见区域内
                if offset.top() > event.rect().bottom():
                    break
                if offset.bottom() >= event.rect().top():
                    # 使用精确渲染器绘制空白字符
                    self.precise_renderer.draw_block_whitespace_precise(painter, block, offset)
                
                block = block.next()
        finally:
            # 确保 QPainter 正确结束
            painter.end()
    
    def setFont(self, font):
        """
        重写 setFont 方法，在字体变化时清除缓存
        
        Args:
            font (QFont): 新字体
        """
        super().setFont(font)
        # 字体变化时需要重新计算tab宽度和清除缓存
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        # 检查 precise_renderer 是否已经初始化
        if hasattr(self, 'precise_renderer'):
            self.precise_renderer.clear_cache()
        
    def setTabStopDistance(self, distance):
        """
        重写 setTabStopDistance 方法，在tab宽度变化时清除缓存
        
        Args:
            distance (float): tab停止距离
        """
        super().setTabStopDistance(distance)
        # 检查 precise_renderer 是否已经初始化
        if hasattr(self, 'precise_renderer'):
            self.precise_renderer.clear_cache()
        
    def line_number_area_width(self):
        """计算行号区域的宽度"""
        # 获取最大行号的位数
        digits = len(str(max(1, self.blockCount())))
        # 计算宽度，包括一些额外的边距
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self):
        """更新行号区域的宽度，并设置编辑器的左边距"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """
        当编辑器滚动时，更新行号区域
        
        Args:
            rect (QRect): 更新的矩形区域
            dy (int): 垂直滚动的距离
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def resizeEvent(self, event):
        """
        重写 resizeEvent，在窗口大小改变时调整行号区域的位置
        
        Args:
            event (QResizeEvent): 尺寸改变事件
        """
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        # 窗口大小变化时清除缓存
        if hasattr(self, 'precise_renderer'):
            self.precise_renderer.clear_cache()

    def line_number_area_paint_event(self, event):
        """
        绘制行号区域的内容
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#252526"))  # 设置背景色
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingGeometry(block).height()

        # 遍历所有可见的文本块并绘制行号
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#858585"))  # 设置行号颜色
                painter.drawText(0, int(top), self.line_number_area.width() - 5, self.fontMetrics().height(),
                               Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingGeometry(block).height()
            block_number += 1
    
    def keyPressEvent(self, event):
        """
        重写键盘事件处理，添加自定义快捷键功能
        
        Args:
            event (QKeyEvent): 键盘事件
        """
        # 处理 Tab/Shift+Tab 缩进
        if event.key() == Qt.Key_Tab or event.key() == Qt.Key_Backtab:
            # Qt.Key_Backtab 是 Shift+Tab 的另一种表示
            if event.key() == Qt.Key_Backtab or (event.key() == Qt.Key_Tab and event.modifiers() & Qt.ShiftModifier):
                # Shift+Tab: 减少缩进（无论是否有选中文本）
                if self.textCursor().hasSelection():
                    self.unindent_selection()
                # 无论是否有选中文本，都要阻止默认行为
                event.accept()
                return
            elif event.key() == Qt.Key_Tab and self.textCursor().hasSelection():
                # Tab: 增加缩进（仅在有选中文本时）
                self.indent_selection()
                event.accept()
                return
        
        # 处理 Ctrl+Shift+U (大写)
        elif (event.key() == Qt.Key_U and
              event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier)):
            self.convert_selection_to_upper()
            event.accept()
            return
        
        # 处理 Ctrl+Shift+L (小写)
        elif (event.key() == Qt.Key_L and
              event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier)):
            self.convert_selection_to_lower()
            event.accept()
            return
        
        # 其他按键交给父类处理
        super().keyPressEvent(event)
    
    def indent_selection(self):
        """
        对选中的行增加缩进（在每行开头添加4个空格）
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        # 获取选中区域的起始和结束位置
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        # 移动到选中区域的开始行
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.StartOfBlock)
        
        # 记录处理前的选中区域
        first_block_pos = cursor.position()
        
        # 处理每一行
        while cursor.position() <= end and not cursor.atEnd():
            # 在行首插入4个空格
            cursor.insertText("    ")
            # 更新结束位置（因为插入了字符）
            end += 4
            
            # 移动到下一行
            if not cursor.movePosition(QTextCursor.NextBlock):
                break
        
        # 恢复选中状态
        cursor.setPosition(first_block_pos)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        
        cursor.endEditBlock()
        self.setTextCursor(cursor)
    
    def unindent_selection(self):
        """
        对选中的行减少缩进（删除每行开头的最多4个空格或1个Tab）
        """
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        # 获取选中区域的起始和结束位置
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        # 移动到选中区域的开始行
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.StartOfBlock)
        
        # 记录处理前的选中区域
        first_block_pos = cursor.position()
        
        # 处理每一行
        while cursor.position() <= end and not cursor.atEnd():
            # 保存当前位置
            current_pos = cursor.position()
            
            # 获取当前行的文本
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            line_text = cursor.selectedText()
            cursor.setPosition(current_pos)  # 回到行首
            
            # 计算要删除的字符数
            chars_to_remove = 0
            
            # 如果行首是Tab，删除一个Tab
            if line_text and line_text[0] == '\t':
                chars_to_remove = 1
            else:
                # 否则删除最多4个空格
                for i, char in enumerate(line_text):
                    if char == ' ' and i < 4:
                        chars_to_remove += 1
                    else:
                        break
            
            # 删除字符
            if chars_to_remove > 0:
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, chars_to_remove)
                cursor.removeSelectedText()
                # 更新结束位置
                end -= chars_to_remove
            
            # 移动到下一行
            cursor.movePosition(QTextCursor.StartOfBlock)
            if not cursor.movePosition(QTextCursor.NextBlock):
                break
        
        # 恢复选中状态
        cursor.setPosition(first_block_pos)
        cursor.setPosition(max(first_block_pos, end), QTextCursor.KeepAnchor)
        
        cursor.endEditBlock()
        self.setTextCursor(cursor)
    
    def convert_selection_to_upper(self):
        """
        将选中的文本转换为大写
        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(selected_text.upper())
    
    def convert_selection_to_lower(self):
        """
        将选中的文本转换为小写
        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(selected_text.lower())