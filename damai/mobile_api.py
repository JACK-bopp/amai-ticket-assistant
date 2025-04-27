# 大麦网移动端API请求模块

import time
import json
import random
import logging
from typing import Dict, Any, Optional
from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore    
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from appium import webdriver as appium_webdriver # type: ignore
from appium.webdriver.common.mobileby import MobileBy # type: ignore
from appium.webdriver.common.touch_action import TouchAction # type: ignore
import requests

class DamaiMobileAPI:
    """大麦网移动端API请求类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化移动端API请求类
        
        Args:
            config: 配置信息，包含账号、设备设置等
        """
        self.config = config
        self.session = requests.Session()
        self.logger = logging.getLogger("damai.mobile_api")
        self.driver = None
        self._setup_appium()
        self.setup_session()
    
    def _setup_appium(self):
        """设置Appium配置"""
        try:
            # Appium服务器配置
            appium_config = self.config.get("appium", {})
            desired_caps = {
                "platformName": "Android",  # 或 "iOS"
                "platformVersion": appium_config.get("platform_version", ""),  # 安卓版本号
                "deviceName": appium_config.get("device_name", ""),  # 设备名称
                "browserName": "Chrome",  # 使用Chrome浏览器
                "chromedriverExecutable": appium_config.get("chromedriver_path", ""),  # ChromeDriver路径
                "automationName": "UiAutomator2",  # Android自动化引擎
                "noReset": True,  # 不重置应用状态
                "newCommandTimeout": 600,  # 命令超时时间
                "unicodeKeyboard": True,  # 使用Unicode输入法
                "resetKeyboard": True  # 重置输入法
            }
            
            # 连接Appium服务器
            self.driver = appium_webdriver.Remote(
                f"http://localhost:{appium_config.get('port', 4723)}/wd/hub",
                desired_caps
            )
            
            # 设置隐式等待时间
            self.driver.implicitly_wait(10)
            self.logger.info("Appium初始化成功")
            
        except Exception as e:
            self.logger.error(f"Appium初始化失败: {str(e)}")
            raise
    
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
                return {"success": False, "message": f"提交订单失败: HTTP {response.status_code}"}
            
        except Exception as e:
            self.logger.error(f"购票过程发生错误: {str(e)}")
            return {"success": False, "message": f"购票出错: {str(e)}"}
    
    def submit_order(self, show_url: str) -> Dict[str, Any]:
        """提交订单
        
        Args:
            show_url: 演出详情页URL
            
        Returns:
            Dict: 订单提交结果
        """
        try:
            # 转换为移动端URL
            mobile_url = show_url.replace("detail.damai.cn", "m.damai.cn/damai/detail/item.html")
            self.driver.get(mobile_url)
            self.logger.info("正在加载演出详情页")
            
            # 等待页面加载
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((MobileBy.CLASS_NAME, "buy-btn"))
            )
            
            # 选择场次（如果有）
            try:
                session_list = self.driver.find_elements(MobileBy.CLASS_NAME, "session-item")
                if session_list:
                    # 选择第一个可选场次
                    for session in session_list:
                        if "disabled" not in session.get_attribute("class"):
                            session.click()
                            time.sleep(1)
                            break
            except Exception as e:
                self.logger.warning("选择场次失败，尝试继续执行")
            
            # 点击购买按钮
            buy_btn = self.driver.find_element(MobileBy.CLASS_NAME, "buy-btn")
            btn_text = buy_btn.text.strip()
            
            if "已售完" in btn_text or "暂时缺货" in btn_text:
                return {"success": False, "message": f"当前场次无票: {btn_text}"}
            
            buy_btn.click()
            
            # 等待跳转到订单确认页
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("buy.damai.cn/orderConfirm")
            )
            
            # 选择购票人
            self._select_buyers_mobile()
            
            # 确认订单信息
            try:
                # 同意服务协议
                agreement = self.driver.find_element(MobileBy.CLASS_NAME, "service-agreement")
                if not agreement.is_selected():
                    agreement.click()
                    time.sleep(0.5)
                
                # 获取提交按钮
                submit_btn = self.driver.find_element(MobileBy.CLASS_NAME, "submit-wrapper")
                
                if self.config["strategy"]["auto_submit"]:
                    submit_btn.click()
                    
                    # 等待跳转到支付页面
                    WebDriverWait(self.driver, 15).until(
                        EC.url_contains("pay.damai.cn")
                    )
                    
                    self.logger.info("订单提交成功，已跳转到支付页面")
                    return {"success": True, "message": "订单提交成功，请在手机上完成支付"}
                else:
                    self.logger.info("订单已准备好，等待手动提交")
                    return {"success": True, "message": "订单已准备好，请在手机上手动提交"}
                
            except Exception as e:
                self.logger.error(f"订单确认失败: {str(e)}")
                return {"success": False, "message": f"订单确认失败: {str(e)}"}
            
        except Exception as e:
            self.logger.error(f"提交订单失败: {str(e)}")
            self.logger.debug("异常详细信息:", exc_info=True)
            return {"success": False, "message": f"提交订单失败: {str(e)}"}
    
    def _select_buyers_mobile(self) -> bool:
        """移动端选择购票人
        
        Returns:
            bool: 是否成功选择购票人
        """
        try:
            # 等待购票人列表加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((MobileBy.CLASS_NAME, "buyer-list"))
            )
            
            time.sleep(1.5)
            
            # 获取所有购票人
            buyer_items = self.driver.find_elements(MobileBy.CLASS_NAME, "buyer-item")
            
            if not buyer_items:
                self.logger.error("未找到可用的购票人")
                return False
            
            required_count = len(self.config.get("buyer", [])) or 1
            selected_buyers = []
            
            # 选择配置的购票人
            if self.config.get("buyer"):
                for buyer_info in self.config["buyer"]:
                    buyer_name = buyer_info["name"].strip()
                    
                    for item in buyer_items:
                        try:
                            name_element = item.find_element(MobileBy.CLASS_NAME, "buyer-name")
                            current_name = name_element.text.strip()
                            
                            if buyer_name == current_name:
                                checkbox = item.find_element(MobileBy.TAG_NAME, "input")
                                
                                if not checkbox.is_selected():
                                    # 使用TouchAction模拟点击
                                    action = TouchAction(self.driver)
                                    action.tap(item).perform()
                                    time.sleep(0.5)
                                    
                                    if not checkbox.is_selected():
                                        self.logger.warning(f"选择购票人 {buyer_name} 失败")
                                        continue
                                
                                selected_buyers.append(buyer_name)
                                self.logger.info(f"已选择购票人: {buyer_name}")
                                break
                        except Exception as e:
                            continue
            
            # 补充选择其他购票人
            if len(selected_buyers) < required_count:
                for item in buyer_items:
                    if len(selected_buyers) >= required_count:
                        break
                    
                    try:
                        name_element = item.find_element(MobileBy.CLASS_NAME, "buyer-name")
                        buyer_name = name_element.text.strip()
                        
                        if buyer_name not in selected_buyers:
                            checkbox = item.find_element(MobileBy.TAG_NAME, "input")
                            
                            if not checkbox.is_selected():
                                action = TouchAction(self.driver)
                                action.tap(item).perform()
                                time.sleep(0.5)
                                
                                if checkbox.is_selected():
                                    selected_buyers.append(buyer_name)
                                    self.logger.info(f"已选择补充购票人: {buyer_name}")
                    except Exception as e:
                        continue
            
            if len(selected_buyers) < required_count:
                self.logger.error(f"未能选择足够的购票人，需要 {required_count} 人，实际选择 {len(selected_buyers)} 人")
                return False
            
            self.logger.info(f"成功选择 {len(selected_buyers)} 个购票人: {', '.join(selected_buyers)}")
            return True
            
        except Exception as e:
            self.logger.error(f"选择购票人时发生异常: {str(e)}")
            self.logger.debug("异常详细信息:", exc_info=True)
            return False
    
    def close(self):
        """关闭驱动"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("已关闭移动端驱动")
        try:
            self.session.close()
        except:
            pass 