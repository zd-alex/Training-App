# src/main.py
import sys
import os
from pathlib import Path

# Добавляем корень проекта в путь для импорта config.py
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication
from controllers.main_controller import MainController


def main():
    app = QApplication(sys.argv)
   
    # Устанавливаем стили
    app.setStyle("Fusion")
    
    # Создаем и запускаем контроллер
    controller = MainController()
    controller.run()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()