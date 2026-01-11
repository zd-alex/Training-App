# src/models/base_repository.py
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseRepository(ABC):
    """Базовый класс для всех репозиториев"""
    
    def __init__(self, db):
        self.db = db
    
    @abstractmethod
    def table_name(self) -> str:
        """Имя таблицы в БД"""
        pass

    def execute_select(self, query: str, params: tuple = ()) -> List[Dict]:
        """Выполняет SELECT запросы и возвращает список словарей"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Выполняет INSERT и возвращает ID новой записи"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Выполняет UPDATE и возвращает количество обновленных строк"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """Выполняет DELETE и возвращает количество удаленных строк"""
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
