#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import yaml # type: ignore
import logging
from datetime import datetime
from typing import Dict, Any
from damai.mobile_api import DamaiMobileAPI

def setup_logging(config: Dict[str, Any]) -> None:
    """设置日志配置"""
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_file = log_config.get("file", "mobile_damai.log")
    
    # 创建日志目录
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_config(config_file: str = "config_mobile.yaml") -> Dict[str, Any]:
    """加载配置文件"""
    try:
        if not os.path.exists(config_file):
            print(f"配置文件 {config_file} 不存在，请创建配置文件")
            sys.exit(1)
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 验证必要的配置项
        if not config.get("account", {}).get("username") or not config.get("account", {}).get("password"):
            raise ValueError("请在配置文件中填写账号和密码")
        
        if not config.get("target", {}).get("url") and not config.get("target", {}).get("show_id"):
            raise ValueError("请在配置文件中填写目标演出URL或ID")
            
        return config
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

def wait_until_start_time(start_time: str) -> bool:
    """等待到指定时间，返回是否需要继续执行"""
    try:
        if not start_time:
            print("未设置开售时间，将直接开始抢票")
            return True
            
        target_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        
        if current_time >= target_time:
            print("开售时间已过，将直接尝试抢票")
            return True
            
        wait_seconds = (target_time - current_time).total_seconds()
        print(f"等待开售，距离开始还有 {wait_seconds:.1f} 秒")
        
        # 提前10秒准备，但等待时间不少于1秒
        preparation_time = min(10, max(1, wait_seconds * 0.1))
        
        if wait_seconds > preparation_time:
            sleep_time = wait_seconds - preparation_time
            # 每隔10秒输出一次等待信息
            while sleep_time > 0:
                time.sleep(min(10, sleep_time))
                sleep_time -= 10
                remaining = target_time - datetime.now()
                if remaining.total_seconds() > 0:
                    print(f"剩余等待时间: {remaining.total_seconds():.1f} 秒")
                    
        print("准备开始抢票...")
        
        # 等待到开售时间或稍微提前一点开始（避免时间不同步问题）
        remaining = (target_time - datetime.now()).total_seconds()
        if remaining > 0:
            time.sleep(max(0, remaining - 0.5))  # 提前0.5秒开始抢票
            
        return True
    except Exception as e:
        print(f"等待过程发生错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("大麦移动端抢票程序启动...")
    
    # 加载配置
    config = load_config()
    
    # 设置日志
    setup_logging(config)
    logger = logging.getLogger("damai.mobile")
    
    try:
        # 等待开售时间（如果配置了）
        start_time = config.get("target", {}).get("start_time", "")
        if start_time and not wait_until_start_time(start_time):
            logger.error("等待开售时间失败，程序退出")
            return
        
        # 初始化API
        api = DamaiMobileAPI(config)
        logger.info("初始化移动端API成功")
        
        # 登录
        if not api.login():
            logger.error("登录失败，程序退出")
            return
        
        logger.info("登录成功，开始抢票")
        
        # 获取目标信息
        target_url = config.get("target", {}).get("url", "")
        show_id = config.get("target", {}).get("show_id", "")
        
        if not target_url and not show_id:
            logger.error("未配置目标演出URL或ID，程序退出")
            return
            
        # 如果只有show_id，构造URL
        if not target_url and show_id:
            target_url = f"https://detail.damai.cn/item.htm?id={show_id}"
            logger.info(f"根据演出ID构造URL: {target_url}")
        
        # 抢票设置
        strategy = config.get("strategy", {})
        max_attempts = strategy.get("max_attempts", 0)  # 0表示无限次
        retry_delay = strategy.get("retry_delay", {})
        min_delay = retry_delay.get("min", 0.5)
        max_delay = retry_delay.get("max", 2.0)
        
        # 开始抢票循环
        attempt_count = 0
        
        while max_attempts == 0 or attempt_count < max_attempts:
            attempt_count += 1
            logger.info(f"第 {attempt_count} 次尝试抢票")
            
            try:
                # 提交订单
                result = api.submit_order(target_url)
                
                if result.get("success"):
                    logger.info(f"抢票成功: {result.get('message', '请尽快支付')}")
                    break
                else:
                    logger.warning(f"本次尝试失败: {result.get('message', '未知原因')}")
                    
                # 动态调整等待时间
                if attempt_count % 10 == 0:
                    # 每10次尝试后稍微休息一下，避免请求频率过高
                    logger.info("暂停一下，避免请求频率过高...")
                    time.sleep(max_delay)
                else:
                    time.sleep(min_delay)
                    
            except Exception as e:
                logger.error(f"抢票过程发生错误: {str(e)}")
                # 出错后等待更长时间
                time.sleep(max_delay)
        
        if max_attempts > 0 and attempt_count >= max_attempts:
            logger.warning(f"达到最大尝试次数 {max_attempts}，抢票结束")
    
    except Exception as e:
        logger.error(f"程序运行时发生错误: {str(e)}")
    
    finally:
        # 清理资源
        try:
            if 'api' in locals():
                api.close()
                logger.info("已关闭抢票会话")
        except Exception as e:
            logger.error(f"关闭会话时发生错误: {str(e)}")
            
        print("抢票程序已结束")

if __name__ == "__main__":
    main() 