import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit,
                              QPushButton, QListWidget, QLabel, QStatusBar, QHBoxLayout)
from PySide6.QtCore import Qt

class SQLParser:
    @staticmethod
    def parse_select(sql):
        # 解析SELECT语句的WHERE/HAVING子句
        where_matches = re.findall(r'(?:WHERE|HAVING)\s+([^;]+)', sql, re.IGNORECASE)
        if not where_matches:
            return []
        
        # 提取参数占位符前的字段名
        fields = []
        for condition in where_matches:
            # 移除注释
            condition = re.sub(r'--.*?$|/\*.*?\*/', '', condition, flags=re.DOTALL)
            # 匹配字段名
            field_matches = re.findall(r'([\w.]+)\s*[=<>!]+\s*\?', condition)
            fields.extend(field_matches)
        
        return list(set(fields))

    @staticmethod
    def parse_insert(sql):
        # 改进后的正则表达式匹配模式
        match = re.search(
            r'INSERT\s+INTO\s+[\w.]+\s*\s*\(([^)]+)\)',
            sql,
            re.IGNORECASE | re.DOTALL
        )
        if not match:
            return []
        
        fields_str = match.group(1)
        # 处理多行字段和空格
        fields_str = re.sub(r'\s+', ' ', fields_str)  # 合并空白字符
        fields = [f.strip() for f in fields_str.split(',') if f.strip()]
        
        return fields

    @staticmethod
    def parse_update(sql):
        # 解析UPDATE语句的SET和WHERE部分
        set_matches = re.findall(r'SET\s+([^;]+?)(?:WHERE|$)', sql, re.IGNORECASE)
        where_matches = re.findall(r'WHERE\s+([^;]+)', sql, re.IGNORECASE)
        
        fields = []
        
        # 处理SET部分
        if set_matches:
            set_clause = set_matches[0]
            set_clause = re.sub(r'--.*?$|/\*.*?\*/', '', set_clause, flags=re.DOTALL)
            set_fields = re.findall(r'([\w.]+)\s*=\s*\?', set_clause)
            fields.extend(set_fields)
        
        # 处理WHERE部分
        if where_matches:
            where_clause = where_matches[0]
            where_clause = re.sub(r'--.*?$|/\*.*?\*/', '', where_clause, flags=re.DOTALL)
            where_fields = re.findall(r'([\w.]+)\s*[=<>!]+\s*\?', where_clause)
            fields.extend(where_fields)
        
        return list(set(fields))

    @staticmethod
    def parse_delete(sql):
        # 解析DELETE语句的WHERE子句
        where_matches = re.findall(r'WHERE\s+([^;]+)', sql, re.IGNORECASE)
        if not where_matches:
            return []
        
        fields = []
        for condition in where_matches:
            # 移除注释
            condition = re.sub(r'--.*?$|/\*.*?\*/', '', condition, flags=re.DOTALL)
            # 匹配字段名
            field_matches = re.findall(r'([\w.]+)\s*[=<>!]+\s*\?', condition)
            fields.extend(field_matches)
        
        return list(set(fields))

    @classmethod
    def parse_sql(cls, sql):
        # 移除所有注释
        clean_sql = re.sub(r'--.*?$|/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # 根据SQL类型调用不同的解析方法
        if re.search(r'^\s*SELECT', clean_sql, re.IGNORECASE):
            return cls.parse_select(clean_sql)
        elif re.search(r'^\s*INSERT', clean_sql, re.IGNORECASE):
            return cls.parse_insert(clean_sql)
        elif re.search(r'^\s*UPDATE', clean_sql, re.IGNORECASE):
            return cls.parse_update(clean_sql)
        elif re.search(r'^\s*DELETE', clean_sql, re.IGNORECASE):
            return cls.parse_delete(clean_sql)
        else:
            return []


class SQLParserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL参数解析工具")
        self.resize(800, 600)
        
        # 主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # 输入区域
        self.setup_input_area()
        
        # 按钮区域
        self.setup_button_area()
        
        # 结果区域
        self.setup_result_area()
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪")
        
        # 设置样式
        self.setup_styles()
    
    def setup_input_area(self):
        # 输入标签
        self.input_label = QLabel("输入SQL语句:")
        self.main_layout.addWidget(self.input_label)
        
        # SQL输入框
        self.sql_input = QTextEdit()
        self.sql_input.setPlaceholderText("请输入SQL语句(支持SELECT/INSERT/UPDATE/DELETE)...")
        self.sql_input.setMinimumHeight(150)
        self.main_layout.addWidget(self.sql_input)
    
    def setup_button_area(self):
        # 按钮布局
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        
        # 解析按钮
        self.parse_btn = QPushButton("解析字段")
        self.parse_btn.setFixedWidth(100)
        self.parse_btn.clicked.connect(self.parse_sql)
        self.button_layout.addWidget(self.parse_btn)
        
        # 清空按钮
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setFixedWidth(100)
        self.clear_btn.clicked.connect(self.clear_all)
        self.button_layout.addWidget(self.clear_btn)
        
        # 复制按钮
        self.copy_btn = QPushButton("复制字段")
        self.copy_btn.setFixedWidth(100)
        self.copy_btn.clicked.connect(self.copy_fields)
        self.button_layout.addWidget(self.copy_btn)
        
        # 添加按钮布局
        self.button_layout.addStretch()
        self.main_layout.addLayout(self.button_layout)
    
    def setup_result_area(self):
        # 结果标签
        self.result_label = QLabel("解析结果:")
        self.main_layout.addWidget(self.result_label)
        
        # 结果列表
        self.result_list = QListWidget()
        self.result_list.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.result_list)
    
    def setup_styles(self):
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QTextEdit, QListWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                background-color: #4CAF50;
                color: white;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
            }
            
            QLabel {
                font-weight: bold;
            }
            
            QListWidget {
                font-family: monospace;
            }
        """)
    
    def parse_sql(self):
        sql = self.sql_input.toPlainText().strip()
        if not sql:
            self.status_bar.showMessage("错误: 请输入SQL语句")
            return
        
        try:
            fields = SQLParser.parse_sql(sql)
            self.result_list.clear()
            
            if not fields:
                self.status_bar.showMessage("警告: 未找到可解析的参数占位符")
                return
            
            self.result_list.addItems(fields)
            self.status_bar.showMessage(f"成功: 找到 {len(fields)} 个参数字段")
        except Exception as e:
            self.status_bar.showMessage(f"错误: {str(e)}")
    
    def clear_all(self):
        self.sql_input.clear()
        self.result_list.clear()
        self.status_bar.showMessage("已清空")
        
    def copy_fields(self):
        """将解析出的字段复制到剪贴板"""
        if self.result_list.count() == 0:
            self.status_bar.showMessage("错误: 没有可复制的字段")
            return
            
        fields = [self.result_list.item(i).text() for i in range(self.result_list.count())]
        QApplication.clipboard().setText('\n'.join(fields))
        self.status_bar.showMessage(f"成功: 已复制 {len(fields)} 个字段到剪贴板")


if __name__ == "__main__":
    app = QApplication([])
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    window = SQLParserApp()
    window.show()
    app.exec()