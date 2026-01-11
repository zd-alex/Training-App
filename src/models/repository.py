# src/models/repository.py
from .database import Database


class ItemRepository:
    def __init__(self, db: Database = None):
        self.db = db or Database()
    
    def get_all(self):
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM items")
            return [dict(row) for row in cursor.fetchall()]
    
    def create(self, name, description):
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO items (name, description) VALUES (?, ?)",
                (name, description)
            )
            return cursor.lastrowid