from PyQt5.QtWidgets import QApplication
from views import MainWindow
import sys
import ctypes

def main():
    # Для правильного отображения в Windows
    if hasattr(ctypes, 'windll'):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('elevator.company.app')
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()