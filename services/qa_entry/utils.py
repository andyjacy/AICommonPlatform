import logging
import json
from typing import Optional
from redis import Redis
from pythonjsonlogger import jsonlogger

def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """
    配置日志记录
    
    参数：
    - name: logger名称
    - level: 日志级别
    
    返回：
    - logger: 配置好的logger对象
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # 控制台处理器 - JSON格式
    console_handler = logging.StreamHandler()
    json_formatter = jsonlogger.JsonFormatter()
    console_handler.setFormatter(json_formatter)
    
    # 添加处理器
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger

def get_redis_client(redis_url: str) -> Redis:
    """
    获取Redis客户端
    
    参数：
    - redis_url: Redis连接URL
    
    返回：
    - redis: Redis客户端
    """
    return Redis.from_url(redis_url, decode_responses=True)

def extract_keywords(text: str) -> list:
    """
    从文本中提取关键词（简单实现）
    
    参数：
    - text: 输入文本
    
    返回：
    - keywords: 关键词列表
    """
    # 简单的分词（在生产环境应使用专业分词库如jieba）
    import re
    words = re.findall(r'\w+', text)
    return words

def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（简单实现）
    
    参数：
    - text1: 文本1
    - text2: 文本2
    
    返回：
    - similarity: 相似度分数(0-1)
    """
    # 简单的基于共同词汇的相似度计算
    words1 = set(extract_keywords(text1.lower()))
    words2 = set(extract_keywords(text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0
