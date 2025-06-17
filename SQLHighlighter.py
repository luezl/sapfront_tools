from PySide6.QtGui import QTextCharFormat,QSyntaxHighlighter,QColor

class SQLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#3D96D6")) # blue
        self.keyword_format.setFontWeight(100)

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#DA8F70")) # red

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6DB487")) # green

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