@echo off
echo 正在启动大麦抢票助手...
python damai_app.py
if %ERRORLEVEL% NEQ 0 (
    echo 启动失败，请确保已安装Python和必要的依赖
    echo 可尝试运行: pip install -r requirements.txt
    pause
) 