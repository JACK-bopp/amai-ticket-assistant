[app]
# 应用信息
title = 大麦抢票助手
package.name = damaiticket
package.domain = com.damai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,yaml
version = 1.0.0

# 应用图标和启动画面
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

# 应用权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 程序依赖
requirements = python3,kivy==2.2.1,requests==2.31.0,pyyaml==6.0.1,pillow==9.5.0,certifi==2023.7.22,charset-normalizer==3.3.2,idna==3.6,urllib3==2.0.7,kivy_deps.sdl2,kivy_deps.glew

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
# 使用main.py作为入口点
android.entrypoint = main

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