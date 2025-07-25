import os
import shutil
import json
import logging
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

# 配置日志
logging.basicConfig(
    filename='file_manager.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FileManager')

# 文件分类映射
FILE_CATEGORIES = {
    "图像": ['.jpg', '.jpeg', '.png', '.gif'],
    "视频": ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv'],
    "音频": ['.mp3', '.wav', '.flac', '.aac'],
    "HTML": ['.html', '.htm'],
    "文档": ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
           '.txt', '.md', '.epub', '.mobi', '.azw3', '.chm']
}

EN_CATEGORY_MAP = {
    "图像": "images",
    "视频": "videos",
    "音频": "audios",
    "HTML": "htmls",
    "文档": "documents"
}

class FileTransferThread(QThread):
    progress_updated = pyqtSignal(int, str)
    transfer_complete = pyqtSignal(tuple)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, file_list, target_dir, categorize_files, auto_rename_images, rename_pattern):
        super().__init__()
        self.file_list = file_list
        self.target_dir = target_dir
        self.categorize_files = categorize_files
        self.auto_rename_images = auto_rename_images
        self.rename_pattern = rename_pattern
        self.total_files = len(file_list)

    def run(self):
        error_files = []
        processed_files = []
        
        # 确保目标目录存在
        if not os.path.exists(self.target_dir):
            try:
                os.makedirs(self.target_dir)
            except Exception as e:
                self.error_occurred.emit("目录创建失败", f"无法创建目标目录: {str(e)}")
                return
        
        # 创建分类目录
        if self.categorize_files:
            for category in EN_CATEGORY_MAP.values():
                category_dir = os.path.join(self.target_dir, category)
                if not os.path.exists(category_dir):
                    try:
                        os.makedirs(category_dir)
                    except Exception as e:
                        self.error_occurred.emit("目录创建失败", f"无法创建分类目录: {str(e)}")
                        return
        
        # 计数器用于自动重命名
        image_counter = 1
        
        # 移动文件（剪切）
        for idx, (src_path, custom_name) in enumerate(self.file_list):
            try:
                # 获取文件扩展名
                _, ext = os.path.splitext(src_path)
                ext = ext.lower()
                
                # 查找文件分类
                file_category = "其他"
                for cat, exts in FILE_CATEGORIES.items():
                    if ext in exts:
                        file_category = EN_CATEGORY_MAP[cat]
                        break
                
                # 视频文件特殊处理 - 直接使用原始文件名
                if file_category == "videos":
                    new_name = os.path.splitext(os.path.basename(src_path))[0]
                # 自动重命名处理 - 仅对图片文件
                elif self.auto_rename_images and file_category == "images":
                    # 应用新的重命名模式
                    if self.rename_pattern == "秒级时间戳+序号":
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        new_name = f"{timestamp}_{image_counter:02d}"
                    elif self.rename_pattern == "毫秒级时间戳+序号":
                        millisecond = datetime.now().strftime("%f")[:3]  # 获取毫秒部分的前3位
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S") + millisecond
                        new_name = f"{timestamp}_{image_counter:02d}"
                    else:
                        # 默认使用秒级时间戳
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        new_name = f"{timestamp}_{image_counter:02d}"
                    
                    image_counter += 1
                else:
                    # 对于非图片文件或未开启自动重命名，使用自定义名称或原始名称
                    new_name = custom_name if custom_name else os.path.splitext(os.path.basename(src_path))[0]
                
                # 确定目标路径
                if self.categorize_files and file_category != "其他":
                    dest_dir = os.path.join(self.target_dir, file_category)
                else:
                    dest_dir = self.target_dir
                
                # 构建目标路径
                dest_path = os.path.join(dest_dir, new_name + ext)
                
                # 更新进度
                self.progress_updated.emit(int((idx + 1) / self.total_files * 100), 
                                          f"正在移动: {new_name}{ext}")
                
                # 添加详细的日志记录
                logger.debug(f"Processing file: {src_path}")
                logger.debug(f"File category: {file_category}")
                logger.debug(f"New name: {new_name}{ext}")
                logger.debug(f"Destination path: {dest_path}")
                
                # 确保目标目录存在
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                
                # 移动文件（剪切）
                shutil.move(src_path, dest_path)
                
                # 记录处理信息
                processed_files.append({
                    "name": new_name + ext,
                    "category": file_category,
                    "folder": os.path.basename(dest_dir),
                    "path": dest_path,
                    "relative_path": os.path.join(os.path.basename(dest_dir), new_name + ext)
                })
                
                logger.debug(f"File moved successfully: {src_path}")
                
            except Exception as e:
                error_msg = f"Error moving file {src_path}: {str(e)}"
                logger.error(error_msg)
                error_files.append((src_path, str(e)))
        
        self.transfer_complete.emit((error_files, processed_files))