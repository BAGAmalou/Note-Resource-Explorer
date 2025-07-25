import os
import json
import logging

# 配置日志
logging.basicConfig(
    filename='file_viewer.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FileViewer')

class Config:
    @staticmethod
    def load_last_folder():
        try:
            with open("file_viewer_gui.json", "r", encoding="utf-8") as file:
                config = json.load(file)
                return config.get("last_folder")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"加载上次文件夹失败: {str(e)}")
            return None

    @staticmethod
    def save_last_folder(folder_path):
        if folder_path:
            config = {
                "last_folder": folder_path
            }
            try:
                with open("file_viewer_gui.json", "w", encoding="utf-8") as file:
                    json.dump(config, file, ensure_ascii=False, indent=4)
                logger.info(f"已保存路径: {folder_path}")
            except Exception as e:
                logger.error(f"保存路径失败: {str(e)}")