"""
下载历史管理器 - 记录和管理下载历史
"""
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional


class HistoryManager:
    """下载历史管理器"""
    
    def __init__(self):
        # 获取数据目录
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.data_dir = os.path.join(base_path, 'data')
        self.history_file = os.path.join(self.data_dir, 'download_history.json')
        
        # 确保数据目录存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 加载历史记录
        self.history: List[Dict] = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def add_record(
        self,
        url: str,
        title: str,
        platform: str,
        filepath: str,
        thumbnail: Optional[str] = None,
        duration: Optional[int] = None,
        quality: Optional[str] = None,
        status: str = 'completed'
    ):
        """
        添加下载记录
        
        Args:
            url: 视频URL
            title: 视频标题
            platform: 平台名称
            filepath: 下载文件路径
            thumbnail: 缩略图URL
            duration: 视频时长(秒)
            quality: 下载质量
            status: 状态 (completed/failed)
        """
        record = {
            'id': len(self.history) + 1,
            'url': url,
            'title': title,
            'platform': platform,
            'filepath': filepath,
            'thumbnail': thumbnail,
            'duration': duration,
            'quality': quality,
            'status': status,
            'download_time': datetime.now().isoformat(),
        }
        
        self.history.insert(0, record)  # 新记录在前
        
        # 限制历史记录数量
        if len(self.history) > 500:
            self.history = self.history[:500]
        
        self._save_history()
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """获取历史记录"""
        return self.history[:limit]
    
    def search_history(self, keyword: str) -> List[Dict]:
        """搜索历史记录"""
        keyword = keyword.lower()
        return [
            record for record in self.history
            if keyword in record.get('title', '').lower()
            or keyword in record.get('platform', '').lower()
        ]
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self._save_history()
    
    def delete_record(self, record_id: int):
        """删除单条记录"""
        self.history = [r for r in self.history if r.get('id') != record_id]
        self._save_history()


# 全局实例
history_manager = HistoryManager()
