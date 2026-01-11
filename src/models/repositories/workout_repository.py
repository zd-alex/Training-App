# src/models/repositories/workout_repository.py
from typing import List, Optional
from .base_repository import BaseRepository

class WorkoutRepository(BaseRepository):
    """Репозиторий для работы с тренировками"""
    
    def table_name(self):
        return "workouts"
    
    def create(self, user_id: int, name: str, work_time: int, rest_time: int, reps: int, sets: int) -> int:
        """Создание новой тренировки для пользователя"""
        query = f"""
            INSERT INTO {self.table_name()} (user_id, name, work_time, rest_time, reps, sets)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (user_id, name, work_time, rest_time, reps, sets))
    
    def update(self, workout_id: int, user_id: int, name: str, rest_time: int, work_time: int, reps: int, sets: int) -> bool:
        """Обновление данных тренировки пользователя"""
        query = f"""
            UPDATE {self.table_name()} 
            SET name = ?, 
                rest_time = ?, 
                work_time = ?, 
                reps = ?, 
                sets = ?
            WHERE user_id = ? AND id = ?
        """
        return self.execute_update(query, (name, rest_time, work_time, reps, sets, user_id, workout_id))
    
    def delete(self, workout_id: int, user_id: int) -> bool:
        """Удаление тренировки пользователя"""
        query = f"""
            DELETE FROM {self.table_name()} 
            WHERE id = ? and user_id = ? 
        """
        affected_rows = self.execute_delete(query, (workout_id, user_id))
        return affected_rows > 0
    
    def get_user_workouts(self, user_id: int) -> List[dict]:
        """Получение тренировок пользователя"""
        query = f"""
            SELECT * FROM {self.table_name()} 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """
        return self.execute_select(query, (user_id,))    
   
    def get_by_id(self, workout_id: int, user_id: int = None) -> Optional[dict]:
        """Получение тренировки по ID с проверкой владельца"""
        if user_id:
            query = f"SELECT * FROM {self.table_name()} WHERE id = ? AND user_id = ?"
            results = self.execute_select(query, (workout_id, user_id))
        else:
            query = f"SELECT * FROM {self.table_name()} WHERE id = ?"
            results = self.execute_select(query, (workout_id,))
        return results[0] if results else None
    
    def get_user_stats(self, user_id: int) -> List[dict]:
        """Получение статистики пользователя (количество тренировок, общее время тренировок)"""
        query = f"""
            SELECT 
                COUNT(*) as total_workouts,
                SUM(work_time) as total_duration
            FROM {self.table_name()} 
            WHERE user_id = ?
        """
        return self.execute_select(query, (user_id,))
