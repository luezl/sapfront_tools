from PySide6.QtWidgets import (QApplication, QMainWindow, QInputDialog, QFileDialog,
                              QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, QPlainTextEdit,
                              QMenu, QTabWidget, QPushButton, QLabel, QTabBar)
from PySide6.QtGui import (QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QIcon,
                          QUndoStack, QKeySequence, QAction, QTextCursor, QTextDocument, QPainter)
from PySide6.QtCore import Qt, QRect, Signal, QSize
import sqlparse
import chardet
import re
from CodeEditor import CodeEditor
from SQLHighlighter import SQLHighlighter
from FindReplaceDialog import FindReplaceDialog
import os




class TabEditor(QWidget):
    """单个标签页编辑器组件"""
    
    def __init__(self, file_path=None, content=""):
        super().__init__()
        self.file_path = file_path
        self.is_modified = False
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建代码编辑器
        self.editor = CodeEditor()
        self.editor.setStyleSheet('''
            QPlainTextEdit {
                font-family: Consolas;
                font-size: 11pt;
                background-color: #2b2b2b;
                color: #a9b7c6;
                padding: 10px;
            }
        ''')
        
        # 设置内容
        if content:
            self.editor.setPlainText(content)
        
        # 添加语法高亮
        self.highlighter = SQLHighlighter(self.editor.document())
        
        # 监听文本变化
        self.editor.textChanged.connect(self.on_text_changed)
        
        layout.addWidget(self.editor)
        
    def on_text_changed(self):
        """文本变化时标记为已修改"""
        self.is_modified = True
        
    def get_display_name(self):
        """获取显示名称"""
        if self.file_path:
            name = os.path.basename(self.file_path)
        else:
            name = "未命名"
        
        if self.is_modified:
            name += " *"
        
        return name
        
    def save(self, file_path=None):
        """保存文件"""
        if file_path:
            self.file_path = file_path
            
        if self.file_path:
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.is_modified = False
                return True
            except Exception as e:
                return False
        return False


class SQLFormatterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SQL编辑器")  # 设置主窗口标题
        self.resize(1000, 700)  # 设置初始窗口尺寸，稍大以适应多标签页
         # 设置窗口图标
        current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
        icon_path = os.path.join(current_dir, "icons", "Editor.png")  # 构建完整路径
        self.setWindowIcon(QIcon(icon_path))

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页组件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)  # 允许关闭标签页
        self.tab_widget.setMovable(True)  # 允许拖拽标签页
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # 创建新建标签页按钮
        self.new_tab_button = QPushButton("＋")
        self.new_tab_button.setFixedSize(28, 28)
        self.new_tab_button.setToolTip("新建标签页 (Ctrl+N)")
        self.new_tab_button.clicked.connect(self.new_tab)
        self.new_tab_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #858585;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: normal;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)
        
        # 将按钮设置为标签栏的角落组件
        self.tab_widget.setCornerWidget(self.new_tab_button)
        
        layout.addWidget(self.tab_widget)
        
        # 创建第一个标签页
        self.new_tab()

        # 初始化菜单栏
        self.setup_menus()
        
        # 添加撤销/重做功能
        self.undo_stack = QUndoStack(self)
        self.setup_undo_redo_actions()

    def setup_menus(self):
        """设置菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu('文件(&F)')
        file_menu.addAction('新建', self.new_tab).setShortcut('Ctrl+N')
        file_menu.addAction('打开', self.open_file).setShortcut('Ctrl+O')
        file_menu.addSeparator()
        file_menu.addAction('保存', self.save_file).setShortcut('Ctrl+S')
        file_menu.addAction('另存为', self.save_as_file).setShortcut('Ctrl+Shift+S')
        file_menu.addSeparator()
        file_menu.addAction('关闭标签页', self.close_current_tab).setShortcut('Ctrl+W')
        file_menu.addAction('退出', self.exit_app).setShortcut('Ctrl+Q')
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu('编辑(&E)')
        edit_menu.addAction('查找替换', self.show_find_replace_dialog).setShortcut('Ctrl+H')
        edit_menu.addSeparator()
        
        # 显示空白字符选项
        self.show_whitespace_action = edit_menu.addAction('显示空格和Tab')
        self.show_whitespace_action.setCheckable(True)
        self.show_whitespace_action.setChecked(True)
        self.show_whitespace_action.triggered.connect(self.toggle_whitespace_visibility)

        # 工具菜单
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
        
    def new_tab(self, file_path=None, content=""):
        """创建新标签页"""
        tab_editor = TabEditor(file_path, content)
        
        # 监听文本变化以更新标签页标题
        tab_editor.editor.textChanged.connect(lambda: self.update_tab_title(tab_editor))
        
        # 应用当前的空白字符显示设置
        if hasattr(self, 'show_whitespace_action'):
            show_whitespace = self.show_whitespace_action.isChecked()
            tab_editor.editor.set_show_whitespace(show_whitespace)
        
        # 添加标签页
        index = self.tab_widget.addTab(tab_editor, tab_editor.get_display_name())
        self.tab_widget.setCurrentIndex(index)
        
        # 更新窗口标题
        self.update_window_title()
        
        return tab_editor
        
            
    def close_tab(self, index):
        """关闭指定标签页"""
        if self.tab_widget.count() <= 1:
            # 如果只有一个标签页，创建新的空标签页
            self.new_tab()
            
        tab_editor = self.tab_widget.widget(index)
        
        # 检查是否有未保存的更改
        if tab_editor.is_modified:
            reply = QMessageBox.question(
                self, '确认关闭',
                f'文件 "{tab_editor.get_display_name()}" 有未保存的更改，是否保存？',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                if not self.save_tab(tab_editor):
                    return  # 保存失败，不关闭
            elif reply == QMessageBox.Cancel:
                return  # 取消关闭
                
        self.tab_widget.removeTab(index)
        self.update_window_title()
        
    def close_current_tab(self):
        """关闭当前标签页"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)
            
    def get_current_editor(self):
        """获取当前活动的编辑器"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            return current_tab.editor
        return None
        
    def get_current_tab_editor(self):
        """获取当前活动的标签页编辑器"""
        return self.tab_widget.currentWidget()
        
    def update_tab_title(self, tab_editor):
        """更新标签页标题"""
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i) == tab_editor:
                self.tab_widget.setTabText(i, tab_editor.get_display_name())
                break
        self.update_window_title()
        
    def update_window_title(self):
        """更新窗口标题"""
        current_tab = self.get_current_tab_editor()
        if current_tab and current_tab.file_path:
            self.setWindowTitle(f"SQL编辑器 - {current_tab.file_path}")
        else:
            self.setWindowTitle("SQL编辑器")
    def setup_undo_redo_actions(self):
        """设置撤销和重做操作"""
        # 撤销动作
        undo_action = QAction("撤销", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo_current)
        
        # 重做动作
        redo_action = QAction("重做", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo_current)
        
        # 获取编辑菜单
        menu_bar = self.menuBar()
        for menu in menu_bar.findChildren(QMenu):
            if menu.title() == '编辑(&E)':
                menu.addAction(undo_action)
                menu.addAction(redo_action)
                return
                
    def undo_current(self):
        """撤销当前编辑器的操作"""
        editor = self.get_current_editor()
        if editor:
            editor.undo()
            
    def redo_current(self):
        """重做当前编辑器的操作"""
        editor = self.get_current_editor()
        if editor:
            editor.redo()

    def format_sql(self):
        """格式化当前标签页的SQL"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        sql = editor.toPlainText()
        try:
            # Format SQL with uppercase keywords
            formatted_sql = sqlparse.format(sql,
                reindent=True,
                keyword_case='upper',
                strip_comments=True,
                use_space_around_operators=True,
                comma_first=True
            )
            # 使用 QTextCursor 替换文本，支持撤销功能
            cursor = editor.textCursor()
            cursor.beginEditBlock()
            cursor.select(cursor.SelectionType.Document)
            cursor.insertText(formatted_sql)
            cursor.endEditBlock()
        except Exception as e:
            QMessageBox.critical(self, '格式化错误', f'SQL格式化失败: {str(e)}')

    def convert_to_java_format(self):
        """将当前标签页的SQL转换为Java格式"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        sql = editor.toPlainText()
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
        cursor = editor.textCursor()
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
        """从Java格式转回SQL"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        java_code = editor.toPlainText()
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
            cursor = editor.textCursor()
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
        editor = self.get_current_editor()
        if not editor:
            return
            
        # 获取当前SQL语句
        sql = editor.toPlainText()
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
        cursor = editor.textCursor()
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
        editor = self.get_current_editor()
        if not editor:
            return
            
        # 获取当前文本
        java_code = editor.toPlainText()
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
        cursor = editor.textCursor()
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
        editor = self.get_current_editor()
        if not editor:
            return
            
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
        text = editor.toPlainText()
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
            cursor = editor.textCursor()
            # 开始复合编辑操作，这样整个替换操作会被视为一个撤销步骤
            cursor.beginEditBlock()
            # 选择所有文本
            cursor.select(cursor.SelectionType.Document)
            # 替换选中的文本
            cursor.insertText('\n'.join(result_lines))
            # 结束复合编辑操作
            cursor.endEditBlock()

    def open_file(self):
        """打开文件到新标签页"""
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
                
                # 创建新标签页并设置内容
                tab_editor = self.new_tab(file_path, text)
                tab_editor.is_modified = False  # 刚打开的文件标记为未修改
                self.update_tab_title(tab_editor)
                
            except Exception as e:
                QMessageBox.critical(self, '打开失败', f'文件解码失败: {str(e)}')
    
    def save_file(self):
        """保存当前标签页的文件"""
        current_tab = self.get_current_tab_editor()
        if not current_tab:
            return
            
        if current_tab.file_path:
            if current_tab.save():
                self.update_tab_title(current_tab)
                self.update_window_title()
            else:
                QMessageBox.critical(self, '保存失败', '文件保存失败')
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """另存为当前标签页的文件"""
        current_tab = self.get_current_tab_editor()
        if not current_tab:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, '另存为', '', 'SQL Files (*.sql);;All Files (*)')
        if file_path:
            if current_tab.save(file_path):
                self.update_tab_title(current_tab)
                self.update_window_title()
            else:
                QMessageBox.critical(self, '保存失败', '文件保存失败')
                
    def save_tab(self, tab_editor):
        """保存指定标签页"""
        if tab_editor.file_path:
            return tab_editor.save()
        else:
            # 如果没有文件路径，弹出另存为对话框
            file_path, _ = QFileDialog.getSaveFileName(self, '保存文件', '', 'SQL Files (*.sql);;All Files (*)')
            if file_path:
                return tab_editor.save(file_path)
        return False
    
    def exit_app(self):
        QApplication.instance().quit()

    def show_about(self):
        """
        显示关于对话框
        
        显示软件信息、版本、作者等详细信息
        """
        about_text = """
        <h2>SQL编辑器</h2>
        <p><b>版本:</b> 1.1.0</p>
        <p><b>描述:</b> 一个功能强大的SQL编辑和格式化工具</p>
        <br>
        <h3>功能特性:</h3>
        <ul>
            <li>多标签页支持 - 同时编辑多个文件</li>
            <li>SQL语法高亮显示</li>
            <li>SQL代码格式化</li>
            <li>Java代码格式转换</li>
            <li>参数填充功能</li>
            <li>注释对齐功能</li>
            <li>代码模板填充</li>
            <li>撤销/重做支持</li>
            <li>查找替换功能</li>
            <li>显示空格和Tab字符</li>
        </ul>
        <br>
        <h3>使用说明:</h3>
        <ul>
            <li>Ctrl+N: 新建标签页</li>
            <li>Ctrl+O: 打开文件到新标签页</li>
            <li>Ctrl+W: 关闭当前标签页</li>
            <li>点击标签栏+按钮: 创建新标签页</li>
        </ul>
        <br>
        <h3>作者信息:</h3>
        <p><b>作者:</b> 刘忠亮</p>
        <p><b>邮箱:</b> zhongliang.liu@lixil.com</p>
        <br>
        <p><b>开发时间:</b> 2025年</p>
        """
        
        QMessageBox.about(self, "关于 SQL编辑器", about_text)

    def show_find_replace_dialog(self):
        """
        显示查找替换对话框（非模态）
        如果当前有选中的文本，会自动填充到查找框中
        """
        current_editor = self.get_current_editor()
        if not current_editor:
            return
            
        # 如果已存在查找替换窗口且未关闭，则激活它
        if hasattr(self, '_find_replace_dialog') and self._find_replace_dialog is not None:
            self._find_replace_dialog.activateWindow()
            self._find_replace_dialog.raise_()
            return
        # 创建新对话框
        self._find_replace_dialog = FindReplaceDialog(self, current_editor)
        # 关闭时清理引用
        self._find_replace_dialog.finished.connect(lambda _: setattr(self, '_find_replace_dialog', None))
        self._find_replace_dialog.show()
        
    def toggle_whitespace_visibility(self):
        """切换空白字符显示状态"""
        show_whitespace = self.show_whitespace_action.isChecked()
        
        # 对所有标签页应用设置
        for i in range(self.tab_widget.count()):
            tab_editor = self.tab_widget.widget(i)
            if tab_editor and hasattr(tab_editor, 'editor'):
                tab_editor.editor.set_show_whitespace(show_whitespace)
