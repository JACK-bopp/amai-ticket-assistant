#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
环境检查脚本
确保所有必要的目录和文件都存在
"""

import os
import sys
import json
import shutil

def print_section(title):
    """打印分隔符和标题"""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50 + "\n")

def check_directory(path, create=True):
    """检查目录是否存在，不存在则创建"""
    if os.path.exists(path):
        if os.path.isdir(path):
            print(f"✓ 目录 {path} 存在")
            return True
        else:
            print(f"✗ {path} 已存在但不是目录")
            return False
    else:
        if create:
            try:
                os.makedirs(path)
                print(f"✓ 已创建目录 {path}")
                return True
            except Exception as e:
                print(f"✗ 创建目录 {path} 失败: {str(e)}")
                return False
        else:
            print(f"✗ 目录 {path} 不存在")
            return False

def check_file(path, template_path=None):
    """检查文件是否存在，不存在则从模板创建"""
    if os.path.exists(path):
        if os.path.isfile(path):
            print(f"✓ 文件 {path} 存在")
            return True
        else:
            print(f"✗ {path} 已存在但不是文件")
            return False
    else:
        if template_path and os.path.exists(template_path):
            try:
                shutil.copy(template_path, path)
                print(f"✓ 已从模板创建文件 {path}")
                return True
            except Exception as e:
                print(f"✗ 从模板创建文件 {path} 失败: {str(e)}")
                return False
        else:
            print(f"✗ 文件 {path} 不存在")
            return False

def check_init_file(path):
    """检查__init__.py文件是否存在，不存在则创建"""
    init_file = os.path.join(path, "__init__.py")
    if os.path.exists(init_file):
        print(f"✓ 文件 {init_file} 存在")
        return True
    else:
        try:
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('"""大麦抢票助手模块"""\n\n')
                f.write('__version__ = "1.1.0"\n')
            print(f"✓ 已创建文件 {init_file}")
            return True
        except Exception as e:
            print(f"✗ 创建文件 {init_file} 失败: {str(e)}")
            return False

def check_config():
    """检查配置文件是否存在并有效"""
    config_path = "config.json"
    if not os.path.exists(config_path):
        if os.path.exists("config.example.json"):
            try:
                shutil.copy("config.example.json", config_path)
                print(f"✓ 已从样例创建配置文件 {config_path}")
            except Exception as e:
                print(f"✗ 从样例创建配置文件失败: {str(e)}")
                return False
        else:
            try:
                default_config = {
                    "account": {
                        "username": "13800138000",
                        "password": "your_password_here"
                    },
                    "target": {
                        "show_id": "721889827293",
                        "start_time": "2024-05-10 12:00:00"
                    },
                    "buyer": [
                        {
                            "name": "张三"
                        }
                    ],
                    "browser": {
                        "headless": False,
                        "window_size": {
                            "width": 1366,
                            "height": 768
                        }
                    }
                }
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                print(f"✓ 已创建默认配置文件 {config_path}")
            except Exception as e:
                print(f"✗ 创建默认配置文件失败: {str(e)}")
                return False
    
    # 验证配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必要的配置项
        required_keys = [
            ("account", "username"),
            ("account", "password"),
            ("target", "show_id"),
            ("target", "start_time"),
            ("buyer", 0, "name")
        ]
        
        for keys in required_keys:
            if len(keys) == 2:
                if keys[0] not in config or keys[1] not in config[keys[0]]:
                    print(f"✗ 配置文件缺少必要项: {keys[0]}.{keys[1]}")
                    return False
            elif len(keys) == 3:
                if keys[0] not in config or len(config[keys[0]]) <= keys[1] or keys[2] not in config[keys[0]][keys[1]]:
                    print(f"✗ 配置文件缺少必要项: {keys[0]}[{keys[1]}].{keys[2]}")
                    return False
        
        print("✓ 配置文件有效")
        return True
    except Exception as e:
        print(f"✗ 验证配置文件失败: {str(e)}")
        return False

def main():
    """主函数"""
    print_section("环境检查")
    
    # 检查必要的目录
    check_directory("assets")
    check_directory("damai")
    check_directory("damai_ticket")
    check_directory("docs")
    check_directory("examples")
    
    # 检查__init__.py文件
    check_init_file("damai")
    check_init_file("damai_ticket")
    
    # 检查必要的文件
    check_file("damai/browser.py")
    check_file("main.py")
    check_file("requirements.txt")
    check_file("buildozer.spec")
    
    # 检查配置文件
    check_config()
    
    print("\n环境检查完成")

if __name__ == "__main__":
    main() 