@echo off
chcp 65001 >nul
echo ========================================
echo    视频下载器 - 打包脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

REM 检查并安装依赖
echo [1/3] 安装依赖包...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

REM 安装PyInstaller
echo [2/3] 检查PyInstaller...
pip install pyinstaller --quiet

REM 打包
echo [3/3] 开始打包...
echo.

pyinstaller --noconfirm --onefile --windowed ^
    --name "视频下载器" ^
    --icon "NONE" ^
    --add-data "gui;gui" ^
    --add-data "core;core" ^
    --add-data "utils;utils" ^
    --hidden-import "yt_dlp" ^
    --hidden-import "customtkinter" ^
    --hidden-import "PIL" ^
    --collect-all "customtkinter" ^
    main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包完成！
echo    输出文件: dist\视频下载器.exe
echo ========================================
echo.
pause
