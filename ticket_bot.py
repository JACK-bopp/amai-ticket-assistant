import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TicketBot:
    def __init__(self):
        self.config = self.load_config()
        self.driver = None

    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("配置文件不存在，请先创建config.json文件")
            return None

    def init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def login(self):
        self.driver.get('https://kyfw.12306.cn/otn/resources/login.html')
        print("请在浏览器中手动完成登录")
        
        try:
            # 等待用户完成登录
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.ID, "J-index"))
            )
            print("登录成功！")
            return True
        except TimeoutException:
            print("登录超时，请重试")
            return False

    def search_ticket(self):
        try:
            # 跳转到车票预订页面
            self.driver.get('https://kyfw.12306.cn/otn/leftTicket/init')
            
            # 输入出发地
            from_input = self.driver.find_element(By.ID, "fromStationText")
            from_input.click()
            from_input.send_keys(self.config['from_station'])
            
            # 输入目的地
            to_input = self.driver.find_element(By.ID, "toStationText")
            to_input.click()
            to_input.send_keys(self.config['to_station'])
            
            # 输入出发日期
            date_input = self.driver.find_element(By.ID, "train_date")
            self.driver.execute_script(
                f"document.getElementById('train_date').value='{self.config['train_date']}'"
            )
            
            # 点击查询按钮
            search_button = self.driver.find_element(By.ID, "query_ticket")
            search_button.click()
            
            print("开始查询车票...")
            time.sleep(2)  # 等待查询结果加载
            
            return True
        except Exception as e:
            print(f"查询车票时发生错误: {str(e)}")
            return False

    def run(self):
        try:
            self.init_driver()
            if not self.login():
                return
            
            while True:
                if self.search_ticket():
                    print("查询完成，请在浏览器中查看结果")
                time.sleep(5)  # 等待5秒后再次查询
                
        except KeyboardInterrupt:
            print("\n程序已停止")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    bot = TicketBot()
    bot.run() 