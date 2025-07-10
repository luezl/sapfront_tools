from PySide6.QtWidgets import QPlainTextEdit, QWidget
from PySide6.QtGui import QTextFormat, QPainter, QColor, QTextOption, QPen, QFont, QTextLayout
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
        使用 QTextLayout 精确绘制空白字符
        
        Args:
            painter (QPainter): 绘制器
            block (QTextBlock): 文本块
            block_rect (QRectF): 块的矩形区域
        """
        text = block.text()
        if not text:
            return
        
        # 先尝试简单的回退方案，确保能显示空白字符
        self._draw_whitespace_fallback(painter, text, block_rect)
    
    def _draw_whitespace_fallback(self, painter, text, block_rect):
        """
        回退方案：使用简单的字符宽度计算绘制空白字符
        
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
        
        # 当前绘制位置
        x = block_rect.left()
        
        for i, char in enumerate(text):
            if char == ' ':
                # 绘制空格实心点
                center_x = x + space_width / 2
                center_y = baseline_y - line_height / 4
                painter.setBrush(self.editor.whitespace_color)
                painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                painter.setBrush(Qt.NoBrush)  # 恢复无填充
                x += space_width
            elif char == '\t':
                # 计算tab停止位置
                current_offset = x - block_rect.left()
                next_tab_stop = ((current_offset // tab_width) + 1) * tab_width
                new_x = block_rect.left() + next_tab_stop
                
                # 绘制Tab箭头，两边增加3px空隙
                arrow_y = baseline_y - line_height / 4
                arrow_start_x = x + 3  # 左边3px空隙
                arrow_end_x = new_x - 3  # 右边3px空隙
                
                # 确保箭头有最小长度
                if arrow_end_x <= arrow_start_x:
                    arrow_end_x = arrow_start_x + 8
                
                # 绘制箭头
                painter.drawLine(int(arrow_start_x), int(arrow_y), int(arrow_end_x), int(arrow_y))
                painter.drawLine(int(arrow_end_x), int(arrow_y), int(arrow_end_x - 4), int(arrow_y - 2))
                painter.drawLine(int(arrow_end_x), int(arrow_y), int(arrow_end_x - 4), int(arrow_y + 2))
                
                x = new_x
            else:
                # 普通字符，计算其宽度
                char_width = fm.horizontalAdvance(char)
                x += char_width
    
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
            return
            
        line = layout.lineAt(0)
        if not line.isValid():
            return
            
        fm = self.editor.fontMetrics()
        baseline_y = block_rect.top() + fm.ascent()
        
        for i, char in enumerate(text):
            if char in [' ', '\t']:
                try:
                    # 获取字符的精确 x 坐标
                    char_x = line.cursorToX(i)
                    next_char_x = line.cursorToX(i + 1)
                    
                    # 检查返回值是否有效
                    if char_x < 0 or next_char_x < 0:
                        continue
                    
                    # 转换为视口坐标
                    screen_x = block_rect.left() + char_x
                    screen_next_x = block_rect.left() + next_char_x
                except Exception:
                    # 如果获取位置失败，跳过这个字符
                    continue
                
                if char == ' ':
                    # 绘制空格点
                    center_x = screen_x + (screen_next_x - screen_x) / 2
                    center_y = baseline_y - fm.height() / 4
                    painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                
                elif char == '\t':
                    # 绘制 tab 箭头
                    arrow_y = baseline_y - fm.height() / 4
                    arrow_start_x = screen_x + 4
                    arrow_end_x = screen_next_x - 4
                    
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
        重写绘制事件，添加自定义空白字符绘制
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        # 先调用父类的paintEvent绘制正常文本
        super().paintEvent(event)
        
        # 如果需要显示空白字符，则使用精确渲染器绘制
        if self.show_whitespace:
            self.draw_whitespace_characters(event)
    
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