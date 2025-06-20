from PySide6.QtWidgets import (QApplication, QMainWindow, QInputDialog, QFileDialog, 
                              QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QPlainTextEdit,
                              QMenu)  
from PySide6.QtGui import (QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QIcon, 
                          QUndoStack, QKeySequence, QAction)  
from PySide6.QtCore import Qt
import sqlparse
import chardet
from CodeEditor import CodeEditor
from SQLHighlighter import SQLHighlighter
import os


class SQLFormatterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SQL编辑器")  # 设置主窗口标题
        self.resize(800, 600)  # 设置初始窗口尺寸
         # 设置窗口图标
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
        icon_path = os.path.join(current_dir, "icons", "Editor.png")  # 构建完整路径
        self.setWindowIcon(QIcon(icon_path))

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
                
        # 初始化文本编辑器
        # self.sql_text_edit = QPlainTextEdit()
        self.sql_text_edit = CodeEditor()
        self.sql_text_edit.setStyleSheet('''
            QPlainTextEdit {
                font-family: Consolas;
                font-size: 11pt;
                background-color: #2b2b2b;
                color: #a9b7c6;
                padding: 10px;
            }
        ''')
        layout.addWidget(self.sql_text_edit)




        # 初始化菜单栏
        file_menu = self.menuBar().addMenu('文件(&F)')
        file_menu.addAction('打开', self.open_file).setShortcut('Ctrl+O')
        file_menu.addAction('保存', self.save_file).setShortcut('Ctrl+S')
        file_menu.addSeparator()
        file_menu.addAction('退出', self.exit_app).setShortcut('Ctrl+Q')
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu('编辑(&E)')

        self.current_file = None

        tool_menu = self.menuBar().addMenu('工具(&T)')
        tool_menu.addAction('格式化SQL', self.format_sql).setShortcut('Ctrl+F')
        tool_menu.addAction('转换Java格式', self.convert_to_java_format).setShortcut('Ctrl+J')
        tool_menu.addAction('从Java转回SQL', self.convert_back_to_sql).setShortcut('Ctrl+K')
        tool_menu.addAction('对齐注释', self.align_comments).setShortcut('Ctrl+L')
        tool_menu.addAction('填充参数', self.fill_sql_parameters).setShortcut('Ctrl+P')
        tool_menu.addAction('代码填充', self.fill_code).setShortcut('Ctrl+M')

        # 帮助菜单
        help_menu = self.menuBar().addMenu('帮助(&H)')
        help_menu.addAction('关于', self.show_about).setShortcut('F1')

        # 删除原有按钮相关代码
        self.highlighter = SQLHighlighter(self.sql_text_edit.document())
        
        # 然后创建布局和菜单
        self.editor_widget = QWidget()
        self.editor_layout = QHBoxLayout()
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_layout.setSpacing(0)

        # 行号区域
        self.line_number_area = QWidget()
        self.line_number_area.setFixedWidth(40)
        self.line_number_area.setStyleSheet("""
            background-color: #252526;
            color: #858585;
            font-family: Consolas;
            font-size: 13px;
            padding-right: 5px;
        """)

         # 添加撤销/重做功能
        self.undo_stack = QUndoStack(self)  # 新增
        self.setup_undo_redo_actions()  # 新增

        # 文本编辑区域
        # self.sql_text_edit = QTextEdit()
        # self.sql_text_edit.setFont(QFont("Consolas", 12))
        # self.sql_text_edit.setStyleSheet("padding: 10px;")
        # self.sql_text_edit.setFixedHeight(470)
        
        # 删除以下按钮定义
        # self.format_button = QPushButton("格式化SQL")
        # self.java_format_button = QPushButton("转换为Java格式")
        # self.reverse_button = QPushButton("从Java转回SQL")
        # self.fill_params_button = QPushButton("填充参数")
        # self.align_comments_button = QPushButton("对齐注释")
        
        # 删除按钮事件连接
        # self.format_button.clicked.connect(self.format_sql)
        # self.java_format_button.clicked.connect(self.convert_to_java_format)
        # self.reverse_button.clicked.connect(self.convert_back_to_sql)
        # self.fill_params_button.clicked.connect(self.fill_sql_parameters)
        # self.align_comments_button.clicked.connect(self.align_comments)
    def setup_undo_redo_actions(self):
        """设置撤销和重做操作"""
        # 撤销动作
        undo_action = QAction("撤销", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.sql_text_edit.undo)
        
        # 重做动作
        redo_action = QAction("重做", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.sql_text_edit.redo)
        
        # 获取工具菜单（确保名称完全匹配，包括'&'符号）
        menu_bar = self.menuBar()
        for menu in menu_bar.findChildren(QMenu):
            if menu.title() == '编辑(&E)':
                menu.addAction(undo_action)
                menu.addAction(redo_action)
                return
        
        # 如果没有找到工具菜单，就添加到编辑菜单
        edit_menu = menu_bar.addMenu('编辑(&E)')
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

    def format_sql(self):
        sql = self.sql_text_edit.toPlainText()
        try:
            # Format SQL with uppercase keywords
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            # 使用 QTextCursor 替换文本，支持撤销功能
            cursor = self.sql_text_edit.textCursor()
            cursor.beginEditBlock()
            cursor.select(cursor.SelectionType.Document)
            cursor.insertText(formatted_sql)
            cursor.endEditBlock()
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
        
        # 使用 QTextCursor 替换文本，支持撤销功能
        cursor = self.sql_text_edit.textCursor()
        cursor.beginEditBlock()
        cursor.select(cursor.SelectionType.Document)
        cursor.insertText(java_code)
        cursor.endEditBlock()

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
            # 使用 QTextCursor 替换文本，支持撤销功能
            cursor = self.sql_text_edit.textCursor()
            cursor.beginEditBlock()
            cursor.select(cursor.SelectionType.Document)
            cursor.insertText(sql)
            cursor.endEditBlock()

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
        
        # 使用 QTextCursor 替换文本，支持撤销功能
        cursor = self.sql_text_edit.textCursor()
        cursor.beginEditBlock()
        cursor.select(cursor.SelectionType.Document)
        cursor.insertText(sql)
        cursor.endEditBlock()

   
    def align_comments(self):
        """
        对齐代码中的注释。

        该方法将Java代码中的tab转换为4个空格，并使注释对齐。
        支持处理单行注释(//)和Javadoc注释(/** */模式)。

        参数:
            无

        返回值:
            无
        """
        # 获取当前文本
        java_code = self.sql_text_edit.toPlainText()
        if not java_code:
            return

        # 按行分割
        lines = java_code.splitlines()
        result_lines = []
        
        # 第一次处理：将tab转换为空格，记录最大注释位置
        max_comment_pos = 0
        processed_lines = []
        
        for line in lines:
            # 将tab转换为4个空格
            line_with_spaces = line.replace('\t', '    ')
            
            # 查找注释位置
            comment_pos = line_with_spaces.find('//')
            if comment_pos != -1:
                # 更新最大注释位置
                max_comment_pos = max(max_comment_pos, comment_pos)
                
            # 保存处理后的行和注释位置
            processed_lines.append((line_with_spaces, comment_pos))
        
        # 第二次处理：对齐注释
        for line, comment_pos in processed_lines:
            if comment_pos != -1:
                # 如果是注释行，添加适当的前导空格
                aligned_line = line[:comment_pos] + ' ' * (max_comment_pos - comment_pos) + line[comment_pos:]
                result_lines.append(aligned_line)
            else:
                # 非注释行直接添加
                result_lines.append(line)
        
        # 使用 QTextCursor 替换文本，支持撤销功能
        aligned_java_code = '\n'.join(result_lines)
        cursor = self.sql_text_edit.textCursor()
        cursor.beginEditBlock()
        cursor.select(cursor.SelectionType.Document)
        cursor.insertText(aligned_java_code)
        cursor.endEditBlock()

    def fill_code(self):
        """
        填充代码模板。

        该方法弹出输入对话框获取代码模板，将文本编辑器中的内容按照模板进行填充。
        支持使用{0}、{1}等占位符的模板格式。修改后的版本支持撤销功能。

        参数:
            无

        返回值:
            无
        """
        # 创建多行输入对话框
        # 使用 getMultiLineText 方法创建多行输入对话框
        template, ok = QInputDialog.getMultiLineText(
            self, 
            '输入模板', 
            '请输入代码模板（使用{0}, {1}作为占位符）:', 
            ''
        )
            
        if not ok or not template:
            return

        # 获取当前文本编辑器的内容
        text = self.sql_text_edit.toPlainText()
        if not text:
            return

        # 按行处理文本
        lines = text.splitlines()
        result_lines = []
        
        for line in lines:
            # 跳过空行
            if not line.strip():
                continue
                
            # 分割行内容
            parts = [part.strip() for part in line.split('\t')]
            
            # 替换模板中的占位符
            try:
                formatted_line = template.format(*parts)
                result_lines.extend(formatted_line.split('\n'))  # 支持多行输出
            except IndexError as e:
                QMessageBox.warning(self, '模板错误', f'模板占位符与实际参数不匹配: {str(e)}')
                return

        # 使用 QTextCursor 替换文本，这样可以支持撤销功能
        if result_lines:
            cursor = self.sql_text_edit.textCursor()
            # 开始复合编辑操作，这样整个替换操作会被视为一个撤销步骤
            cursor.beginEditBlock()
            # 选择所有文本
            cursor.select(cursor.SelectionType.Document)
            # 替换选中的文本
            cursor.insertText('\n'.join(result_lines))
            # 结束复合编辑操作
            cursor.endEditBlock()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '打开文件', '', 'SQL Files (*.sql);;All Files (*)')
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    # 自动检测文件编码
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] or 'gbk'
                    try:
                        text = raw_data.decode(encoding)
                    except UnicodeDecodeError:
                        text = raw_data.decode('gbk', errors='replace')
                    # 分步解码策略
                    try:
                        text = raw_data.decode('utf-8')
                    except UnicodeDecodeError:
                        detected = chardet.detect(raw_data)
                        text = raw_data.decode(detected['encoding'] or 'gb18030', errors='replace')
                
                # 使用 QTextCursor 替换文本，支持撤销功能
                cursor = self.sql_text_edit.textCursor()
                cursor.beginEditBlock()
                cursor.select(cursor.SelectionType.Document)
                cursor.insertText(text)
                cursor.endEditBlock()
                
            except Exception as e:
                QMessageBox.critical(self, '打开失败', f'文件解码失败: {str(e)}')
            self.current_file = file_path
            self.setWindowTitle(f'SQL编辑器 - {file_path}')
    
    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.sql_text_edit.toPlainText())
        else:
            self.save_as_file()
    
    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '另存为', '', 'SQL Files (*.sql);;All Files (*)')
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.sql_text_edit.toPlainText())
            self.current_file = file_path
            self.setWindowTitle(f'SQL编辑器 - {file_path}')
    
    def exit_app(self):
        QApplication.instance().quit()

    def show_about(self):
        """
        显示关于对话框
        
        显示软件信息、版本、作者等详细信息
        """
        about_text = """
        <h2>SQL编辑器</h2>
        <p><b>版本:</b> 1.0.0</p>
        <p><b>描述:</b> 一个功能强大的SQL编辑和格式化工具</p>
        <br>
        <h3>功能特性:</h3>
        <ul>
            <li>SQL语法高亮显示</li>
            <li>SQL代码格式化</li>
            <li>Java代码格式转换</li>
            <li>参数填充功能</li>
            <li>注释对齐功能</li>
            <li>代码模板填充</li>
            <li>撤销/重做支持</li>
        </ul>
        <br>
        <h3>作者信息:</h3>
        <p><b>作者:</b> 刘忠亮</p>
        <p><b>邮箱:</b> zhongliang.liu@lixil.com</p>
        <br>
        <p><b>开发时间:</b> 2025年</p>
        """
        
        QMessageBox.about(self, "关于 SQL编辑器", about_text)
