@echo off
echo ===== 大麦抢票助手APK构建工具 (WSL版) =====
echo.

REM 检查WSL是否安装
where wsl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到WSL（Windows Subsystem for Linux）
    echo 请先安装WSL，可参考：https://docs.microsoft.com/zh-cn/windows/wsl/install
    goto :end
)

echo [信息] 检测到WSL已安装
echo.
echo [提示] 脚本将使用WSL构建APK
echo 构建过程中可能需要您输入密码以授予sudo权限
echo.

REM 确保build_apk.sh有执行权限
echo [步骤1] 设置脚本执行权限...
wsl chmod +x build_apk.sh

echo [步骤2] 通过WSL执行构建脚本...
echo.
wsl ./build_apk.sh

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] APK构建失败，请检查上方日志获取详细信息
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