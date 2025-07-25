import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QFileDialog, QMessageBox, QDialog, QGroupBox, QStatusBar
)
from PyQt6.QtCore import QSettings, QCoreApplication, Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QClipboard

class PresetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("预设文本")
        self.setGeometry(400, 400, 500, 300)
        self.parent = parent
        
        # 应用深色主题
        self.apply_dark_theme()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("预设文本")
        title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(title_label)
        
        # 预设文本区域
        self.preset_text = QTextEdit()
        self.preset_text.setPlaceholderText("输入需要删除的文本字段，每行一个...")
        self.preset_text.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #e0e0e0;
                padding: 10px;
                border: 1px solid #424242;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.preset_text)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存预设")
        self.clear_btn = QPushButton("清空预设")
        self.load_btn = QPushButton("导入预设")
        
        # 设置按钮样式
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 6px 10px; font-size: 9pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 6px 10px; font-size: 9pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 6px 10px; font-size: 9pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.load_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 连接信号和槽
        self.save_btn.clicked.connect(parent.save_config)
        self.clear_btn.clicked.connect(parent.clear_preset)
        self.load_btn.clicked.connect(parent.import_preset)
        
    def apply_dark_theme(self):
        # 设置深色主题
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(224, 224, 224))
        palette.setColor(QPalette.ColorRole.Base, QColor(18, 18, 18))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Text, QColor(224, 224, 224))
        self.setPalette(palette)

class TextProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文本处理器")
        self.setGeometry(300, 300, 800, 400)
        self.setMinimumSize(600, 300)
        
        # 配置设置
        QCoreApplication.setOrganizationName("MyCompany")
        QCoreApplication.setApplicationName("TextProcessor")
        self.settings = QSettings()
        
        # 创建预设对话框
        self.preset_dialog = PresetDialog(self)
        
        self.init_ui()
        self.load_config()
        self.apply_dark_theme()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("文本处理器")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #ffffff;")
        main_layout.addWidget(title_label)
        
        # 预设按钮
        preset_btn_layout = QHBoxLayout()
        self.preset_btn = QPushButton("预设文本")
        self.preset_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                padding: 6px 10px; font-size: 9pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.preset_btn.clicked.connect(self.show_preset_dialog)
        preset_btn_layout.addWidget(self.preset_btn)
        main_layout.addLayout(preset_btn_layout)
        
        # 输入文本区域
        input_group = QGroupBox("输入文本")
        input_group.setStyleSheet("""
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
        
        input_layout = QVBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("粘贴需要处理的文本内容...")
        self.input_text.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: #e0e0e0;
                padding: 10px;
                border: 1px solid #424242;
                border-radius: 5px;
            }
        """)
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # 按钮布局（粘贴和处理并复制并排）
        buttons_layout = QHBoxLayout()
        self.paste_btn = QPushButton("粘贴")
        self.paste_btn.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                padding: 6px 10px; font-size: 9pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        self.paste_btn.clicked.connect(self.paste_text)
        
        self.process_copy_btn = QPushButton("处理并复制")
        self.process_copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                font-weight: bold;
                padding: 6px 10px; font-size: 9pt;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.process_copy_btn.clicked.connect(self.process_and_copy_text)
        
        buttons_layout.addWidget(self.paste_btn)
        buttons_layout.addWidget(self.process_copy_btn)
        main_layout.addLayout(buttons_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 初始化状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
        
    def show_preset_dialog(self):
        # 显示预设对话框
        self.preset_dialog.exec()
        
    def load_config(self):
        # 从注册表/ini文件加载预设
        preset = self.settings.value("preset_text", "")
        self.preset_dialog.preset_text.setPlainText(preset)
        
    def save_config(self):
        # 保存预设到配置
        self.settings.setValue("preset_text", self.preset_dialog.preset_text.toPlainText())
        QMessageBox.information(self, "成功", "预设文本已保存！")
        self.update_status_bar()
        
    def import_preset(self):
        # 从文件导入预设
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文本文件", "", "文本文件 (*.txt);;所有文件 (*.*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.preset_dialog.preset_text.setPlainText(f.read())
                    self.update_status_bar()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法读取文件:\n{str(e)}")
        
    def clear_preset(self):
        self.preset_dialog.preset_text.clear()
        self.update_status_bar()
        
    def paste_text(self):
        # 从剪贴板粘贴文本并刷新程序
        clipboard = QApplication.clipboard()
        self.input_text.setPlainText(clipboard.text())
        # 刷新程序状态
        self.update_status_bar()
        self.apply_dark_theme()
        
    def process_and_copy_text(self):
        # 获取文本内容
        input_content = self.input_text.toPlainText()
        preset_content = self.preset_dialog.preset_text.toPlainText()
        
        if not input_content:
            QMessageBox.warning(self, "警告", "请输入需要处理的文本！")
            return
        
        # 调试信息
        print(f"输入文本: '{input_content}'")
        print(f"输入文本长度: {len(input_content)}")
        print(f"预设文本: '{preset_content}'")
        print(f"预设文本行数: {len([p for p in preset_content.splitlines() if p.strip()])}")
        
        # 处理文本
        result = input_content
        for pattern in preset_content.splitlines():
            pattern = pattern.strip()  # 移除模式两端的空格
            if pattern:
                print(f"替换模式: '{pattern}'")
                original_len = len(result)
                # 尝试匹配并替换
                result = result.replace(pattern, "")
                # 处理可能的路径分隔符差异
                pattern_with_backslash = pattern.replace('/', '\\')
                result = result.replace(pattern_with_backslash, "")
                pattern_with_forward_slash = pattern.replace('\\', '/')
                result = result.replace(pattern_with_forward_slash, "")
                new_len = len(result)
                print(f"替换后减少了 {original_len - new_len} 个字符")
        
        # 复制结果到剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(result)
        QMessageBox.information(self, "成功", "处理结果已复制到剪贴板！")
        print(f"处理后文本: '{result}'")
        print(f"处理后文本长度: {len(result)}")
        
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
        
    def update_status_bar(self):
        # 更新状态栏信息
        preset_count = len([p for p in self.preset_dialog.preset_text.toPlainText().splitlines() if p.strip()])
        status_text = f"预设文本数量: {preset_count}"
        self.status_bar.showMessage(status_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextProcessorApp()
    window.show()
    sys.exit(app.exec())