# src/controllers/workout_controller.py
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from models.database import Database
from models.repositories.workout_repository import WorkoutRepository
from models.repositories.history_repository import WorkoutHistoryRepository
from models.repositories.user_repository import UserRepository


class WorkoutController:
    """Контроллер для управления тренировками"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.workout_repo = WorkoutRepository(self.db)
        self.history_repo = WorkoutHistoryRepository(self.db)
        self.user_repo = UserRepository(self.db)
        self.current_workout = None
    
    # ========== МЕТОДЫ ДЛЯ ТРЕНИРОВОК ==========
    
    def create_workout(self, user_id: int, name: str, work_time: int = 0,
                      rest_time: int = 0, reps: int = 0, sets: int = 1) -> Dict[str, Any]:
        """Создание новой тренировки"""
        # # Валидация входных данных
        # validation_result = self._validate_workout_params(rest_time, cycles, sets)
        
        # if not validation_result["success"]:
        #     return validation_result
        
        try:
            # Создаем тренировку
            workout_id = self.workout_repo.create(
                user_id=user_id,
                name=name,
                work_time=0,
                rest_time=rest_time,
                reps=0,
                sets=0
            )
            
            # Получаем созданную тренировку
            workout = self.workout_repo.get_by_id(workout_id, user_id)
            self.current_workout = workout
            
            # # Рассчитываем общее время
            # total_time = self.calculate_total_time(workout)
            
            return {
                "success": True,
                "workout_id": workout_id,
                "workout": workout,
                # "total_time": total_time,
                "message": "Тренировка создана успешно"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка создания тренировки: {str(e)}"
            }
    
    def get_current_workout(self) -> Optional[Dict[str, Any]]:
        """Получение текущей тренировки"""
        return self.current_workout

    def get_user_exercises(self, user_id: int) -> Dict[str, Any]:
        """
        Получение всех тренировок пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict со списком тренировок
        """
        try:
            workouts = self.workout_repo.get_user_workouts(user_id)
            
            # # Добавляем расчетное время для каждой тренировки
            # for workout in workouts:
            #     workout['total_time'] = self.calculate_total_time(workout)
            #     workout['total_cycles'] = workout['cycles'] * workout['sets']
            
            return {
                "success": True,
                "workouts": workouts,
                "count": len(workouts)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка загрузки тренировок: {str(e)}"
            }
    
    def get_exercise_by_id(self, workout_id: int, user_id: int = None) -> Dict[str, Any]:
        """
        Получение тренировки по ID
        
        Args:
            workout_id: ID тренировки
            user_id: ID пользователя (для проверки доступа)
            
        Returns:
            Dict с информацией о тренировке
        """
        try:
            workout = self.workout_repo.get_by_id(workout_id, user_id)
            
            if not workout:
                return {
                    "success": False,
                    "message": "Тренировка не найдена"
                }
            
            # Добавляем расчетное время
            # workout['total_time'] = self.calculate_total_time(workout)
            # workout['total_cycles'] = workout['cycles'] * workout['sets']

            return {
                "success": True,
                "workout": workout
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка загрузки тренировки: {str(e)}"
            }
    
    def update_workout(self, **kwargs) -> Dict[str, Any]:
        """
        Обновление тренировки
        
        Args:
            workout_id: ID тренировки
            user_id: ID пользователя (для проверки владельца)
            **kwargs: Поля для обновления
            
        Returns:
            Dict с результатом обновления
        """
        try:
            # Проверяем существование и доступ
            workout = self.workout_repo.get_by_id(self.current_workout['id'], self.current_workout['user_id'])
            if not workout:
                return {
                    "success": False,
                    "message": "Тренировка не найдена или нет доступа"
                }
            
            # # Валидация параметров, если они есть
            # if any(key in kwargs for key in ['rest_time', 'cycles', 'sets']):
            #     validation = self._validate_workout_params(
            #         # kwargs.get('work_time', workout['work_time']),
            #         kwargs.get('rest_time', workout['rest_time']),
            #         kwargs.get('cycles', workout['cycles']),
            #         kwargs.get('sets', workout['sets'])
            #     )
                
            #     if not validation["success"]:
            #         return validation
            
            # Обновляем тренировку
            new_data = {
                "name": kwargs.get('name', workout['name']),
                "work_time": kwargs.get('work_time', workout['work_time']),
                "rest_time": kwargs.get('rest_time', workout['rest_time']),
                "reps": kwargs.get('reps', workout['reps']),
                "sets": kwargs.get('sets', workout['sets'])
            }
            success = self.workout_repo.update(self.current_workout['id'], self.current_workout['user_id'], **new_data)
            
            if success:
                # Получаем обновленную тренировку
                updated_workout = self.workout_repo.get_by_id(workout['id'], workout['user_id'])
                # updated_workout['total_time'] = self.calculate_total_time(updated_workout)
                
                return {
                    "success": True,
                    "workout": updated_workout,
                    "message": "Тренировка обновлена успешно"
                }
            else:
                return {
                    "success": False,
                    "message": "Не удалось обновить тренировку"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка обновления тренировки: {str(e)}"
            }
    
    def delete_workout(self, workout_id: int, user_id: int) -> Dict[str, Any]:
        """
        Удаление тренировки
        
        Args:
            workout_id: ID тренировки
            user_id: ID пользователя (для проверки владельца)
            
        Returns:
            Dict с результатом удаления
        """
        try:
            # Проверяем существование и доступ
            workout = self.workout_repo.get_by_id(workout_id, user_id)
            if not workout:
                return {
                    "success": False,
                    "message": "Тренировка не найдена или нет доступа"
                }
            
            # Удаляем тренировку
            success = self.workout_repo.delete(workout_id, user_id)
            
            if success:
                return {
                    "success": True,
                    "message": "Тренировка удалена успешно"
                }
            else:
                return {
                    "success": False,
                    "message": "Не удалось удалить тренировку"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка удаления тренировки: {str(e)}"
            }

    # ========== МЕТОДЫ ДЛЯ ИСТОРИИ ТРЕНИРОВОК ==========
    
    def save_workout_result(self, current_set: int, cycle: int, duration: int) -> Dict[str, Any]:
        """
        Сохранение результата выполненной тренировки
        
        Args:
            workout_id: ID тренировки
            user_id: ID пользователя
            duration: Фактическое время выполнения (сек)
            
        Returns:
            Dict с результатом сохранения
        """
        try:
            # Проверяем существование тренировки
            workout = self.workout_repo.get_by_id(self.current_workout['id'], self.current_workout['user_id'])
            if not workout:
                return {
                    "success": False,
                    "message": "Тренировка не найдена"
                }
            
            # Сохраняем результат
            history_id = self.history_repo.save_result(
                self.current_workout['id'], 
                current_set, 
                cycle,
                duration
            )
            
            return {
                "success": True,
                "history_id": history_id,
                "message": "Результат сохранен"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка сохранения результата: {str(e)}"
            }
    
    def get_workout_history(self, user_id: int, workout_id: int = None, 
                           limit: int = 50) -> Dict[str, Any]:
        """
        Получение истории тренировок
        
        Args:
            user_id: ID пользователя
            workout_id: ID конкретной тренировки (опционально)
            limit: Ограничение количества записей
            
        Returns:
            Dict с историей тренировок
        """
        try:
            if workout_id:
                history = self.history_repo.get_by_workout(user_id, workout_id)
            else:
                history = self.workout_repo.get_user_workouts(user_id)  #, limit)
            
            # # Добавляем информацию о тренировках
            # for record in history:
            #     workout = self.workout_repo.get_by_id(record['id'], user_id)
            #     if workout:
            #         record['workout_name'] = workout['name']
            
            return {
                "success": True,
                "history": history,
                "count": len(history)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка загрузки истории: {str(e)}"
            }
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получение статистики пользователя        
        Args:
            user_id: ID пользователя            
        Returns:
            Dict со статистикой
        """
        try:
            # Общая статистика
            total_stats = self.workout_repo.get_user_stats(user_id)[0]
            
            # # Статистика по периодам
            # weekly_stats = self.history_repo.get_period_stats(user_id, 7)
            # monthly_stats = self.history_repo.get_period_stats(user_id, 30)
            
            # # Самые частые тренировки
            # favorite_workouts = self.history_repo.get_favorite_workouts(user_id, 5)
            
            # # Прогресс
            # progress = self._calculate_progress(user_id)
            
            return {
                "success": True,
                "stats": {
                    "Всего тренировок": total_stats['total_workouts'],
                    "Общее время": total_stats['total_duration'],
                    # "weekly": weekly_stats,
                    # "monthly": monthly_stats,
                    # "favorites": favorite_workouts,
                    # "progress": progress
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка загрузки статистики: {str(e)}"
            }
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    @staticmethod
    def calculate_total_time(workout: Dict) -> int:
        """
        Расчет общего времени тренировки
        
        Args:
            workout: Словарь с данными тренировки
            
        Returns:
            Общее время в секундах
        """
        work_time = workout.get('work_time', 20)
        rest_time = workout.get('rest_time', 10)
        cycles = workout.get('cycles', 8)
        sets = workout.get('sets', 1)
        
        # Формула: (время работы + время отдыха) * циклы * сеты - последний отдых
        cycle_time = work_time + rest_time
        total_cycles = cycles * sets
        
        if total_cycles > 0:
            return (cycle_time * total_cycles) - rest_time
        return 0
    
    @staticmethod
    def _validate_workout_params(rest_time: int, cycles: int, sets: int) -> Dict[str, Any]:
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
        
        if cycles < 1:
            errors.append("Количество циклов должно быть положительным")
        elif cycles > 100:
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
    
    def _calculate_progress(self, user_id: int) -> Dict[str, Any]:
        """
        Расчет прогресса пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict с данными о прогрессе
        """
        try:
            # Получаем историю за последние 30 дней
            history = self.history_repo.get_period_history(user_id, 30)
            
            if not history:
                return {
                    "trend": "stable",
                    "improvement": 0,
                    "consistency": 0
                }
            
            # Группируем по неделям
            weekly_data = {}
            for record in history:
                week_num = datetime.fromisoformat(record['completed_at']).isocalendar()[1]
                if week_num not in weekly_data:
                    weekly_data[week_num] = []
                weekly_data[week_num].append(record['duration'])
            
            # Анализируем тренд
            if len(weekly_data) >= 2:
                weeks = sorted(weekly_data.keys())
                first_week_avg = sum(weekly_data[weeks[0]]) / len(weekly_data[weeks[0]])
                last_week_avg = sum(weekly_data[weeks[-1]]) / len(weekly_data[weeks[-1]])
                
                improvement = ((last_week_avg - first_week_avg) / first_week_avg * 100 
                              if first_week_avg > 0 else 0)
                
                if improvement > 5:
                    trend = "improving"
                elif improvement < -5:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
                improvement = 0
            
            # Рассчитываем консистентность (стандартное отклонение)
            durations = [record['duration'] for record in history]
            if len(durations) > 1:
                avg_duration = sum(durations) / len(durations)
                variance = sum((x - avg_duration) ** 2 for x in durations) / len(durations)
                consistency = max(0, 100 - (variance / avg_duration * 100)) if avg_duration > 0 else 0
            else:
                consistency = 0
            
            return {
                "trend": trend,
                "improvement": round(improvement, 1),
                "consistency": round(consistency, 1),
                "total_sessions": len(history),
                "avg_duration": round(sum(durations) / len(durations) if durations else 0, 1)
            }
            
        except Exception:
            return {
                "trend": "unknown",
                "improvement": 0,
                "consistency": 0,
                "total_sessions": 0,
                "avg_duration": 0
            }
    
    def generate_workout_report(self, user_id: int, start_date: str = None, 
                               end_date: str = None) -> Dict[str, Any]:
        """
        Генерация отчета по тренировкам
        
        Args:
            user_id: ID пользователя
            start_date: Начальная дата (YYYY-MM-DD)
            end_date: Конечная дата (YYYY-MM-DD)
            
        Returns:
            Dict с отчетом
        """
        try:
            # Получаем данные за период
            history = self.history_repo.get_date_range_history(
                user_id, start_date, end_date
            )
            
            if not history:
                return {
                    "success": False,
                    "message": "Нет данных за указанный период"
                }
            
            # Агрегируем данные
            total_duration = sum(record['duration'] for record in history)
            total_sessions = len(history)
            avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
            
            # Самые популярные тренировки
            workout_counts = {}
            for record in history:
                workout_id = record['workout_id']
                workout_counts[workout_id] = workout_counts.get(workout_id, 0) + 1
            
            top_workouts = sorted(workout_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Преобразуем в читаемый формат
            top_workouts_info = []
            for workout_id, count in top_workouts:
                workout = self.workout_repo.get_by_id(workout_id, user_id)
                if workout:
                    top_workouts_info.append({
                        'name': workout['name'],
                        'count': count,
                        'percentage': round(count / total_sessions * 100, 1)
                    })
            
            # Распределение по дням недели
            day_stats = {i: 0 for i in range(7)}  # 0=Понедельник, 6=Воскресенье
            for record in history:
                day_of_week = datetime.fromisoformat(record['completed_at']).weekday()
                day_stats[day_of_week] += 1
            
            return {
                "success": True,
                "report": {
                    "period": {
                        "start": start_date or "начало",
                        "end": end_date or "сегодня"
                    },
                    "summary": {
                        "total_sessions": total_sessions,
                        "total_duration": total_duration,
                        "avg_duration": round(avg_duration, 1),
                        "avg_per_week": round(total_sessions / 4.33, 1)  # Приблизительно
                    },
                    "top_workouts": top_workouts_info,
                    "day_distribution": day_stats,
                    "recommendations": self._generate_recommendations(history)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка генерации отчета: {str(e)}"
            }
    
    @staticmethod
    def _generate_recommendations(history: List[Dict]) -> List[str]:
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
        if len(set([record['workout_id'] for record in history])) == 1:
            recommendations.append("Добавьте разнообразия в ваши тренировки")
        
        # Положительные моменты
        if len(history) >= 8:
            recommendations.append("Отличная регулярность! Продолжайте в том же духе!")
        
        return recommendations