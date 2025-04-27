#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import yaml # type: ignore
import logging
from datetime import datetime
from typing import Dict, Any
from damai.app_api import DamaiAppAPI

def setup_logging(config: Dict[str, Any]) -> None:
    """设置日志配置"""
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_file = log_config.get("file", "damai_app.log")
    
    # 创建日志目录
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 仅保留必要的日志处理器，避免重复日志
    handlers = [
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
    
    # 简洁的日志格式
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    # 配置根日志
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
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
        
        if not config.get("target", {}).get("show_id"):
            raise ValueError("请在配置文件中填写目标演出ID")
            
        if not config.get("target", {}).get("start_time"):
            raise ValueError("请在配置文件中填写开售时间")
            
        if not config.get("buyer") or not config.get("buyer")[0].get("name"):
            raise ValueError("请在配置文件中填写观演人信息")
            
        return config
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

def wait_until_start_time(start_time: str) -> bool:
    """等待到指定时间，返回是否需要继续执行"""
    try:
        target_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        
        # 如果已经过了开售时间，直接返回
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
    print("大麦APP抢票程序启动...")
    
    # 加载配置
    config = load_config()
    
    # 设置日志
    setup_logging(config)
    logger = logging.getLogger("damai.main")
    
    try:
        # 等待到开售时间
        if not wait_until_start_time(config["target"]["start_time"]):
            logger.error("等待开售时间失败，程序退出")
            return
        
        # 初始化API
        api = DamaiAppAPI(config)
        logger.info("初始化APP自动化成功")
        
        # 检查登录状态
        if not api.login_if_needed():
            logger.error("登录失败，程序退出")
            return
        
        logger.info("登录成功，开始抢票")
        
        # 获取目标演出ID
        show_id = config["target"]["show_id"]
        
        # 抢票设置
        max_attempts = config.get("strategy", {}).get("max_attempts", 0)  # 0表示无限次
        retry_delay = config.get("strategy", {}).get("retry_delay", 0.5)  # 重试延迟
        
        # 开始抢票循环
        attempt_count = 0
        while max_attempts == 0 or attempt_count < max_attempts:
            attempt_count += 1
            
            try:
                logger.info(f"第 {attempt_count} 次尝试抢票")
                
                # 跳转到演出详情页
                if not api.go_to_show(show_id):
                    logger.warning("无法进入演出详情页，重试中...")
                    time.sleep(retry_delay)
                    continue
                
                # 执行购票
                result = api.buy_ticket()
                if result:
                    logger.info("抢票成功！请在大麦APP中完成支付。")
                    break
                
                # 短暂等待后重试，使用动态延迟
                if attempt_count % 10 == 0:
                    # 每10次尝试后稍微休息一下，避免请求过于频繁
                    logger.info("暂停一下，避免请求频率过高...")
                    time.sleep(retry_delay * 2)
                else:
                    time.sleep(retry_delay)
            
            except Exception as e:
                logger.error(f"抢票过程发生错误: {str(e)}")
                time.sleep(retry_delay * 2)  # 出错后等待更长时间
        
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

if __name__ == "__main__":
    main() 