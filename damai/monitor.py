# 大麦网票务监控模块

import time
import logging
import threading
from typing import Dict, Any, List, Callable
from datetime import datetime

from .api import DamaiAPI

class TicketMonitor:
    """票务监控类，负责监控目标演出的票务状态"""
    
    def __init__(self, config: Dict[str, Any], api: DamaiAPI):
        """初始化票务监控器
        
        Args:
            config: 配置信息
            api: DamaiAPI实例
        """
        self.config = config
        self.api = api
        self.logger = logging.getLogger("damai.monitor")
        self.running = False
        self.monitor_thread = None
        self.target_shows = []
        self.callbacks = []
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """添加票务状态变化回调函数
        
        Args:
            callback: 回调函数，接收票务状态信息作为参数
        """
        self.callbacks.append(callback)
    
    def _notify_callbacks(self, status: Dict[str, Any]):
        """通知所有回调函数
        
        Args:
            status: 票务状态信息
        """
        for callback in self.callbacks:
            try:
                callback(status)
            except Exception as e:
                self.logger.error(f"执行回调函数失败: {str(e)}")
    
    def search_target_shows(self) -> List[Dict[str, Any]]:
        """搜索目标演出
        
        Returns:
            List: 符合条件的演出列表
        """
        keyword = self.config["target"]["keyword"]
        search_results = self.api.search_shows(keyword)
        
        # 筛选符合条件的演出
        filtered_shows = []
        date_range = self.config["target"]["date_range"]
        price_range = self.config["target"]["price_range"]
        
        for show in search_results["results"]:
            # 解析日期
            try:
                show_date_str = show["time"].split()[0]
                show_date = datetime.strptime(show_date_str, "%Y.%m.%d")
                start_date = datetime.strptime(date_range["start"], "%Y-%m-%d")
                end_date = datetime.strptime(date_range["end"], "%Y-%m-%d")
                
                # 检查日期是否在范围内
                if start_date <= show_date <= end_date:
                    # 解析价格
                    price_text = show["price"].replace("¥", "").split("-")
                    min_price = float(price_text[0])
                    
                    # 检查价格是否在范围内
                    if price_range["min"] <= min_price <= price_range["max"]:
                        filtered_shows.append(show)
            except Exception as e:
                self.logger.warning(f"解析演出信息失败: {str(e)}")
        
        self.logger.info(f"找到 {len(filtered_shows)} 个符合条件的演出")
        return filtered_shows
    
    def start_monitoring(self):
        """开始监控票务状态"""
        if self.running:
            self.logger.warning("监控器已经在运行中")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_task)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("票务监控已启动")
    
    def stop_monitoring(self):
        """停止监控票务状态"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
            self.monitor_thread = None
        self.logger.info("票务监控已停止")
    
    def _monitoring_task(self):
        """监控任务主循环"""
        attempt_count = 0
        max_attempts = self.config["strategy"]["max_attempts"]
        
        while self.running and attempt_count < max_attempts:
            try:
                # 如果目标演出列表为空，则搜索目标演出
                if not self.target_shows:
                    self.target_shows = self.search_target_shows()
                    if not self.target_shows:
                        self.logger.warning("未找到符合条件的演出，将在下次循环重新搜索")
                        time.sleep(self.config["strategy"]["monitor_interval"]["normal"])
                        continue
                
                # 检查每个目标演出的票务状态
                for show in self.target_shows:
                    status = self.api.check_ticket_status(show["link"])
                    
                    # 如果有票，通知回调函数
                    if status["can_buy"]:
                        self.logger.info(f"发现可购买票: {show['title']}")
                        status["show_info"] = show
                        self._notify_callbacks(status)
                    
                    # 添加随机延迟
                    self.api.add_random_delay()
                
                # 增加尝试次数
                attempt_count += 1
                self.logger.debug(f"监控循环 {attempt_count}/{max_attempts}")
                
                # 根据策略设置不同的监控间隔
                if any(show["status_text"] == "即将开抢" for show in self.target_shows):
                    # 爆发模式 - 即将开抢时使用更短的间隔
                    interval = self.config["strategy"]["monitor_interval"]["rush"]
                else:
                    # 常规模式
                    interval = self.config["strategy"]["monitor_interval"]["normal"]
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"监控任务异常: {str(e)}")
                time.sleep(self.config["strategy"]["monitor_interval"]["normal"])
        
        if attempt_count >= max_attempts:
            self.logger.info(f"已达到最大尝试次数 {max_attempts}，监控停止")
        
        self.running = False
    
    def is_running(self) -> bool:
        """检查监控器是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self.running