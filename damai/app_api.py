#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 大麦APP自动化API模块

import time
import random
import logging
from typing import Dict, Any, Optional, List
from appium import webdriver # type: ignore
from appium.webdriver.common.mobileby import MobileBy # type: ignore
from appium.webdriver.common.touch_action import TouchAction # type: ignore

class DamaiAppAPI:
    """大麦APP自动化API类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化APP自动化API
        
        Args:
            config: 配置信息，包含账号、设备设置等
        """
        self.logger = logging.getLogger("damai.app_api")
        self.config = config
        self.username = config["account"]["username"]
        self.password = config["account"]["password"]
        self.buyers = config["buyer"]
        self.driver = None
        self._setup_appium()
    
    def _setup_appium(self):
        """设置Appium配置"""
        try:
            # Appium服务器配置
            appium_config = self.config.get("appium", {})
            desired_caps = {
                "platformName": "Android",
                "platformVersion": appium_config.get("platform_version", ""),
                "deviceName": appium_config.get("device_name", ""),
                "appPackage": "cn.damai",  # 大麦APP包名
                "appActivity": "cn.damai.homepage.MainActivity",  # 大麦APP主活动
                "noReset": True,  # 保留APP数据和缓存
                "automationName": "UiAutomator2",
                "unicodeKeyboard": True,
                "resetKeyboard": True
            }
            
            # 连接Appium服务器
            self.driver = webdriver.Remote(
                f"http://localhost:{appium_config.get('port', 4723)}/wd/hub",
                desired_caps
            )
            
            self.driver.implicitly_wait(10)
            self.logger.info("Appium初始化成功")
            
        except Exception as e:
            self.logger.error(f"Appium初始化失败: {str(e)}")
            raise
    
    def login_if_needed(self) -> bool:
        """检查登录状态并在需要时登录
        
        Returns:
            bool: 是否已登录
        """
        self.logger.info(f"尝试使用账号 {self.username} 登录")
        try:
            # 检查是否已登录
            if self._is_logged_in():
                self.logger.info("已经登录")
                return True
            
            self.logger.info("未登录，开始登录流程")
            
            # 点击"我的"tab
            self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("我的")').click()
            time.sleep(1)
            
            # 点击登录按钮
            login_btn = self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("登录/注册")')
            login_btn.click()
            time.sleep(2)
            
            # 输入账号密码
            username_input = self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("请输入手机号")')
            password_input = self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("请输入登录密码")')
            
            # 模拟手动输入
            username_input.send_keys(self.username)
            time.sleep(random.uniform(0.5, 1.0))
            password_input.send_keys(self.password)
            time.sleep(random.uniform(0.5, 1.0))
            
            # 点击登录
            self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("登录")').click()
            
            # 等待登录成功
            time.sleep(3)
            return self._is_logged_in()
            
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            return False
    
    def _is_logged_in(self) -> bool:
        """检查是否已登录
        
        Returns:
            bool: 是否已登录
        """
        try:
            # 点击"我的"tab
            self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("我的")').click()
            time.sleep(1)
            
            # 检查是否存在"登录/注册"按钮
            login_btns = self.driver.find_elements(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("登录/注册")')
            return len(login_btns) == 0
            
        except Exception:
            return False
    
    def go_to_show(self, show_id: str) -> bool:
        """跳转到演出详情页
        
        Args:
            show_id: 演出ID
            
        Returns:
            bool: 是否成功跳转
        """
        self.logger.info(f"跳转到演出 {show_id} 详情页")
        try:
            # 回到首页
            self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("首页")').click()
            time.sleep(1)
            
            # 点击搜索框
            search_box = self.driver.find_element(MobileBy.ID, "cn.damai:id/search_edit")
            search_box.click()
            time.sleep(1)
            
            # 输入演出ID
            search_input = self.driver.find_element(MobileBy.ID, "cn.damai:id/search_input")
            search_input.send_keys(show_id)
            time.sleep(1)
            
            # 点击搜索
            self.driver.find_element(MobileBy.ID, "cn.damai:id/search_btn").click()
            time.sleep(2)
            
            # 点击第一个搜索结果
            first_result = self.driver.find_element(MobileBy.ID, "cn.damai:id/item_title")
            first_result.click()
            time.sleep(2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"跳转到演出详情页失败: {str(e)}")
            return False
    
    def buy_ticket(self) -> bool:
        """执行购票操作
        
        Returns:
            bool: 是否抢票成功
        """
        self.logger.info("尝试购票")
        try:
            # 检查是否有"立即购买"按钮
            buy_btns = self.driver.find_elements(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("立即购买")')
            
            if not buy_btns:
                self.logger.warning("未找到购买按钮，可能已售罄")
                return False
            
            # 点击立即购买
            buy_btns[0].click()
            time.sleep(1)
            
            # 选择观演人
            self._select_buyers()
            
            # 同意协议并提交订单
            confirm_btn = self.driver.find_element(MobileBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("同意协议并提交订单")')
            
            if self.config["strategy"]["auto_submit"]:
                confirm_btn.click()
                time.sleep(1)
                self.logger.info("订单提交成功")
                return True
            else:
                self.logger.info("订单已准备，等待手动提交")
                return True
            
        except Exception as e:
            self.logger.error(f"购票失败: {str(e)}")
            return False
    
    def _select_buyers(self) -> bool:
        """选择观演人
        
        Returns:
            bool: 是否选择成功
        """
        try:
            # 等待观演人列表加载
            time.sleep(2)
            
            # 获取所有观演人
            buyers = self.driver.find_elements(MobileBy.ID, "cn.damai:id/viewer_item")
            
            if not buyers:
                self.logger.error("未找到可选观演人")
                return False
            
            # 获取需要选择的人数
            required_count = len(self.buyers) or 1
            selected = 0
            
            # 如果配置了指定观演人
            if self.buyers:
                for buyer_info in self.buyers:
                    buyer_name = buyer_info["name"].strip()
                    
                    # 查找并选择指定观演人
                    for buyer in buyers:
                        name = buyer.find_element(MobileBy.ID, "cn.damai:id/name").text
                        if name == buyer_name:
                            if not buyer.is_selected():
                                buyer.click()
                                time.sleep(0.5)
                            selected += 1
                            break
            
            # 如果未选够，补充选择其他观演人
            while selected < required_count and buyers:
                for buyer in buyers:
                    if not buyer.is_selected():
                        buyer.click()
                        time.sleep(0.5)
                        selected += 1
                        if selected >= required_count:
                            break
            
            return selected >= required_count
            
        except Exception as e:
            self.logger.error(f"选择观演人失败: {str(e)}")
            return False
    
    def close(self):
        """关闭驱动"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("已关闭APP驱动") 