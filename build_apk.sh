#!/bin/bash

# 大麦抢票助手APK构建脚本
# 在Linux环境下运行此脚本

set -e  # 遇到错误立即停止

echo "===== 大麦抢票助手 APK 构建工具 ====="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请安装Python 3.7+"
    exit 1
fi

# 检查pip是否可用
if ! command -v pip3 &> /dev/null; then
    echo "[错误] 未找到pip3，请确保Python安装正确"
    exit 1
fi

echo "[步骤1] 安装必要的依赖项..."
pip3 install --upgrade pip
pip3 install buildozer==1.5.0
pip3 install cython==0.29.33
pip3 install kivy
pip3 install pillow
pip3 install kivymd
pip3 install requests
pip3 install pyyaml
pip3 install selenium==4.18.1
pip3 install webdriver-manager==4.0.1

echo "[步骤2] 安装系统依赖项..."
if [ "$(uname)" == "Linux" ]; then
    if command -v apt-get &> /dev/null; then
        echo "检测到 Debian/Ubuntu 系统，安装依赖..."
        sudo apt-get update
        sudo apt-get install -y \
            python3-pip \
            build-essential \
            git \
            python3 \
            python3-dev \
            ffmpeg \
            libsdl2-dev \
            libsdl2-image-dev \
            libsdl2-mixer-dev \
            libsdl2-ttf-dev \
            libportmidi-dev \
            libswscale-dev \
            libavformat-dev \
            libavcodec-dev \
            zlib1g-dev
    else
        echo "[警告] 无法确定您的Linux发行版，请手动安装所需依赖"
    fi
else
    echo "[警告] 非Linux环境，请确保已安装所需的系统依赖"
fi

echo "[步骤3] 创建资源文件..."
python3 -c "
from PIL import Image, ImageDraw
import os

# 确保目录存在
os.makedirs('assets', exist_ok=True)

# 创建图标
img = Image.new('RGBA', (512, 512), color=(51, 153, 255, 255))
d = ImageDraw.Draw(img)
d.ellipse((100, 100, 412, 412), fill=(255, 255, 255, 255))
d.text((200, 200), '票', fill=(51, 153, 255, 255), font_size=150)
img.save('assets/icon.png')
img.save('assets/presplash.png')
print('图标文件已创建')
"

echo "[步骤4] 准备构建环境..."
if [ ! -f "buildozer.spec" ]; then
    echo "[信息] 初始化buildozer环境..."
    buildozer init
else
    echo "[信息] buildozer.spec已存在"
fi

echo "[步骤5] 检查必要文件..."
if [ ! -d "damai" ]; then
    echo "[错误] damai目录不存在"
    exit 1
fi

if [ ! -f "damai/browser.py" ]; then
    echo "[错误] browser.py不存在"
    exit 1
fi

if [ ! -f "damai/__init__.py" ]; then
    echo "创建damai/__init__.py..."
    echo '"""大麦网API和浏览器自动化模块"""' > damai/__init__.py
    echo "__version__ = '1.1.0'" >> damai/__init__.py
    echo "__author__ = 'DamaiTicket'" >> damai/__init__.py
fi

if [ ! -d "damai_ticket" ]; then
    echo "[错误] damai_ticket目录不存在"
    exit 1
fi

if [ ! -f "damai_ticket/__init__.py" ]; then
    echo "创建damai_ticket/__init__.py..."
    echo '"""大麦抢票助手 - Android版"""' > damai_ticket/__init__.py
    echo "__version__ = '1.1.0'" >> damai_ticket/__init__.py
    echo "__author__ = 'DamaiTicket'" >> damai_ticket/__init__.py
fi

echo "[步骤6] 开始构建APK..."
echo "[警告] 第一次构建可能需要较长时间，请耐心等待"
echo ""
buildozer -v android debug

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] APK构建失败，请查看上方日志获取详细信息"
    exit 1
fi

echo ""
echo "[成功] APK构建完成!"
echo ""
echo "APK文件位于 bin 目录下"
echo "请将APK文件传输到Android手机安装使用"
echo "" 