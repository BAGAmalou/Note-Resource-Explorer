import os
import os
import webbrowser
import logging
from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

logger = logging.getLogger('FileViewer')

class FileOperations:
    @staticmethod
    def display_file(file_path, layout):
        # 创建卡片框架
        card_frame = QFrame()
        card_frame.setFrameShape(QFrame.Shape.StyledPanel)
        card_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #424242; border-radius: 5px;")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(10)

        # 文件名标签
        file_name = os.path.basename(file_path)
        name_label = QLabel(file_name)
        name_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #e0e0e0;")
        card_layout.addWidget(name_label)

        # 尝试显示缩略图（仅对图片文件）
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            try:
                # 创建缩略图标签
                thumbnail_label = QLabel()
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 缩放图片到合适大小
                    scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    thumbnail_label.setPixmap(scaled_pixmap)
                    thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    card_layout.addWidget(thumbnail_label)
            except Exception as e:
                logger.error(f"无法加载缩略图: {str(e)}")

        # 操作按钮框架
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: #1e1e1e;")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(5)

        # 预览按钮
        preview_button = QPushButton("预览")
        preview_button.setFont(QFont("Microsoft YaHei", 10))
        preview_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        preview_button.clicked.connect(lambda: FileOperations.preview_file(file_path))
        button_layout.addWidget(preview_button)

        # 复制路径按钮
        path_button = QPushButton("复制路径")
        path_button.setFont(QFont("Microsoft YaHei", 10))
        path_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #bd2130;
            }
        """)
        path_button.clicked.connect(lambda: FileOperations.copy_to_clipboard(file_path))
        button_layout.addWidget(path_button)

        # 复制HTML代码按钮
        html_button = QPushButton("复制HTML")
        html_button.setFont(QFont("Microsoft YaHei", 10))
        html_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        html_button.clicked.connect(lambda: FileOperations.copy_html_code(file_path))
        button_layout.addWidget(html_button)

        # 复制MD链接按钮
        md_button = QPushButton("复制MD链接")
        md_button.setFont(QFont("Microsoft YaHei", 10))
        md_button.setStyleSheet("""
            QPushButton {
                background-color: #9c27b0;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #7b1fa2;
            }
        """)
        md_button.clicked.connect(lambda: FileOperations.copy_md_link(file_path))
        button_layout.addWidget(md_button)

        # 删除按钮
        delete_button = QPushButton("删除")
        delete_button.setFont(QFont("Microsoft YaHei", 10))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #b71c1c;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_button.clicked.connect(lambda: FileOperations.delete_file(file_path, card_frame, layout))
        button_layout.addWidget(delete_button)

        card_layout.addWidget(button_frame)
        layout.addWidget(card_frame)
        card_frame.show()

    @staticmethod
    def delete_file(file_path, card_frame, layout):
        # 显示确认对话框
        reply = QMessageBox.question(None, "确认删除", f"确定要删除文件 '{os.path.basename(file_path)}' 吗？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 从布局中移除卡片
                layout.removeWidget(card_frame)
                card_frame.hide()
                
                # 删除文件
                os.remove(file_path)
                logger.info(f"已删除文件: {file_path}")
                QMessageBox.information(None, "成功", f"文件 '{os.path.basename(file_path)}' 已删除")
            except Exception as e:
                logger.error(f"无法删除文件: {str(e)}")
                QMessageBox.critical(None, "错误", f"无法删除文件: {str(e)}")

    @staticmethod
    def preview_file(file_path):
        try:
            # 调用系统默认程序打开文件
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            else:
                webbrowser.open(file_path)
            logger.info(f"已预览文件: {file_path}")
        except Exception as e:
            logger.error(f"无法预览文件: {str(e)}")
            QMessageBox.critical(None, "错误", f"无法预览文件: {str(e)}")

    @staticmethod
    def copy_to_clipboard(text):
        from PyQt6.QtGui import QGuiApplication
        try:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(None, "成功", "已复制到剪贴板！")
            logger.info("已复制内容到剪贴板")
        except Exception as e:
            logger.error(f"无法复制内容: {str(e)}")
            QMessageBox.critical(None, "错误", f"无法复制内容: {str(e)}")

    @staticmethod
    def copy_html_code(file_path):
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        # 根据文件类型生成对应的HTML代码
        if ext in ['.mp3', '.wav', '.aac', '.flac']:
            html_code = f'<audio src="{file_path}" controls>'
        elif ext in ['.txt', '.pdf', '.docx', '.doc', '.wps', '.xls', '.xlsx', '.csv', '.pptx', '.ppt', '.epub', '.mobi', '.azw3']:
            html_code = f'<a href="{file_path}">{file_name}</a>'
        elif ext in ['.html', '.htm']:
            html_code = f'<a href="{file_path}">{file_name}</a>'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            html_code = f'<img src="{file_path}" alt="{file_name}">'
        elif ext in ['.mp4', '.avi', '.mkv']:
            html_code = f'<video src="{file_path}" controls>'
        else:
            html_code = f'<a href="{file_path}">{file_name}</a>'

        FileOperations.copy_to_clipboard(html_code)

    @staticmethod
    def copy_md_link(file_path):
        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        # 根据文件类型生成对应的MD链接
        if ext in ['.mp3', '.wav', '.aac', '.flac']:
            md_link = f'[{file_name}]({file_path})'
        elif ext in ['.txt', '.pdf', '.docx', '.doc', '.wps', '.xls', '.xlsx', '.csv', '.pptx', '.ppt', '.epub', '.mobi', '.azw3']:
            md_link = f'[{file_name}]({file_path})'
        elif ext in ['.html', '.htm']:
            md_link = f'[{file_name}]({file_path})'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            md_link = f'![{file_name}]({file_path})'
        elif ext in ['.mp4', '.avi', '.mkv']:
            md_link = f'[{file_name}]({file_path})'
        else:
            md_link = f'[{file_name}]({file_path})'

        FileOperations.copy_to_clipboard(md_link)