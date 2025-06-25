# SQL编辑器（sapfront-tools）

<div align="center">

![SQL编辑器](icons/Editor.png)

**一个功能强大的SQL编辑和格式化桌面工具**

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.9.1+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-Internal%20Use-red.svg)](#许可证)

[功能特性](#功能特性) • [快速开始](#快速开始) • [文档](#文档) • [截图展示](#截图展示)

</div>

## 项目简介

SQL编辑器是一个基于PySide6开发的专业桌面SQL编辑工具，专为提高SQL开发效率而设计。它集成了SQL语法高亮、代码格式化、Java代码转换、参数填充、查找替换等多种实用功能，是SQL开发者和数据库管理员的得力助手。

## 功能特性

### 🎨 编辑体验
- **多标签页**: 支持同时打开和编辑多个SQL文件，提高工作效率
- **语法高亮**: 支持SQL关键字、字符串、注释的智能高亮显示
- **行号显示**: 左侧行号区域，便于代码定位和调试
- **深色主题**: 护眼的深色编辑界面，长时间编码不疲劳
- **撤销重做**: 支持多步撤销与重做，操作更安全

### 🔧 核心功能
- **SQL格式化**: 一键美化SQL代码，关键字大写、智能缩进
- **Java代码转换**: SQL与Java StringBuffer代码双向转换
- **参数填充**: 批量替换SQL中的`?`占位符为实际参数值
- **注释对齐**: 智能对齐Java代码中的注释，提升代码美观度
- **代码模板**: 支持自定义模板批量生成重复性代码

### 🔍 查找替换
- **实时高亮**: 自动高亮所有匹配项，可视化查找结果
- **正则支持**: 强大的正则表达式匹配功能
- **批量替换**: 支持一键替换所有匹配项
- **大小写敏感**: 可选的大小写敏感匹配

### 📁 文件管理
- **智能编码**: 自动检测文件编码，支持UTF-8、GBK等多种格式
- **文件操作**: 完整的打开、保存、另存为功能
- **格式支持**: 专门优化SQL文件的读写处理

## 快速开始

### 环境要求

- **Python**: >= 3.13
- **操作系统**: Windows 10/11, macOS, Linux

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd sapfront-tools
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
   或使用项目配置安装：
   ```bash
   pip install .
   ```

3. **启动程序**
   
   **方式一：Python命令行**
   ```bash
   python main.py
   ```
   
   **方式二：Windows批处理**
   ```bash
   # 双击运行
   start_sql_formatter.bat
   ```

### 快速使用

1. **编写SQL**: 在编辑器中输入或粘贴SQL代码
2. **格式化**: 按`Ctrl+F`格式化SQL代码
3. **转换**: 按`Ctrl+J`转换为Java格式
4. **查找**: 按`Ctrl+H`打开查找替换对话框

## 文档

### 📚 完整文档
- [📖 用户手册](docs/用户手册.md) - 详细的使用指南和功能说明
- [🔧 技术文档](docs/技术文档.md) - 架构设计和技术实现
- [📋 API文档](docs/API文档.md) - 开发者接口参考

### 🎯 快捷键参考

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 新建标签页 | `Ctrl+N` | 创建新的编辑标签页 |
| 打开文件 | `Ctrl+O` | 打开SQL文件到新标签页 |
| 保存文件 | `Ctrl+S` | 保存当前标签页文件 |
| 另存为 | `Ctrl+Shift+S` | 另存为当前文件 |
| 关闭标签页 | `Ctrl+W` | 关闭当前标签页 |
| 格式化SQL | `Ctrl+F` | 美化SQL代码 |
| 转换Java格式 | `Ctrl+J` | SQL转Java代码 |
| 从Java转回SQL | `Ctrl+K` | Java代码转SQL |
| 查找替换 | `Ctrl+H` | 打开查找替换 |
| 填充参数 | `Ctrl+P` | 替换?占位符 |
| 对齐注释 | `Ctrl+L` | 对齐代码注释 |
| 代码填充 | `Ctrl+M` | 模板代码生成 |

## 项目结构

```
sapfront-tools/
├── 📁 docs/                    # 文档目录
│   ├── 📄 用户手册.md           # 用户使用指南
│   ├── 📄 技术文档.md           # 技术架构文档
│   └── 📄 API文档.md            # 开发者API参考
├── 📁 icons/                   # 图标资源
│   ├── 🖼️ app.ico              # 应用程序图标
│   └── 🖼️ Editor.png           # 编辑器图标
├── 📄 main.py                  # 🚀 程序入口
├── 📄 SQLFormatterApp.py       # 🏠 主应用程序
├── 📄 CodeEditor.py            # ✏️ 代码编辑器
├── 📄 SQLHighlighter.py        # 🎨 语法高亮器
├── 📄 FindReplaceDialog.py     # 🔍 查找替换对话框
├── 📄 pyproject.toml           # ⚙️ 项目配置
├── 📄 uv.lock                  # 🔒 依赖锁定
├── 📄 start_sql_formatter.bat  # 🪟 Windows启动脚本
└── 📄 README.md                # 📖 项目说明
```

## 截图展示

### 主界面
```
┌─────────────────────────────────────────────────────────────┐
│ 文件(F)  编辑(E)  工具(T)  帮助(H)                            │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────┐┌─────────┐┌─────────┐                    [×] [+] │ ← 多标签页
│ │ users.sql││ query.sql││ 未命名 *│                           │
│ └─────────┘└─────────┘└─────────┘                           │
├─────────────────────────────────────────────────────────────┤
│ ┌───┐ ┌─────────────────────────────────────────────────┐   │
│ │ 1 │ │ SELECT u.id,                                    │   │
│ │ 2 │ │        u.name,                                  │   │
│ │ 3 │ │        u.email                                  │   │
│ │ 4 │ │ FROM users u                                    │   │
│ │ 5 │ │ WHERE u.status = 'active'                       │   │
│ │ 6 │ │   AND u.created_date >= '2023-01-01'            │   │
│ │ 7 │ │ ORDER BY u.created_date DESC                    │   │
│ └───┘ └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 多标签页特性
- **标签页管理**: 每个文件在独立的标签页中打开
- **拖拽排序**: 可以拖拽标签页改变顺序
- **关闭按钮**: 每个标签页都有关闭按钮
- **修改标识**: 未保存的文件标签页显示 * 标记
- **+按钮**: 标签栏右侧的+按钮，一键创建新标签页

### 功能演示

**SQL格式化前后对比:**
```sql
-- 格式化前
select id,name,email from users where status='active' and created_date>='2023-01-01'

-- 格式化后
SELECT id,
       name,
       email
FROM users
WHERE status = 'active'
  AND created_date >= '2023-01-01'
```

**Java代码转换:**
```java
// SQL转Java
StringBuffer sb = new StringBuffer();
sb.append(" SELECT * FROM users ");
sb.append(" WHERE id = ? ");
sb.append(" AND status = 'active' ");
```

## 技术架构

### 核心技术栈
- **GUI框架**: PySide6 (Qt6的Python绑定)
- **SQL解析**: sqlparse 0.4.4
- **编码检测**: chardet 5.2.0
- **Python版本**: 3.13+

### 架构特点
- **模块化设计**: 清晰的模块分离，易于维护和扩展
- **事件驱动**: 基于Qt信号槽机制的响应式架构
- **插件友好**: 预留扩展接口，支持功能插件开发
- **性能优化**: 针对大文件和复杂SQL的性能优化

## 开发指南

### 环境搭建
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
pip install -e .
```

### 代码规范
- 遵循PEP 8 Python代码规范
- 使用类型注解提高代码可读性
- 编写完整的文档字符串
- 保持模块间的低耦合

### 扩展开发
参考[API文档](docs/API文档.md)了解如何：
- 添加新的语法高亮规则
- 创建自定义功能插件
- 扩展文件格式支持
- 自定义主题和样式

## 版本历史

### v1.0.0 (2025年)
- ✨ 初始版本发布
- 🎨 SQL语法高亮支持
- 🔧 SQL格式化功能
- 🔄 Java代码转换
- 🔍 查找替换功能
- 📁 文件操作支持
- ⚡ 参数填充和代码模板

## 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork项目** 到您的GitHub账户
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

### 贡献类型
- 🐛 Bug修复
- ✨ 新功能开发
- 📚 文档改进
- 🎨 UI/UX优化
- ⚡ 性能优化

## 常见问题

### Q: 程序启动失败怎么办？
**A**: 请检查Python版本(>=3.13)和依赖包安装情况，尝试重新安装PySide6。

### Q: 文件打开时出现乱码？
**A**: 程序会自动检测编码，如仍有问题，建议将文件转换为UTF-8编码。

### Q: 如何添加自定义SQL关键字？
**A**: 修改`SQLHighlighter.py`中的`keywords`列表，添加新的关键字。

更多问题请参考[用户手册](docs/用户手册.md)的常见问题章节。

## 技术支持

- 📧 **邮箱**: zhongliang.liu@lixil.com
- 📖 **文档**: 查看`docs/`目录下的详细文档
- 🐛 **Bug报告**: 在项目仓库中提交Issue
- 💡 **功能建议**: 欢迎提交Feature Request

## 作者信息

<div align="center">

**刘忠亮**
*软件开发工程师*

📧 zhongliang.liu@lixil.com
🗓️ 开发时间：2025年

</div>

## 许可证

本项目仅供学习与内部使用，禁止商业用途。

---

<div align="center">

**感谢使用SQL编辑器！**
*如果这个项目对您有帮助，请给我们一个⭐*

[⬆ 回到顶部](#sql编辑器sapfront-tools)

</div>
