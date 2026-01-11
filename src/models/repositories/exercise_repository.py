# src/models/repositories/exercise_repository.py
from typing import List, Optional
from .base_repository import BaseRepository

class ExerciseRepository(BaseRepository):
    """Репозиторий для работы с упражнениями"""
    
    def table_name(self):
        return "exercises"
    
    def create(self, user_id: int, name: str, description: str, rest_time: int, prepare_time: int, reps: int, sets: int) -> int:
        """Создание нового упражнения для пользователя"""
        query = f"""
            INSERT INTO {self.table_name()} (user_id, name, description, rest_time, prepare_time, reps, sets)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (user_id, name, description, rest_time, prepare_time, reps, sets))
    
    def update(self, exercise_id: int, user_id: int, name: str, description: str, rest_time: int, prepare_time: int, reps: int, sets: int) -> bool:
        """Обновление данных упражнения пользователя"""
        query = f"""
            UPDATE {self.table_name()} 
            SET name = ?, 
                description = ?, 
                rest_time = ?, 
                prepare_time = ?, 
                reps = ?, 
                sets = ?
            WHERE user_id = ? AND id = ?
        """
        return self.execute_update(query, (name, description, rest_time, prepare_time, reps, sets, user_id, exercise_id))
    
    def delete(self, exercise_id: int, user_id: int) -> bool:
        """Удаление упражнения пользователя"""
        query = f"""
            DELETE FROM {self.table_name()} 
            WHERE id = ? and user_id = ? 
        """
        affected_rows = self.execute_delete(query, (exercise_id, user_id))
        return affected_rows > 0
    
    def get_user_exercises(self, user_id: int) -> List[dict]:
        """Получение упражнений пользователя"""
        query = f"""
            SELECT * FROM {self.table_name()} 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """
        return self.execute_select(query, (user_id,))    
   
    def get_by_id(self, exercise_id: int, user_id: int = None) -> Optional[dict]:
        """Получение упражнения по ID с проверкой владельца"""
        if user_id:
            query = f"SELECT * FROM {self.table_name()} WHERE id = ? AND user_id = ?"
            results = self.execute_select(query, (exercise_id, user_id))
        else:
            query = f"SELECT * FROM {self.table_name()} WHERE id = ?"
            results = self.execute_select(query, (exercise_id,))
        return results[0] if results else None
    

