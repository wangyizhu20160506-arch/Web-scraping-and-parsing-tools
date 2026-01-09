"""
视频下载器 - 核心下载逻辑
"""
import yt_dlp
import threading
import os
from typing import Optional, Callable, Dict, Any
from utils.helpers import get_default_download_path, sanitize_filename


class VideoDownloader:
    """视频下载器"""
    
    def __init__(self, output_path: Optional[str] = None):
        """
        初始化下载器
        
        Args:
            output_path: 输出目录，默认为用户下载文件夹
        """
        self.output_path = output_path or get_default_download_path()
        self.current_download = None
        self.is_cancelled = False
        self._progress_callback = None
        self._complete_callback = None
        self._error_callback = None
        
        # 新增选项
        self.download_subtitles = False  # 是否下载字幕
        self.subtitle_langs = ['zh', 'en']  # 字幕语言
        self.embed_subtitles = False  # 是否嵌入字幕
        self.output_format = 'mp4'  # 输出格式
    
    def set_output_path(self, path: str):
        """设置输出目录"""
        self.output_path = path
        if not os.path.exists(path):
            os.makedirs(path)
    
    def set_callbacks(
        self,
        progress: Optional[Callable[[Dict], None]] = None,
        complete: Optional[Callable[[str], None]] = None,
        error: Optional[Callable[[str], None]] = None
    ):
        """
        设置回调函数
        
        Args:
            progress: 进度回调，参数为进度信息字典
            complete: 完成回调，参数为文件路径
            error: 错误回调，参数为错误信息
        """
        self._progress_callback = progress
        self._complete_callback = complete
        self._error_callback = error
    
    def _progress_hook(self, d: Dict[str, Any]):
        """yt-dlp进度钩子"""
        if self.is_cancelled:
            raise Exception("下载已取消")
        
        if d['status'] == 'downloading':
            progress_info = {
                'status': 'downloading',
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes') or d.get('total_bytes_estimate', 0),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0),
                'filename': d.get('filename', ''),
                'percent': 0
            }
            
            if progress_info['total_bytes'] > 0:
                progress_info['percent'] = (
                    progress_info['downloaded_bytes'] / progress_info['total_bytes'] * 100
                )
            
            if self._progress_callback:
                self._progress_callback(progress_info)
                
        elif d['status'] == 'finished':
            if self._progress_callback:
                self._progress_callback({
                    'status': 'finished',
                    'percent': 100,
                    'filename': d.get('filename', '')
                })
    
    def download(
        self,
        url: str,
        format_id: str = 'best',
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        下载视频
        
        Args:
            url: 视频URL
            format_id: 格式ID，默认为最佳质量
            filename: 自定义文件名
            
        Returns:
            下载的文件路径，失败返回None
        """
        self.is_cancelled = False
        
        # 检测是否为Bilibili
        is_bilibili = 'bilibili.com' in url.lower() or 'b23.tv' in url.lower()
        
        # 构建输出模板
        if filename:
            output_template = os.path.join(
                self.output_path,
                sanitize_filename(filename) + '.%(ext)s'
            )
        else:
            output_template = os.path.join(
                self.output_path,
                '%(title)s.%(ext)s'
            )
        
        # 根据format_id和平台构建格式选择
        if is_bilibili:
            # Bilibili: 需要合并视频和音频流
            # 使用 bv*+ba* 格式选择最佳视频+最佳音频
            if format_id == 'best' or format_id == '最佳质量':
                format_selector = 'bv*+ba*/b*'  # best video + best audio / best
            elif format_id == 'bestaudio':
                format_selector = 'ba*/b*'  # best audio / best
            elif 'p' in format_id:
                height = format_id.replace('p', '')
                format_selector = f'bv*[height<={height}]+ba*/b*[height<={height}]/b*'
            else:
                format_selector = 'bv*+ba*/b*'
        else:
            # 其他平台（YouTube等）
            if format_id == 'best' or format_id == '最佳质量':
                format_selector = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            elif format_id == 'bestaudio':
                format_selector = 'bestaudio/best'
            elif 'p' in format_id:
                height = format_id.replace('p', '')
                format_selector = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best'
            else:
                format_selector = format_id
        
        # 基础配置
        ydl_opts = {
            'format': format_selector,
            'outtmpl': output_template,
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': self.output_format,  # 输出格式
        }
        
        # 字幕下载选项
        if self.download_subtitles:
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True  # 自动生成的字幕
            ydl_opts['subtitleslangs'] = self.subtitle_langs
            ydl_opts['subtitlesformat'] = 'srt/ass/vtt'
            
            # 嵌入字幕到视频
            if self.embed_subtitles:
                ydl_opts.setdefault('postprocessors', []).append({
                    'key': 'FFmpegEmbedSubtitle',
                })
        
        # 尝试设置FFmpeg位置
        try:
            from utils.ffmpeg_manager import ffmpeg_manager
            ffmpeg_path = ffmpeg_manager.get_ffmpeg_path()
            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path
        except:
            pass
        
        # 格式转换后处理
        postprocessors = ydl_opts.get('postprocessors', [])
        
        # 音频后处理
        if format_id == 'bestaudio':
            postprocessors.append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            })
        # 视频格式转换
        elif self.output_format != 'mp4':
            postprocessors.append({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': self.output_format,
            })
        
        if postprocessors:
            ydl_opts['postprocessors'] = postprocessors
        
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.current_download = ydl
                info = ydl.extract_info(url, download=True)
                
                if info:
                    # 获取实际的文件路径
                    if 'requested_downloads' in info:
                        filepath = info['requested_downloads'][0].get('filepath')
                    else:
                        filepath = ydl.prepare_filename(info)
                    
                    if self._complete_callback:
                        self._complete_callback(filepath)
                    
                    return filepath
                    
        except Exception as e:
            error_msg = str(e)
            if "下载已取消" not in error_msg:
                if self._error_callback:
                    self._error_callback(error_msg)
            return None
        finally:
            self.current_download = None
        
        return None
    
    def download_async(
        self,
        url: str,
        format_id: str = 'best',
        filename: Optional[str] = None
    ) -> threading.Thread:
        """
        异步下载视频
        
        Args:
            url: 视频URL
            format_id: 格式ID
            filename: 自定义文件名
            
        Returns:
            下载线程
        """
        thread = threading.Thread(
            target=self.download,
            args=(url, format_id, filename),
            daemon=True
        )
        thread.start()
        return thread
    
    def cancel(self):
        """取消当前下载"""
        self.is_cancelled = True
