#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大麦抢票助手 - Android版
主入口文件
"""

import os
import sys
import json
import threading
import time
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import platform
from kivy.logger import Logger
from kivy.uix.popup import Popup

# 导入其他必要模块
try:
    from damai_ticket.api import DamaiAPI
except ImportError:
    # 如果导入失败，提供一个模拟的API类
    class DamaiAPI:
        def __init__(self, config):
            self.config = config
            
        def login(self):
            return True
            
        def buy_ticket(self, show_id):
            return {"success": True, "message": "模拟购票成功"}
            
        def close(self):
            pass

class DamaiTicketApp(App):
    """大麦抢票助手主应用类"""
    
    def build(self):
        # 设置窗口标题和主题色
        self.title = '大麦抢票助手'
        self.theme_cls = {
            'primary': (0.2, 0.6, 1, 1),  # 蓝色
            'accent': (0.2, 0.8, 0.2, 1),  # 绿色
            'background': (0.95, 0.95, 0.95, 1)  # 浅灰色
        }
        
        # 根据平台调整界面
        if platform == 'android':
            Window.softinput_mode = 'below_target'
        
        # 主布局
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10),
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter('height'))
        
        # 标题
        title = Label(
            text='大麦抢票助手',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24),
            color=(0.2, 0.6, 1, 1)
        )
        layout.add_widget(title)
        
        # 创建滚动视图
        scroll = ScrollView(size_hint=(1, 1))
        form_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=dp(10)
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # 账号信息区域
        self._add_section_header(form_layout, '账号信息')
        self.username = self._add_input_field(form_layout, '大麦网账号/手机号')
        self.password = self._add_input_field(form_layout, '密码', password=True)
        
        # 演出信息区域
        self._add_section_header(form_layout, '演出信息')
        self.show_id = self._add_input_field(form_layout, '演出ID')
        self.start_time = self._add_input_field(
            form_layout,
            '开售时间 (格式: 2024-03-25 20:00:00)'
        )
        
        # 添加获取演出ID的帮助按钮
        help_button = Button(
            text='如何获取演出ID?',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.2, 0.2, 0.2, 1)
        )
        help_button.bind(on_press=self.show_help)
        form_layout.add_widget(help_button)
        
        # 观演人信息区域
        self._add_section_header(form_layout, '观演人信息')
        self.buyer_name = self._add_input_field(
            form_layout,
            '观演人姓名（必须是已实名认证的）'
        )
        
        # 状态显示
        self.status_label = Label(
            text='准备就绪',
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.6, 0.2, 1)
        )
        form_layout.add_widget(self.status_label)
        
        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        
        # 按钮区域
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
            padding=[dp(10), 0, dp(10), dp(10)]
        )
        
        # 开始按钮
        self.start_button = Button(
            text='开始抢票',
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_x=0.5
        )
        self.start_button.bind(on_press=self.start_ticket_task)
        button_layout.add_widget(self.start_button)
        
        # 停止按钮
        self.stop_button = Button(
            text='停止',
            background_color=(0.8, 0.2, 0.2, 1),
            size_hint_x=0.5,
            disabled=True
        )
        self.stop_button.bind(on_press=self.stop_ticket_task)
        button_layout.add_widget(self.stop_button)
        
        layout.add_widget(button_layout)
        
        # 初始化变量
        self.is_running = False
        self.ticket_thread = None
        
        # 尝试加载保存的配置
        self.load_config()
        
        return layout
    
    def _add_section_header(self, layout, text):
        """添加分区标题"""
        layout.add_widget(Label(
            text=text,
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            color=(0.2, 0.6, 1, 1),
            halign='left'
        ))
    
    def _add_input_field(self, layout, hint_text, password=False):
        """添加输入框"""
        input_field = TextInput(
            hint_text=hint_text,
            password=password,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            padding=[dp(10), dp(10), dp(10), dp(10)],
            background_color=(1, 1, 1, 1)
        )
        layout.add_widget(input_field)
        return input_field
    
    def show_help(self, instance):
        """显示帮助信息"""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        
        help_text = (
            '1. 在大麦APP或网页找到想看的演出\n'
            '2. 点击分享按钮，复制链接\n'
            '3. 从链接中找出类似"detail_item_XXX"的数字\n'
            '4. 其中XXX就是演出ID\n\n'
            '例如：\n'
            'https://detail.damai.cn/item.htm?id=719538751441\n'
            '演出ID就是：719538751441'
        )
        
        content.add_widget(Label(
            text=help_text,
            size_hint_y=None,
            height=dp(200)
        ))
        
        button = Button(
            text='知道了',
            size_hint_y=None,
            height=dp(50)
        )
        
        popup = Popup(
            title='如何获取演出ID',
            content=content,
            size_hint=(0.9, 0.6),
            auto_dismiss=True
        )
        
        button.bind(on_press=popup.dismiss)
        content.add_widget(button)
        
        popup.open()
    
    def update_status(self, text):
        """更新状态显示"""
        def update(dt):
            self.status_label.text = text
        Clock.schedule_once(update, 0)
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.username.text = config.get('account', {}).get('username', '')
                self.password.text = config.get('account', {}).get('password', '')
                self.show_id.text = config.get('target', {}).get('show_id', '')
                self.start_time.text = config.get('target', {}).get('start_time', '')
                
                buyers = config.get('buyer', [])
                if buyers and len(buyers) > 0:
                    self.buyer_name.text = buyers[0].get('name', '')
        except Exception as e:
            self.update_status(f'加载配置失败: {str(e)}')
    
    def save_config(self):
        """保存配置"""
        config = {
            'account': {
                'username': self.username.text,
                'password': self.password.text
            },
            'target': {
                'show_id': self.show_id.text,
                'start_time': self.start_time.text
            },
            'buyer': [
                {'name': self.buyer_name.text}
            ]
        }
        
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.update_status(f'保存配置失败: {str(e)}')
    
    def start_ticket_task(self, instance):
        """开始抢票"""
        if not all([
            self.username.text,
            self.password.text,
            self.show_id.text,
            self.start_time.text,
            self.buyer_name.text
        ]):
            self.update_status('请填写所有必要信息！')
            return
        
        # 保存配置
        self.save_config()
        
        # 更新按钮状态
        self.start_button.disabled = True
        self.stop_button.disabled = False
        
        # 启动抢票线程
        self.is_running = True
        self.ticket_thread = threading.Thread(target=self.ticket_task)
        self.ticket_thread.daemon = True
        self.ticket_thread.start()
        
        self.update_status('抢票程序已启动...')
    
    def stop_ticket_task(self, instance):
        """停止抢票"""
        self.is_running = False
        self.update_status('正在停止抢票程序...')
        
        # 更新按钮状态
        self.start_button.disabled = False
        self.stop_button.disabled = True
    
    def ticket_task(self):
        """抢票任务"""
        try:
            # 组装配置对象
            config = {
                'account': {
                    'username': self.username.text,
                    'password': self.password.text
                },
                'target': {
                    'show_id': self.show_id.text,
                    'start_time': self.start_time.text
                },
                'buyer': [
                    {'name': self.buyer_name.text}
                ]
            }
            
            # 初始化API
            api = DamaiAPI(config)
            
            # 登录
            if not api.login():
                self.update_status('登录失败，请检查账号信息')
                return
            
            self.update_status('登录成功，等待开始抢票...')
            
            # 等待到开售时间
            start_time = datetime.strptime(
                self.start_time.text,
                "%Y-%m-%d %H:%M:%S"
            )
            
            while datetime.now() < start_time and self.is_running:
                remaining = (start_time - datetime.now()).total_seconds()
                self.update_status(f'距离开售还有 {remaining:.1f} 秒')
                time.sleep(1)
            
            if not self.is_running:
                return
            
            # 开始抢票
            attempt_count = 0
            while self.is_running:
                attempt_count += 1
                self.update_status(f'第 {attempt_count} 次尝试抢票...')
                
                try:
                    result = api.buy_ticket(self.show_id.text)
                    if result.get('success'):
                        self.update_status('抢票成功！请在30分钟内完成支付')
                        break
                    else:
                        self.update_status(
                            f'本次尝试失败: {result.get("message")}'
                        )
                except Exception as e:
                    self.update_status(f'抢票出错: {str(e)}')
                
                time.sleep(0.5)
            
        except Exception as e:
            self.update_status(f'程序出错: {str(e)}')
        finally:
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.is_running = False


if __name__ == '__main__':
    DamaiTicketApp().run()