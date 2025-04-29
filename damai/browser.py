#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大麦网浏览器自动化模块
提供浏览器初始化、操作等通用功能
"""

import time
import logging
from typing import Dict, Any, Optional, Union, Tuple

from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore    
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.common.exceptions import TimeoutException, NoSuchElementException # type: ignore
from webdriver_manager.chrome import ChromeDriverManager # type: ignore


class Browser:
    """浏览器自动化类，提供浏览器初始化、操作等通用功能"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化浏览器自动化类
        
        Args:
            config: 配置信息，包含浏览器设置、代理等
        """
        self.config = config
        self.browser = None
        self.logger = logging.getLogger("damai.browser")
    
    def init_browser(self, headless: bool = None, mobile: bool = False) -> webdriver.Chrome:
        """初始化Chrome浏览器
        
        Args:
            headless: 是否使用无头模式，None时使用配置文件设置
            mobile: 是否使用移动设备模拟
            
        Returns:
            webdriver.Chrome: 浏览器实例
        """
        chrome_options = Options()
        
        # 确定是否使用无头模式
        use_headless = headless if headless is not None else self.config["browser"].get("headless", False)
        if use_headless:
            chrome_options.add_argument("--headless")
        
        # 设置窗口大小
        window_width = self.config["browser"]["window_size"].get("width", 1920)
        window_height = self.config["browser"]["window_size"].get("height", 1080)
        chrome_options.add_argument(f"--window-size={window_width},{window_height}")
        
        # 设置User-Agent
        user_agent = self.config["browser"].get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument(f"--user-agent={user_agent}")
        
        # 移动设备模拟
        if mobile:
            mobile_emulation = {
                "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
                "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            }
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # 反爬虫设置
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # 设置代理（如果启用）
        if self.config.get("risk_control", {}).get("use_proxy", False):
            proxy_config = self.config["risk_control"]["proxy"]
            proxy_url = f"{proxy_config['host']}:{proxy_config['port']}"
            chrome_options.add_argument(f"--proxy-server={proxy_url}")
        
        # 初始化浏览器
        try:
            self.browser = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # 执行反爬虫检测规避的JavaScript
            self.browser.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)
            
            self.logger.info("浏览器初始化完成")
            
        except Exception as e:
            self.logger.error(f"浏览器初始化失败: {str(e)}")
            raise
        
        return self.browser
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.quit()
            self.browser = None
            self.logger.info("浏览器已关闭")
    
    def wait_for_element(self, by: str, value: str, timeout: int = 10) -> Optional[webdriver.remote.webelement.WebElement]:
        """等待元素出现
        
        Args:
            by: 定位方式，如 By.ID, By.XPATH 等
            value: 元素定位值
            timeout: 超时时间（秒）
            
        Returns:
            WebElement: 找到的元素，超时返回None
        """
        if not self.browser:
            self.logger.error("浏览器未初始化")
            return None
            
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素 {by}={value} 超时")
            return None
    
    def wait_for_clickable(self, by: str, value: str, timeout: int = 10) -> Optional[webdriver.remote.webelement.WebElement]:
        """等待元素可点击
        
        Args:
            by: 定位方式，如 By.ID, By.XPATH 等
            value: 元素定位值
            timeout: 超时时间（秒）
            
        Returns:
            WebElement: 找到的元素，超时返回None
        """
        if not self.browser:
            self.logger.error("浏览器未初始化")
            return None
            
        try:
            element = WebDriverWait(self.browser, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.logger.warning(f"等待元素可点击 {by}={value} 超时")
            return None
    
    def safe_click(self, element) -> bool:
        """安全点击元素，处理可能的异常
        
        Args:
            element: 要点击的元素
            
        Returns:
            bool: 是否点击成功
        """
        if not element:
            return False
            
        try:
            element.click()
            return True
        except Exception as e:
            self.logger.warning(f"点击元素失败: {str(e)}")
            
            # 尝试使用JavaScript点击
            try:
                self.browser.execute_script("arguments[0].click();", element)
                return True
            except Exception as js_e:
                self.logger.error(f"JavaScript点击元素也失败: {str(js_e)}")
                return False
    
    def get_cookies_dict(self) -> Dict[str, str]:
        """获取浏览器Cookies为字典格式
        
        Returns:
            Dict[str, str]: Cookies字典
        """
        if not self.browser:
            self.logger.error("浏览器未初始化")
            return {}
            
        cookies = {}
        for cookie in self.browser.get_cookies():
            cookies[cookie['name']] = cookie['value']
        
        return cookies
    
    def add_random_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """添加随机延迟，模拟人工操作
        
        Args:
            min_seconds: 最小延迟时间（秒）
            max_seconds: 最大延迟时间（秒）
        """
        delay = min_seconds + (max_seconds - min_seconds) * (time.time() % 1)
        time.sleep(delay) 