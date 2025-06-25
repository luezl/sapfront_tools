from PySide6.QtWidgets import QPlainTextEdit, QWidget
from PySide6.QtGui import QTextFormat, QPainter, QColor, QTextOption, QPen, QFont
from PySide6.QtCore import Qt, QRect, QSize

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
        
        # 设置Tab宽度为4个空格
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 10)
        
        # 空白字符颜色设置
        self.whitespace_color = QColor("#6A737D")  # 深灰色
        
        # 连接信号和槽
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        
        # 初始化时更新行号区域宽度
        self.update_line_number_area_width()
        
    def set_show_whitespace(self, show):
        """
        设置是否显示空白字符
        
        Args:
            show (bool): True显示空白字符，False隐藏
        """
        self.show_whitespace = show
        # 不使用Qt内置的空白字符显示，我们自己绘制
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
        
        # 如果需要显示空白字符，则自定义绘制
        if self.show_whitespace:
            self.draw_whitespace_characters(event)
    
    def draw_whitespace_characters(self, event):
        """
        绘制空白字符（空格和Tab）
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        painter = QPainter(self.viewport())
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
                self.draw_block_whitespace(painter, block, offset)
            
            block = block.next()
    
    def draw_block_whitespace(self, painter, block, offset):
        """
        绘制单个文本块中的空白字符
        
        Args:
            painter (QPainter): 绘制器
            block (QTextBlock): 文本块
            offset (QRectF): 块的偏移位置
        """
        text = block.text()
        if not text:
            return
        
        # 字体度量
        fm = self.fontMetrics()
        space_width = fm.horizontalAdvance(' ')
        tab_width = self.tabStopDistance()
        line_height = fm.height()
        
        # 计算基线位置
        baseline_y = offset.top() + fm.ascent()
        
        x = offset.left()
        for i, char in enumerate(text):
            if char == ' ':
                # 绘制空格点
                center_x = x + space_width / 2
                center_y = baseline_y - line_height / 4
                painter.drawEllipse(int(center_x - 1), int(center_y - 1), 2, 2)
                x += space_width
            elif char == '\t':
                # 绘制Tab箭头
                arrow_y = baseline_y - line_height / 4
                arrow_start_x = x + 4
                arrow_end_x = x + tab_width - 4
                
                # 绘制箭头线
                painter.drawLine(int(arrow_start_x), int(arrow_y), int(arrow_end_x), int(arrow_y))
                # 绘制箭头头部
                painter.drawLine(int(arrow_end_x), int(arrow_y), int(arrow_end_x - 4), int(arrow_y - 2))
                painter.drawLine(int(arrow_end_x), int(arrow_y), int(arrow_end_x - 4), int(arrow_y + 2))
                
                x += tab_width
            else:
                # 普通字符，计算其宽度
                char_width = fm.horizontalAdvance(char)
                x += char_width
        
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