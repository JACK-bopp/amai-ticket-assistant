# 大麦网API请求模块

import time
import json
import random
import logging
import requests # type: ignore
from typing import Dict, Any, Optional
from selenium import webdriver # type: ignore           
from selenium.webdriver.chrome.options import Options # type: ignore    
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from webdriver_manager.chrome import ChromeDriverManager # type: ignore

class DamaiAPI:
    """大麦网API请求类,负责处理与大麦网的所有网络交互"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化API请求类
        
        Args:
            config: 配置信息，包含账号、浏览器设置等
        """
        self.config = config
        self.logger = logging.getLogger("damai.api")
        self.session = requests.Session()
        self.browser = None
        self.cookies = {}
        self._setup_session()
    
    def _setup_session(self):
        """设置请求会话，包括请求头、代理等"""
        # 设置通用请求头
        self.session.headers.update({
            "User-Agent": self.config["browser"]["user_agent"],
            "Referer": "https://www.damai.cn/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://www.damai.cn",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        })
        
        # 设置代理（如果启用）
        if self.config["risk_control"]["use_proxy"]:
            try:
                proxy_config = self.config["risk_control"]["proxy"]
                proxy_type = proxy_config.get("type", "http").lower()
                
                # 验证代理类型
                if proxy_type not in ["http", "https", "socks5"]:
                    raise ValueError(f"不支持的代理类型: {proxy_type}")
                
                # 构建代理URL
                auth = ""
                if proxy_config.get("username") and proxy_config.get("password"):
                    auth = f"{proxy_config['username']}:{proxy_config['password']}@"
                
                proxy_url = f"{proxy_type}://{auth}{proxy_config['host']}:{int(proxy_config['port'])}"
                
                self.session.proxies = {
                    "http": proxy_url,
                    "https": proxy_url
                }
                
                # 测试代理连接
                test_url = "https://www.damai.cn/"
                timeout = proxy_config.get("timeout", 10)
                self.session.get(test_url, timeout=timeout)
                
                self.logger.info(f"代理设置成功: {proxy_url}")
            except Exception as e:
                self.logger.error(f"代理设置失败: {str(e)}")
                if self.config["risk_control"].get("proxy_required", False):
                    raise
                else:
                    self.logger.warning("继续使用直连模式")
                    self.session.proxies = {}

    
    def init_browser(self):
        """初始化浏览器，用于模拟用户操作和获取加密参数"""
        chrome_options = Options()
        if self.config["browser"]["headless"]:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument(f"--window-size={self.config['browser']['window_size']['width']},{self.config['browser']['window_size']['height']}")
        chrome_options.add_argument(f"--user-agent={self.config['browser']['user_agent']}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # 设置代理（如果启用）
        if self.config["risk_control"]["use_proxy"]:
            proxy_config = self.config["risk_control"]["proxy"]
            proxy_url = f"{proxy_config['host']}:{proxy_config['port']}"
            chrome_options.add_argument(f"--proxy-server={proxy_config['host']}:{int(proxy_config['port'])}")  # 修复端口类型转换
        
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # 执行反爬虫检测规避的JavaScript
        self.browser.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        window.navigator.chrome = {runtime: {}};
        Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)
        
        self.logger.info("浏览器初始化完成")
        return self.browser
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.quit()
            self.browser = None
            self.logger.info("浏览器已关闭")
    
    def login(self) -> bool:
        """登录大麦网账号
        
        Returns:
            bool: 登录是否成功
        """
        if not self.browser:
            self.init_browser()
        
        try:
            # 访问登录页面
            if self.browser:
                self.browser.get("https://passport.damai.cn/login")
            self.logger.info("正在访问登录页面")
            
            # 等待登录框加载
            try:
                login_box = WebDriverWait(self.browser, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "login-box"))
                )
            except Exception as e:
                self.logger.error("登录页面加载失败")
                return False
            
            # 确保页面完全加载
            time.sleep(2)
            
            # 切换到账号密码登录
            try:
                switch_btn = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "login-method-tab"))
                )
                switch_btn.click()
                time.sleep(1)
            except Exception:
                self.logger.warning("切换到账号密码登录失败，尝试直接输入")
            
            # 输入账号密码
            try:
                username_input = WebDriverWait(self.browser, 8).until(
                    EC.presence_of_element_located((By.ID, "fm-login-id"))
                )
                password_input = WebDriverWait(self.browser, 8).until(
                    EC.presence_of_element_located((By.ID, "fm-login-password"))
                )
            except Exception as e:
                self.logger.error("找不到账号密码输入框")
                return False
            
            # 清空输入框并输入账号密码
            username_input.clear()
            password_input.clear()
            time.sleep(0.5)  # 添加短暂延迟，模拟人工输入
            username_input.send_keys(self.config["account"]["username"])
            time.sleep(0.5)
            password_input.send_keys(self.config["account"]["password"])
            
            # 点击登录按钮
            try:
                login_button = WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "fm-button"))
                )
                login_button.click()
            except Exception as e:
                self.logger.error("找不到登录按钮")
                return False
            
            # 等待登录成功
            try:
                WebDriverWait(self.browser, 15).until(
                    lambda driver: "login" not in driver.current_url and 
                    "damai.cn" in driver.current_url
                )
            except Exception as e:
                self.logger.error("登录超时或失败")
                return False
            
            # 获取cookies并更新到session
            self._update_cookies_from_browser()
            
            self.logger.info("登录成功")
            return True
            
        except Exception as e:
            self.logger.error(f"登录过程发生异常: {str(e)}")
            self.logger.debug("异常详细信息:", exc_info=True)
            return False
    
    def _update_cookies_from_browser(self):
        """从浏览器获取cookies并更新到requests session"""
        if not self.browser:
            return
        
        browser_cookies = self.browser.get_cookies()
        for cookie in browser_cookies:
            self.cookies[cookie["name"]] = cookie["value"]
            self.session.cookies.set(cookie["name"], cookie["value"])
        
        self.logger.debug(f"已更新 {len(browser_cookies)} 个cookies")
    
    def search_shows(self, keyword: str | None = None) -> Dict[str, Any]:
        """搜索演出信息
        
        Args:
            keyword: 搜索关键词，默认使用配置中的关键词
            
        Returns:
            Dict: 搜索结果
        """
        if not keyword:
            keyword = self.config["target"]["keyword"]
        
        # 使用浏览器访问搜索页面获取加密参数
        if not self.browser:
            self.init_browser()
        
        search_url = f"https://search.damai.cn/search.html?keyword={keyword}"
        self.browser.get(search_url)
        
        # 带重试的搜索结果等待（修正版）
        from selenium.common.exceptions import TimeoutException # type: ignore  
        
        retry_count = 0
        while retry_count < 3:
            try:
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search__itemlist"))
                )
                break
            except TimeoutException:
                retry_count += 1
                if retry_count >= 3:
                    raise
                self.logger.info(f"搜索列表加载超时，重新加载页面(第{retry_count}次重试)")
                self.browser.refresh()
        
        # 提取搜索结果
        show_elements = self.browser.find_elements(By.CLASS_NAME, "search__item")
        
        results = []
        for element in show_elements:
            try:
                title = element.find_element(By.CLASS_NAME, "search__item__name").text
                venue = element.find_element(By.CLASS_NAME, "search__item__venue").text
                show_time = element.find_element(By.CLASS_NAME, "search__item__time").text
                price = element.find_element(By.CLASS_NAME, "search__item__price").text
                link = element.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                results.append({
                    "title": title,
                    "venue": venue,
                    "time": show_time,
                    "price": price,
                    "link": link
                })
            except Exception as e:
                self.logger.warning(f"提取演出信息失败: {str(e)}")
        
        self.logger.info(f"搜索到 {len(results)} 个演出")
        return {"keyword": keyword, "results": results}
    
    def get_show_detail(self, show_url: str) -> Dict[str, Any]:
        """获取演出详情
        
        Args:
            show_url: 演出详情页URL
            
        Returns:
            Dict: 演出详情信息
        """
        if not self.browser:
            self.init_browser()
        
        self.browser.get(show_url)
        
        # 等待详情页加载
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "perform__order__select"))
        )
        
        # 提取演出详情
        try:
            title = self.browser.find_element(By.CLASS_NAME, "perform__title").text
            price_elements = self.browser.find_elements(By.CLASS_NAME, "perform__price__item")
            prices = []
            for price_element in price_elements:
                price_text = price_element.text
                price_value = price_element.find_element(By.CLASS_NAME, "price__value").text
                prices.append({"text": price_text, "value": price_value})
            
            # 提取场次信息
            session_elements = self.browser.find_elements(By.CLASS_NAME, "perform__session__item")
            sessions = []
            for session_element in session_elements:
                session_text = session_element.text
                sessions.append(session_text)
            
            detail = {
                "title": title,
                "prices": prices,
                "sessions": sessions,
                "url": show_url
            }
            
            self.logger.info(f"获取演出详情成功: {title}")
            return detail
            
        except Exception as e:
            self.logger.error(f"获取演出详情失败: {str(e)}")
            self.logger.debug("异常详细信息:", exc_info=True)
            return {"error": str(e)}
    
    def check_ticket_status(self, show_url: str) -> Dict[str, Any]:
        """检查票务状态
        
        Args:
            show_url: 演出详情页URL
            
        Returns:
            Dict: 票务状态信息
        """
        if not self.browser:
            self.init_browser()
        
        self.browser.get(show_url)
        
        # 等待详情页加载
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "perform__order__select"))
        )
        
        # 检查是否有可购买的票
        buy_btn = self.browser.find_element(By.CLASS_NAME, "buybtn")
        btn_text = buy_btn.text
        
        status = {
            "url": show_url,
            "can_buy": False,
            "status_text": btn_text
        }
        
        if "立即购买" in btn_text or "立即预订" in btn_text or "选座购买" in btn_text:
            status["can_buy"] = True
            self.logger.info(f"票务状态: 可购买 - {btn_text}")
        else:
            self.logger.info(f"票务状态: 不可购买 - {btn_text}")
        
        return status
    
    def submit_order(self, show_url: str) -> Dict[str, Any]:
        """提交订单
        
        Args:
            show_url: 演出详情页URL
            
        Returns:
            Dict: 订单提交结果
        """
        if not self.browser:
            self.init_browser()
        
        try:
            # 访问演出详情页
            self.browser.get(show_url)
            self.logger.info("正在加载演出详情页")
            
            # 等待页面加载
            try:
                WebDriverWait(self.browser, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "perform__order__select"))
                )
            except Exception as e:
                self.logger.error("演出详情页加载失败")
                return {"success": False, "message": "页面加载失败"}
            
            # 选择场次（如果有多个场次）
            try:
                session_list = self.browser.find_elements(By.CSS_SELECTOR, ".perform__order__select .select_right_list .select_right_list_item")
                if session_list:
                    # 选择第一个可选场次
                    for session in session_list:
                        if "select_right_list_item_disabled" not in session.get_attribute("class"):
                            session.click()
                            time.sleep(1)
                            break
            except Exception as e:
                self.logger.warning("选择场次失败，尝试继续执行")
            
            # 检查购买按钮状态
            try:
                buy_btn = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "buybtn"))
                )
                btn_text = buy_btn.text.strip()
                
                if "已售完" in btn_text or "暂时缺货" in btn_text:
                    return {"success": False, "message": f"当前场次无票: {btn_text}"}
                
                # 确保按钮可点击
                WebDriverWait(self.browser, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "buybtn"))
                )
                
                # 点击购买按钮
                try:
                    self.browser.execute_script("arguments[0].click();", buy_btn)
                except:
                    buy_btn.click()
                
            except Exception as e:
                self.logger.error("无法点击购买按钮")
                return {"success": False, "message": "无法点击购买按钮"}
            
            # 等待跳转到订单确认页
            try:
                WebDriverWait(self.browser, 15).until(
                    EC.url_contains("buy.damai.cn/orderConfirm")
                )
            except Exception as e:
                self.logger.error("无法跳转到订单确认页")
                return {"success": False, "message": "无法跳转到订单确认页"}
            
            # 选择购票人
            try:
                buyer_result = self._select_buyers()
                if not buyer_result:
                    return {"success": False, "message": "选择购票人失败"}
            except Exception as e:
                self.logger.error(f"选择购票人时发生错误: {str(e)}")
                return {"success": False, "message": f"选择购票人失败: {str(e)}"}
            
            # 处理订单确认页面
            try:
                # 等待页面元素加载
                WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "submit-wrapper"))
                )
                
                # 确认同意服务协议
                agreement = self.browser.find_element(By.CLASS_NAME, "service-agreement")
                if not agreement.is_selected():
                    agreement.click()
                    time.sleep(0.5)
                
                # 获取提交按钮
                submit_btn = self.browser.find_element(By.CLASS_NAME, "submit-wrapper")
                
                # 根据配置决定是否自动提交
                if self.config["strategy"]["auto_submit"]:
                    submit_btn.click()
                    
                    # 等待跳转到支付页面
                    try:
                        WebDriverWait(self.browser, 15).until(
                            EC.url_contains("pay.damai.cn")
                        )
                        self.logger.info("订单提交成功，已跳转到支付页面")
                        return {"success": True, "message": "订单提交成功，请在浏览器中完成支付"}
                    except:
                        self.logger.error("等待支付页面超时")
                        return {"success": False, "message": "提交订单后未能跳转到支付页面"}
                else:
                    self.logger.info("订单已准备好，等待手动提交")
                    return {"success": True, "message": "订单已准备好，请在浏览器中手动提交"}
                
            except Exception as e:
                self.logger.error(f"处理订单确认页面时发生错误: {str(e)}")
                return {"success": False, "message": f"订单确认页面处理失败: {str(e)}"}
                
        except Exception as e:
            self.logger.error(f"提交订单过程发生异常: {str(e)}")
            self.logger.debug("异常详细信息:", exc_info=True)
            return {"success": False, "message": f"提交订单失败: {str(e)}"}
    
    def _select_buyers(self) -> bool:
        """选择购票人
        
        Returns:
            bool: 是否成功选择购票人
        """
        try:
            # 等待购票人列表加载
            buyer_list = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "buyer-list"))
            )
            
            # 确保页面完全加载
            time.sleep(1.5)
            
            # 获取所有购票人
            buyer_items = WebDriverWait(self.browser, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".buyer-list .buyer-item"))
            )
            
            if not buyer_items:
                self.logger.error("未找到可用的购票人")
                return False
            
            # 获取需要选择的购票人数量
            required_count = len(self.config.get("buyer", [])) or 1
            selected_buyers = []
            
            # 如果配置了指定购票人，优先选择配置的购票人
            if self.config.get("buyer"):
                for buyer_info in self.config["buyer"]:
                    buyer_name = buyer_info["name"].strip()
                    
                    # 在所有购票人中查找匹配的
                    for item in buyer_items:
                        try:
                            name_element = item.find_element(By.CLASS_NAME, "buyer-name")
                            current_name = name_element.text.strip()
                            
                            if buyer_name == current_name:
                                checkbox = item.find_element(By.TAG_NAME, "input")
                                
                                # 如果未选中，尝试选择
                                if not checkbox.is_selected():
                                    try:
                                        # 使用JavaScript点击，更可靠
                                        self.browser.execute_script("arguments[0].click();", checkbox)
                                        time.sleep(0.5)
                                        
                                        # 验证是否选中成功
                                        if not checkbox.is_selected():
                                            self.logger.warning(f"选择购票人 {buyer_name} 失败")
                                            continue
                                    except Exception as e:
                                        self.logger.warning(f"选择购票人 {buyer_name} 时出错: {str(e)}")
                                        continue
                                
                                selected_buyers.append(buyer_name)
                                self.logger.info(f"已选择购票人: {buyer_name}")
                                break
                        except Exception as e:
                            continue
            
            # 如果未能选择足够的购票人，选择其他可用购票人
            if len(selected_buyers) < required_count:
                for item in buyer_items:
                    if len(selected_buyers) >= required_count:
                        break
                        
                    try:
                        name_element = item.find_element(By.CLASS_NAME, "buyer-name")
                        buyer_name = name_element.text.strip()
                        
                        # 如果该购票人未被选择
                        if buyer_name not in selected_buyers:
                            checkbox = item.find_element(By.TAG_NAME, "input")
                            
                            # 如果未选中，尝试选择
                            if not checkbox.is_selected():
                                try:
                                    self.browser.execute_script("arguments[0].click();", checkbox)
                                    time.sleep(0.5)
                                    
                                    if checkbox.is_selected():
                                        selected_buyers.append(buyer_name)
                                        self.logger.info(f"已选择补充购票人: {buyer_name}")
                                except Exception as e:
                                    self.logger.warning(f"选择补充购票人 {buyer_name} 时出错: {str(e)}")
                                    continue
                    except Exception as e:
                        continue
            
            # 验证是否选择了足够的购票人
            if len(selected_buyers) < required_count:
                self.logger.error(f"未能选择足够的购票人，需要 {required_count} 人，实际选择 {len(selected_buyers)} 人")
                return False
            
            self.logger.info(f"成功选择 {len(selected_buyers)} 个购票人: {', '.join(selected_buyers)}")
            return True
            
        except Exception as e:
            self.logger.error(f"选择购票人时发生异常: {str(e)}")
            self.logger.debug("异常详细信息:", exc_info=True)
            return False
    
    def add_random_delay(self):
        """添加随机延迟，避免被识别为机器人"""
        delay_config = self.config["risk_control"]["request_delay"]
        delay_time = random.uniform(delay_config["min"], delay_config["max"])
        time.sleep(delay_time)
        return delay_time