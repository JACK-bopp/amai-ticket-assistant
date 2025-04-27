from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
from datetime import datetime
import logging

class DamaiMobileBot:
    def __init__(self):
        self.config = self.load_config()
        self.driver = None
        self.logger = self.setup_logger()
        
    def setup_logger(self):
        logger = logging.getLogger('damai_mobile')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("请先创建config.json文件")
            return None

    def init_driver(self):
        options = webdriver.ChromeOptions()
        # 设置移动端User-Agent
        mobile_emulation = {
            "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def login(self):
        try:
            self.driver.get('https://m.damai.cn/damai/minilogin/index.html')
            self.logger.info("请在手机浏览器中完成登录")
            
            # 等待登录成功
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.CLASS_NAME, "user-header"))
            )
            self.logger.info("登录成功！")
            return True
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            return False

    def go_to_detail(self, show_id):
        try:
            url = f'https://m.damai.cn/damai/detail/item.html?itemId={show_id}'
            self.driver.get(url)
            self.logger.info("已进入演出详情页")
            return True
        except Exception as e:
            self.logger.error(f"访问详情页失败: {str(e)}")
            return False

    def select_ticket(self):
        try:
            # 等待"立即购买"按钮出现并点击
            buy_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "buy__button"))
            )
            buy_button.click()
            
            # 选择票档
            price_list = self.driver.find_elements(By.CLASS_NAME, "sku-item")
            for price in price_list:
                if not "sold-out" in price.get_attribute("class"):
                    price.click()
                    break
            
            # 选择购票数量
            num_button = self.driver.find_element(By.CLASS_NAME, "number-plus")
            num_button.click()
            
            # 确认购买
            confirm_button = self.driver.find_element(By.CLASS_NAME, "submit-button")
            confirm_button.click()
            
            self.logger.info("已选择票档并提交订单")
            return True
        except Exception as e:
            self.logger.error(f"选择票档失败: {str(e)}")
            return False

    def run(self):
        try:
            self.init_driver()
            if not self.login():
                return

            show_id = self.config['target']['show_id']
            start_time = datetime.strptime(self.config['target']['start_time'], "%Y-%m-%d %H:%M:%S")
            
            # 等待到开售时间
            while datetime.now() < start_time:
                remaining = (start_time - datetime.now()).total_seconds()
                self.logger.info(f"距离开售还有 {remaining:.1f} 秒")
                time.sleep(1)
            
            success = False
            attempt_count = 0
            
            while not success and attempt_count < 100:  # 最多尝试100次
                attempt_count += 1
                self.logger.info(f"第 {attempt_count} 次尝试抢票")
                
                if self.go_to_detail(show_id):
                    if self.select_ticket():
                        self.logger.info("抢票成功！请在30分钟内完成支付")
                        success = True
                        break
                
                time.sleep(0.5)  # 短暂延迟后重试
                
        except KeyboardInterrupt:
            self.logger.info("\n程序已停止")
        except Exception as e:
            self.logger.error(f"程序发生错误: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    bot = DamaiMobileBot()
    bot.run() 