"""
URL解析器 - 解析视频信息
"""
import yt_dlp
from typing import Optional, Dict, Any, List
from utils.helpers import detect_platform


class VideoParser:
    """视频URL解析器"""
    
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        获取视频信息
        
        Args:
            url: 视频URL
            
        Returns:
            视频信息字典，包含标题、时长、格式等
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    return None
                
                # 整理格式列表
                formats = self._parse_formats(info.get('formats', []))
                
                return {
                    'title': info.get('title', '未知标题'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', '未知上传者'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'platform': detect_platform(url),
                    'webpage_url': info.get('webpage_url', url),
                    'formats': formats,
                    'raw_formats': info.get('formats', []),
                }
        except Exception as e:
            print(f"解析视频信息失败: {e}")
            return None
    
    def _parse_formats(self, formats: List[Dict]) -> List[Dict[str, Any]]:
        """
        解析并整理格式列表
        
        Args:
            formats: yt-dlp返回的原始格式列表
            
        Returns:
            整理后的格式列表
        """
        parsed = []
        seen = set()
        
        for fmt in formats:
            # 跳过纯音频格式（除非是音频下载）
            vcodec = fmt.get('vcodec', 'none')
            acodec = fmt.get('acodec', 'none')
            
            # 获取分辨率
            height = fmt.get('height')
            width = fmt.get('width')
            
            if height and vcodec != 'none':
                resolution = f"{height}p"
                
                # 避免重复的分辨率
                if resolution not in seen:
                    seen.add(resolution)
                    parsed.append({
                        'format_id': fmt.get('format_id'),
                        'resolution': resolution,
                        'height': height,
                        'width': width,
                        'ext': fmt.get('ext', 'mp4'),
                        'filesize': fmt.get('filesize') or fmt.get('filesize_approx'),
                        'vcodec': vcodec,
                        'acodec': acodec,
                        'fps': fmt.get('fps'),
                        'tbr': fmt.get('tbr'),  # 总比特率
                    })
        
        # 按分辨率排序（从高到低）
        parsed.sort(key=lambda x: x.get('height', 0), reverse=True)
        
        # 添加"最佳质量"选项
        if parsed:
            parsed.insert(0, {
                'format_id': 'best',
                'resolution': '最佳质量',
                'height': 9999,
                'ext': 'mp4',
            })
        
        # 添加"仅音频"选项
        parsed.append({
            'format_id': 'bestaudio',
            'resolution': '仅音频',
            'height': 0,
            'ext': 'mp3',
        })
        
        return parsed
    
    def get_available_qualities(self, url: str) -> List[str]:
        """
        获取可用的视频质量列表
        
        Args:
            url: 视频URL
            
        Returns:
            质量选项列表
        """
        info = self.get_video_info(url)
        if info and info.get('formats'):
            return [f['resolution'] for f in info['formats']]
        return ['最佳质量', '1080p', '720p', '480p', '360p', '仅音频']
