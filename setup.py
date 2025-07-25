import os
import os
import sys
import shutil
import logging
import argparse
from PyInstaller.__main__ import run as pyinstaller_run

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("packaging.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保中文显示正常
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LC_ALL'] = 'zh_CN.UTF-8'

# 确保路径使用正确的分隔符
os.environ['PYTHONPATH'] = os.pathsep.join(sys.path)

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 应用版本
APP_VERSION = '1.0.0'

# 清理旧的构建文件
def clean_old_files():
    logger.info("清理旧的构建文件...")
    for dir_name in ['build', 'dist']:
        dir_path = os.path.join(PROJECT_ROOT, dir_name)
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                logger.info(f"已删除目录: {dir_path}")
            except Exception as e:
                logger.error(f"删除目录 {dir_path} 失败: {e}")

# 检查依赖
def check_dependencies():
    logger.info("检查依赖...")
    dependencies = {
        'PyQt6': 'pip install PyQt6',
        'PyInstaller': 'pip install PyInstaller'
    }

    all_installed = True
    for dep, install_cmd in dependencies.items():
        try:
            __import__(dep)
            logger.info(f"{dep} 已安装")
        except ImportError:
            logger.error(f"未找到{dep}，请安装: {install_cmd}")
            all_installed = False

    return all_installed

# 检查目录是否存在
def check_directories(dirs):
    logger.info("检查目录是否存在...")
    all_exist = True
    for dir_path in dirs:
        full_path = os.path.join(PROJECT_ROOT, dir_path)
        if not os.path.exists(full_path):
            logger.warning(f"目录不存在: {full_path}")
            all_exist = False
        else:
            logger.info(f"目录存在: {full_path}")
    return all_exist

# 打包应用
def package_app(onefile=True, windowed=True, clean=True, version=APP_VERSION):
    logger.info(f"开始打包应用 (版本: {version})...")

    # 确保依赖已安装
    if not check_dependencies():
        logger.error("依赖检查失败，无法继续打包。")
        return False

    # 检查必要目录是否存在
    required_dirs = ['integrated_app', 'FileDragManager', 'file_viewer_gui', 'Word Processing']
    if not check_directories(required_dirs):
        logger.warning("部分目录不存在，但仍尝试继续打包。")
    else:
        logger.info("所有必要目录已存在，继续打包。")

    # 定义PyInstaller参数
    args = [
        os.path.join(PROJECT_ROOT, 'integrated_app', 'main.py'),  # 主程序入口
        f'--name=综合应用',  # 应用名称
        # 添加搜索路径，确保能找到ui_components和text_editor模块
        f'--paths={os.path.join(PROJECT_ROOT, "file_viewer_gui")}',
        f'--paths={os.path.join(PROJECT_ROOT, "Word Processing")}',
        f'--paths={os.path.join(PROJECT_ROOT, "FileDragManager")}',
        # 注意: PyInstaller的--version参数不接受值，它只是显示PyInstaller版本
        # 我们可以在应用内部设置版本，而不是通过PyInstaller参数
    ]

    # 根据参数添加选项 - 强制窗口模式以解决控制台弹出问题
    args.append('--windowed')
    logger.info("强制使用窗口模式打包，已禁用控制台")

    if onefile:
        args.append('--onefile')
        logger.info("打包成单个文件")
    else:
        args.append('--onedir')
        logger.info("打包成多个文件")

    if clean:
        args.append('--clean')
        logger.info("清理临时文件")

    # 添加数据目录
    data_dirs = [
        ('FileDragManager', 'FileDragManager'),
        ('file_viewer_gui', 'file_viewer_gui'),
        ('Word Processing', 'Word Processing')
    ]

    # 检查并添加数据目录
    for src, dst in data_dirs:
        src_path = os.path.join(PROJECT_ROOT, src)
        if os.path.exists(src_path):
            # 对于FileDragManager目录，确保它被正确包含
            if src == 'FileDragManager':
                logger.info(f"FileDragManager目录存在: {src_path}，将被包含在打包中")
                # 确保main.py文件存在
                main_py_path = os.path.join(src_path, 'main.py')
                if os.path.exists(main_py_path):
                    logger.info(f"FileDragManager/main.py文件存在: {main_py_path}")
                    # 尝试直接导入FileDragManager.main模块
                    try:
                        import sys
                        if src_path not in sys.path:
                            sys.path.append(src_path)
                        import main
                        logger.info("成功导入FileDragManager/main模块")
                    except ImportError as e:
                        logger.error(f"导入FileDragManager/main模块失败: {e}")
                else:
                    logger.warning(f"FileDragManager/main.py文件不存在: {main_py_path}")
            args.append(f'--add-data={src_path};{dst}')
            logger.info(f"添加数据目录: {src_path} -> {dst}")
        else:
            logger.warning(f"数据目录不存在: {src_path}")

    # 尝试使用collect-all选项来包含FileDragManager模块及其所有子模块
    args.append('--collect-all=FileDragManager')
    logger.info("添加collect-all选项来包含FileDragManager模块及其所有子模块")

    # 添加隐藏导入
    hidden_imports = [
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'ui_components',
        'text_editor',
        'FileDragManager.main',
        'FileDragManager.dialogs',
        'FileDragManager.history',
        'FileDragManager.utils',
        'os',
        'sys',
        'shutil'
    ]

    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
        logger.info(f"添加隐藏导入: {imp}")

    # 运行PyInstaller
    try:
        logger.info(f"执行PyInstaller命令: {' '.join(args)}")
        pyinstaller_run(args)
        logger.info("打包完成!")
        dist_dir = os.path.join(PROJECT_ROOT, 'dist')
        logger.info(f"可执行文件位于 {dist_dir} 目录中")
        return True
    except Exception as e:
        logger.error(f"打包失败: {e}")
        return False

# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description='打包应用程序')
    parser.add_argument('--onefile', action='store_true', default=True, help='打包成单个文件')
    parser.add_argument('--onedir', action='store_true', help='打包成多个文件')
    parser.add_argument('--windowed', action='store_true', default=True, help='窗口模式')
    parser.add_argument('--console', action='store_true', help='控制台模式')
    parser.add_argument('--clean', action='store_true', default=True, help='清理临时文件')
    parser.add_argument('--version', default=APP_VERSION, help=f'应用版本 (默认: {APP_VERSION})')
    return parser.parse_args()

# 主函数
def main():
    try:
        # 解析命令行参数
        args = parse_args()

        # 清理旧文件
        if args.clean:
            clean_old_files()

        # 打包应用
        success = package_app(
            onefile=not args.onedir, 
            windowed=not args.console, 
            clean=args.clean, 
            version=args.version
        )

        if success:
            logger.info("打包过程已成功完成!")
            return 0
        else:
            logger.error("打包过程失败!")
            return 1
    except Exception as e:
        logger.error(f"发生未预期的错误: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())