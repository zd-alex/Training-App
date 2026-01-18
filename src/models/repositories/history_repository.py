# src/models/repositories/workout_repository.py
from typing import List, Optional
from .base_repository import BaseRepository

class WorkoutHistoryRepository(BaseRepository):
    """Репозиторий для истории тренировок"""
    
    def table_name(self):
        return "history"
    
    def save_result(self, workout_id: int, set_number: int, reps: int, duration: int) -> int:
        """Создание новой тренировки для пользователя"""
        query = f"""
            INSERT INTO {self.table_name()} (workout_id, set_number, reps, duration)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_insert(query, (workout_id, set_number, reps, duration ))
    
    # def get_user_workouts(self, user_id: int, limit: int= 5) -> List[dict]:
    #     """Получение тренировок пользователя"""
    #     query = f"""
    #         SELECT * FROM {self.table_name()} 
    #         WHERE user_id = ? 
    #         ORDER BY created_at DESC
    #     """
    #     return self.execute_select(query, (user_id, ))  

    def get_data_by_workout_id(self, workout_id: int) -> Optional[dict]:
        """Получение данных тренировки по ID"""
        query = f"SELECT * FROM {self.table_name()} WHERE workout_id = ?"
        results = self.execute_select(query, (workout_id, ))
        return results