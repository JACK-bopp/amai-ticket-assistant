@echo off
echo ===== 大麦抢票助手 =====
echo.

REM 检查Python是否安装
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到Python，请安装Python 3.7+
    goto :end
)

REM 检查pip是否可用
python -m pip --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到pip，请确保Python安装正确
    goto :end
)

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo [步骤1] 创建虚拟环境...
    python -m venv venv
    echo [步骤2] 安装依赖...
    call venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo [信息] 使用已存在的虚拟环境
    call venv\Scripts\activate
)

echo [步骤3] 启动应用...
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 应用启动失败，请查看上方错误信息
) else (
    echo.
    echo [信息] 应用已关闭
)

:end
pause 