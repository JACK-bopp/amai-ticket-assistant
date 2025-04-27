from kivy.app import App # type: ignore
from kivy.uix.boxlayout import BoxLayout # type: ignore 
from kivy.uix.button import Button # type: ignore
from kivy.uix.textinput import TextInput # type: ignore
from kivy.uix.label import Label # type: ignore
from kivy.clock import Clock # type: ignore
from kivy.core.window import Window # type: ignore
from kivy.uix.scrollview import ScrollView # type: ignore
from kivy.metrics import dp # type: ignore
from kivy.uix.popup import Popup # type: ignore
from kivy.utils import platform # type: ignore
from kivy.logger import Logger # type: ignore
import json
import os
import threading
import time
from datetime import datetime
import traceback

# 版本信息
__version__ = "1.1.0"

class DamaiApp(App):
    def build(self):
        # 设置窗口大小和标题
        self.title = '大麦抢票助手'
        self.icon = 'assets/icon.png'
        
        # 根据平台调整界面
        if platform == 'android' or platform == 'ios':
            Window.softinput_mode = 'below_target'  # 防止键盘遮挡输入框
        else:
            Window.size = (dp(400), dp(600))
        
        # 主布局
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 标题
        title = Label(
            text='大麦抢票助手',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24),
            color=(0.2, 0.6, 1, 1)  # 蓝色标题
        )
        layout.add_widget(title)
        
        # 版本信息
        version_label = Label(
            text=f'版本 {__version__}',
            size_hint_y=None,
            height=dp(20),
            font_size=dp(12),
            color=(0.5, 0.5, 0.5, 1)  # 灰色文本
        )
        layout.add_widget(version_label)
        
        # 提示标签
        tips = Label(
            text='填写信息后点击开始抢票即可',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            color=(0.5, 0.5, 0.5, 1)  # 灰色提示
        )
        layout.add_widget(tips)
        
        # 滚动视图
        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # 账号输入
        account_label = Label(
            text='账号信息',
            size_hint_y=None,
            height=dp(20),
            font_size=dp(14),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        account_label.bind(size=account_label.setter('text_size'))
        form_layout.add_widget(account_label)
        
        self.username = TextInput(
            hint_text='大麦网账号/手机号',
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size=dp(16),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        form_layout.add_widget(self.username)
        
        self.password = TextInput(
            hint_text='密码',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size=dp(16),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        form_layout.add_widget(self.password)
        
        # 演出信息标签
        show_label = Label(
            text='演出信息',
            size_hint_y=None,
            height=dp(20),
            font_size=dp(14),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        show_label.bind(size=show_label.setter('text_size'))
        form_layout.add_widget(show_label)
        
        self.show_id = TextInput(
            hint_text='演出ID (从演出链接中获取)',
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size=dp(16),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        form_layout.add_widget(self.show_id)
        
        # 演出ID帮助按钮
        help_button = Button(
            text='如何获取演出ID?',
            size_hint_y=None,
            height=dp(35),
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.3, 0.3, 0.3, 1),
            font_size=dp(14)
        )
        help_button.bind(on_press=self.show_help)
        form_layout.add_widget(help_button)
        
        self.start_time = TextInput(
            hint_text='开售时间 (如: 2024-04-20 12:00:00)',
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size=dp(16),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        form_layout.add_widget(self.start_time)
        
        # 观演人信息标签
        buyer_label = Label(
            text='观演人信息',
            size_hint_y=None,
            height=dp(20),
            font_size=dp(14),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        buyer_label.bind(size=buyer_label.setter('text_size'))
        form_layout.add_widget(buyer_label)
        
        self.buyer_name = TextInput(
            hint_text='观演人姓名 (必须是已实名认证的)',
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size=dp(16),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        form_layout.add_widget(self.buyer_name)
        
        # 状态显示
        status_label = Label(
            text='状态信息',
            size_hint_y=None,
            height=dp(20),
            font_size=dp(14),
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        status_label.bind(size=status_label.setter('text_size'))
        form_layout.add_widget(status_label)
        
        self.status_label = Label(
            text='请填写信息并点击开始抢票',
            size_hint_y=None,
            height=dp(80),
            font_size=dp(16),
            halign='left',
            valign='top',
            color=(0.2, 0.6, 0.2, 1)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        form_layout.add_widget(self.status_label)
        
        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        
        # 按钮区域
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(60))
        
        # 加载按钮
        self.load_button = Button(
            text='加载配置',
            background_color=(0.4, 0.4, 0.8, 1),
            size_hint_x=0.33,
            font_size=dp(16)
        )
        self.load_button.bind(on_press=self.load_config)
        button_layout.add_widget(self.load_button)
        
        # 开始按钮
        self.start_button = Button(
            text='开始抢票',
            background_color=(0.2, 0.8, 0.2, 1),
            size_hint_x=0.34,
            font_size=dp(16)
        )
        self.start_button.bind(on_press=self.start_ticket_bot)
        button_layout.add_widget(self.start_button)
        
        # 停止按钮
        self.stop_button = Button(
            text='停止',
            background_color=(0.8, 0.2, 0.2, 1),
            size_hint_x=0.33,
            disabled=True,
            font_size=dp(16)
        )
        self.stop_button.bind(on_press=self.stop_ticket_bot)
        button_layout.add_widget(self.stop_button)
        
        layout.add_widget(button_layout)
        
        # 初始化变量
        self.is_running = False
        self.ticket_thread = None
        
        # 尝试加载已保存的配置
        self.try_load_saved_config()
        
        return layout
    
    def on_start(self):
        """应用启动时调用"""
        Logger.info(f"DamaiApp: 应用启动，版本 {__version__}")
        
        # 检查Android权限(如果在Android平台)
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.INTERNET,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE
                ])
            except ImportError:
                self.update_status("提示: 无法申请Android权限，某些功能可能受限")
    
    def get_application_config(self):
        """获取应用配置文件路径"""
        if platform == 'android':
            from android.storage import app_storage_path
            app_path = app_storage_path()
            return os.path.join(app_path, 'damai.ini')
        return super().get_application_config()
    
    def get_config_path(self):
        """获取配置文件路径"""
        if platform == 'android':
            from android.storage import app_storage_path
            app_path = app_storage_path()
            return os.path.join(app_path, 'config.json')
        return 'config.json'
    
    def show_help(self, instance):
        """显示获取演出ID的帮助信息"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        help_text = Label(
            text='1. 在大麦APP或网页找到你想看的演出\n'
                 '2. 点击分享按钮，复制链接\n'
                 '3. 从链接中找出类似"detail_item_XXX"的数字部分\n'
                 '4. 其中XXX就是演出ID\n\n'
                 '例如: https://detail.damai.cn/item.htm?id=719538751441\n'
                 '演出ID就是: 719538751441',
            halign='left',
            valign='top',
            font_size=dp(14)
        )
        help_text.bind(size=help_text.setter('text_size'))
        
        content.add_widget(help_text)
        
        close_button = Button(
            text='知道了',
            size_hint_y=None,
            height=dp(50)
        )
        
        popup = Popup(
            title='如何获取演出ID',
            content=content,
            size_hint=(0.9, 0.5),
            auto_dismiss=True
        )
        
        close_button.bind(on_press=popup.dismiss)
        content.add_widget(close_button)
        
        popup.open()
    
    def try_load_saved_config(self):
        """尝试加载保存的配置"""
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 填充界面
                self.username.text = config.get('account', {}).get('username', '')
                self.password.text = config.get('account', {}).get('password', '')
                self.show_id.text = config.get('target', {}).get('show_id', '')
                self.start_time.text = config.get('target', {}).get('start_time', '')
                
                # 尝试获取观演人信息
                buyers = config.get('buyer', [])
                if buyers and len(buyers) > 0:
                    self.buyer_name.text = buyers[0].get('name', '')
                    
                self.update_status('已加载保存的配置')
            except Exception as e:
                self.update_status(f'加载配置失败: {str(e)}')
    
    def update_status(self, text):
        """更新状态显示"""
        def update(dt):
            self.status_label.text = text
            Logger.info(f"DamaiApp: 状态更新 - {text}")
        Clock.schedule_once(update, 0)
    
    def save_config(self):
        """保存配置到文件"""
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
        
        config_path = self.get_config_path()
        try:
            # 确保目录存在
            config_dir = os.path.dirname(config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            Logger.info(f"DamaiApp: 配置已保存到 {config_path}")
        except Exception as e:
            Logger.error(f"DamaiApp: 保存配置失败 - {str(e)}")
            self.update_status(f"保存配置失败: {str(e)}")
    
    def load_config(self, instance):
        """加载配置按钮处理"""
        self.try_load_saved_config()
    
    def start_ticket_bot(self, instance):
        """开始抢票"""
        if not all([self.username.text, self.password.text, self.show_id.text, 
                   self.start_time.text, self.buyer_name.text]):
            self.update_status('请填写所有必要信息!')
            return
        
        # 保存配置
        self.save_config()
        
        # 禁用开始按钮，启用停止按钮
        self.start_button.disabled = True
        self.load_button.disabled = True
        self.stop_button.disabled = False
        
        # 更新状态
        self.update_status('正在启动抢票程序...')
        
        # 启动抢票线程
        self.is_running = True
        self.ticket_thread = threading.Thread(target=self.ticket_bot_thread)
        self.ticket_thread.daemon = True
        self.ticket_thread.start()
    
    def stop_ticket_bot(self, instance):
        """停止抢票"""
        self.is_running = False
        self.update_status('正在停止抢票程序...')
        
        # 启用开始按钮，禁用停止按钮
        self.start_button.disabled = False
        self.load_button.disabled = False
        self.stop_button.disabled = True
    
    def ticket_bot_thread(self):
        """抢票线程"""
        try:
            # 等待到开售时间
            target_time = datetime.strptime(self.start_time.text, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()
            
            if current_time >= target_time:
                self.update_status('开售时间已过! 将尝试直接抢票')
            else:
                wait_seconds = (target_time - current_time).total_seconds()
                self.update_status(f'等待开售, 距开始还有 {wait_seconds:.1f} 秒')
                
                # 每秒更新倒计时
                while wait_seconds > 0 and self.is_running:
                    time.sleep(1)
                    wait_seconds -= 1
                    if wait_seconds % 5 == 0 or wait_seconds < 10:  # 每5秒或最后10秒内每秒更新一次
                        self.update_status(f'等待开售, 距开始还有 {wait_seconds:.0f} 秒')
                
                # 开售前5秒准备
                if wait_seconds <= 5 and self.is_running:
                    self.update_status('准备抢票...')
                    time.sleep(wait_seconds)
            
            # 开始抢票循环
            attempt_count = 0
            while self.is_running:
                attempt_count += 1
                try:
                    # 这里实现实际的抢票逻辑
                    self.update_status(f'第 {attempt_count} 次尝试抢票...')
                    
                    # 模拟抢票过程
                    time.sleep(0.5)
                    
                    # 示例：每10次尝试提示一条不同的信息
                    if attempt_count % 10 == 0:
                        self.update_status(f'第 {attempt_count} 次尝试: 正在确认库存...')
                    elif attempt_count % 10 == 5:
                        self.update_status(f'第 {attempt_count} 次尝试: 提交订单中...')
                    
                    # 这里可以集成API调用，实现真实抢票
                    # 如果要在APK中集成真实抢票，需要添加代码调用damai/mobile_api.py
                    
                except Exception as e:
                    err_msg = f'抢票出错: {str(e)}'
                    Logger.error(f"DamaiApp: {err_msg}")
                    Logger.error(f"DamaiApp: {traceback.format_exc()}")
                    self.update_status(err_msg)
                    time.sleep(1)
            
        except Exception as e:
            err_msg = f'程序出错: {str(e)}'
            Logger.error(f"DamaiApp: {err_msg}")
            Logger.error(f"DamaiApp: {traceback.format_exc()}")
            self.update_status(err_msg)
        finally:
            # 重置按钮状态
            def reset_buttons(dt):
                self.start_button.disabled = False
                self.load_button.disabled = False
                self.stop_button.disabled = True
            Clock.schedule_once(reset_buttons, 0)
            
            if self.is_running:
                self.is_running = False
                self.update_status('抢票已停止')

def main():
    """作为模块导入时的入口点"""
    DamaiApp().run()

if __name__ == '__main__':
    main() 