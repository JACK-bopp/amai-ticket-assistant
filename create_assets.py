#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
此脚本用于创建APK所需的图标和启动画面
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(output_path, size=(512, 512)):
    """创建应用图标"""
    # 创建一个新的RGBA图像
    icon = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon)
    
    # 绘制圆形背景
    circle_diameter = min(size)
    draw.ellipse((0, 0, circle_diameter-1, circle_diameter-1), fill=(51, 153, 255))
    
    # 在圆内写入文字
    try:
        # 尝试加载中文字体
        font = ImageFont.truetype("simhei.ttf", 200)
    except IOError:
        # 如果没有找到中文字体，使用默认字体
        font = ImageFont.load_default()
    
    # 文字内容和颜色
    text = "票"
    text_color = (255, 255, 255)
    
    # 获取文本大小
    text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else (150, 150)
    
    # 计算文本位置（居中）
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2 - 30)
    
    # 绘制文本
    draw.text(position, text, font=font, fill=text_color)
    
    # 保存图标
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    icon.save(output_path, "PNG")
    print(f"图标已创建: {output_path}")

def create_presplash(output_path, size=(1080, 1920)):
    """创建启动画面"""
    # 创建一个新的RGB图像
    presplash = Image.new('RGB', size, (255, 255, 255))
    draw = ImageDraw.Draw(presplash)
    
    # 尝试加载中文字体
    try:
        title_font = ImageFont.truetype("simhei.ttf", 120)
        subtitle_font = ImageFont.truetype("simhei.ttf", 60)
    except IOError:
        # 如果没有找到中文字体，使用默认字体
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # 标题和副标题
    title = "大麦抢票助手"
    subtitle = "让抢票更简单"
    
    # 标题颜色和位置
    title_color = (51, 153, 255)
    subtitle_color = (100, 100, 100)
    
    # 获取文本大小
    title_width, title_height = draw.textsize(title, font=title_font) if hasattr(draw, 'textsize') else (500, 100)
    subtitle_width, subtitle_height = draw.textsize(subtitle, font=subtitle_font) if hasattr(draw, 'textsize') else (300, 50)
    
    # 计算文本位置（居中）
    title_position = ((size[0] - title_width) / 2, size[1] / 3)
    subtitle_position = ((size[0] - subtitle_width) / 2, size[1] / 3 + title_height + 50)
    
    # 绘制标题和副标题
    draw.text(title_position, title, font=title_font, fill=title_color)
    draw.text(subtitle_position, subtitle, font=subtitle_font, fill=subtitle_color)
    
    # 保存启动画面
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    presplash.save(output_path, "PNG")
    print(f"启动画面已创建: {output_path}")

if __name__ == "__main__":
    # 创建应用图标
    create_icon("assets/icon.png")
    
    # 创建启动画面
    create_presplash("assets/presplash.png")
    
    print("资源文件创建完成!") 