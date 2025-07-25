import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

class HistoryItemWidget(QWidget):
    def __init__(self, file_info, parent=None):
        super().__init__(parent)
        self.file_info = file_info
        
        layout = QVBoxLayout()  # 改为垂直布局
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 文件名标签 - 允许换行
        self.file_label = QLabel(f"{file_info['name']} → {file_info['folder']}")
        self.file_label.setStyleSheet("color: #e0e0e0;")
        self.file_label.setWordWrap(True)  # 启用自动换行
        layout.addWidget(self.file_label, 1)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(3)
        
        # 复制Markdown按钮
        self.copy_md_button = QPushButton("MD")
        self.copy_md_button.setFixedSize(30, 25)
        self.copy_md_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.copy_md_button.setToolTip("复制Markdown格式")
        self.copy_md_button.clicked.connect(self.copy_markdown)
        button_layout.addWidget(self.copy_md_button)
        
        # 复制HTML按钮
        self.copy_html_button = QPushButton("HTML")
        self.copy_html_button.setFixedSize(35, 25)
        self.copy_html_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #3e8e40;
            }
        """)
        self.copy_html_button.setToolTip("复制HTML标签")
        self.copy_html_button.clicked.connect(self.copy_html)
        button_layout.addWidget(self.copy_html_button)
        
        # 复制路径按钮
        self.copy_path_button = QPushButton("路径")
        self.copy_path_button.setFixedSize(35, 25)
        self.copy_path_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.copy_path_button.setToolTip("复制文件绝对路径")
        self.copy_path_button.clicked.connect(self.copy_path)
        button_layout.addWidget(self.copy_path_button)
        
        button_layout.addStretch()  # 添加伸缩使按钮右对齐
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def copy_markdown(self):
        """根据文件类型生成并复制Markdown格式"""
        name = self.file_info['name']
        path = self.file_info['path']
        
        if self.file_info['category'] == "images":
            content = f"![{name}]({path})"
        elif self.file_info['category'] == "videos":
            content = f"[{name}]({path})"
        elif self.file_info['category'] == "audios":
            content = f"[{name}]({path})"
        elif self.file_info['category'] == "htmls":
            content = f"[{name}]({path})"
        elif self.file_info['category'] == "documents":
            content = f"[{name}]({path})"
        else:
            content = f"[{name}]({path})"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        
    def copy_html(self):
        """根据文件类型生成并复制HTML标签"""
        name = self.file_info['name']
        path = self.file_info['path']
        
        if self.file_info['category'] == "images":
            content = f'<img src="{path}" alt="{name}" width="300">'
        elif self.file_info['category'] == "videos":
            content = f'<video src="{path}" controls width="500"></video>'
        elif self.file_info['category'] == "audios":
            content = f'<audio src="{path}" controls>Audio</audio>'
        elif self.file_info['category'] == "htmls":
            content = f'<a href="{path}" target="_blank">{name}</a>'
        elif self.file_info['category'] == "documents":
            content = f'<a href="{path}" target="_blank">{name}</a>'
        else:
            content = f'<a href="{path}" target="_blank">{name}</a>'
        
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        
    def copy_path(self):
        """复制文件绝对路径"""
        path = self.file_info['path']
        clipboard = QApplication.clipboard()
        clipboard.setText(path)