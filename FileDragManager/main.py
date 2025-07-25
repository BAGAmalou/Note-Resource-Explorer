import os
import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem, QProgressDialog, QStatusBar,
    QDockWidget, QFrame, QToolBar, QMenu, QMessageBox, QInputDialog, QLineEdit,
    QScrollArea, QGroupBox, QCheckBox, QFormLayout, QComboBox, QSpinBox, QTabWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QAction, QPalette, QGuiApplication, QPixmap
from PyQt6.QtWidgets import QStyle

# 导入自定义模块
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dialogs import ImageRenameDialog, CategoryDialog, ErrorDialog
from utils import FileTransferThread
from history import HistoryItemWidget

class FileManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件拖拽管理器")
        self.setMinimumSize(900, 700)  # 增大窗口尺寸
        self.setGeometry(100, 100, 1100, 800)
        
        # 获取应用路径
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        # 初始化变量
        self.default_dir = os.path.join(application_path, "output")
        self.history_file = os.path.join(application_path, "FileDragManager.json")
        self.settings_file = os.path.join(application_path, "FileDragManager.json")
        self.temp_dir = os.path.join(application_path, "temp")
        
        # 确保临时目录存在
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        # 加载设置
        self.settings = self.load_settings()
        self.target_dir = self.settings.get("target_dir", self.default_dir)
        
        self.files = []  # 存储文件路径和自定义名称的元组列表
        self.history = self.load_history()
        self.categorize_files = self.settings.get("categorize_files", False)  # 从设置中加载分类选项，默认关闭
        
        # 从设置中加载图片重命名设置
        self.auto_rename_images = self.settings.get("auto_rename_images", True)
        self.rename_pattern = self.settings.get("rename_pattern", "秒级时间戳+序号")
        
        # 创建UI后再应用主题
        self.init_ui()
        
        # 应用深色主题
        self.apply_dark_theme()
        
        # 设置窗口图标
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))

    def init_ui(self):
        # 创建主部件和布局
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("文件拖拽管理器")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #ffffff;")
        main_layout.addWidget(title_label)
        
        # 控制面板
        control_group = QGroupBox("控制面板")
        control_group.setStyleSheet("""
            QGroupBox {
                background-color: #1e1e1e;
                border: 1px solid #424242;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #bb86fc;
            }
        """)
        
        control_layout = QGridLayout(control_group)
        control_layout.setSpacing(15)
        control_layout.setColumnStretch(0, 1)
        control_layout.setColumnStretch(1, 2)
        control_layout.setColumnStretch(2, 1)
        
        # 目标目录选择
        dir_label = QLabel("目标目录:")
        dir_label.setStyleSheet("color: #ffffff;")
        self.dir_entry = QLabel(self.target_dir)
        self.dir_entry.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #e0e0e0;
                padding: 8px;
                border: 1px solid #424242;
                border-radius: 4px;
            }
        """)
        self.dir_entry.setMinimumHeight(30)
        dir_button = QPushButton("浏览...")
        dir_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        dir_button.clicked.connect(self.select_target_dir)
        
        control_layout.addWidget(dir_label, 0, 0)
        control_layout.addWidget(self.dir_entry, 0, 1)
        control_layout.addWidget(dir_button, 0, 2)
        
        # 目录记忆管理按钮
        memory_layout = QHBoxLayout()
        
        # 清除记忆按钮
        clear_memory_button = QPushButton("清除记忆")
        clear_memory_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        clear_memory_button.clicked.connect(self.clear_target_dir_memory)
        memory_layout.addWidget(clear_memory_button)
        
        # 更新记忆按钮
        update_memory_button = QPushButton("更新记忆")
        update_memory_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        update_memory_button.clicked.connect(self.update_target_dir_memory)
        memory_layout.addWidget(update_memory_button)
        
        control_layout.addLayout(memory_layout, 1, 0, 1, 3)
        
        # 设置按钮
        settings_layout = QHBoxLayout()
        
        # 分类设置按钮
        self.category_button = QPushButton(self.get_category_button_text())
        self.category_button.setStyleSheet(self.get_category_button_style())
        self.category_button.clicked.connect(self.show_category_dialog)
        settings_layout.addWidget(self.category_button)
        
        # 图片重命名按钮 - 根据设置更新文本
        self.image_rename_button = QPushButton(self.get_image_rename_button_text())
        self.image_rename_button.setStyleSheet(self.get_image_rename_button_style())
        self.image_rename_button.clicked.connect(self.show_image_rename_dialog)
        settings_layout.addWidget(self.image_rename_button)
        
        # 清空列表按钮
        clear_button = QPushButton("清空列表")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #bd2130;
            }
        """)
        clear_button.clicked.connect(self.clear_file_list)
        settings_layout.addWidget(clear_button)
        
        control_layout.addLayout(settings_layout, 2, 0, 1, 3)
        
        # 执行按钮
        self.execute_button = QPushButton("执行文件移动")
        self.execute_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:disabled {
                background-color: #424242;
            }
        """)
        self.execute_button.setEnabled(False)
        self.execute_button.clicked.connect(self.execute_transfer)
        control_layout.addWidget(self.execute_button, 3, 0, 1, 3)
        
        main_layout.addWidget(control_group)
        
        # 文件区域
        file_group = QGroupBox("文件区域")
        file_group.setStyleSheet("""
            QGroupBox {
                background-color: #1e1e1e;
                border: 1px solid #424242;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #bb86fc;
            }
        """)
        
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(15)
        
        # 文件夹输入区域
        folder_input_group = QGroupBox("文件夹输入")
        folder_input_group.setStyleSheet("""
            QGroupBox {
                background-color: #1e1e1e;
                border: 1px solid #424242;
                border-radius: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #bb86fc;
                left: 10px;
            }
        """)
        
        folder_input_layout = QHBoxLayout(folder_input_group)
        folder_input_layout.setSpacing(10)
        
        # 文件夹路径输入
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #121212;
                color: #e0e0e0;
                padding: 8px;
                border: 1px solid #424242;
                border-radius: 4px;
            }
        """)
        self.folder_path_edit.setPlaceholderText("输入文件夹路径...")
        
        # 浏览按钮
        browse_folder_button = QPushButton("浏览...")
        browse_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        browse_folder_button.clicked.connect(self.select_folder)
        
        # 添加刷新按钮
        refresh_button = QPushButton("刷新")
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        refresh_button.clicked.connect(self.refresh_folder)
        
        folder_input_layout.addWidget(self.folder_path_edit, 1)
        folder_input_layout.addWidget(browse_folder_button)
        folder_input_layout.addWidget(refresh_button)
        
        file_layout.addWidget(folder_input_group)
        
        # 截图粘贴区域
        paste_group = QGroupBox("截图粘贴区域")
        paste_group.setStyleSheet("""
            QGroupBox {
                background-color: #1e1e1e;
                border: 1px solid #424242;
                border-radius: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #bb86fc;
                left: 10px;
            }
        """)
        
        paste_layout = QHBoxLayout(paste_group)
        
        # 粘贴按钮
        self.paste_button = QPushButton("粘贴截图")
        self.paste_button.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.paste_button.clicked.connect(self.paste_screenshot)
        paste_layout.addWidget(self.paste_button)
        
        # 截图预览
        self.screenshot_preview = QLabel("无截图")
        self.screenshot_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screenshot_preview.setStyleSheet("""
            QLabel {
                background-color: #121212;
                border: 1px solid #424242;
                border-radius: 5px;
                color: #9e9e9e;
                min-height: 80px;
            }
        """)
        self.screenshot_preview.setFixedHeight(80)
        paste_layout.addWidget(self.screenshot_preview, 1)
        
        file_layout.addWidget(paste_group)
        
        # 拖拽区域
        self.drop_area = QLabel("拖放文件到此处 (支持图像、视频、音频、HTML和文档)")
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 3px dashed #616161;
                border-radius: 10px;
                color: #9e9e9e;
                font-size: 16px;
                padding: 40px;
            }
        """)
        self.drop_area.setMinimumHeight(150)
        file_layout.addWidget(self.drop_area, 1)
        
        # 文件列表区域
        file_list_label = QLabel("已添加文件列表")
        file_list_label.setFont(QFont("Microsoft YaHei", 11))
        file_list_label.setStyleSheet("color: #ffffff;")
        file_layout.addWidget(file_list_label)
        
        # 文件列表控件
        self.file_list_widget = QListWidget()
        self.file_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #121212;
                border: 1px solid #424242;
                border-radius: 5px;
                color: #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #0d47a1;
            }
        """)
        self.file_list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.file_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list_widget.customContextMenuRequested.connect(self.show_context_menu)
        file_layout.addWidget(self.file_list_widget, 2)
        
        main_layout.addWidget(file_group, 1)
        
        # 设置主部件
        self.setCentralWidget(main_widget)
        
        # 创建历史记录侧边栏
        self.create_history_dock()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 启用拖放
        self.setAcceptDrops(True)
        self.drop_area.setAcceptDrops(True)
        
        # 初始化状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
    
    def create_toolbar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #121212;
                border-bottom: 1px solid #424242;
            }
        """)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
        # 查看历史
        history_action = QAction("查看历史", self)
        history_action.triggered.connect(self.toggle_history_panel)
        history_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
        toolbar.addAction(history_action)
        
        # 添加分隔符
        toolbar.addSeparator()
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        about_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        toolbar.addAction(about_action)
    
    # 加载设置
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 加载历史记录面板状态，默认为True
                    if 'history_visible' in settings:
                        return settings
                    else:
                        settings['history_visible'] = True
                        return settings
        except:
            pass
        return {'history_visible': True}
    
    # 保存设置
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                settings = {
                    "target_dir": self.target_dir,
                    "auto_rename_images": self.auto_rename_images,
                    "rename_pattern": self.rename_pattern,
                    "history_visible": self.settings.get('history_visible', True),
                    "categorize_files": self.categorize_files
                }
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
    
    # 清除目录记忆
    def clear_target_dir_memory(self):
        self.target_dir = self.default_dir
        self.dir_entry.setText(self.target_dir)
        self.save_settings()
        self.status_bar.showMessage("目录记忆已清除，恢复为默认目录", 3000)
    
    # 更新目录记忆
    def update_target_dir_memory(self):
        self.save_settings()
        self.status_bar.showMessage("当前目录已保存为记忆目录", 3000)
    
    # 关闭事件 - 保存设置
    def closeEvent(self, event):
        self.save_settings()
        event.accept()
    
    def show_image_rename_dialog(self):
        dialog = ImageRenameDialog(self)
        if dialog.exec():
            settings = dialog.get_settings()
            self.auto_rename_images = settings["enabled"]
            self.rename_pattern = settings["pattern"]
            
            # 更新按钮文本和样式
            self.image_rename_button.setText(self.get_image_rename_button_text())
            self.image_rename_button.setStyleSheet(self.get_image_rename_button_style())
            
            # 更新状态栏
            self.update_status_bar()
    
    def get_image_rename_button_text(self):
        return "图片重命名: 开启" if self.auto_rename_images else "图片重命名: 关闭"
    
    def get_image_rename_button_style(self):
        if self.auto_rename_images:
            return """
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #0b5ed7;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """
    
    def show_category_dialog(self):
        dialog = CategoryDialog(self)
        if dialog.exec():
            self.categorize_files = dialog.get_categorize_option()
            self.save_settings()  # 保存分类设置
            # 更新按钮文本和样式
            self.category_button.setText(self.get_category_button_text())
            self.category_button.setStyleSheet(self.get_category_button_style())
            # 更新状态栏
            self.update_status_bar()

    def get_category_button_text(self):
        return "分类设置: 开启" if self.categorize_files else "分类设置: 关闭"

    def get_category_button_style(self):
        if self.categorize_files:
            return """
                QPushButton {
                    background-color: #2e7d32;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3e8e40;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #424242;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #525252;
                }
            """
    
    def show_about(self):
        QMessageBox.information(
            self, "关于文件拖拽管理器",
            "文件拖拽管理器 v2.0\n\n"
            "功能：\n"
            "- 拖拽接收多种文件类型\n"
            "- 文件分类存储\n"
            "- 图片自动重命名功能\n"
            "- 详细历史记录\n"
            "- 复制目标路径 + 新文件名\n"
            "- 完全黑色主题界面\n\n"
            "支持的文件类型：\n"
            "图像 (.jpg, .jpeg, .png, .gif)\n"
            "视频 (.mp4, .mov, .avi, .mkv, .flv, .wmv)\n"
            "音频 (.mp3, .wav, .flac, .aac)\n"
            "HTML (.html, .htm)\n"
            "文档 (.pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .txt, .md, .epub, .mobi, .azw3, .chm)\n\n"
            "© 2023 文件拖拽管理器"
        )
    
    def create_history_dock(self):
        # 创建历史记录侧边栏
        self.history_dock = QDockWidget("历史记录", self)
        self.history_dock.setStyleSheet("""
            QDockWidget {
                background-color: #121212;
                color: #e0e0e0;
                titlebar-close-icon: url(none);
                titlebar-normal-icon: url(none);
            }
            QDockWidget::title {
                background-color: #121212;
                text-align: left;
                padding-left: 10px;
            }
        """)
        self.history_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                                     QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.history_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                         Qt.DockWidgetArea.RightDockWidgetArea)
        
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setSpacing(10)
        history_layout.setContentsMargins(15, 15, 15, 15)
        
        # 历史记录标题
        history_title = QLabel("最近操作记录")
        history_title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        history_title.setStyleSheet("color: #ffffff;")
        history_layout.addWidget(history_title)
        
        # 历史记录列表
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #121212;
                border: 1px solid #424242;
                border-radius: 5px;
                color: #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #0d47a1;
            }
        """)
        history_layout.addWidget(self.history_list)
        
        self.history_dock.setWidget(history_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.history_dock)
        
        # 根据设置显示或隐藏历史记录面板
        if self.settings.get('history_visible', True):
            self.history_dock.show()
        else:
            self.history_dock.hide()
        
        # 加载历史记录
        self.load_history_to_list()

    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_history(self, processed_files):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "time": now,
            "files": processed_files
        }
        # 确保self.history是列表类型
        if not isinstance(self.history, list):
            self.history = []
        self.history.append(history_entry)
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {str(e)}")
        
        # 更新历史记录显示
        self.load_history_to_list()

    def load_history_to_list(self):
        self.history_list.clear()
        
        # 只显示最近的50条记录，并反转顺序使其从新到旧
        recent_history = self.history[-50:] if isinstance(self.history, list) and self.history else []
        recent_history.reverse()  # 反转列表顺序
        
        for entry in recent_history:
            time_str = entry["time"]
            time_label = QLabel(f"<b>{time_str}</b>")
            time_label.setStyleSheet("color: #bb86fc; background-color: #1e1e1e; padding: 5px;")
            
            time_item = QListWidgetItem()
            time_item.setSizeHint(time_label.sizeHint())
            self.history_list.addItem(time_item)
            self.history_list.setItemWidget(time_item, time_label)
            
            for file_info in entry["files"]:
                # 创建自定义列表项
                item_widget = HistoryItemWidget(file_info)
                
                # 创建列表项并设置自定义widget
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                self.history_list.addItem(item)
                self.history_list.setItemWidget(item, item_widget)

    def select_target_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择目标目录", self.target_dir)
        if dir_path:
            self.target_dir = dir_path
            self.dir_entry.setText(dir_path)
            self.save_settings()
            
    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", os.path.expanduser("~"))
        if folder_path:
            self.folder_path_edit.setText(folder_path)
            # 自动加载文件夹中的文件
            self.load_files_from_folder(folder_path)
    
    def refresh_folder(self):
        folder_path = self.folder_path_edit.text()
        if folder_path and os.path.exists(folder_path):
            self.load_files_from_folder(folder_path)
        else:
            QMessageBox.warning(self, "警告", "请先选择有效的文件夹路径")

    def clear_file_list(self):
        self.files = []
        self.file_list_widget.clear()
        self.execute_button.setEnabled(False)
        self.update_status_bar()
        
    def load_files_from_folder(self, folder_path):
        try:
            # 清空当前文件列表
            self.clear_file_list()
            
            # 遍历文件夹
            file_count = 0
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 检查文件是否存在
                    if os.path.exists(file_path):
                        # 添加文件到列表 (路径, 自定义名称)
                        self.files.append((file_path, None))
                        file_count += 1
                        # 创建文件列表项并添加到UI
                        file_name = os.path.basename(file_path)
                        item = QListWidgetItem(file_name)
                        self.file_list_widget.addItem(item)
                        # 强制更新UI
                        self.file_list_widget.update()
                        QApplication.processEvents()
            
            self.update_status_bar()
            # 启用执行按钮
            if self.files:
                self.execute_button.setEnabled(True)
        except Exception as e:
            self.statusBar().showMessage(f"加载文件夹失败: {str(e)}")
            # 创建错误信息字典
            error_info = {
                'success': [],
                'errors': [(folder_path, str(e))]
            }
            ErrorDialog(error_info, self).exec()

    def execute_transfer(self):
        if not self.files:
            return
        
        # 创建进度对话框
        progress_dialog = QProgressDialog("正在移动文件...", "取消", 0, 100, self)
        progress_dialog.setWindowTitle("文件移动进度")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setAutoClose(True)
        progress_dialog.setAutoReset(True)
        
        # 创建文件传输线程
        transfer_thread = FileTransferThread(
            self.files,
            self.target_dir,
            self.categorize_files,
            self.auto_rename_images,
            self.rename_pattern
        )
        
        # 连接信号和槽
        transfer_thread.progress_updated.connect(progress_dialog.setValue)  # 传递百分比
        transfer_thread.progress_updated.connect(
            lambda percent, text: progress_dialog.setLabelText(text)  # 只传递文本
        )
        transfer_thread.transfer_complete.connect(self.handle_transfer_complete)
        transfer_thread.error_occurred.connect(self.handle_transfer_error)
        
        # 启动线程
        transfer_thread.start()
        
        # 显示进度对话框
        progress_dialog.exec()

    def handle_transfer_complete(self, result):
        error_files, processed_files = result
        errors = {
            "success": processed_files,
            "errors": error_files
        }
        
        # 显示错误对话框
        error_dialog = ErrorDialog(errors, self)
        error_dialog.exec()
        
        # 保存历史记录
        self.save_history(processed_files)
        
        # 清空文件列表
        self.clear_file_list()

    def handle_transfer_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def update_status_bar(self):
        status_text = f"目标目录: {self.target_dir} | "
        status_text += f"文件分类: {'开启' if self.categorize_files else '关闭'} | "
        status_text += f"图片重命名: {'开启' if self.auto_rename_images else '关闭'}"
        self.status_bar.showMessage(status_text)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        remove_action = QAction("移除选中文件", self)
        remove_action.triggered.connect(self.remove_selected_files)
        menu.addAction(remove_action)
        menu.exec(self.file_list_widget.mapToGlobal(pos))

    def remove_selected_files(self):
        selected_items = self.file_list_widget.selectedItems()
        for item in selected_items:
            index = self.file_list_widget.row(item)
            del self.files[index]
            self.file_list_widget.takeItem(index)
        
        if not self.files:
            self.execute_button.setEnabled(False)
        self.update_status_bar()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file_path)
                ext = ext.lower()
                is_supported = False
                # 这里我们假设FILE_CATEGORIES在utils模块中定义
                from .utils import FILE_CATEGORIES
                for exts in FILE_CATEGORIES.values():
                    if ext in exts:
                        is_supported = True
                        break
                if is_supported:
                    self.files.append((file_path, None))
                    item = QListWidgetItem(os.path.basename(file_path))
                    self.file_list_widget.addItem(item)
                    self.execute_button.setEnabled(True)
                    self.update_status_bar()
                else:
                    QMessageBox.warning(self, "不支持的文件类型", f"文件 {os.path.basename(file_path)} 不支持。")
        event.acceptProposedAction()

    def paste_screenshot(self):
        clipboard = QGuiApplication.clipboard()
        pixmap = clipboard.pixmap()
        if not pixmap.isNull():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"{timestamp}.png"
            file_path = os.path.join(self.temp_dir, file_name)
            pixmap.save(file_path)
            self.files.append((file_path, None))
            item = QListWidgetItem(file_name)
            self.file_list_widget.addItem(item)
            self.execute_button.setEnabled(True)
            self.update_status_bar()
            self.screenshot_preview.setPixmap(pixmap.scaled(self.screenshot_preview.size(), Qt.AspectRatioMode.KeepAspectRatio))
        else:
            QMessageBox.warning(self, "无截图", "剪贴板中没有截图。")

    def toggle_history_panel(self):
        if self.history_dock.isVisible():
            self.history_dock.hide()
            self.settings['history_visible'] = False
        else:
            self.history_dock.show()
            self.settings['history_visible'] = True
        self.save_settings()

    def apply_dark_theme(self):
        # 设置深色主题
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 224, 224))
        palette.setColor(QPalette.ColorRole.Base, QColor(18, 18, 18))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(224, 224, 224))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(224, 224, 224))
        palette.setColor(QPalette.ColorRole.Text, QColor(224, 224, 224))
        palette.setColor(QPalette.ColorRole.Button, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(224, 224, 224))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")


def main():
    app = QApplication(sys.argv)
    window = FileManagerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()