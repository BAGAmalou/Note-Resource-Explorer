import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QGroupBox, QComboBox, QListWidget, QListWidgetItem, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# 文件分类映射
EN_CATEGORY_MAP = {
    "图像": "images",
    "视频": "videos",
    "音频": "audios",
    "HTML": "htmls",
    "文档": "documents"
}

class ImageRenameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片重命名设置")
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_label = QLabel("图片重命名设置")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 启用图片自动重命名
        self.enable_auto_rename = QCheckBox("启用图片自动重命名")
        self.enable_auto_rename.setFont(QFont("Microsoft YaHei", 10))
        self.enable_auto_rename.setChecked(True)
        layout.addWidget(self.enable_auto_rename)
        
        # 重命名模式
        rename_group = QGroupBox("重命名模式")
        rename_layout = QVBoxLayout(rename_group)
        
        self.rename_pattern = QComboBox()
        self.rename_pattern.addItems(["秒级时间戳+序号", "毫秒级时间戳+序号"])
        self.rename_pattern.setFont(QFont("Microsoft YaHei", 9))
        rename_layout.addWidget(self.rename_pattern)
        
        # 添加说明
        pattern_label = QLabel("示例: \n- 秒级时间戳+序号: 20250702103015_01.jpg\n- 毫秒级时间戳+序号: 20250702103015678_01.jpg")
        pattern_label.setFont(QFont("Microsoft YaHei", 8))
        pattern_label.setStyleSheet("color: #9e9e9e;")
        rename_layout.addWidget(pattern_label)
        
        layout.addWidget(rename_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 确认按钮
        confirm_button = QPushButton("确认")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_settings(self):
        return {
            "enabled": self.enable_auto_rename.isChecked(),
            "pattern": self.rename_pattern.currentText()
        }

class CategoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文件分类设置")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title_label = QLabel("选择文件分类方式")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 分类说明
        info_label = QLabel("您可以选择将文件复制到目标目录时是否按类型分类：")
        info_label.setFont(QFont("Microsoft YaHei", 9))
        layout.addWidget(info_label)
        
        # 分类选项
        self.categorize_option = QPushButton("按类型分类")
        self.categorize_option.setCheckable(True)
        self.categorize_option.setChecked(True)
        self.categorize_option.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #2e7d32;
            }
            QPushButton:!checked {
                background-color: #424242;
            }
        """)
        self.categorize_option.toggled.connect(self.update_option_text)
        layout.addWidget(self.categorize_option)
        
        # 不分类选项
        self.no_categorize_option = QPushButton("不分类")
        self.no_categorize_option.setCheckable(True)
        self.no_categorize_option.setChecked(False)
        self.no_categorize_option.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #2e7d32;
            }
        """)
        self.no_categorize_option.toggled.connect(self.update_option_text)
        layout.addWidget(self.no_categorize_option)
        
        # 分类预览
        preview_label = QLabel("分类预览:")
        preview_label.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(preview_label)
        
        preview_text = QLabel()
        preview_text.setWordWrap(True)
        preview_text.setText(
            "图像 → images/\n"
            "视频 → videos/\n"
            "音频 → audios/\n"
            "HTML → htmls/\n"
            "文档 → documents/\n"
            "其他文件 → 目标目录根文件夹"
        )
        preview_text.setStyleSheet("background-color: #1e1e1e; padding: 10px; border-radius: 5px;")
        layout.addWidget(preview_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 确认按钮
        confirm_button = QPushButton("确认")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_option_text(self, checked):
        sender = self.sender()
        if sender == self.categorize_option and checked:
            self.no_categorize_option.setChecked(False)
        elif sender == self.no_categorize_option and checked:
            self.categorize_option.setChecked(False)
    
    def get_categorize_option(self):
        return self.categorize_option.isChecked()

class ErrorDialog(QDialog):
    def __init__(self, errors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文件处理错误")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title_label = QLabel(f"成功处理 {len(errors['success'])} 个文件，失败 {len(errors['errors'])} 个文件")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 成功文件标签页
        success_tab = QWidget()
        success_layout = QVBoxLayout(success_tab)
        
        success_list = QListWidget()
        for file_info in errors['success']:
            item = QListWidgetItem(f"{file_info['name']} → {file_info['folder']}")
            success_list.addItem(item)
        
        success_layout.addWidget(success_list)
        tab_widget.addTab(success_tab, "成功文件")
        
        # 错误文件标签页
        error_tab = QWidget()
        error_layout = QVBoxLayout(error_tab)
        
        error_list = QListWidget()
        for file_path, error in errors['errors']:
            file_name = os.path.basename(file_path)
            item = QListWidgetItem(f"{file_name}: {error}")
            error_list.addItem(item)
        
        error_layout.addWidget(error_list)
        tab_widget.addTab(error_tab, "错误文件")
        
        layout.addWidget(tab_widget, 1)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("确定")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)