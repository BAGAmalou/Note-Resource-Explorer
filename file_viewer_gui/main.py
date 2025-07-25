import sys
from PyQt6.QtWidgets import QApplication
from ui_components import FileViewerApp

def main():
    app = QApplication(sys.argv)
    window = FileViewerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()