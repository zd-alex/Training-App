# src/models/database.py
import sqlite3
from pathlib import Path
import hashlib
from contextlib import contextmanager
# from config import DB_PATH
# from typing import Optional, Generator

from config import get_logger

# Получаем логгер для текущего модуля
logger = get_logger(__name__)

class Database:
    def __init__(self, db_path=None):
        logger.debug("Инициализация Database")
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # Создание таблиц
        with self.get_connection() as conn:
            # -- Таблица пользователей
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    last_login TIMESTAMP
                )
            """)
            # -- Таблица настроек тренировки
            conn.execute("""
                CREATE TABLE IF NOT EXISTS exercises (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id           INTEGER NOT NULL,
                    name              TEXT NOT NULL,
                    description       TEXT,
                    sets              INTEGER DEFAULT 3,    -- количество подходов
                    reps              INTEGER,  -- целевое количество повторений
                    rest_time         INTEGER DEFAULT 30,    -- время отдыха между подходами в сек
                    prepare_time      INTEGER DEFAULT 10,    -- время подготовки в сек
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id)
                    REFERENCES users (id) ON DELETE CASCADE
                    -- UNIQUE (user_id, name)
                    );
                """)
            
            # -- Таблица тренировок
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id         INTEGER   PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER   NOT NULL,
                    name       TEXT     NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    work_time  INTEGER,
                    rest_time  INTEGER,
                    sets       INTEGER,
                    reps       INTEGER,
                    FOREIGN KEY ( user_id )
                    REFERENCES users (id) ON DELETE CASCADE
                    );
                """)

            # -- Таблица подходов (основная таблица с данными выполнения)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    workout_id  INTEGER NOT NULL,
                    -- exercise_id INTEGER NOT NULL,
                    set_number  INTEGER NOT NULL,
                    reps        INTEGER,
                    duration    INTEGER,
                    --rest_time   INTEGER,
                    --sets        INTEGER,
                    --notes       TEXT,
                    FOREIGN KEY (workout_id)
                    REFERENCES workouts (id) ON DELETE CASCADE
                    -- FOREIGN KEY (exercise_id)
                    -- REFERENCES exercises (id),
                    -- UNIQUE (
                    --     workout_id,
                    --     exercise_id,
                    --     set_number
                    -- )
                );
            """)

            # Таблица сессий (для запоминания входа)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # НАСТРОЙКА ФОРМАТА ВОЗВРАЩАЕМЫХ ДАННЫХ
        # Теперь строки можно получать как словари: row['column_name']

        try:
            yield conn  # Остановка здесь, пока выполняется код в with
            conn.commit()   # Фиксируем изменения в БД
        except Exception:
            conn.rollback()     # Отменяем все изменения транзакции
            raise   # Пробрасываем исключение дальше
        finally:
            conn.close()    # Освобождаем ресурсы

    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_database_info(self) -> dict:
        """Получение информации о базе данных"""
        try:
            with self.get_connection() as conn:
                # Размер базы данных
                size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                # Количество записей в таблицах
                tables = ['users', 'workouts', 'exercises', 'user_sessions']
                counts = {}
                
                for table in tables:
                    result = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                    counts[table] = result['count'] if result else 0
                
                # Версия SQLite
                version_result = conn.execute("SELECT sqlite_version() as version").fetchone()
                sqlite_version = version_result['version'] if version_result else "unknown"
                
                return {
                    "path": str(self.db_path),
                    "size_bytes": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "exists": self.db_path.exists(),
                    "table_counts": counts,
                    "sqlite_version": sqlite_version,
                    "config_source": "custom" if hasattr(self, '_custom_path') else "default"
                }
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {"error": str(e)}
        

# # Функция для удобного создания экземпляра Database
# def create_database(db_path: Optional[str] = None) -> Database:
#     """
#     Создание экземпляра Database
    
#     Args:
#         db_path: Путь к базе данных (опционально)
        
#     Returns:
#         Экземпляр Database
#     """
#     return Database(db_path)


# # Глобальный экземпляр для использования во всем приложении
# # (опционально, можно создавать экземпляры по мере необходимости)
# _database_instance = None

# def get_database(db_path: Optional[str] = None) -> Database:
#     """
#     Получение глобального экземпляра Database (синглтон)
    
#     Args:
#         db_path: Путь к базе данных (только для первого вызова)
        
#     Returns:
#         Экземпляр Database
#     """
#     global _database_instance
    
#     if _database_instance is None:
#         _database_instance = create_database(db_path)
    
#     return _database_instance