# 🎬 视频下载器 - Video Downloader

一款功能强大的本地视频下载工具，支持 YouTube、Bilibili 等 1000+ 网站。

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特性

- 🌐 **多平台支持**: YouTube、Bilibili、Twitter/X、TikTok、Instagram 等 1000+ 网站
- 🎨 **现代化界面**: 深色主题，美观易用
- 📊 **实时进度**: 下载进度、速度实时显示
- 🎚️ **质量选择**: 支持多种画质选项（最佳、1080p、720p、480p、360p、仅音频）
- 📁 **自定义路径**: 可自定义下载保存位置
- 🔄 **多任务下载**: 支持同时下载多个视频

## 📦 安装方法

### 方法一：直接运行（推荐）

1. 确保已安装 Python 3.11+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python main.py
   ```

### 方法二：打包为 EXE

1. 双击运行 `build.bat`
2. 等待打包完成
3. 在 `dist` 目录找到 `视频下载器.exe`

## 🚀 使用方法

1. **复制视频链接**: 从浏览器复制视频页面的URL
2. **粘贴并解析**: 将链接粘贴到输入框，点击"解析"
3. **选择画质**: 在下拉菜单中选择需要的画质
4. **开始下载**: 点击"下载"按钮开始下载

## 📁 项目结构

```
网页抓取工具/
├── main.py              # 程序入口
├── gui/
│   ├── __init__.py
│   ├── app.py           # 主窗口
│   └── components.py    # UI组件
├── core/
│   ├── __init__.py
│   ├── downloader.py    # 下载核心
│   └── parser.py        # URL解析器
├── utils/
│   ├── __init__.py
│   └── helpers.py       # 辅助函数
├── requirements.txt     # 依赖列表
├── build.bat            # 打包脚本
└── README.md            # 说明文档
```

## 🔧 技术栈

- **Python 3.11+**: 核心语言
- **yt-dlp**: 视频下载引擎
- **CustomTkinter**: 现代化GUI框架
- **PyInstaller**: EXE打包工具

## ⚠️ 注意事项

1. **网络要求**: 部分网站（如YouTube）可能需要特殊网络环境
2. **法律声明**: 请确保您有权下载相关内容，仅供个人学习使用
3. **FFmpeg**: 合并音视频需要FFmpeg，建议安装并添加到系统PATH

### 安装 FFmpeg (可选)

1. 下载 FFmpeg: https://ffmpeg.org/download.html
2. 解压并将 `bin` 目录添加到系统环境变量 PATH

## 🐛 常见问题

**Q: 下载YouTube视频失败？**
A: 请确保网络可以正常访问YouTube，或尝试更新yt-dlp: `pip install -U yt-dlp`

**Q: 打包后的exe无法运行？**
A: 确保杀毒软件没有误报，或尝试以管理员身份运行

**Q: Bilibili视频没有声音？**
A: 安装FFmpeg后可以正确合并音视频

## 📜 开源协议

MIT License

## 🙏 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 强大的视频下载库
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化Tkinter主题
