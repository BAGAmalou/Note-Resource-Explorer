import os
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QFrame, QComboBox, QLineEdit, 
    QTabWidget, QScrollArea, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette

from config import Config
from file_operations import FileOperations

# 文件分类映射
FILE_CATEGORIES = {
    "图像": ['.jpg', '.jpeg', '.png', '.gif'],
    "视频": ['.mp4', '.avi', '.mkv'],
    "音频": ['.mp3', '.wav', '.aac', '.flac'],
    "HTML": ['.html', '.htm'],
    "文档": ['.txt', '.pdf', '.docx', '.doc', '.wps', '.xls', '.xlsx', '.csv', '.pptx', '.ppt', '.epub', '.mobi', '.azw3']
}

EN_CATEGORY_MAP = {
    "图像": "images",
    "视频": "videos",
    "音频": "audios",
    "HTML": "htmls",
    "文档": "documents"
}

class FileViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件查看器")
        self.setMinimumSize(1000, 800)
        self.setGeometry(100, 100, 1100, 800)

        # 初始化筛选条件
        self.time_filter = "全部时间"
        self.name_filter = ""
        self.last_folder = None

        # 创建主部件和布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # 创建标题
        self.create_title()

        # 创建筛选框
        self.create_filter_frame()

        # 创建路径显示和控制按钮
        self.create_path_controls()

        # 创建标签页
        self.create_tabs()

        # 加载上次选择的文件夹
        self.load_last_folder()

        # 更新路径标签
        self.update_path_label()

        # 应用深色主题
        self.apply_dark_theme()

        # 设置窗口图标
        from PyQt6.QtWidgets import QStyle
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))

        # 初始化状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

    def create_title(self):
        # 标题
        title_label = QLabel("文件查看器")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #ffffff;")
        self.main_layout.addWidget(title_label)

    def create_filter_frame(self):
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.Shape.StyledPanel)
        filter_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #424242; border-radius: 8px;")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)

        # 时间筛选
        time_label = QLabel("时间筛选:")
        time_label.setFont(QFont("Microsoft YaHei", 10))
        time_label.setStyleSheet("color: #ffffff;")
        filter_layout.addWidget(time_label)

        self.time_combo = QComboBox()
        time_options = ["全部时间", "今天", "本周", "本月"]
        self.time_combo.addItems(time_options)
        self.time_combo.setCurrentText(self.time_filter)
        self.time_combo.currentTextChanged.connect(self.on_time_filter_changed)
        self.time_combo.setStyleSheet("""
            QComboBox {
                background-color: #121212;
                color: #e0e0e0;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        filter_layout.addWidget(self.time_combo)

        # 名称筛选
        name_label = QLabel("名称筛选:")
        name_label.setFont(QFont("Microsoft YaHei", 10))
        name_label.setStyleSheet("color: #ffffff;")
        filter_layout.addWidget(name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setText(self.name_filter)
        self.name_edit.textChanged.connect(self.on_name_filter_changed)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #121212;
                color: #e0e0e0;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        filter_layout.addWidget(self.name_edit)

        filter_layout.addStretch()
        self.main_layout.addWidget(filter_frame)

    def create_path_controls(self):
        path_frame = QFrame()
        path_frame.setFrameShape(QFrame.Shape.StyledPanel)
        path_frame.setStyleSheet("background-color: #1e1e1e; border: 1px solid #424242; border-radius: 8px;")
        path_layout = QVBoxLayout(path_frame)
        path_layout.setContentsMargins(15, 15, 15, 15)

        # 选择文件夹按钮
        button_layout = QHBoxLayout()
        self.select_folder_button = QPushButton("选择文件夹")
        self.select_folder_button.setFont(QFont("Microsoft YaHei", 10))
        self.select_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.select_folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_folder_button)

        # 路径记忆按钮
        self.remember_path_button = QPushButton("记忆当前路径")
        self.remember_path_button.setFont(QFont("Microsoft YaHei", 10))
        self.remember_path_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3e8e40;
            }
        """)
        self.remember_path_button.clicked.connect(self.remember_current_path)
        button_layout.addWidget(self.remember_path_button)

        path_layout.addLayout(button_layout)

        # 路径标签
        self.path_label = QLabel("当前路径: 未选择文件夹")
        self.path_label.setFont(QFont("Microsoft YaHei", 10))
        self.path_label.setStyleSheet("""
            QLabel {
                background-color: #121212;
                color: #e0e0e0;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        path_layout.addWidget(self.path_label)

        self.main_layout.addWidget(path_frame)

    def create_tabs(self):
        # 创建标签页控件
        self.notebook = QTabWidget()
        self.notebook.setTabPosition(QTabWidget.TabPosition.North)
        self.notebook.setStyleSheet("""
            QTabWidget::tab-bar {alignment: center;}
            QTabBar::tab {
                background-color: #424242;
                color: #e0e0e0;
                padding: 10px 20px;
                font-size: 10pt;
                font-family: 'Microsoft YaHei';
            }
            QTabBar::tab:selected {
                background-color: #121212;
                color: #bb86fc;
            }
        """)

        # 创建分类标签页
        self.tabs = {}
        self.scroll_areas = {}

        for category in FILE_CATEGORIES.keys():
            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("background-color: #121212; border: 1px solid #424242; border-radius: 5px;")

            # 创建内容框架
            content_frame = QFrame()
            content_frame.setStyleSheet("background-color: #121212;")
            content_layout = QVBoxLayout(content_frame)
            content_layout.setSpacing(10)

            scroll_area.setWidget(content_frame)
            self.notebook.addTab(scroll_area, category)

            self.tabs[category] = content_layout
            self.scroll_areas[category] = scroll_area

        self.main_layout.addWidget(self.notebook)
        
    def load_last_folder(self):
        self.last_folder = Config.load_last_folder()

    def save_last_folder(self):
        Config.save_last_folder(self.last_folder)

    def display_folder_contents(self, folder_path):
        # 清空每个标签页
        for layout in self.tabs.values():
            while layout.count() > 0:
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    layout.removeWidget(widget)
                    widget.hide()

        # 文件分类
        categorized_files = {category: [] for category in FILE_CATEGORIES}

        try:
            file_count = 0
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    ext = os.path.splitext(item)[1].lower()
                    for category, extensions in FILE_CATEGORIES.items():
                        if ext in extensions:
                            categorized_files[category].append(item_path)
                            file_count += 1
                            break
            print(f"已加载 {file_count} 个文件")
        except Exception as e:
            print(f"读取文件夹内容失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"无法读取文件夹内容: {str(e)}")
            return

        # 显示分类内容
        for category, files in categorized_files.items():
            if files:
                layout = self.tabs[category]
                for file_path in files:
                    FileOperations.display_file(file_path, layout)

    def on_time_filter_changed(self, text):
        self.time_filter = text
        if self.last_folder:
            self.display_folder_contents(self.last_folder)

    def on_name_filter_changed(self, text):
        self.name_filter = text
        if self.last_folder:
            self.display_folder_contents(self.last_folder)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.last_folder = folder
            self.save_last_folder()
            self.update_path_label()
            self.display_folder_contents(folder)

    def remember_current_path(self):
        if self.last_folder:
            self.save_last_folder()
            QMessageBox.information(self, "成功", "已记忆当前路径")
        else:
            QMessageBox.warning(self, "警告", "请先选择一个文件夹")

    def update_path_label(self):
        if self.last_folder:
            self.path_label.setText(f"当前路径: {self.last_folder}")
        else:
            self.path_label.setText("当前路径: 未选择文件夹")

    def update_status_bar(self):
        self.status_bar.showMessage("就绪")

    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 224, 224))
        self.setPalette(palette)