# SQL编辑器 API文档

## 概述

本文档描述了SQL编辑器项目中各个模块的API接口，供开发者进行二次开发或集成使用。

## 模块结构

```
sapfront-tools/
├── main.py                 # 应用程序入口
├── SQLFormatterApp.py      # 主应用程序类
├── CodeEditor.py           # 代码编辑器组件
├── SQLHighlighter.py       # SQL语法高亮器
└── FindReplaceDialog.py    # 查找替换对话框
```

## 主要类和接口

### 1. SQLFormatterApp 类

**文件**: `SQLFormatterApp.py`  
**继承**: `QMainWindow`  
**描述**: 主应用程序窗口，包含所有核心功能

#### 构造函数

```python
def __init__(self):
    """
    初始化SQL格式化应用程序
    
    功能:
    - 创建主窗口界面
    - 初始化菜单栏和工具栏
    - 设置代码编辑器
    - 配置语法高亮器
    """
```

#### 核心方法

##### format_sql()
```python
def format_sql(self) -> None:
    """
    格式化SQL代码
    
    功能:
    - 使用sqlparse库格式化SQL
    - 关键字转大写
    - 自动缩进和换行
    - 支持撤销操作
    
    异常:
    - Exception: SQL解析错误时打印错误信息
    """
```

##### convert_to_java_format()
```python
def convert_to_java_format(self) -> None:
    """
    将SQL转换为Java StringBuffer格式
    
    功能:
    - 将SQL语句转换为Java字符串拼接代码
    - 自动处理引号转义
    - 保持原有格式
    
    输出格式:
    StringBuffer sb = new StringBuffer();
    sb.append(" SQL_LINE_1 ");
    sb.append(" SQL_LINE_2 ");
    """
```

##### convert_back_to_sql()
```python
def convert_back_to_sql(self) -> None:
    """
    从Java格式转回SQL
    
    功能:
    - 从Java StringBuffer代码中提取SQL
    - 去除Java语法包装
    - 恢复原始SQL格式
    
    处理逻辑:
    - 提取引号内的内容
    - 去除多余空白
    - 重新组合SQL语句
    """
```

##### fill_sql_parameters()
```python
def fill_sql_parameters(self) -> None:
    """
    填充SQL参数
    
    功能:
    - 将?占位符替换为实际参数
    - 参数数量验证
    - 自动添加单引号
    
    用户交互:
    - 弹出输入对话框
    - 接受逗号分隔的参数
    
    异常处理:
    - 参数数量不匹配时显示警告
    """
```

##### align_comments()
```python
def align_comments(self) -> None:
    """
    对齐代码注释
    
    功能:
    - Tab转换为4个空格
    - 智能计算注释对齐位置
    - 支持单行注释(//)
    
    算法:
    1. 扫描所有行，找到注释位置
    2. 计算最大注释位置
    3. 对齐所有注释到统一位置
    """
```

##### fill_code()
```python
def fill_code(self) -> None:
    """
    代码模板填充
    
    功能:
    - 使用自定义模板生成代码
    - 支持{0}, {1}等占位符
    - 处理Tab分隔的数据
    
    模板语法:
    - {0}, {1}, {2}... 对应数据列
    - 支持多行模板
    
    异常处理:
    - 模板占位符与数据不匹配时显示错误
    """
```

#### 文件操作方法

##### open_file()
```python
def open_file(self) -> None:
    """
    打开文件
    
    功能:
    - 文件选择对话框
    - 自动编码检测
    - 支持多种编码格式
    
    编码支持:
    - UTF-8 (优先)
    - GBK/GB18030 (备选)
    - 自动检测 (chardet)
    
    异常处理:
    - 文件读取失败时显示错误对话框
    """
```

##### save_file()
```python
def save_file(self) -> None:
    """
    保存文件
    
    功能:
    - 保存到当前文件路径
    - 如无当前文件则调用另存为
    - 使用UTF-8编码保存
    """
```

##### save_as_file()
```python
def save_as_file(self) -> None:
    """
    另存为文件
    
    功能:
    - 文件保存对话框
    - 设置新的当前文件路径
    - 更新窗口标题
    """
```

#### 界面方法

##### show_about()
```python
def show_about(self) -> None:
    """
    显示关于对话框
    
    内容:
    - 软件版本信息
    - 功能特性列表
    - 作者信息
    - 开发时间
    """
```

##### show_find_replace_dialog()
```python
def show_find_replace_dialog(self) -> None:
    """
    显示查找替换对话框
    
    功能:
    - 创建非模态对话框
    - 自动填充选中文本
    - 防止重复创建
    """
```

### 2. CodeEditor 类

**文件**: `CodeEditor.py`  
**继承**: `QPlainTextEdit`  
**描述**: 带行号的代码编辑器

#### 构造函数

```python
def __init__(self, parent=None):
    """
    初始化代码编辑器
    
    参数:
    - parent (QWidget): 父组件
    
    功能:
    - 创建行号区域
    - 连接信号和槽
    - 初始化行号宽度
    """
```

#### 核心方法

##### line_number_area_width()
```python
def line_number_area_width(self) -> int:
    """
    计算行号区域宽度
    
    返回:
    - int: 行号区域的像素宽度
    
    算法:
    - 计算最大行号的位数
    - 根据字体宽度计算所需空间
    - 添加适当的边距
    """
```

##### update_line_number_area_width()
```python
def update_line_number_area_width(self) -> None:
    """
    更新行号区域宽度
    
    功能:
    - 重新计算行号区域宽度
    - 设置编辑器左边距
    - 响应文本变化
    """
```

##### line_number_area_paint_event()
```python
def line_number_area_paint_event(self, event) -> None:
    """
    绘制行号区域
    
    参数:
    - event (QPaintEvent): 绘制事件
    
    功能:
    - 绘制行号背景
    - 绘制行号文本
    - 处理可见区域
    """
```

### 3. LineNumberArea 类

**文件**: `CodeEditor.py`  
**继承**: `QWidget`  
**描述**: 行号显示区域

#### 构造函数

```python
def __init__(self, editor):
    """
    初始化行号区域
    
    参数:
    - editor (CodeEditor): 关联的代码编辑器
    """
```

#### 方法

##### sizeHint()
```python
def sizeHint(self) -> QSize:
    """
    返回推荐尺寸
    
    返回:
    - QSize: 推荐的组件尺寸
    """
```

##### paintEvent()
```python
def paintEvent(self, event) -> None:
    """
    处理绘制事件
    
    参数:
    - event (QPaintEvent): 绘制事件
    
    功能:
    - 委托给编辑器的绘制方法
    """
```

### 4. SQLHighlighter 类

**文件**: `SQLHighlighter.py`  
**继承**: `QSyntaxHighlighter`  
**描述**: SQL语法高亮器

#### 构造函数

```python
def __init__(self, parent=None):
    """
    初始化SQL语法高亮器
    
    参数:
    - parent (QTextDocument): 父文档对象
    
    功能:
    - 初始化格式配置
    - 设置关键字列表
    - 配置颜色方案
    """
```

#### 属性

##### 格式配置
```python
# 关键字格式 (蓝色)
self.keyword_format: QTextCharFormat

# 字符串格式 (红色)  
self.string_format: QTextCharFormat

# 注释格式 (绿色)
self.comment_format: QTextCharFormat
```

##### 关键字列表
```python
self.keywords: List[str]
# 包含75+个SQL关键字
# 如: SELECT, FROM, WHERE, INSERT, UPDATE, DELETE 等
```

#### 核心方法

##### highlightBlock()
```python
def highlightBlock(self, text: str) -> None:
    """
    高亮文本块
    
    参数:
    - text (str): 需要高亮的文本行
    
    功能:
    - 高亮SQL关键字
    - 高亮字符串字面量
    - 高亮行注释
    
    算法:
    1. 扫描关键字并应用关键字格式
    2. 查找字符串(单引号包围)并应用字符串格式
    3. 查找注释(--开头)并应用注释格式
    """
```

### 5. FindReplaceDialog 类

**文件**: `FindReplaceDialog.py`  
**继承**: `QDialog`  
**描述**: 查找替换对话框

#### 构造函数

```python
def __init__(self, parent=None, text_editor=None):
    """
    初始化查找替换对话框
    
    参数:
    - parent (QWidget): 父组件
    - text_editor (QTextEdit): 目标文本编辑器
    
    功能:
    - 创建用户界面
    - 设置信号连接
    - 初始化高亮格式
    """
```

#### 属性

```python
# 目标文本编辑器
self.text_editor: QTextEdit

# 高亮格式
self.highlight_format: QTextCharFormat

# 当前高亮列表
self.current_highlights: List[QTextCursor]
```

#### 核心方法

##### highlight_all_matches()
```python
def highlight_all_matches(self) -> None:
    """
    高亮所有匹配项
    
    功能:
    - 清除之前的高亮
    - 根据查找条件查找所有匹配
    - 应用高亮格式
    - 更新状态信息
    
    支持:
    - 正则表达式匹配
    - 大小写敏感选项
    - 实时更新
    """
```

##### find_next()
```python
def find_next(self, backward: bool = False) -> None:
    """
    查找下一个匹配项
    
    参数:
    - backward (bool): 是否反向查找
    
    功能:
    - 从当前位置查找
    - 支持循环查找
    - 自动选中匹配文本
    - 更新光标位置
    """
```

##### find_previous()
```python
def find_previous(self) -> None:
    """
    查找上一个匹配项
    
    功能:
    - 调用find_next(backward=True)
    """
```

##### replace_current()
```python
def replace_current(self) -> None:
    """
    替换当前选中项
    
    功能:
    - 检查是否有选中文本
    - 执行替换操作
    - 支持撤销
    - 更新高亮显示
    """
```

##### replace_all()
```python
def replace_all(self) -> None:
    """
    替换所有匹配项
    
    功能:
    - 批量替换所有匹配
    - 支持正则表达式替换
    - 显示替换数量
    - 支持撤销
    """
```

##### clear_highlights()
```python
def clear_highlights(self) -> None:
    """
    清除所有高亮
    
    功能:
    - 重置文本格式
    - 清空高亮列表
    - 更新视图
    """
```

## 事件和信号

### SQLFormatterApp 信号

```python
# 文件操作信号
file_opened = Signal(str)      # 文件打开时发出
file_saved = Signal(str)       # 文件保存时发出

# 编辑操作信号  
text_changed = Signal()        # 文本内容改变时发出
format_applied = Signal()      # 格式化应用时发出
```

### CodeEditor 信号

```python
# 继承自QPlainTextEdit的信号
blockCountChanged = Signal(int)    # 行数改变
updateRequest = Signal(QRect, int) # 更新请求
textChanged = Signal()             # 文本改变
```

### FindReplaceDialog 信号

```python
# 查找替换信号
find_performed = Signal(str)       # 执行查找时发出
replace_performed = Signal(str, str) # 执行替换时发出
```

## 配置和常量

### 颜色配置

```python
# SQLHighlighter 颜色
KEYWORD_COLOR = "#3D96D6"    # 关键字颜色 (蓝色)
STRING_COLOR = "#DA8F70"     # 字符串颜色 (红色)
COMMENT_COLOR = "#6DB487"    # 注释颜色 (绿色)

# CodeEditor 颜色
BACKGROUND_COLOR = "#2b2b2b"  # 编辑器背景色
TEXT_COLOR = "#a9b7c6"       # 文本颜色
LINE_NUMBER_BG = "#252526"   # 行号背景色
LINE_NUMBER_FG = "#858585"   # 行号前景色

# FindReplaceDialog 颜色
HIGHLIGHT_COLOR = "#FFFF00"  # 高亮背景色 (黄色)
```

### 字体配置

```python
# 编辑器字体
EDITOR_FONT_FAMILY = "Consolas"
EDITOR_FONT_SIZE = 11

# 行号字体
LINE_NUMBER_FONT_FAMILY = "Consolas"  
LINE_NUMBER_FONT_SIZE = 13
```

### 快捷键配置

```python
# 文件操作
SHORTCUT_OPEN = "Ctrl+O"
SHORTCUT_SAVE = "Ctrl+S"
SHORTCUT_QUIT = "Ctrl+Q"

# 编辑操作
SHORTCUT_UNDO = "Ctrl+Z"
SHORTCUT_REDO = "Ctrl+Y"
SHORTCUT_FIND_REPLACE = "Ctrl+H"

# 工具功能
SHORTCUT_FORMAT_SQL = "Ctrl+F"
SHORTCUT_TO_JAVA = "Ctrl+J"
SHORTCUT_FROM_JAVA = "Ctrl+K"
SHORTCUT_ALIGN_COMMENTS = "Ctrl+L"
SHORTCUT_FILL_PARAMS = "Ctrl+P"
SHORTCUT_FILL_CODE = "Ctrl+M"

# 帮助
SHORTCUT_ABOUT = "F1"
```

## 扩展接口

### 自定义语法高亮

```python
class CustomHighlighter(SQLHighlighter):
    """
    自定义语法高亮器
    
    扩展方法:
    - 添加新的关键字类型
    - 自定义颜色方案
    - 支持其他语言语法
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 添加自定义关键字
        self.custom_keywords = ["CUSTOM_KEYWORD"]
        
    def highlightBlock(self, text):
        # 调用父类方法
        super().highlightBlock(text)
        # 添加自定义高亮逻辑
        self.highlight_custom_syntax(text)
        
    def highlight_custom_syntax(self, text):
        """自定义语法高亮逻辑"""
        pass
```

### 自定义功能插件

```python
class PluginInterface:
    """
    插件接口定义
    """
    
    def get_name(self) -> str:
        """返回插件名称"""
        pass
        
    def get_description(self) -> str:
        """返回插件描述"""
        pass
        
    def execute(self, text_editor: QTextEdit) -> None:
        """执行插件功能"""
        pass

class CustomPlugin(PluginInterface):
    """
    自定义插件示例
    """
    
    def get_name(self):
        return "自定义功能"
        
    def get_description(self):
        return "这是一个自定义功能插件"
        
    def execute(self, text_editor):
        # 实现自定义功能
        text = text_editor.toPlainText()
        # 处理文本...
        text_editor.setPlainText(processed_text)
```

## 错误处理

### 异常类型

```python
class SQLFormatterError(Exception):
    """SQL格式化错误"""
    pass

class FileEncodingError(Exception):
    """文件编码错误"""
    pass

class TemplateError(Exception):
    """模板处理错误"""
    pass
```

### 错误处理示例

```python
try:
    # SQL格式化
    formatted_sql = sqlparse.format(sql, **options)
except Exception as e:
    QMessageBox.critical(self, "格式化错误", f"SQL格式化失败: {str(e)}")
    
try:
    # 文件读取
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        text = self.decode_file(raw_data)
except FileEncodingError as e:
    QMessageBox.warning(self, "编码错误", f"文件编码检测失败: {str(e)}")
except IOError as e:
    QMessageBox.critical(self, "文件错误", f"文件读取失败: {str(e)}")
```

## 性能优化建议

### 大文件处理

```python
# 使用QPlainTextEdit而非QTextEdit
# 按需加载和渲染
# 限制语法高亮的文本长度

def optimized_highlight(self, text):
    """优化的语法高亮"""
    if len(text) > 10000:  # 大文件时简化高亮
        self.simple_highlight(text)
    else:
        self.full_highlight(text)
```

### 内存管理

```python
# 及时清理资源
def cleanup_resources(self):
    """清理资源"""
    self.clear_highlights()
    self.text_editor.document().clear()
    
# 使用弱引用避免循环引用
import weakref
self.parent_ref = weakref.ref(parent)
```

## 测试接口

### 单元测试示例

```python
import unittest
from SQLFormatterApp import SQLFormatterApp

class TestSQLFormatter(unittest.TestCase):
    
    def setUp(self):
        self.app = SQLFormatterApp()
        
    def test_format_sql(self):
        """测试SQL格式化"""
        input_sql = "select * from users where id=1"
        expected = "SELECT *\nFROM users\nWHERE id = 1"
        
        self.app.sql_text_edit.setPlainText(input_sql)
        self.app.format_sql()
        result = self.app.sql_text_edit.toPlainText()
        
        self.assertEqual(result.strip(), expected.strip())
        
    def test_java_conversion(self):
        """测试Java代码转换"""
        input_sql = "SELECT * FROM users"
        self.app.sql_text_edit.setPlainText(input_sql)
        self.app.convert_to_java_format()
        
        result = self.app.sql_text_edit.toPlainText()
        self.assertIn("StringBuffer sb", result)
        self.assertIn("sb.append", result)
```

---

**注意**: 本API文档基于当前版本，后续版本可能会有变化。建议在使用前查看最新的源代码注释。