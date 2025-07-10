@echo off
echo ========================================
echo SQL Formatter App 打包脚本
echo ========================================
echo.

REM 检查PyInstaller是否已安装
echo 正在检查PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller未安装，正在安装...
    python -m pip install pyinstaller
) else (
    echo PyInstaller已安装
)
echo.

REM 清理之前的构建
echo 正在清理之前的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM 开始打包
echo 开始打包程序...
echo 这可能需要几分钟时间，请耐心等待...
echo.

REM 使用spec文件打包
pyinstaller main.spec --clean

echo.
if errorlevel 1 (
    echo [错误] 打包失败！
    echo 请检查错误信息并重试。
    pause
    exit /b 1
) else (
    echo ========================================
    echo 打包成功！
    echo.
    echo 可执行文件位置：
    echo dist\SQLFormatterApp\SQLFormatterApp.exe
    echo.
    echo 文件夹包含所有必要的依赖文件。
    echo 您可以将整个 SQLFormatterApp 文件夹复制到其他电脑使用。
    echo ========================================
)

echo.
echo 按任意键退出...
pause >nul