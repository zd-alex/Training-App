from cx_Freeze import setup, Executable
import sys
import os

# Добавляем пути к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Определяем базовые директории
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, 'src')
data_dir = os.path.join(base_dir, 'data')

# # Настройки сборки
# build_exe_options = {
#     # "packages": [
#     #     "os", 
#     #     "sys",
#     #     "json",
#     #     "sqlite3",
#     #     "datetime",
#     #     "hashlib",
#     #     "typing",
#     #     "collections",
#     #     "PyQt6",
#     #     "PyQt6.QtCore",
#     #     "PyQt6.QtWidgets",
#     #     "PyQt6.QtGui"
#     # ],
#     "excludes": [
#         "tkinter",
#         "unittest",
#         "email",
#         "http",
#         "xml",
#         "pydoc",
#         "pytest",
#         "numpy",
#         "pandas",
#         "matplotlib"
#     ],
#     # "include_files": [
#     #     # Включаем данные
#     #     (os.path.join(data_dir, "database"), "data/database"),
#     #     (os.path.join(data_dir, "session.json"), "data/session.json"),
        
#     #     # Включаем конфигурационные файлы
#     #     ("config.py", "config.py"),
        
#     #     # Создаем директории если их нет
#     #     # ("data", "data"),
#     # ],
#     # "includes": [
#     #     "src",
#     #     "src.controllers",
#     #     "src.models", 
#     #     "src.views",
#     #     "src.models.repositories"
#     # ],
#     # "path": [src_dir],
#     "optimize": 1,
# }

# Настройки для разных платформ
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Скрыть консольное окно на Windows

# Основные настройки приложения
setup(
    name="FitnessTracker",
    version="1.0.0",
    description="Приложение для отслеживания тренировок",
    # options={"build_exe": build_exe_options},
    executables=[
        Executable(
            script=os.path.join(src_dir, "main.py"),
            base=base,
            target_name="FitnessTracker.exe",
            icon=None,  # Можно добавить путь к иконке .ico
            copyright="Copyright © 2026 zd-alex",
            shortcut_name="Fitness Tracker"
        )
    ],
    author="zd-alex",
    author_email="alex.zderev@gmail.com"
)