# src/controllers/exercise_controller.py
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from models.database import Database
from models.repositories.exercise_repository import ExerciseRepository
# from models.repositories.workout_repository import WorkoutRepository
from models.repositories.user_repository import UserRepository


class ExerciseController:
    """Контроллер для управления тренировками"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.exercise_repo = ExerciseRepository(self.db)
        # self.workout_repo = WorkoutRepository(self.db)
        # self.history_repo = exerciseHistoryRepository(self.db)
        self.user_repo = UserRepository(self.db)
    
    # ========== МЕТОДЫ ДЛЯ ТРЕНИРОВОК ==========
    
    def create_exercise(self, user_id: int, name: str, description: str, prepare_time: int = 0,
                      rest_time: int = 10, reps: int = 8, sets: int = 1) -> Dict[str, Any]:
        """Создание нового упражнения"""
        # Валидация входных данных
        validation_result = self._validate_exercise_params(rest_time, reps, sets)
        
        if not validation_result["success"]:
            return validation_result
        
        try:
            # Создаем упражнение
            exercise_id = self.exercise_repo.create(
                user_id=user_id,
                name=name,
                description=description,
                rest_time=rest_time,
                prepare_time=prepare_time,
                reps=reps,
                sets=sets
            )
            
            # Получаем созданное упражнение
            exercise = self.exercise_repo.get_by_id(exercise_id, user_id)
            
            # # Рассчитываем общее время
            # total_time = self.calculate_total_time(exercise)
            
            return {
                "success": True,
                "exercise_id": exercise_id,
                "exercise": exercise,
                # "total_time": total_time,
                "message": "Тренировка создана успешно"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка создания упражнения: {str(e)}"
            }
    
    def get_user_exercises(self, user_id: int) -> Dict[str, Any]:
        """
        Получение всех упражнений пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict со списком тренировок
        """
        try:
            exercises = self.exercise_repo.get_user_exercises(user_id)
            
            # # Добавляем расчетное время для каждого упражнения
            # for exercise in exercises:
            #     exercise['total_time'] = self.calculate_total_time(exercise)
            #     exercise['total_cycles'] = exercise['cycles'] * exercise['sets']
            
            return {
                "success": True,
                "exercises": exercises,
                "count": len(exercises)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка загрузки упражнений: {str(e)}"
            }
    
    def get_exercise_by_id(self, exercise_id: int, user_id: int = None) -> Dict[str, Any]:
        """
        Получение упражнения по ID
        
        Args:
            exercise_id: ID упражнения
            user_id: ID пользователя (для проверки доступа)
            
        Returns:
            Dict с информацией об упражнении
        """
        try:
            exercise = self.exercise_repo.get_by_id(exercise_id, user_id)
            
            if not exercise:
                return {
                    "success": False,
                    "message": "Упражнение не найдено"
                }
            
            # Добавляем расчетное время
            # exercise['total_time'] = self.calculate_total_time(exercise)
            # exercise['total_cycles'] = exercise['cycles'] * exercise['sets']

            return {
                "success": True,
                "exercise": exercise
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка загрузки упражнения: {str(e)}"
            }
        
    
    
    def update_exercise(self, exercise_id: int, user_id: int, **kwargs) -> Dict[str, Any]:
        """
        Обновление упражнения
        
        Args:
            exercise_id: ID упражнения
            user_id: ID пользователя (для проверки владельца)
            **kwargs: Поля для обновления
            
        Returns:
            Dict с результатом обновления
        """
        try:
            # Проверяем существование и доступ
            exercise = self.exercise_repo.get_by_id(exercise_id, user_id)
            if not exercise:
                return {
                    "success": False,
                    "message": "Упражнение не найдено или нет доступа"
                }
            
            # Валидация параметров, если они есть
            if any(key in kwargs for key in ['rest_time', 'reps', 'sets']):
                validation = self._validate_exercise_params(
                    kwargs.get('rest_time', exercise['rest_time']),
                    kwargs.get('reps', exercise['reps']),
                    kwargs.get('sets', exercise['sets'])
                )
                
                if not validation["success"]:
                    return validation
            
            # Обновляем упражнение
            success = self.exercise_repo.update(exercise_id, user_id, **kwargs)
            
            if success:
                # Получаем обновленное упражнение
                updated_exercise = self.exercise_repo.get_by_id(exercise_id, user_id)
                # updated_exercise['total_time'] = self.calculate_total_time(updated_exercise)
                
                return {
                    "success": True,
                    "exercise": updated_exercise,
                    "message": "Упражнение обновлено успешно"
                }
            else:
                return {
                    "success": False,
                    "message": "Не удалось обновить упражнение"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка обновления упражнения: {str(e)}"
            }
    
    def delete_exercise(self, exercise_id: int, user_id: int) -> Dict[str, Any]:
        """
        Удаление упражнения
        
        Args:
            exercise_id: ID упражнения
            user_id: ID пользователя (для проверки владельца)
            
        Returns:
            Dict с результатом удаления
        """
        try:
            # Проверяем существование и доступ
            exercise = self.exercise_repo.get_by_id(exercise_id, user_id)
            if not exercise:
                return {
                    "success": False,
                    "message": "Упражнение не найдено или нет доступа"
                }
            
            # Удаляем упражнение
            success = self.exercise_repo.delete(exercise_id, user_id)
            
            if success:
                return {
                    "success": True,
                    "message": "Упражнение удалено успешно"
                }
            else:
                return {
                    "success": False,
                    "message": "Не удалось удалить упражнение"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка удаления упражнения: {str(e)}"
            }
    
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    # @staticmethod
    # def calculate_total_time(exercise: Dict) -> int:
    #     """
    #     Расчет общего времени тренировки
        
    #     Args:
    #         exercise: Словарь с данными тренировки
            
    #     Returns:
    #         Общее время в секундах
    #     """
    #     work_time = exercise.get('work_time', 20)
    #     rest_time = exercise.get('rest_time', 10)
    #     cycles = exercise.get('cycles', 8)
    #     sets = exercise.get('sets', 1)
        
    #     # Формула: (время работы + время отдыха) * циклы * сеты - последний отдых
    #     cycle_time = work_time + rest_time
    #     total_cycles = cycles * sets
        
    #     if total_cycles > 0:
    #         return (cycle_time * total_cycles) - rest_time
    #     return 0
    
    @staticmethod
    def _validate_exercise_params(rest_time: int, reps: int, sets: int) -> Dict[str, Any]:
        """
        Валидация параметров тренировки
        
        Returns:
            Dict с результатом валидации
        """
        errors = []
        
        if rest_time < 1:
            errors.append("Время отдыха должно быть положительным")
        elif rest_time > 300:
            errors.append("Время отдыха не должно превышать 5 минут")
        
        if reps < 1:
            errors.append("Количество циклов должно быть положительным")
        elif reps > 100:
            errors.append("Количество циклов не должно превышать 100")
        
        if sets < 1:
            errors.append("Количество сетов должно быть положительным")
        elif sets > 20:
            errors.append("Количество сетов не должно превышать 20")
        
        # # Проверка общего времени (не более 2 часов)
        # total_time = (work_time + rest_time) * cycles * sets
        # if total_time > 7200:  # 2 часа
        #     errors.append("Общее время тренировки не должно превышать 2 часов")
        
        if errors:
            return {
                "success": False,
                "message": ";\n".join(errors)
            }
        
        return {"success": True}
    

        """
        Генерация рекомендаций на основе истории
        
        Args:
            history: История тренировок
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        if not history:
            recommendations.append("Начните свою первую тренировку!")
            return recommendations
        
        # Анализируем частоту тренировок
        if len(history) < 4:
            recommendations.append("Увеличьте частоту тренировок до 3-4 раз в неделю")
        
        # Анализируем время тренировок
        durations = [record['duration'] for record in history]
        avg_duration = sum(durations) / len(durations)
        
        if avg_duration < 300:  # Менее 5 минут
            recommendations.append("Попробуйте увеличить продолжительность тренировок")
        elif avg_duration > 1800:  # Более 30 минут
            recommendations.append("Рассмотрите возможность разделения длинных тренировок")
        
        # Анализируем консистентность
        if len(set([record['exercise_id'] for record in history])) == 1:
            recommendations.append("Добавьте разнообразия в ваши тренировки")
        
        # Положительные моменты
        if len(history) >= 8:
            recommendations.append("Отличная регулярность! Продолжайте в том же духе!")
        
        return recommendations