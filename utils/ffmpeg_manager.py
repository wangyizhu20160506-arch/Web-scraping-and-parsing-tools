"""
FFmpeg 管理器 - 自动下载和配置FFmpeg
"""
import os
import sys
import zipfile
import shutil
import urllib.request
from typing import Optional


class FFmpegManager:
    """FFmpeg便携版管理器"""
    
    # FFmpeg便携版下载地址 (使用GitHub release)
    FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    def __init__(self):
        # 获取程序目录
        if getattr(sys, 'frozen', False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.ffmpeg_dir = os.path.join(self.base_path, 'ffmpeg')
        self.ffmpeg_exe = os.path.join(self.ffmpeg_dir, 'bin', 'ffmpeg.exe')
    
    def is_available(self) -> bool:
        """检查FFmpeg是否可用"""
        # 检查本地便携版
        if os.path.exists(self.ffmpeg_exe):
            return True
        
        # 检查系统PATH
        return shutil.which('ffmpeg') is not None
    
    def get_ffmpeg_path(self) -> Optional[str]:
        """获取FFmpeg路径"""
        if os.path.exists(self.ffmpeg_exe):
            return os.path.join(self.ffmpeg_dir, 'bin')
        
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            return os.path.dirname(system_ffmpeg)
        
        return None
    
    def setup_environment(self):
        """设置FFmpeg环境变量"""
        ffmpeg_path = self.get_ffmpeg_path()
        if ffmpeg_path:
            # 添加到PATH
            current_path = os.environ.get('PATH', '')
            if ffmpeg_path not in current_path:
                os.environ['PATH'] = ffmpeg_path + os.pathsep + current_path
            return True
        return False
    
    def download_ffmpeg(self, progress_callback=None) -> bool:
        """
        下载FFmpeg便携版
        
        Args:
            progress_callback: 进度回调函数，参数为(downloaded, total)
            
        Returns:
            是否下载成功
        """
        try:
            zip_path = os.path.join(self.base_path, 'ffmpeg_temp.zip')
            
            # 下载
            def report_progress(block_num, block_size, total_size):
                if progress_callback:
                    downloaded = block_num * block_size
                    progress_callback(downloaded, total_size)
            
            print("正在下载 FFmpeg...")
            urllib.request.urlretrieve(
                self.FFMPEG_URL,
                zip_path,
                reporthook=report_progress
            )
            
            # 解压
            print("正在解压 FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 获取压缩包内的根目录名
                root_dir = zip_ref.namelist()[0].split('/')[0]
                zip_ref.extractall(self.base_path)
            
            # 重命名目录
            extracted_dir = os.path.join(self.base_path, root_dir)
            if os.path.exists(self.ffmpeg_dir):
                shutil.rmtree(self.ffmpeg_dir)
            os.rename(extracted_dir, self.ffmpeg_dir)
            
            # 清理临时文件
            os.remove(zip_path)
            
            print("FFmpeg 安装完成！")
            return True
            
        except Exception as e:
            print(f"下载FFmpeg失败: {e}")
            return False


# 全局实例
ffmpeg_manager = FFmpegManager()


def ensure_ffmpeg():
    """确保FFmpeg可用，如果不可用则提示用户"""
    if ffmpeg_manager.setup_environment():
        return True
    return False
