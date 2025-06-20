# SQL编辑器（sapfront-tools）

## 项目简介

本项目是一个基于 PySide6 的桌面 SQL 编辑与格式化工具，支持 SQL 语法高亮、格式化、Java 代码转换、参数填充、注释对齐、代码模板填充、查找替换等多种实用功能，适用于日常 SQL 编写、调试和代码转换场景。

## 主要功能

- **SQL 语法高亮**：支持 SQL 关键字、字符串、注释的高亮显示，提升代码可读性。
- **SQL 格式化**：一键美化 SQL 代码，关键字大写、缩进规范。
- **Java 代码格式转换**：可将 SQL 转为 Java 字符串拼接代码，或反向还原。
- **参数填充**：支持将 SQL 中的 `?` 占位符批量替换为实际参数。
- **注释对齐**：对 Java 代码中的注释进行智能对齐，支持单行和 Javadoc 注释。
- **代码模板填充**：支持自定义模板批量生成代码。
- **查找与替换**：支持正则、区分大小写、批量替换等。
- **撤销/重做**：支持多步撤销与重做。
- **文件操作**：支持 SQL 文件的打开、保存、另存为。

## 安装与依赖

### 依赖环境
- Python >= 3.13
- [PySide6](https://pypi.org/project/PySide6/) >= 6.9.1
- [chardet](https://pypi.org/project/chardet/) >= 5.2.0
- [sqlparse](https://pypi.org/project/sqlparse/) == 0.4.4

### 安装依赖

```bash
pip install -r requirements.txt
```
或根据 `pyproject.toml` 安装：
```bash
pip install .
```

## 启动方法

### 方式一：命令行启动

```bash
python main.py
```

### 方式二：Windows 批处理启动

双击 `start_sql_formatter.bat` 即可。

## 目录结构说明

- `main.py`：程序入口，启动主窗口。
- `SQLFormatterApp.py`：主界面与核心逻辑，集成所有功能。
- `CodeEditor.py`：自定义代码编辑器，支持行号显示。
- `SQLHighlighter.py`：SQL 语法高亮模块。
- `FindReplaceDialog.py`：查找与替换对话框。
- `icons/`：图标资源。
- `pyproject.toml`、`uv.lock`：依赖与环境配置。

## 主要模块说明

### 1. SQLFormatterApp
- 主窗口类，集成菜单栏、编辑区、功能按钮。
- 支持 SQL 格式化、Java 转换、参数填充、注释对齐、模板填充、查找替换等。
- 支持文件的打开、保存、另存为。

### 2. CodeEditor
- 继承自 QPlainTextEdit，支持左侧行号显示。
- 响应窗口缩放、滚动等事件，自动调整行号区宽度。

### 3. SQLHighlighter
- 继承 QSyntaxHighlighter，实现 SQL 关键字、字符串、注释的高亮。
- 支持主流 SQL 关键字。

### 4. FindReplaceDialog
- 查找与替换对话框，支持正则、区分大小写、批量替换。
- 实时高亮所有匹配项，支持定位、替换当前/全部。

## 作者信息

- 作者：刘忠亮
- 邮箱：zhongliang.liu@lixil.com
- 开发时间：2025年

## 许可证

本项目仅供学习与内部使用，禁止商业用途。
