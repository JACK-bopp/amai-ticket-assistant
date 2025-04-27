#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大麦网抢票脚本主程序
"""

import os
import sys
import time
import logging
import argparse
from typing import Dict, Any
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
import json
import threading
from datetime import datetime

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from damai.api import DamaiAPI
from damai.monitor import TicketMonitor
from damai.order import OrderProcessor
from damai.utils import setup_logger, load_config
from risk.proxy import ProxyManager
from risk.fingerprint import FingerprintSimulator


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="大麦网抢票脚本")
    parser.add_argument("-c", "--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("-d", "--debug", action="store_true", help="启用调试模式")
    parser.add_argument("-u", "--url", help="指定演出URL，覆盖配置文件中的设置")
    parser.add_argument("-a", "--auto", action="store_true", help="全自动模式，无需人工干预")
    return parser.parse_args()


def on_ticket_available(status: Dict[str, Any], order_processor: OrderProcessor):
    """票务可用时的回调函数
    
    Args:
        status: 票务状态信息
        order_processor: 订单处理器
    """
    logger = logging.getLogger("main")
    show_info = status["show_info"]
    
    logger.info(f"发现可购买票: {show_info['title']}")
    logger.info(f"演出时间: {show_info['time']}")
    logger.info(f"演出场馆: {show_info['venue']}")
    logger.info(f"票价: {show_info['price']}")
    
    # 处理订单
    order_result = order_processor.process_order(show_info)
    
    if order_result["success"]:
        logger.info(f"订单处理成功: {order_result['message']}")
    else:
        logger.error(f"订单处理失败: {order_result['message']}")


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(log_level)
    logger.info("大麦网抢票脚本启动")
    
    try:
        # 加载配置
        config = load_config(args.config)
        logger.info(f"已加载配置文件: {args.config}")
        
        # 如果指定了URL，覆盖配置中的URL
        if args.url:
            config["target"]["url"] = args.url
            logger.info(f"使用命令行指定的URL: {args.url}")
        
        # 如果指定了自动模式，覆盖配置中的自动提交设置
        if args.auto:
            config["strategy"]["auto_submit"] = True
            logger.info("已启用全自动模式")
        
        # 初始化风险控制模块
        proxy_manager = ProxyManager(config)
        proxy_manager.init_proxy()
        
        fingerprint_simulator = FingerprintSimulator(config)
        
        # 初始化API模块
        api = DamaiAPI(config)
        
        # 初始化浏览器
        browser = api.init_browser()
        logger.info("浏览器初始化完成")
        
        # 登录账号
        login_success = api.login()
        if not login_success:
            logger.error("登录失败，请检查账号信息或手动登录")
            # 等待用户手动登录
            input("请在浏览器中手动登录，完成后按回车继续...")
        
        # 初始化票务监控器
        monitor = TicketMonitor(config, api)
        
        # 初始化订单处理器
        order_processor = OrderProcessor(config, api)
        
        # 添加票务可用回调
        monitor.add_callback(lambda status: on_ticket_available(status, order_processor))
        
        # 开始监控
        logger.info("开始监控票务状态")
        monitor.start_monitoring()
        
        try:
            # 主循环
            while monitor.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("用户中断，停止监控")
            monitor.stop_monitoring()
        
        # 关闭浏览器
        api.close_browser()
        logger.info("抢票脚本已停止")
        
    except Exception as e:
        logger.exception(f"程序异常: {str(e)}")
        return 1
    
    return 0


class DamaiTicketApp(App):
    def build(self):
        # 设置窗口标题
        self.title = '大麦抢票助手'
        
        # 根据平台调整界面
        if platform == 'android':
            Window.softinput_mode = 'below_target'
        
        # 主布局
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 标题
        title = Label(
            text='大麦抢票助手',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24)
        )
        layout.add_widget(title)
        
        # 滚动视图
        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # 账号输入
        form_layout.add_widget(Label(
            text='账号信息',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16)
        ))
        
        self.username = TextInput(
            hint_text='大麦网账号/手机号',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.username)
        
        self.password = TextInput(
            hint_text='密码',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.password)
        
        # 演出信息
        form_layout.add_widget(Label(
            text='演出信息',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16)
        ))
        
        self.show_id = TextInput(
            hint_text='演出ID',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.show_id)
        
        self.start_time = TextInput(
            hint_text='开售时间 (格式: 2024-03-25 20:00:00)',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.start_time)
        
        # 观演人信息
        form_layout.add_widget(Label(
            text='观演人信息',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16)
        ))
        
        self.buyer_name = TextInput(
            hint_text='观演人姓名（必须是已实名认证的）',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.buyer_name)
        
        # 状态显示
        self.status_label = Label(
            text='准备就绪',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(14)
        )
        form_layout.add_widget(self.status_label)
        
        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        
        # 按钮区域
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
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
        
        return layout
    
    def update_status(self, text):
        def update(dt):
            self.status_label.text = text
        Clock.schedule_once(update, 0)
    
    def save_config(self):
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
        if not all([self.username.text, self.password.text, 
                   self.show_id.text, self.start_time.text,
                   self.buyer_name.text]):
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
        self.is_running = False
        self.update_status('正在停止抢票程序...')
        
        # 更新按钮状态
        self.start_button.disabled = False
        self.stop_button.disabled = True
    
    def ticket_task(self):
        try:
            from damai.mobile_api import DamaiMobileAPI
            api = DamaiMobileAPI(self.load_config())
            
            # 登录
            if not api.login():
                self.update_status('登录失败，请检查账号信息')
                return
            
            self.update_status('登录成功，等待开始抢票...')
            
            # 等待到开售时间
            start_time = datetime.strptime(self.start_time.text, "%Y-%m-%d %H:%M:%S")
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
                        self.update_status(f'本次尝试失败: {result.get("message")}')
                except Exception as e:
                    self.update_status(f'抢票出错: {str(e)}')
                
                time.sleep(0.5)
            
        except Exception as e:
            self.update_status(f'程序出错: {str(e)}')
        finally:
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.is_running = False


if __name__ == "__main__":
    sys.exit(main())

if __name__ == '__main__':
    DamaiTicketApp().run()