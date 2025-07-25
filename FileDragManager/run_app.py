import sys
import os

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入并运行应用
from main import main

if __name__ == "__main__":
    main()