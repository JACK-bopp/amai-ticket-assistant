#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大麦抢票助手 Android APK构建测试脚本
"""

import os
import sys
import platform
import subprocess

def print_section(title):
    """打印分隔符和标题"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50 + "\n")

def check_environment():
    """检查构建环境"""
    print_section("检查环境")
    
    # 检查Python版本
    python_version = platform.python_version()
    print(f"Python版本: {python_version}")
    
    # 检查操作系统
    system = platform.system()
    release = platform.release()
    print(f"操作系统: {system} {release}")
    
    # 检查文件结构
    print("\n文件结构检查:")
    important_files = [
        "main.py", 
        "buildozer.spec", 
        "damai_ticket/__init__.py",
        "damai_ticket/app.py",
        "damai_ticket/api.py",
        "assets/icon.png", 
        "assets/presplash.png"
    ]
    
    for file in important_files:
        if os.path.exists(file):
            print(f"✓ {file} 已找到")
        else:
            print(f"✗ {file} 未找到")

def run_command(command):
    """运行命令并打印输出"""
    print(f"运行命令: {command}")
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # 实时输出命令执行结果
    for line in iter(process.stdout.readline, ''):
        print(line.strip())
    
    # 等待命令执行完成
    process.wait()
    return process.returncode

def setup_buildozer():
    """安装和配置buildozer"""
    print_section("安装和配置Buildozer")
    
    # 检查buildozer是否已安装
    try:
        import buildozer
        print("Buildozer已安装")
    except ImportError:
        print("安装Buildozer...")
        run_command("pip install buildozer")
    
    # 检查buildozer.spec文件
    if os.path.exists("buildozer.spec"):
        print("buildozer.spec文件已存在")
    else:
        print("初始化buildozer.spec...")
        run_command("buildozer init")

def build_apk():
    """构建APK"""
    print_section("构建APK")
    
    # 执行构建命令
    return run_command("buildozer -v android debug")

def main():
    """主函数"""
    print_section("大麦抢票助手 Android APK构建")
    
    # 检查环境
    check_environment()
    
    # 设置buildozer
    setup_buildozer()
    
    # 构建APK
    result = build_apk()
    
    if result == 0:
        print_section("构建成功!")
        apk_files = [f for f in os.listdir("bin") if f.endswith(".apk")]
        if apk_files:
            print(f"APK文件: bin/{apk_files[0]}")
        else:
            print("未找到构建的APK文件.")
    else:
        print_section("构建失败!")
        sys.exit(1)

if __name__ == "__main__":
    main() 