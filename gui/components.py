"""
UI组件 - 可复用的界面组件
"""
import customtkinter as ctk
from typing import Optional, Callable
from utils.helpers import format_size, format_duration


class DownloadCard(ctk.CTkFrame):
    """下载项卡片组件"""
    
    def __init__(
        self,
        master,
        title: str,
        platform: str,
        thumbnail_url: Optional[str] = None,
        on_cancel: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.title = title
        self.platform = platform
        self.on_cancel = on_cancel
        
        self.configure(fg_color="#2b2b2b", corner_radius=10)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建卡片内的组件"""
        # 标题行
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # 平台标签
        self.platform_label = ctk.CTkLabel(
            self.title_frame,
            text=self.platform,
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w"
        )
        self.platform_label.pack(side="left")
        
        # 状态标签
        self.status_label = ctk.CTkLabel(
            self.title_frame,
            text="准备中...",
            font=ctk.CTkFont(size=11),
            text_color="#4CAF50",
            anchor="e"
        )
        self.status_label.pack(side="right")
        
        # 视频标题
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title[:50] + "..." if len(self.title) > 50 else self.title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(fill="x", padx=15, pady=5)
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(self, height=8)
        self.progress_bar.pack(fill="x", padx=15, pady=5)
        self.progress_bar.set(0)
        
        # 进度信息行
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        # 进度百分比
        self.percent_label = ctk.CTkLabel(
            self.info_frame,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.percent_label.pack(side="left")
        
        # 下载速度
        self.speed_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.speed_label.pack(side="right")
        
        # 取消按钮
        if self.on_cancel:
            self.cancel_btn = ctk.CTkButton(
                self.info_frame,
                text="取消",
                width=60,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color="#ff4444",
                hover_color="#cc3333",
                command=self.on_cancel
            )
            self.cancel_btn.pack(side="right", padx=(0, 10))
    
    def update_progress(self, percent: float, speed: float = 0, status: str = "下载中..."):
        """更新进度"""
        self.progress_bar.set(percent / 100)
        self.percent_label.configure(text=f"{percent:.1f}%")
        self.status_label.configure(text=status)
        
        if speed > 0:
            speed_text = format_size(speed) + "/s"
            self.speed_label.configure(text=speed_text)
    
    def set_complete(self):
        """设置为完成状态"""
        self.progress_bar.set(1)
        self.percent_label.configure(text="100%")
        self.status_label.configure(text="✓ 完成", text_color="#4CAF50")
        self.speed_label.configure(text="")
        
        # 隐藏取消按钮
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.pack_forget()
    
    def set_error(self, message: str = "下载失败"):
        """设置为错误状态"""
        self.status_label.configure(text="✗ " + message[:20], text_color="#ff4444")
        self.speed_label.configure(text="")


class SettingsPanel(ctk.CTkFrame):
    """设置面板组件"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="#2b2b2b", corner_radius=10)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建设置组件"""
        # 标题
        self.title_label = ctk.CTkLabel(
            self,
            text="⚙️ 设置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(15, 10))
        
        # 下载路径设置
        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.pack(fill="x", padx=15, pady=10)
        
        self.path_label = ctk.CTkLabel(
            self.path_frame,
            text="下载路径:",
            font=ctk.CTkFont(size=12)
        )
        self.path_label.pack(side="left")
        
        self.path_entry = ctk.CTkEntry(
            self.path_frame,
            placeholder_text="选择下载目录...",
            width=250
        )
        self.path_entry.pack(side="left", padx=10)
        
        self.browse_btn = ctk.CTkButton(
            self.path_frame,
            text="浏览",
            width=60,
            height=28
        )
        self.browse_btn.pack(side="left")


class VideoInfoCard(ctk.CTkFrame):
    """视频信息卡片"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="#2b2b2b", corner_radius=10)
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        # 标题
        self.title_label = ctk.CTkLabel(
            self,
            text="视频信息",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(fill="x", padx=15, pady=(15, 10))
        
        # 信息容器
        self.info_container = ctk.CTkFrame(self, fg_color="transparent")
        self.info_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # 占位文本
        self.placeholder = ctk.CTkLabel(
            self.info_container,
            text="请输入视频URL并点击解析",
            text_color="#666666"
        )
        self.placeholder.pack(pady=20)
    
    def update_info(
        self,
        title: str,
        uploader: str,
        duration: int,
        platform: str,
        view_count: int = None
    ):
        """更新视频信息"""
        # 清除占位符
        for widget in self.info_container.winfo_children():
            widget.destroy()
        
        # 视频标题
        title_text = ctk.CTkLabel(
            self.info_container,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            wraplength=350,
            anchor="w",
            justify="left"
        )
        title_text.pack(fill="x", pady=(0, 10))
        
        # 信息行
        info_items = [
            ("📺", platform),
            ("👤", uploader),
            ("⏱️", format_duration(duration)),
        ]
        
        if view_count:
            info_items.append(("👁️", f"{view_count:,} 次观看"))
        
        for icon, text in info_items:
            row = ctk.CTkFrame(self.info_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row,
                text=f"{icon} {text}",
                font=ctk.CTkFont(size=12),
                text_color="#aaaaaa",
                anchor="w"
            ).pack(side="left")
    
    def clear(self):
        """清除信息"""
        for widget in self.info_container.winfo_children():
            widget.destroy()
        
        self.placeholder = ctk.CTkLabel(
            self.info_container,
            text="请输入视频URL并点击解析",
            text_color="#666666"
        )
        self.placeholder.pack(pady=20)
