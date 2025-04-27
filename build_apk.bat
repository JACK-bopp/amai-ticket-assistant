@echo off
echo ===== 大麦抢票助手APK构建工具 =====
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

echo [步骤1] 安装必要的依赖项...
python -m pip install buildozer Cython==0.29.33 pillow kivymd kivy requests

echo [步骤2] 创建资源文件...
python create_assets.py

echo [步骤3] 准备构建环境...
if not exist ".buildozer" (
    echo [信息] 初始化buildozer环境...
    buildozer init
) else (
    echo [信息] buildozer环境已存在
)

echo [步骤4] 开始构建APK...
echo [警告] 第一次构建可能需要较长时间，请耐心等待
echo.
buildozer -v android debug

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] APK构建失败，请查看上方日志获取详细信息
    goto :end
)

echo.
echo [成功] APK构建完成!
echo.
echo APK文件位于 bin 目录下
echo 请将APK文件传输到Android手机安装使用
echo.

:end
pause 