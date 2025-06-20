from PySide6.QtWidgets import QPlainTextEdit, QWidget
from PySide6.QtGui import QTextFormat, QPainter, QColor
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
        
        # 连接信号和槽
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        
        # 初始化时更新行号区域宽度
        self.update_line_number_area_width()
        
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