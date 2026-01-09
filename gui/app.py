"""
主应用程序 - 视频下载器GUI
"""
import customtkinter as ctk
import threading
import os
import io
import urllib.request
from tkinter import filedialog, messagebox
from typing import Optional, Dict, List
from PIL import Image

from core.parser import VideoParser
from core.downloader import VideoDownloader
from gui.components import DownloadCard, VideoInfoCard
from utils.helpers import (
    get_default_download_path,
    is_valid_url,
    detect_platform,
    format_size
)
from utils.ffmpeg_manager import ffmpeg_manager
from utils.history_manager import history_manager


# 设置主题
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VideoDownloaderApp(ctk.CTk):
    """视频下载器主应用"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口设置
        self.title("🎬 视频下载器 - Video Downloader")
        self.geometry("1000x750")
        self.minsize(900, 650)
        
        # 检查并设置FFmpeg
        self._check_ffmpeg()
        
        # 核心组件
        self.parser = VideoParser()
        self.downloader = VideoDownloader()
        
        # 状态变量
        self.current_video_info: Optional[Dict] = None
        self.download_cards: List[DownloadCard] = []
        self.download_path = get_default_download_path()
        self.batch_urls: List[str] = []  # 批量下载URL列表
        
        # 新功能选项
        self.download_subtitles = ctk.BooleanVar(value=False)
        self.embed_subtitles = ctk.BooleanVar(value=False)
        self.output_format = ctk.StringVar(value="mp4")
        
        # 创建UI
        self._create_ui()
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _check_ffmpeg(self):
        """检查FFmpeg是否可用"""
        if not ffmpeg_manager.setup_environment():
            # FFmpeg不可用，稍后提示用户
            self.after(1000, self._prompt_ffmpeg_download)
    
    def _create_ui(self):
        """创建用户界面"""
        # 主容器
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题区域
        self._create_header()
        
        # 输入区域
        self._create_input_section()
        
        # 内容区域（左右分栏）
        self._create_content_section()
    
    def _create_header(self):
        """创建标题区域"""
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # 主标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎬 视频下载器",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(side="left")
        
        # 副标题
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="支持 YouTube、Bilibili 等 1000+ 网站",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        )
        subtitle_label.pack(side="left", padx=(15, 0), pady=(8, 0))
        
        # 设置按钮
        settings_btn = ctk.CTkButton(
            header_frame,
            text="⚙️ 设置",
            width=80,
            height=32,
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            command=self._open_settings
        )
        settings_btn.pack(side="right")
        
        # 历史记录按钮
        history_btn = ctk.CTkButton(
            header_frame,
            text="📋 历史",
            width=80,
            height=32,
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            command=self._open_history
        )
        history_btn.pack(side="right", padx=(0, 10))
        
        # 批量下载按钮
        batch_btn = ctk.CTkButton(
            header_frame,
            text="📦 批量",
            width=80,
            height=32,
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            command=self._open_batch_download
        )
        batch_btn.pack(side="right", padx=(0, 10))
    
    def _create_input_section(self):
        """创建输入区域"""
        input_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#2b2b2b",
            corner_radius=15
        )
        input_frame.pack(fill="x", pady=(0, 20))
        
        # 内部容器
        inner_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=20, pady=20)
        
        # URL输入框
        self.url_entry = ctk.CTkEntry(
            inner_frame,
            placeholder_text="🔗 粘贴视频链接... (YouTube, Bilibili, etc.)",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # 绑定回车键
        self.url_entry.bind("<Return>", lambda e: self._parse_url())
        
        # 解析按钮
        self.parse_btn = ctk.CTkButton(
            inner_frame,
            text="🔍 解析",
            width=100,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            command=self._parse_url
        )
        self.parse_btn.pack(side="left")
    
    def _create_content_section(self):
        """创建内容区域"""
        content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # 左侧：视频信息和下载选项
        left_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # 视频预览卡片（包含缩略图）
        self.preview_frame = ctk.CTkFrame(left_panel, fg_color="#2b2b2b", corner_radius=10)
        self.preview_frame.pack(fill="x", pady=(0, 15))
        
        preview_inner = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        preview_inner.pack(fill="x", padx=15, pady=15)
        
        # 缩略图占位
        self.thumbnail_label = ctk.CTkLabel(
            preview_inner,
            text="🎬\n视频预览",
            width=180,
            height=100,
            fg_color="#1a1a1a",
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.thumbnail_label.pack(side="left", padx=(0, 15))
        
        # 视频信息容器
        info_container = ctk.CTkFrame(preview_inner, fg_color="transparent")
        info_container.pack(side="left", fill="both", expand=True)
        
        # 视频标题
        self.title_label = ctk.CTkLabel(
            info_container,
            text="等待解析视频...",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            justify="left",
            wraplength=350
        )
        self.title_label.pack(fill="x", pady=(0, 8))
        
        # 平台和上传者
        self.uploader_label = ctk.CTkLabel(
            info_container,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            anchor="w"
        )
        self.uploader_label.pack(fill="x", pady=(0, 4))
        
        # 时长和观看数
        self.stats_label = ctk.CTkLabel(
            info_container,
            text="粘贴视频链接并点击解析",
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            anchor="w"
        )
        self.stats_label.pack(fill="x")
        
        # 下载选项区域
        options_frame = ctk.CTkFrame(left_panel, fg_color="#2b2b2b", corner_radius=10)
        options_frame.pack(fill="x", pady=(0, 15))
        
        # 第一行：质量和格式
        row1 = ctk.CTkFrame(options_frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(15, 10))
        
        # 质量选择
        quality_label = ctk.CTkLabel(row1, text="画质:", font=ctk.CTkFont(size=13))
        quality_label.pack(side="left")
        
        self.quality_var = ctk.StringVar(value="最佳质量")
        self.quality_menu = ctk.CTkOptionMenu(
            row1,
            variable=self.quality_var,
            values=["最佳质量", "1080p", "720p", "480p", "360p", "仅音频"],
            width=120,
            height=32,
            corner_radius=8
        )
        self.quality_menu.pack(side="left", padx=(10, 20))
        
        # 格式选择
        format_label = ctk.CTkLabel(row1, text="格式:", font=ctk.CTkFont(size=13))
        format_label.pack(side="left")
        
        format_menu = ctk.CTkOptionMenu(
            row1,
            variable=self.output_format,
            values=["mp4", "mkv", "webm", "avi", "mov"],
            width=100,
            height=32,
            corner_radius=8
        )
        format_menu.pack(side="left", padx=(10, 0))
        
        # 第二行：字幕选项
        row2 = ctk.CTkFrame(options_frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(0, 10))
        
        subtitle_check = ctk.CTkCheckBox(
            row2,
            text="下载字幕",
            variable=self.download_subtitles,
            font=ctk.CTkFont(size=12)
        )
        subtitle_check.pack(side="left")
        
        embed_check = ctk.CTkCheckBox(
            row2,
            text="嵌入字幕",
            variable=self.embed_subtitles,
            font=ctk.CTkFont(size=12)
        )
        embed_check.pack(side="left", padx=(20, 0))
        
        # 第三行：按钮
        row3 = ctk.CTkFrame(options_frame, fg_color="transparent")
        row3.pack(fill="x", padx=15, pady=(0, 15))
        
        # 下载按钮
        self.download_btn = ctk.CTkButton(
            row3,
            text="⬇️ 下载",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            corner_radius=10,
            command=self._start_download,
            state="disabled"
        )
        self.download_btn.pack(side="right")
        
        # 打开下载目录按钮
        open_folder_btn = ctk.CTkButton(
            row3,
            text="📁 打开目录",
            width=100,
            height=35,
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            corner_radius=8,
            command=self._open_download_folder
        )
        open_folder_btn.pack(side="right", padx=(0, 10))
        
        # 右侧：下载列表
        right_panel = ctk.CTkFrame(
            content_frame,
            fg_color="#2b2b2b",
            corner_radius=10,
            width=350
        )
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # 下载列表标题
        list_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        list_header.pack(fill="x", padx=15, pady=(15, 10))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="📥 下载列表",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_title.pack(side="left")
        
        # 清空按钮
        clear_btn = ctk.CTkButton(
            list_header,
            text="清空",
            width=50,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            corner_radius=5,
            command=self._clear_download_list
        )
        clear_btn.pack(side="right")
        
        # 下载列表滚动区域
        self.download_list_frame = ctk.CTkScrollableFrame(
            right_panel,
            fg_color="transparent"
        )
        self.download_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 空列表提示
        self.empty_label = ctk.CTkLabel(
            self.download_list_frame,
            text="暂无下载任务\n\n输入视频链接开始下载",
            text_color="#666666",
            font=ctk.CTkFont(size=12)
        )
        self.empty_label.pack(pady=50)
    
    def _parse_url(self):
        """解析视频URL"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("提示", "请输入视频链接")
            return
        
        if not is_valid_url(url):
            messagebox.showwarning("提示", "请输入有效的URL")
            return
        
        # 更新UI状态
        self.parse_btn.configure(state="disabled", text="解析中...")
        self.download_btn.configure(state="disabled")
        
        # 在新线程中解析
        def parse_thread():
            try:
                info = self.parser.get_video_info(url)
                
                # 在主线程中更新UI
                self.after(0, lambda: self._on_parse_complete(info))
            except Exception as e:
                self.after(0, lambda: self._on_parse_error(str(e)))
        
        threading.Thread(target=parse_thread, daemon=True).start()
    
    def _on_parse_complete(self, info: Optional[Dict]):
        """解析完成回调"""
        self.parse_btn.configure(state="normal", text="🔍 解析")
        
        if info:
            self.current_video_info = info
            
            # 更新标题
            title = info.get('title', '未知标题')
            self.title_label.configure(text=title[:80] + "..." if len(title) > 80 else title)
            
            # 更新平台和上传者
            uploader_parts = []
            if info.get('platform'):
                uploader_parts.append(f"📺 {info['platform']}")
            if info.get('uploader'):
                uploader_parts.append(f"👤 {info['uploader']}")
            self.uploader_label.configure(text="  •  ".join(uploader_parts))
            
            # 更新时长和观看数
            stats_parts = []
            if info.get('duration'):
                total_seconds = int(info['duration'])
                hours, remainder = divmod(total_seconds, 3600)
                mins, secs = divmod(remainder, 60)
                if hours > 0:
                    stats_parts.append(f"⏱️ {hours}:{mins:02d}:{secs:02d}")
                else:
                    stats_parts.append(f"⏱️ {mins}:{secs:02d}")
            if info.get('view_count'):
                views = info['view_count']
                if views >= 10000:
                    stats_parts.append(f"👁️ {views/10000:.1f}万次观看")
                else:
                    stats_parts.append(f"👁️ {views:,}次观看")
            if info.get('like_count'):
                stats_parts.append(f"👍 {info['like_count']:,}")
            self.stats_label.configure(text="  •  ".join(stats_parts) if stats_parts else "")
            
            # 加载缩略图
            if info.get('thumbnail'):
                self._load_thumbnail(info['thumbnail'])
            
            # 更新质量选项
            formats = info.get('formats', [])
            if formats:
                qualities = [f['resolution'] for f in formats]
                self.quality_menu.configure(values=qualities)
                self.quality_var.set(qualities[0])
            else:
                # 没有格式信息时使用默认选项
                self.quality_menu.configure(values=["最佳质量", "1080p", "720p", "480p", "仅音频"])
                self.quality_var.set("最佳质量")
            
            # 启用下载按钮（无论如何都要启用）
            self.download_btn.configure(state="normal")
            print(f"下载按钮已启用，当前状态: {self.download_btn.cget('state')}")
        else:
            messagebox.showerror("错误", "无法解析该视频链接")
    
    def _on_parse_error(self, error: str):
        """解析错误回调"""
        self.parse_btn.configure(state="normal", text="🔍 解析")
        messagebox.showerror("解析错误", f"解析失败: {error}")
    
    def _start_download(self):
        """开始下载"""
        if not self.current_video_info:
            return
        
        url = self.url_entry.get().strip()
        quality = self.quality_var.get()
        title = self.current_video_info.get('title', '视频')
        platform = self.current_video_info.get('platform', '未知')
        thumbnail = self.current_video_info.get('thumbnail')
        duration = self.current_video_info.get('duration')
        
        # 隐藏空列表提示
        self.empty_label.pack_forget()
        
        # 创建下载卡片
        card = DownloadCard(
            self.download_list_frame,
            title=title,
            platform=platform,
            on_cancel=lambda: self._cancel_download(card)
        )
        card.pack(fill="x", pady=(0, 10))
        self.download_cards.append(card)
        
        # 获取格式ID
        format_id = 'best'
        if quality == "仅音频":
            format_id = 'bestaudio'
        elif quality == "最佳质量":
            format_id = 'best'
        elif 'p' in quality:
            format_id = quality
        
        # 创建新的下载器实例并配置选项
        downloader = VideoDownloader(self.download_path)
        downloader.download_subtitles = self.download_subtitles.get()
        downloader.embed_subtitles = self.embed_subtitles.get()
        downloader.output_format = self.output_format.get()
        
        # 设置回调
        def progress_callback(info):
            if info['status'] == 'downloading':
                self.after(0, lambda: card.update_progress(
                    percent=info.get('percent', 0),
                    speed=info.get('speed', 0),
                    status="下载中..."
                ))
            elif info['status'] == 'finished':
                self.after(0, lambda: card.set_complete())
        
        def complete_callback(filepath):
            self.after(0, lambda: card.set_complete())
            # 保存到历史记录
            history_manager.add_record(
                url=url,
                title=title,
                platform=platform,
                filepath=filepath,
                thumbnail=thumbnail,
                duration=duration,
                quality=quality,
                status='completed'
            )
        
        def error_callback(error):
            self.after(0, lambda: card.set_error(error[:30]))
        
        downloader.set_callbacks(
            progress=progress_callback,
            complete=complete_callback,
            error=error_callback
        )
        
        # 保存下载器引用
        card.downloader = downloader
        
        # 开始异步下载
        downloader.download_async(url, format_id)
    
    def _cancel_download(self, card: DownloadCard):
        """取消下载"""
        if hasattr(card, 'downloader'):
            card.downloader.cancel()
        card.set_error("已取消")
    
    def _clear_download_list(self):
        """清空下载列表"""
        for card in self.download_cards:
            if hasattr(card, 'downloader'):
                card.downloader.cancel()
            card.destroy()
        
        self.download_cards.clear()
        
        # 显示空列表提示
        self.empty_label.pack(pady=50)
    
    def _open_download_folder(self):
        """打开下载目录"""
        if os.path.exists(self.download_path):
            os.startfile(self.download_path)
        else:
            messagebox.showinfo("提示", f"下载目录不存在: {self.download_path}")
    
    def _open_settings(self):
        """打开设置窗口"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("设置")
        settings_window.geometry("500x300")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # 设置内容
        content = ctk.CTkFrame(settings_window, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # 下载路径设置
        path_label = ctk.CTkLabel(
            content,
            text="下载保存位置:",
            font=ctk.CTkFont(size=14)
        )
        path_label.pack(anchor="w", pady=(0, 10))
        
        path_frame = ctk.CTkFrame(content, fg_color="transparent")
        path_frame.pack(fill="x", pady=(0, 20))
        
        path_entry = ctk.CTkEntry(
            path_frame,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        path_entry.insert(0, self.download_path)
        
        def browse():
            folder = filedialog.askdirectory(initialdir=self.download_path)
            if folder:
                path_entry.delete(0, "end")
                path_entry.insert(0, folder)
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="浏览",
            width=80,
            height=40,
            command=browse
        )
        browse_btn.pack(side="right")
        
        # 保存按钮
        def save_settings():
            new_path = path_entry.get().strip()
            if new_path and os.path.isdir(new_path):
                self.download_path = new_path
                self.downloader.set_output_path(new_path)
                settings_window.destroy()
                messagebox.showinfo("成功", "设置已保存")
            else:
                messagebox.showwarning("警告", "请选择有效的目录")
        
        save_btn = ctk.CTkButton(
            content,
            text="保存设置",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=save_settings
        )
        save_btn.pack(pady=20)
    
    def _on_closing(self):
        """窗口关闭事件"""
        # 取消所有下载
        for card in self.download_cards:
            if hasattr(card, 'downloader'):
                card.downloader.cancel()
        
        self.destroy()
    
    def _load_thumbnail(self, url: str):
        """加载视频缩略图"""
        def load_thread():
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = response.read()
                    image = Image.open(io.BytesIO(data))
                    image = image.resize((200, 112), Image.Resampling.LANCZOS)
                    photo = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 112))
                    self.after(0, lambda: self.thumbnail_label.configure(image=photo, text=""))
                    self.thumbnail_label.image = photo  # 保持引用
            except Exception as e:
                print(f"加载缩略图失败: {e}")
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _open_batch_download(self):
        """打开批量下载窗口"""
        batch_window = ctk.CTkToplevel(self)
        batch_window.title("📦 批量下载")
        batch_window.geometry("600x500")
        batch_window.transient(self)
        
        content = ctk.CTkFrame(batch_window, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 说明
        ctk.CTkLabel(
            content,
            text="每行输入一个视频链接：",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(0, 10))
        
        # 多行文本框
        text_box = ctk.CTkTextbox(content, height=300, font=ctk.CTkFont(size=12))
        text_box.pack(fill="both", expand=True, pady=(0, 15))
        
        # 按钮行
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        def start_batch():
            urls = text_box.get("1.0", "end").strip().split("\n")
            urls = [u.strip() for u in urls if u.strip() and is_valid_url(u.strip())]
            
            if not urls:
                messagebox.showwarning("提示", "请输入有效的视频链接")
                return
            
            batch_window.destroy()
            
            # 批量添加到下载队列
            for url in urls:
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, url)
                self._parse_and_download_direct(url)
        
        ctk.CTkButton(
            btn_frame,
            text=f"开始下载",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45a049",
            command=start_batch
        ).pack(side="right")
        
        ctk.CTkLabel(
            btn_frame,
            text="💡 支持 YouTube、Bilibili 等链接混合输入",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(side="left")
    
    def _parse_and_download_direct(self, url: str):
        """直接解析并下载（用于批量下载）"""
        def batch_thread():
            try:
                info = self.parser.get_video_info(url)
                if info:
                    self.after(0, lambda: self._batch_download_item(url, info))
            except Exception as e:
                print(f"批量下载解析失败: {e}")
        
        threading.Thread(target=batch_thread, daemon=True).start()
    
    def _batch_download_item(self, url: str, info: Dict):
        """批量下载单个项目"""
        title = info.get('title', '视频')
        platform = info.get('platform', '未知')
        
        self.empty_label.pack_forget()
        
        card = DownloadCard(
            self.download_list_frame,
            title=title,
            platform=platform,
            on_cancel=lambda: self._cancel_download(card)
        )
        card.pack(fill="x", pady=(0, 10))
        self.download_cards.append(card)
        
        downloader = VideoDownloader(self.download_path)
        downloader.download_subtitles = self.download_subtitles.get()
        downloader.embed_subtitles = self.embed_subtitles.get()
        downloader.output_format = self.output_format.get()
        
        def progress_callback(prog_info):
            if prog_info['status'] == 'downloading':
                self.after(0, lambda: card.update_progress(
                    percent=prog_info.get('percent', 0),
                    speed=prog_info.get('speed', 0),
                    status="下载中..."
                ))
            elif prog_info['status'] == 'finished':
                self.after(0, lambda: card.set_complete())
        
        def complete_callback(filepath):
            self.after(0, lambda: card.set_complete())
            history_manager.add_record(
                url=url, title=title, platform=platform,
                filepath=filepath, thumbnail=info.get('thumbnail'),
                duration=info.get('duration'), quality="最佳质量"
            )
        
        def error_callback(error):
            self.after(0, lambda: card.set_error(error[:30]))
        
        downloader.set_callbacks(progress=progress_callback, complete=complete_callback, error=error_callback)
        card.downloader = downloader
        downloader.download_async(url, 'best')
    
    def _open_history(self):
        """打开历史记录窗口"""
        history_window = ctk.CTkToplevel(self)
        history_window.title("📋 下载历史")
        history_window.geometry("700x500")
        history_window.transient(self)
        
        content = ctk.CTkFrame(history_window, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题栏
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header,
            text="下载历史",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        def clear_history():
            if messagebox.askyesno("确认", "确定要清空所有历史记录吗？"):
                history_manager.clear_history()
                history_window.destroy()
                self._open_history()
        
        ctk.CTkButton(
            header,
            text="清空历史",
            width=80,
            height=30,
            fg_color="#ff4444",
            hover_color="#cc3333",
            command=clear_history
        ).pack(side="right")
        
        # 历史列表
        list_frame = ctk.CTkScrollableFrame(content, fg_color="transparent")
        list_frame.pack(fill="both", expand=True)
        
        history = history_manager.get_history(limit=50)
        
        if not history:
            ctk.CTkLabel(
                list_frame,
                text="暂无下载历史",
                font=ctk.CTkFont(size=14),
                text_color="#666666"
            ).pack(pady=50)
        else:
            for record in history:
                item = ctk.CTkFrame(list_frame, fg_color="#2b2b2b", corner_radius=8)
                item.pack(fill="x", pady=(0, 8))
                
                inner = ctk.CTkFrame(item, fg_color="transparent")
                inner.pack(fill="x", padx=12, pady=10)
                
                # 标题
                title_text = record.get('title', '未知')[:40]
                ctk.CTkLabel(
                    inner,
                    text=title_text,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    anchor="w"
                ).pack(fill="x")
                
                # 信息行
                info_text = f"📺 {record.get('platform', '未知')}  |  🕐 {record.get('download_time', '')[:10]}"
                ctk.CTkLabel(
                    inner,
                    text=info_text,
                    font=ctk.CTkFont(size=11),
                    text_color="#888888",
                    anchor="w"
                ).pack(fill="x")
    
    def _prompt_ffmpeg_download(self):
        """提示用户下载FFmpeg"""
        result = messagebox.askyesno(
            "需要 FFmpeg",
            "检测到系统未安装 FFmpeg。\n\n"
            "FFmpeg 是下载和合并视频所必需的组件。\n"
            "没有它，Bilibili 等网站的视频可能无法正常下载。\n\n"
            "是否现在自动下载 FFmpeg？\n"
            "(约 100MB，下载后自动配置)"
        )
        
        if result:
            self._download_ffmpeg()
    
    def _download_ffmpeg(self):
        """下载FFmpeg"""
        # 创建下载进度窗口
        progress_window = ctk.CTkToplevel(self)
        progress_window.title("下载 FFmpeg")
        progress_window.geometry("400x150")
        progress_window.transient(self)
        progress_window.grab_set()
        
        # 进度内容
        content = ctk.CTkFrame(progress_window, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        status_label = ctk.CTkLabel(
            content,
            text="正在下载 FFmpeg，请稍候...",
            font=ctk.CTkFont(size=14)
        )
        status_label.pack(pady=(0, 15))
        
        progress_bar = ctk.CTkProgressBar(content, width=300)
        progress_bar.pack()
        progress_bar.set(0)
        
        percent_label = ctk.CTkLabel(
            content,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        percent_label.pack(pady=(10, 0))
        
        def download_thread():
            def progress_callback(downloaded, total):
                if total > 0:
                    percent = downloaded / total
                    self.after(0, lambda: progress_bar.set(percent))
                    self.after(0, lambda: percent_label.configure(
                        text=f"{percent*100:.1f}% ({downloaded//1024//1024}MB / {total//1024//1024}MB)"
                    ))
            
            success = ffmpeg_manager.download_ffmpeg(progress_callback)
            
            def on_complete():
                progress_window.destroy()
                if success:
                    ffmpeg_manager.setup_environment()
                    messagebox.showinfo("成功", "FFmpeg 安装完成！\n现在可以正常下载视频了。")
                else:
                    messagebox.showerror(
                        "下载失败",
                        "FFmpeg 下载失败。\n\n"
                        "请手动下载 FFmpeg 并添加到系统 PATH：\n"
                        "https://ffmpeg.org/download.html"
                    )
            
            self.after(0, on_complete)
        
        threading.Thread(target=download_thread, daemon=True).start()


def main():
    """主函数"""
    app = VideoDownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
