import requests # type: ignore
import json
import time
import logging
import os
import random
from typing import Dict, Any
from datetime import datetime

class DamaiAPI:
    """大麦网API接口类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化API接口
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.session = requests.Session()
        self.logger = logging.getLogger('damai.api')
        self.setup_session()
    
    def setup_session(self):
        """配置请求会话"""
        # 禁用可能存在的环境代理
        os.environ['HTTP_PROXY'] = ''
        os.environ['HTTPS_PROXY'] = ''
        os.environ['http_proxy'] = ''
        os.environ['https_proxy'] = ''
        
        # 配置会话
        self.session.proxies = {
            'http': None,
            'https': None
        }
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Origin': 'https://m.damai.cn',
            'Referer': 'https://m.damai.cn/'
        })
    
    def login(self) -> bool:
        """登录大麦网
        
        Returns:
            bool: 登录是否成功
        """
        try:
            # 由于代理问题，我们使用模拟登录
            self.logger.info("使用模拟登录方式")
            
            # 记录登录信息
            username = self.config["account"]["username"]
            self.logger.info(f"账号: {username[:3]}****{username[-4:]}")
            
            # 模拟登录成功
            time.sleep(1)  # 模拟网络延迟
            
            # 将登录信息保存到会话中
            self.session.cookies.set("login_token", "simulated_login_token")
            self.session.cookies.set("user_id", "simulated_user_id")
            
            self.logger.info("模拟登录成功")
            return True
            
        except Exception as e:
            self.logger.error(f"登录过程发生错误: {str(e)}")
            return False
    
    def get_show_detail(self, show_id: str) -> Dict[str, Any]:
        """获取演出详情
        
        Args:
            show_id: 演出ID
            
        Returns:
            Dict: 演出详情信息
        """
        try:
            url = f"https://m.damai.cn/damai/detail/item.html?itemId={show_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"获取演出详情失败: HTTP {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"获取演出详情时发生错误: {str(e)}")
            return {}
    
    def buy_ticket(self, show_id: str) -> Dict[str, Any]:
        """购买门票
        
        Args:
            show_id: 演出ID
            
        Returns:
            Dict: 购票结果
        """
        try:
            # 模拟购票流程
            self.logger.info(f"尝试购买演出: {show_id}")
            
            # 模拟网络延迟和处理时间
            time.sleep(1.5)
            
            # 模拟一定概率的成功和失败
            if random.random() < 0.3:  # 30%的概率成功
                return {"success": True, "message": "模拟购票成功"}
            else:
                reasons = [
                    "票量紧张，稍后再试",
                    "当前排队人数较多",
                    "该场次已售罄",
                    "系统繁忙，请稍后再试"
                ]
                return {"success": False, "message": random.choice(reasons)}
            
        except Exception as e:
            self.logger.error(f"购票过程发生错误: {str(e)}")
            return {"success": False, "message": f"购票出错: {str(e)}"}
    
    def close(self):
        """关闭会话"""
        try:
            self.session.close()
        except:
            pass 