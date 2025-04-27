[app]
# 应用信息
title = 大麦抢票助手
package.name = damaiticket
package.domain = com.damai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,yaml
source.include_patterns = assets/*,damai_ticket/*,main.py,README*
source.exclude_dirs = .buildozer,bin,WIT-SecondHand,mnt,venv,.venv,upload_files,risk,__pycache__
source.exclude_patterns = *.pyc,*.pyo,*.swp,*.swo,*.git*
version = 1.0.0

# 应用图标和启动画面
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

# 应用权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 程序依赖
requirements = python3,kivy==2.2.1,requests==2.31.0,pyyaml==6.0.1,pillow==9.5.0,certifi,charset-normalizer,idna,urllib3

# 应用界面和行为
orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk = 25c
android.arch = arm64-v8a

# 配置文件路径
android.services = DATA_INPUT_SERVICE

# Android构建相关
android.accept_sdk_license = True
android.gradle_dependencies = org.chromium:chromium-webview:83.0.4103.106
p4a.bootstrap = sdl2

# 主要入口点
android.entrypoint = main:DamaiTicketApp

# 提示和帮助文本
p4a.hook = 

# 构建相关配置
[buildozer]
log_level = 2
warn_on_root = 1
# 在GitHub Actions中需要设置为False
offline = False

# 自定义构建命令
# 构建命令: buildozer android debug