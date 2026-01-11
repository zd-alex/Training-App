# test_imports.py в корне проекта
import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from models.database import Database
    from models.repository import ItemRepository
    from views.main_window import MainWindow
    from controllers.main_controller import MainController
    
    print("✅ Все импорты работают!")
    
    # Тестируем создание объектов
    db = Database()
    print(f"✅ База данных: {db.db_path}")
    
    repo = ItemRepository(db)
    print("✅ Репозиторий создан")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()