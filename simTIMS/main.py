from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow
from action.setup_trdp_window import TrdpWindow
import tkinter.messagebox as msgbox
import sys,os

# class MainWindow():
#     def __init__(self):
#         super().__init__()
#
#         # 加载 UI 文件
#         ui_file_path = "ui/simTIMS.ui"
#         loader = QUiLoader()
#         ui_file = QFile(ui_file_path)
#         ui_file.open(QFile.OpenModeFlag.ReadOnly)
#         self.ui = loader.load(ui_file)
#         ui_file.close()
#         self.ui.show()

if __name__ == "__main__":
    '''加载运行ui界面 '''
    # 获取正确的路径
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        base_path = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        base_path = os.path.dirname(os.path.abspath(os.path.abspath(__file__)))

    # ui_path = os.path.join(base_path, "ui", "simTIMS.ui")

    try:
        app = QApplication([])
        window = TrdpWindow()
        window.setup(base_path)
        app.aboutToQuit.connect(lambda :print("应用程序即将退出"))
        sys.exit(app.exec())
    except Exception as e:
        print(f"程序启动错误: {e}")
        # 如果GUI不可用，至少显示错误信息
        try:
            msgbox.showerror("错误", f"程序启动失败:\n{e}")
        except:
            print(f"程序启动失败: {e}")
        sys.exit(1)
