from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QInputDialog, QMessageBox
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from PySide6.QtCore import Qt
import sqlparse

class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("blue"))
        self.keyword_format.setFontWeight(75)

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("red"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("green"))

    def highlightBlock(self, text):
        # Simple highlighting for SQL keywords, strings and comments
        # This is a basic implementation, you might want to use a more complete SQL parser
        # For a production application, consider using a proper SQL syntax definition
        
        # Highlight keywords (basic implementation)
        keywords = ["SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", 
                   "UPDATE", "SET", "DELETE", "CREATE", "TABLE", "AS","LEFT",
                    "RIGHT", "INNER", "OUTER", "JOIN", "ON", "AND", "OR", "NOT", 
                    "LIKE", "BETWEEN", "IS", "NULL", "ASC", "DESC", "DISTINCT",
                     "COUNT", "SUM", "AVG", "MAX", "MIN", "GROUP", "HAVING", "ORDER","BY"]
        
        for word in text.split():
            if word.upper() in keywords:
                start = text.find(word)
                self.setFormat(start, len(word), self.keyword_format)
        
        # Highlight strings
        in_string = False
        start_idx = -1
        for i, char in enumerate(text):
            if char == "'" and not in_string:
                in_string = True
                start_idx = i
            elif char == "'" and in_string:
                self.setFormat(start_idx, i - start_idx + 1, self.string_format)
                in_string = False
                start_idx = -1
        
        # Highlight comments
        comment_start = text.find("--")
        if comment_start != -1:
            self.setFormat(comment_start, len(text) - comment_start, self.comment_format)

class SQLFormatterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL Formatter")
        self.setGeometry(100, 100, 800, 600)

        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTextEdit {
                background-color: #ffffff;
                font-family: Consolas;
            }
        """)

        # Create widgets
        self.sql_text_edit = QTextEdit()
        self.sql_text_edit.setFont(QFont("Consolas", 12))
        self.sql_text_edit.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        self.sql_text_edit.setFixedHeight(470)
        
        self.highlighter = SQLHighlighter(self.sql_text_edit.document())
        
        self.format_button = QPushButton("格式化SQL")
        self.java_format_button = QPushButton("转换为Java格式")
        self.reverse_button = QPushButton("从Java转回SQL")
        self.fill_params_button = QPushButton("填充参数")  # 新增按钮
        
        # Set button styles
        button_style = """
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        
        self.format_button.setStyleSheet(button_style)
        self.java_format_button.setStyleSheet(button_style)
        self.reverse_button.setStyleSheet(button_style)
        self.fill_params_button.setStyleSheet(button_style)  # 为新增按钮设置样式
        
        # Main layout with spacing and margins
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title label
        title_label = QLabel("SQL 格式化工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add SQL editor
        main_layout.addWidget(self.sql_text_edit)
        
        # Add button layout with spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch(1)
        button_layout.addWidget(self.format_button)
        button_layout.addWidget(self.java_format_button)
        button_layout.addWidget(self.reverse_button)
        button_layout.addWidget(self.fill_params_button)  # 将新增按钮添加到按钮布局中
        button_layout.addStretch(1)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1)
        
        # Container widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Connect buttons to functions
        self.format_button.clicked.connect(self.format_sql)
        self.java_format_button.clicked.connect(self.convert_to_java_format)
        self.reverse_button.clicked.connect(self.convert_back_to_sql)
        self.fill_params_button.clicked.connect(self.fill_sql_parameters)  # 连接新增按钮的点击事件到fill_sql_parameters方法

    def format_sql(self):
        sql = self.sql_text_edit.toPlainText()
        try:
            # Format SQL with uppercase keywords
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            self.sql_text_edit.setPlainText(formatted_sql)
        except Exception as e:
            print(f"Error formatting SQL: {e}")

    def convert_to_java_format(self):
        sql = self.sql_text_edit.toPlainText()
        if not sql:
            return
        
        # Split SQL into lines
        lines = sql.split('\n')
        
        # Create Java string builder code
        java_code = "StringBuffer sb = new StringBuffer();\n"
        for line in lines:
            # Escape quotes and preserve whitespace
            escaped_line = line.replace('"', '\\"').replace('\\', '\\\\')
            # Add each line as append statement
            java_code += f'sb.append(" {escaped_line} ");\n'
        
        # Set the Java code in the text edit
        self.sql_text_edit.setPlainText(java_code)

    """
    将Java代码格式的SQL转换回原始SQL语句。

    该方法从文本编辑框中获取Java格式的SQL代码，提取引号内的内容并去除多余的空白，
    最终将清理后的SQL语句重新设置到文本编辑框中。

    参数:
        无

    返回值:
        无
    """
    def convert_back_to_sql(self):
        java_code = self.sql_text_edit.toPlainText()
        lines = java_code.splitlines()
        result_lines = []
        
        for index, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                continue
                
            # Extract content inside quotes
            if '"' in line:
                content = line.split('"')[1]
            else:
                continue  # Skip if no quoted content
                
            # Remove leading whitespace for all except first line
            if index > 0:
                content = content.lstrip()
                
            result_lines.append(content)
            
        sql = "\n".join(result_lines)
        
       
        if sql:
            self.sql_text_edit.setPlainText(sql)

    def fill_sql_parameters(self):
        """
        填充SQL参数。

        该方法从用户输入中获取参数值，将SQL语句中的占位符?替换为实际参数值。
        参数值应以逗号分隔的格式输入。

        参数:
            无

        返回值:
            无
        """
        # 获取当前SQL语句
        sql = self.sql_text_edit.toPlainText()
        if not sql:
            return

        # 弹出输入对话框获取参数
        params_text, ok = QInputDialog.getText(self, '输入参数', '请输入参数值(逗号分隔):')
        if not ok or not params_text:
            return

        # 处理参数
        params = [param.strip() for param in params_text.split(',')]
        
        # 替换SQL中的占位符
        placeholder_count = sql.count('?')
        if placeholder_count != len(params):
            QMessageBox.warning(self, '参数错误', f'占位符数量({placeholder_count})与参数数量({len(params)})不匹配!')
            return

        # 用参数值替换占位符
        for param in params:
            sql = sql.replace('?', f"'{param}'", 1)  # 只替换第一个匹配项
        
        # 显示填充后的SQL
        self.sql_text_edit.setPlainText(sql)
