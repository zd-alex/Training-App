#!/usr/bin/env python3
"""
Скрипт для сборки приложения Fitness Tracker
"""

import subprocess
import sys
import os

def main():
    """Основная функция сборки"""
    print("=== Сборка Fitness Tracker ===")
    
    # Проверяем зависимости
    try:
        import cx_Freeze
        print("✓ cx_Freeze установлен")
    except ImportError:
        print("✗ cx_Freeze не установлен")
        print("Установите: pip install cx_Freeze")
        return
    
    try:
        import PyQt6
        print("✓ PyQt6 установлен")
    except ImportError:
        print("✗ PyQt6 не установлен")
        print("Установите: pip install PyQt6")
        return
    
    # Запускаем сборку
    print("\nНачинаем сборку...")
    try:
        subprocess.run([sys.executable, "setup.py", "build"], check=True)
        print("\n✓ Сборка завершена успешно!")
        print(f"Исполняемый файл находится в папке: build/")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Ошибка при сборке: {e}")
        return 1
    
    print("\n=== Готово ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())