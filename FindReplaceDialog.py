"""
查找替换对话框模块
"""

import re
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QGridLayout, 
                               QLabel, QLineEdit, QCheckBox, QHBoxLayout, 
                               QPushButton)
from PySide6.QtGui import QTextCharFormat, QColor, QTextCursor, QTextDocument
from PySide6.QtCore import Qt


class FindReplaceDialog(QDialog):
    """
    查找替换对话框类
    
    提供查找、替换、正则表达式、实时高亮等功能。
    """
    
    def __init__(self, parent=None, text_editor=None):
        """
        初始化查找替换对话框
        
        Args:
            parent (QWidget): 父组件
            text_editor (QTextEdit): 需要操作的文本编辑器
        """
        super().__init__(parent)
        self.text_editor = text_editor
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QColor("#FFFF00"))  # 黄色背景
        self.current_highlights = []
        
        self.setup_ui()
        self.setup_connections()
        
        # 初始化时自动填充选中的文本
        self.auto_fill_selected_text()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("查找和替换")
        self.setModal(False)  # 设置为非模态，允许与主窗口交互
        self.resize(450, 300)
        
        layout = QVBoxLayout(self)
        
        # 查找组
        find_group = QGroupBox("查找")
        find_layout = QGridLayout(find_group)
        find_layout.addWidget(QLabel("查找内容:"), 0, 0)
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("输入要查找的内容...")
        find_layout.addWidget(self.find_edit, 0, 1)
        
        self.regex_checkbox = QCheckBox("使用正则表达式")
        find_layout.addWidget(self.regex_checkbox, 1, 1)
        
        self.case_sensitive_checkbox = QCheckBox("区分大小写")
        find_layout.addWidget(self.case_sensitive_checkbox, 2, 1)
        
        layout.addWidget(find_group)
        
        # 替换组
        replace_group = QGroupBox("替换")
        replace_layout = QGridLayout(replace_group)
        replace_layout.addWidget(QLabel("替换为:"), 0, 0)
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("输入替换内容...")
        replace_layout.addWidget(self.replace_edit, 0, 1)
        
        layout.addWidget(replace_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.find_button = QPushButton("查找下一个")
        self.find_prev_button = QPushButton("查找上一个")
        self.replace_button = QPushButton("替换")
        self.replace_all_button = QPushButton("全部替换")
        
        button_layout.addWidget(self.find_button)
        button_layout.addWidget(self.find_prev_button)
        button_layout.addWidget(self.replace_button)
        button_layout.addWidget(self.replace_all_button)
        layout.addLayout(button_layout)
        
        # 关闭和状态
        footer_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        self.close_button = QPushButton("关闭")
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.close_button)
        layout.addLayout(footer_layout)
        
    def setup_connections(self):
        """设置信号和槽的连接"""
        self.find_edit.textChanged.connect(self.highlight_all_matches)
        self.regex_checkbox.toggled.connect(self.highlight_all_matches)
        self.case_sensitive_checkbox.toggled.connect(self.highlight_all_matches)
        
        self.find_button.clicked.connect(self.find_next)
        self.find_prev_button.clicked.connect(self.find_previous)
        self.replace_button.clicked.connect(self.replace_current)
        self.replace_all_button.clicked.connect(self.replace_all)
        self.close_button.clicked.connect(self.close)
        
        # 对话框关闭时自动清除高亮
        self.finished.connect(self.clear_highlights)
        
    def auto_fill_selected_text(self):
        """如果编辑器中有选中的文本，自动填充到查找框"""
        if not self.text_editor:
            return
            
        cursor = self.text_editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            if selected_text.strip():
                self.find_edit.setText(selected_text)
                self.highlight_all_matches()
                
    def highlight_all_matches(self):
        """高亮显示所有匹配的文本"""
        self.clear_highlights()
        find_text = self.find_edit.text()
        if not find_text:
            return
        
        try:
            if self.regex_checkbox.isChecked():
                flags = re.IGNORECASE if not self.case_sensitive_checkbox.isChecked() else 0
                pattern = re.compile(find_text, flags)
                text = self.text_editor.toPlainText()
                for match in pattern.finditer(text):
                    self.highlight_range(match.start(), match.end())
            else:
                flags = QTextDocument.FindFlags()
                if self.case_sensitive_checkbox.isChecked():
                    flags |= QTextDocument.FindCaseSensitively
                
                cursor = self.text_editor.document().find(find_text, 0, flags)
                while not cursor.isNull():
                    self.highlight_range(cursor.selectionStart(), cursor.selectionEnd())
                    cursor = self.text_editor.document().find(find_text, cursor, flags)
            
            self.update_status()
        except re.error as e:
            self.status_label.setText(f"正则表达式错误: {e}")
            
    def highlight_range(self, start, end):
        """高亮指定范围的文本"""
        cursor = QTextCursor(self.text_editor.document())
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        cursor.mergeCharFormat(self.highlight_format)
        self.current_highlights.append(cursor)
        
    def clear_highlights(self):
        """清除所有高亮"""
        # 创建一个默认的QTextCharFormat来清除格式
        default_format = QTextCharFormat()
        
        # 获取文档的第一个块
        block = self.text_editor.document().begin()
        
        # 遍历所有文本块
        while block.isValid():
            # 获取块的布局
            layout = block.layout()
            if layout:
                # 遍历布局中的所有格式范围
                for frange in layout.formats():
                    # 如果格式是高亮格式，则清除它
                    if frange.format.background() == self.highlight_format.background():
                        cursor = QTextCursor(block)
                        cursor.setPosition(block.position() + frange.start, QTextCursor.MoveAnchor)
                        cursor.setPosition(block.position() + frange.start + frange.length, QTextCursor.KeepAnchor)
                        cursor.setCharFormat(default_format)
            
            # 移动到下一个块
            block = block.next()
        
        # 更新UI
        self.text_editor.viewport().update()
        self.current_highlights.clear()
        self.status_label.setText("已清除高亮")

    def find_next(self, backward=False):
        """查找下一个或上一个匹配项"""
        find_text = self.find_edit.text()
        if not find_text:
            return
            
        try:
            cursor = self.text_editor.textCursor()
            
            if self.regex_checkbox.isChecked():
                flags = re.IGNORECASE if not self.case_sensitive_checkbox.isChecked() else 0
                pattern = re.compile(find_text, flags)
                text = self.text_editor.toPlainText()
                
                matches = list(pattern.finditer(text))
                if not matches:
                    self.status_label.setText("未找到匹配项")
                    return
                
                current_pos = cursor.position()
                if backward:
                    found = next((m for m in reversed(matches) if m.start() < cursor.selectionStart()), matches[-1])
                else:
                    found = next((m for m in matches if m.start() > current_pos), matches[0])
                    
                cursor.setPosition(found.start())
                cursor.setPosition(found.end(), QTextCursor.KeepAnchor)
            else:
                find_flags = QTextDocument.FindFlags()
                if backward:
                    find_flags |= QTextDocument.FindBackward
                if self.case_sensitive_checkbox.isChecked():
                    find_flags |= QTextDocument.FindCaseSensitively
                
                found_cursor = self.text_editor.document().find(find_text, cursor, find_flags)
                if found_cursor.isNull():
                    # 没找到，从头/尾开始重新查找
                    start_cursor = QTextCursor(self.text_editor.document())
                    start_cursor.movePosition(QTextCursor.End if backward else QTextCursor.Start)
                    found_cursor = self.text_editor.document().find(find_text, start_cursor, find_flags)
                
                if found_cursor.isNull():
                    self.status_label.setText("未找到匹配项")
                    return
                cursor = found_cursor

            self.text_editor.setTextCursor(cursor)
            self.status_label.setText(f"找到匹配项于 {cursor.selectionStart()}-{cursor.selectionEnd()}")
            
        except re.error as e:
            self.status_label.setText(f"正则表达式错误: {e}")

    def find_previous(self):
        """查找上一个匹配项"""
        self.find_next(backward=True)
        
    def replace_current(self):
        """替换当前选中的文本"""
        cursor = self.text_editor.textCursor()
        if not cursor.hasSelection():
            self.find_next()
            return
            
        replace_text = self.replace_edit.text()
        cursor.beginEditBlock()
        cursor.insertText(replace_text)
        cursor.endEditBlock()
        
        self.status_label.setText("已替换当前匹配项")
        self.highlight_all_matches()
        
    def replace_all(self):
        """替换所有匹配项"""
        find_text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        if not find_text:
            return
            
        try:
            text = self.text_editor.toPlainText()
            
            if self.regex_checkbox.isChecked():
                flags = re.IGNORECASE if not self.case_sensitive_checkbox.isChecked() else 0
                pattern = re.compile(find_text, flags)
                new_text = pattern.sub(replace_text, text)
            else:
                if self.case_sensitive_checkbox.isChecked():
                    new_text = text.replace(find_text, replace_text)
                else:
                    pattern = re.compile(re.escape(find_text), re.IGNORECASE)
                    new_text = pattern.sub(replace_text, text)
                    
            cursor = self.text_editor.textCursor()
            cursor.beginEditBlock()
            cursor.select(QTextCursor.Document)
            cursor.insertText(new_text)
            cursor.endEditBlock()
            
            self.status_label.setText(f"已替换 {self.update_status()} 个匹配项")
            self.highlight_all_matches()
            
        except re.error as e:
            self.status_label.setText(f"正则表达式错误: {e}")
            
    def update_status(self):
        """更新状态栏信息，并返回匹配数量"""
        count = len(self.current_highlights)
        if count > 0:
            self.status_label.setText(f"找到 {count} 个匹配项")
        else:
            self.status_label.setText("未找到匹配项")
        return count

    def closeEvent(self, event):
        """重写关闭事件，确保清除高亮"""
        self.clear_highlights()
        super().closeEvent(event) 