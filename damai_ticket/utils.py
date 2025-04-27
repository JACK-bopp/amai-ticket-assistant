import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

def setup_logging(log_dir: str = "logs") -> None:
    """设置日志配置
    
    Args:
        log_dir: 日志目录
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(
        log_dir,
        f"damai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """加载配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        Dict: 配置信息
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"加载配置文件失败: {str(e)}")
        return {}

def save_config(config: Dict[str, Any], config_file: str = "config.json") -> bool:
    """保存配置文件
    
    Args:
        config: 配置信息
        config_file: 配置文件路径
        
    Returns:
        bool: 是否保存成功
    """
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logging.error(f"保存配置文件失败: {str(e)}")
        return False

def format_time(timestamp: float) -> str:
    """格式化时间戳
    
    Args:
        timestamp: 时间戳
        
    Returns:
        str: 格式化后的时间字符串
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_show_url(show_id: str) -> str:
    """获取演出详情页URL
    
    Args:
        show_id: 演出ID
        
    Returns:
        str: 演出详情页URL
    """
    return f"https://m.damai.cn/damai/detail/item.html?itemId={show_id}"

def validate_config(config: Dict[str, Any]) -> bool:
    """验证配置信息
    
    Args:
        config: 配置信息
        
    Returns:
        bool: 配置是否有效
    """
    required_fields = {
        'account': ['username', 'password'],
        'buyer': ['name']
    }
    
    try:
        for section, fields in required_fields.items():
            if section not in config:
                logging.error(f"缺少配置节: {section}")
                return False
                
            for field in fields:
                if field not in config[section]:
                    logging.error(f"缺少配置项: {section}.{field}")
                    return False
                    
        return True
        
    except Exception as e:
        logging.error(f"验证配置信息失败: {str(e)}")
        return False 