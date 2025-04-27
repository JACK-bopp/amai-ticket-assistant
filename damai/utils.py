# 大麦网抢票工具函数模块

import os
import yaml
import logging
import random
import string
from typing import Dict, Any
from datetime import datetime

def setup_logger(log_level=logging.INFO):
    """设置日志记录器
    
    Args:
        log_level: 日志级别
    
    Returns:
        logging.Logger: 日志记录器
    """
    # 创建logs目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"damai_{timestamp}.log")
    
    # 配置根日志记录器
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def load_config(config_path="config.yaml") -> Dict[str, Any]:
    """加载配置文件
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        Dict: 配置信息
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        raise Exception(f"加载配置文件失败: {str(e)}")

def generate_random_string(length=8):
    """生成随机字符串
    
    Args:
        length: 字符串长度
    
    Returns:
        str: 随机字符串
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def parse_price(price_str):
    """解析价格字符串
    
    Args:
        price_str: 价格字符串，如"¥280"
    
    Returns:
        float: 价格数值
    """
    try:
        return float(price_str.replace("¥", "").strip())
    except:
        return 0.0

def format_show_info(show):
    """格式化演出信息
    
    Args:
        show: 演出信息字典
    
    Returns:
        str: 格式化后的演出信息
    """
    return f"《{show['title']}》 {show['time']} {show['venue']} {show['price']}"