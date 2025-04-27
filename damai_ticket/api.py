import requests
import json
import time
import logging
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
            # 登录URL
            login_url = "https://m.damai.cn/damai/minilogin/index.html"
            
            # 登录参数
            data = {
                "loginId": self.config["account"]["username"],
                "password": self.config["account"]["password"]
            }
            
            # 发送登录请求
            response = self.session.post(
                "https://m.damai.cn/damai/login/v1/login.html",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.logger.info("登录成功")
                    return True
                else:
                    self.logger.error(f"登录失败: {result.get('message')}")
            else:
                self.logger.error(f"登录请求失败: HTTP {response.status_code}")
            
            return False
            
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
            # 获取演出详情
            detail = self.get_show_detail(show_id)
            if not detail:
                return {"success": False, "message": "获取演出详情失败"}
            
            # 检查是否可以购买
            if not detail.get("canBuy"):
                return {"success": False, "message": "当前不可购买"}
            
            # 选择票档
            sku_list = detail.get("skuList", [])
            available_sku = None
            
            for sku in sku_list:
                if sku.get("inventory") > 0:
                    available_sku = sku
                    break
            
            if not available_sku:
                return {"success": False, "message": "无可用票档"}
            
            # 构建订单参数
            order_data = {
                "itemId": show_id,
                "skuId": available_sku["skuId"],
                "count": 1,
                "buyerId": self.config["buyer"][0]["name"],
                "channel": "damai_app"
            }
            
            # 提交订单
            response = self.session.post(
                "https://m.damai.cn/damai/create/v1/order.html",
                json=order_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return {"success": True, "message": "下单成功"}
                else:
                    return {"success": False, "message": result.get("message")}
            else:
                return {
                    "success": False,
                    "message": f"提交订单失败: HTTP {response.status_code}"
                }
            
        except Exception as e:
            self.logger.error(f"购票过程发生错误: {str(e)}")
            return {"success": False, "message": f"购票出错: {str(e)}"}
    
    def close(self):
        """关闭会话"""
        try:
            self.session.close()
        except:
            pass 