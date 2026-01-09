"""
视频下载器 - 主程序入口
支持 YouTube、Bilibili 等 1000+ 网站

使用方法:
1. 直接运行: python main.py
2. 或运行打包后的exe文件
"""

import sys
import os

# 添加项目根目录到路径
if getattr(sys, 'frozen', False):
    # 打包后的exe
    application_path = os.path.dirname(sys.executable)
else:
    # 开发环境
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)

# 导入并启动应用
from gui.app import VideoDownloaderApp


def main():
    """主函数"""
    try:
        app = VideoDownloaderApp()
        app.mainloop()
    except Exception as e:
        import traceback
        print(f"程序启动失败: {e}")
        traceback.print_exc()
        input("按回车键退出...")


if __name__ == "__main__":
    main()
