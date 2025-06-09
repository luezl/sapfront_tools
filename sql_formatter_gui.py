from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
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
        java_code = "StringBuilder sb = new StringBuilder();\n"
        for line in lines:
            # Escape quotes and preserve whitespace
            escaped_line = line.replace('"', '\\"').replace('\\', '\\\\')
            # Add each line as append statement
            java_code += f'sb.append(" {escaped_line} ");\n'
        
        # Set the Java code in the text edit
        self.sql_text_edit.setPlainText(java_code)