# 大麦网订单处理模块

import time
import logging
from typing import Dict, Any, List

from .api import DamaiAPI

class OrderProcessor:
    """订单处理类，负责处理订单提交和支付流程"""
    
    def __init__(self, config: Dict[str, Any], api: DamaiAPI):
        """初始化订单处理器
        
        Args:
            config: 配置信息
            api: DamaiAPI实例
        """
        self.config = config
        self.api = api
        self.logger = logging.getLogger("damai.order")
    
    def process_order(self, show_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理订单
        
        Args:
            show_info: 演出信息
            
        Returns:
            Dict: 订单处理结果
        """
        self.logger.info(f"开始处理订单: {show_info['title']}")
        
        # 获取演出详情
        show_detail = self.api.get_show_detail(show_info["link"])
        if "error" in show_detail:
            self.logger.error(f"获取演出详情失败: {show_detail['error']}")
            return {"success": False, "message": f"获取演出详情失败: {show_detail['error']}"}
        
        # 选择最佳票档
        best_price = self._select_best_price(show_detail["prices"])
        if not best_price:
            self.logger.warning("未找到合适的票档")
            return {"success": False, "message": "未找到合适的票档"}
        
        self.logger.info(f"选择票档: {best_price['text']} - {best_price['value']}")
        
        # 提交订单
        order_result = self.api.submit_order(show_info["link"])
        
        return order_result
    
    def _select_best_price(self, prices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """选择最佳票档
        
        Args:
            prices: 票档列表
            
        Returns:
            Dict: 最佳票档信息
        """
        if not prices:
            return None
        
        # 获取票档优先级配置
        priority_config = self.config["ticket_priority"]
        price_range = self.config["target"]["price_range"]
        
        # 按优先级排序票档
        prioritized_prices = []
        
        # 首先检查是否有匹配优先级配置的票档
        for price in prices:
            price_text = price["text"]
            price_value = float(price["value"].replace("¥", ""))
            
            # 检查价格是否在范围内
            if price_value < price_range["min"] or price_value > price_range["max"]:
                continue
            
            # 检查是否匹配优先级配置
            priority = 999  # 默认优先级最低
            for p_config in priority_config:
                if p_config["name"] in price_text:
                    priority = p_config["priority"]
                    break
            
            prioritized_prices.append({
                "text": price_text,
                "value": price["value"],
                "priority": priority
            })
        
        # 按优先级排序
        prioritized_prices.sort(key=lambda x: x["priority"])
        
        # 如果没有匹配优先级的票档，则返回价格范围内的第一个票档
        if not prioritized_prices:
            for price in prices:
                price_value = float(price["value"].replace("¥", ""))
                if price_range["min"] <= price_value <= price_range["max"]:
                    return price
            return None
        
        # 返回优先级最高的票档
        return prioritized_prices[0]