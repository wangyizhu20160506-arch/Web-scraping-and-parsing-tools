"""
辅助工具函数
"""
import os
import re
from datetime import timedelta


def format_size(bytes_size: int) -> str:
    """格式化文件大小"""
    if bytes_size is None:
        return "未知"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def format_duration(seconds: int) -> str:
    """格式化时长"""
    if seconds is None:
        return "未知"
    
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    # Windows非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, '_', filename)
    # 移除控制字符
    filename = ''.join(c for c in filename if ord(c) >= 32)
    # 限制长度
    if len(filename) > 200:
        filename = filename[:200]
    return filename.strip()


def get_default_download_path() -> str:
    """获取默认下载路径"""
    # 优先使用用户的下载文件夹
    download_path = os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloader")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    return download_path


def detect_platform(url: str) -> str:
    """检测视频平台"""
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'YouTube'
    elif 'bilibili.com' in url_lower or 'b23.tv' in url_lower:
        return 'Bilibili'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'Twitter/X'
    elif 'tiktok.com' in url_lower:
        return 'TikTok'
    elif 'instagram.com' in url_lower:
        return 'Instagram'
    elif 'facebook.com' in url_lower:
        return 'Facebook'
    elif 'vimeo.com' in url_lower:
        return 'Vimeo'
    else:
        return '其他平台'


def is_valid_url(url: str) -> bool:
    """验证URL格式"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None
