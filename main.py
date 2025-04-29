#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大麦抢票助手 - 主程序入口
"""

import os
import time
import logging
import threading
from datetime import datetime
from damai_ticket.app import DamaiTicketApp as AppBase
from damai_ticket.api import DamaiAPI

# 确保日志目录存在
if not os.path.exists('logs'):
    os.makedirs('logs')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/damai_{time.strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class DamaiTicketApp(AppBase):
    """大麦抢票助手应用"""
    
    def ticket_task(self):
        """抢票任务"""
        try:
            # 从配置界面获取配置
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
                    logging.error(f'抢票出错: {str(e)}')
                
                time.sleep(0.5)
            
        except Exception as e:
            self.update_status(f'程序出错: {str(e)}')
            logging.error(f'抢票任务出错: {str(e)}')
        finally:
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.is_running = False

if __name__ == "__main__":
    app = DamaiTicketApp()
    app.run()