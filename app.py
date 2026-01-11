import sys
from pathlib import Path
import os
# os.environ['QT_DEBUG_PLUGINS'] = '0'  # Отключает отладку плагинов
# os.environ['QT_FATAL_WARNINGS'] = '0'  # Предотвращает падение при предупреждениях

# Добавляем src в путь для импорта
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import main

if __name__ == "__main__":
    main()