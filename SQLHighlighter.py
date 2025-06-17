from PySide6.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor


class SQLHighlighter(QSyntaxHighlighter):
    """
    SQL语法高亮器类，用于在文本编辑器中高亮显示SQL语法
    支持关键字、字符串和注释的高亮显示
    """
    
    def __init__(self, parent=None):
        """初始化SQL语法高亮器"""
        super().__init__(parent)
        
        # 初始化关键字格式（蓝色）
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#3D96D6"))
        self.keyword_format.setFontWeight(100)

        # 初始化字符串格式（红色）
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#DA8F70"))

        # 初始化注释格式（绿色）
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6DB487"))

        # SQL关键字列表
        self.keywords = [
            "ABSOLUTE", "ACTION", "ADD", "ADMIN", "AFTER", "AGGREGATE", "ALIAS", "ALL",
            "ALLOCATE", "ALTER", "AND", "ANY", "ARE", "ARRAY", "AS", "ASC", "ASSERTION",
            "AT", "AUTHORIZATION", "BEFORE", "BEGIN", "BETWEEN", "BINARY", "BIT", "BLOB",
            "BOOLEAN", "BOTH", "BREADTH", "BY", "CALL", "CASCADE", "CASCADED", "CASE",
            "CAST", "CATALOG", "CHAR", "CHARACTER", "CHECK", "CLASS", "CLOB", "CLOSE",
            "COLLATE", "COLLATION", "COLUMN", "COMMENT", "COMMIT", "COMPLETION", "CONNECT",
            "CONNECTION", "CONSTRAINT", "CONSTRAINTS", "CONSTRUCTOR", "CONTINUE",
            "CORRESPONDING", "CREATE", "CROSS", "CUBE", "CURRENT", "CURRENT_DATE",
            "CURRENT_PATH", "CURRENT_ROLE", "CURRENT_TIME", "CURRENT_TIMESTAMP",
            "CURRENT_USER", "CURSOR", "CYCLE", "DATA", "DATE", "DAY", "DEALLOCATE",
            "DEC", "DECIMAL", "DECLARE", "DEFAULT", "DEFERRABLE", "DEFERRED", "DELETE",
            "DEPTH", "DEREF", "DESC", "DESCRIBE", "DESCRIPTOR", "DESTROY", "DESTRUCTOR",
            "DETERMINISTIC", "DIAGNOSTICS", "DICTIONARY", "DISCONNECT", "DISTINCT",
            "DOMAIN", "DOUBLE", "DROP", "DYNAMIC", "DYNAMIC_FUNCTION_CODE", "EACH",
            "ELSE", "END", "END-EXEC", "EQUALS", "ESCAPE", "EVERY", "EXCEPT", "EXCEPTION",
            "EXEC", "EXECUTE", "EXISTS", "EXTERNAL", "FALSE", "FETCH", "FIRST", "FLOAT",
            "FOLLOWING", "FOR", "FOREIGN", "FOUND", "FREE", "FROM", "FULL", "FUNCTION",
            "GENERAL", "GET", "GLOBAL", "GO", "GOTO", "GRANT", "GROUP", "GROUPING",
            "HAVING", "HOST", "HOUR", "IDENTITY", "IF", "IGNORE", "IMMEDIATE", "IN",
            "INDEX", "INDICATOR", "INITIALIZE", "INITIALLY", "INNER", "INOUT", "INPUT",
            "INSERT", "INT", "INTEGER", "INTERSECT", "INTERVAL", "INTO", "IS", "ISOLATION",
            "ITERATE", "JOIN", "KEY", "LANGUAGE", "LARGE", "LAST", "LATERAL", "LEADING",
            "LEFT", "LESS", "LEVEL", "LIKE", "LIMIT", "LOCAL", "LOCALTIME", "LOCALTIMESTAMP",
            "LOCATOR", "MAP", "MATCH", "MATCHED", "MATERIALIZED", "MERGE", "MINUS",
            "MINUTE", "MODIFIES", "MODIFY", "MODULE", "MONTH", "NAMES", "NATIONAL",
            "NATURAL", "NCHAR", "NCLOB", "NEW", "NEXT", "NO", "NONE", "NOT", "NULL",
            "NULLS", "NUMERIC", "OBJECT", "OF", "OFF", "OFFSET", "OLD", "ON", "ONLY",
            "OPEN", "OPERATION", "OPTION", "OR", "ORDER", "ORDINALITY", "OUT", "OUTER",
            "OUTPUT", "OVER", "PAD", "PARAMETER", "PARAMETERS", "PARTIAL", "PARTITION",
            "PATH", "POSTFIX", "PRECEDING", "PRECISION", "PREFIX", "PREORDER", "PREPARE",
            "PRESERVE", "PRIMARY", "PRIOR", "PRIVILEGES", "PROCEDURE", "PUBLIC", "RANGE",
            "READ", "READS", "REAL", "RECURSIVE", "REF", "REFERENCES", "REFERENCING",
            "RELATIVE", "REPLACE", "RESPECT", "RESTRICT", "RESULT", "RETURN",
            "RETURNED_LENGTH", "RETURNING", "RETURNS", "REVOKE", "RIGHT", "ROLE",
            "ROLLBACK", "ROLLUP", "ROUTINE", "ROW", "ROWS", "SAVEPOINT", "SCHEMA",
            "SCOPE", "SCROLL", "SEARCH", "SECOND", "SECTION", "SELECT", "SEQUENCE",
            "SESSION", "SESSION_USER", "SET", "SETS", "SIMILAR", "SIZE", "SMALLINT",
            "SOME", "SPACE", "SPECIFIC", "SPECIFICTYPE", "SQL", "SQLEXCEPTION",
            "SQLSTATE", "SQLWARNING", "START", "STATE", "STATEMENT", "STATIC",
            "STRUCTURE", "SYSTEM_USER", "TABLE", "TEMPORARY", "TERMINATE", "THAN",
            "THEN", "TIME", "TIMESTAMP", "TIMEZONE_HOUR", "TIMEZONE_MINUTE", "TO",
            "TRAILING", "TRANSACTION", "TRANSLATION", "TREAT", "TRIGGER", "TRUE",
            "TRUNCATE", "UNBOUNDED", "UNDER", "UNION", "UNIQUE", "UNKNOWN", "UNNEST",
            "UPDATE", "USAGE", "USER", "USING", "VALUE", "VALUES", "VARCHAR",
            "VARIABLE", "VARYING", "VIEW", "WHEN", "WHENEVER", "WHERE", "WHILE",
            "WINDOW", "WITH", "WITHOUT", "WORK", "WRITE", "YEAR", "ZONE"
        ]

    def highlightBlock(self, text):
        """
        高亮显示文本块中的SQL语法元素
        
        Args:
            text (str): 需要高亮显示的文本
        """
        # 高亮关键字
        for word in text.split():
            if word.upper() in self.keywords:
                start = text.find(word)
                self.setFormat(start, len(word), self.keyword_format)
        
        # 高亮字符串
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
        
        # 高亮注释
        comment_start = text.find("--")
        if comment_start != -1:
            self.setFormat(comment_start, len(text) - comment_start, self.comment_format)