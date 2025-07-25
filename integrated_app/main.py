import os
import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QSplitter, QPushButton, QMessageBox, QTextEdit
from PyQt6.QtCore import Qt

# 设置日志重定向
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

# 配置日志
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 重定向stdout和stderr到日志
class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message.strip():
            self.level(message.strip())

    def flush(self):
        pass

sys.stdout = LoggerWriter(logging.info)
sys.stderr = LoggerWriter(logging.error)

# 隐藏控制台窗口
if hasattr(sys, 'frozen') and sys.frozen in ('windows_exe', 'console_exe'):
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# 添加项目路径到系统路径
file_viewer_gui_path = os.path.join(os.path.dirname(__file__), '..', 'file_viewer_gui')
if file_viewer_gui_path not in sys.path:
    sys.path.append(file_viewer_gui_path)

file_drag_manager_path = os.path.join(os.path.dirname(__file__), '..', 'FileDragManager')
if file_drag_manager_path not in sys.path:
    sys.path.append(file_drag_manager_path)

word_processing_path = os.path.join(os.path.dirname(__file__), '..', 'Word Processing')
if word_processing_path not in sys.path:
    sys.path.append(word_processing_path)

# 导入模块
try:
    from ui_components import FileViewerApp
    print("成功导入ui_components模块")
except ImportError:
    print(f"无法导入ui_components模块，检查路径: {file_viewer_gui_path}")
    sys.exit(1)

try:
    from text_editor import TextProcessorApp
    print("成功导入text_editor模块")
except ImportError:
    print(f"无法导入text_editor模块，检查路径: {word_processing_path}")
    sys.exit(1)

# 导入FileManagerApp
try:
    from FileDragManager.main import FileManagerApp
    print("成功导入FileManagerApp")
except ImportError as e:
    # 尝试使用相对路径导入
    try:
        import sys
        import os
        # 确保FileDragManager目录在系统路径中
        file_drag_manager_path = os.path.join(os.path.dirname(__file__), '..', 'FileDragManager')
        if file_drag_manager_path not in sys.path:
            sys.path.append(file_drag_manager_path)
        from main import FileManagerApp
        print("成功导入FileManagerApp")
    except Exception as e2:
        print(f"无法导入FileManagerApp: {e2}")
        sys.exit(1)

class IntegratedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("整合应用")
        self.setMinimumSize(1200, 900)
        self.setGeometry(100, 100, 1200, 900)

        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet("""
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

        # 创建文件拖拽管理器标签页
        self.file_drag_manager_tab = QWidget()
        self.file_drag_manager_layout = QVBoxLayout(self.file_drag_manager_tab)
        self.file_drag_manager = FileManagerApp()
        self.file_drag_manager_layout.addWidget(self.file_drag_manager)
        self.tab_widget.addTab(self.file_drag_manager_tab, "文件拖拽管理器")

        # 创建文件查看器标签页
        self.file_viewer_tab = QWidget()
        self.file_viewer_layout = QVBoxLayout(self.file_viewer_tab)
        self.file_viewer = FileViewerApp()
        self.file_viewer_layout.addWidget(self.file_viewer)
        self.tab_widget.addTab(self.file_viewer_tab, "文件查看器")

        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # 创建左右分栏布局
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧面板 - Word Processing
        self.word_processor = TextProcessorApp()
        splitter.addWidget(self.word_processor)
        
        # 右侧面板 - 现有标签页
        splitter.addWidget(self.tab_widget)
        
        # 设置分割比例
        # 将左侧面板宽度设置为5厘米(约189像素)
        left_width = 189  # 5cm * 37.8像素/cm
        splitter.setSizes([left_width, 800])
        self.word_processor.setMinimumWidth(left_width)
        self.word_processor.setMaximumWidth(left_width)
        
        self.setCentralWidget(splitter)

        # 添加关于按钮
        self.about_button = QPushButton("关于")
        self.about_button.clicked.connect(self.show_about)
        self.statusBar().addPermanentWidget(self.about_button)

    def show_about(self):
        # 创建自定义对话框
        dialog = QMessageBox(self)
        dialog.setWindowTitle("关于")
        dialog.setIcon(QMessageBox.Icon.Information)
        
        # 创建文本编辑控件显示日志
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setMinimumSize(600, 400)
        
        # 读取日志文件
        try:
            # 获取日志文件路径
            if hasattr(sys, 'frozen'):
                # 当应用被打包为exe时
                base_path = os.path.dirname(sys.executable)
            else:
                # 开发环境
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            log_path = os.path.join(base_path, '..', 'logs', 'app.log')
            log_path = os.path.abspath(log_path)
            
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                log_text.setText(log_content)
                dialog.setText(f"整合应用 v1.0\n\n日志文件路径: {log_path}")
            else:
                log_text.setText("日志文件不存在或尚无日志记录")
                dialog.setText("整合应用 v1.0\n\n这是一个整合了文件拖拽管理器、文件查看器和文本处理器的应用程序。")
        except Exception as e:
            log_text.setText(f"无法读取日志文件: {str(e)}")
            dialog.setText("整合应用 v1.0\n\n日志查看功能出错")
        
        # 设置对话框布局
        layout = QVBoxLayout()
        layout.addWidget(dialog.layout())
        layout.addWidget(log_text)
        
        # 创建容器窗口并设置布局
        container = QWidget()
        container.setLayout(layout)
        dialog.setLayout(layout)
        
        dialog.exec()

    def on_tab_changed(self, index):
        # 当标签页切换时刷新当前程序
        if index == 0:
            # 刷新文件拖拽管理器
            pass
        elif index == 1:
            # 刷新文件查看器
            if hasattr(self.file_viewer, 'last_folder') and self.file_viewer.last_folder:
                self.file_viewer.display_folder_contents(self.file_viewer.last_folder)

def main():
    app = QApplication(sys.argv)
    window = IntegratedApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()