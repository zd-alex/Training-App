# src/controllers/main_controller.py
import sys
import os
import json
from pathlib import Path
from models.database import Database
from controllers.auth_controller import AuthController
from controllers.exercise_controller import ExerciseController
from controllers.workout_controller import WorkoutController
from views.main_window import MainWindow
from config import config, setup_logging, get_logger

setup_logging(config)
# Получаем логгер для текущего модуля
logger = get_logger(__name__)

class MainController:
    """Основной контроллер приложения"""
    
    def __init__(self):
        self.config = config

        # Инициализация базы данных
        self.db = Database(config.DB_PATH)
        
        # Контроллеры
        self.auth_controller = AuthController(self.db)
        self.exercise_controller = ExerciseController(self.db)
        self.workout_controller = WorkoutController(self.db)
        
        # Загрузка сохраненной сессии
        self.load_session()
        
        # Главное окно
        self.view = MainWindow(self.auth_controller, self.exercise_controller, self.workout_controller)
        self.view.login_required.connect(self.handle_login_required)
        self.view.user_changed.connect(self.handle_user_changed)
        
        # Обновляем интерфейс
        if self.auth_controller.is_authenticated():
            self.view.current_user = self.auth_controller.get_current_user()
            self.view.update_user_display()
    
    def run(self):
        """Запуск приложения"""
        self.view.show()
    
    def load_session(self):
        """Загрузка сохраненной сессии"""
        session_file = Path(__file__).parent.parent.parent / "data" / "session.json"
        
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    session_token = session_data.get('session_token')
                    
                    if session_token and self.auth_controller.check_session(session_token):
                        print("Сессия восстановлена")
            except Exception as e:
                print(f"Ошибка загрузки сессии: {e}")
    
    def save_session(self):
        """Сохранение сессии"""
        if self.auth_controller.session_token:
            session_file = Path(__file__).parent.parent.parent / "data" / "session.json"
            session_file.parent.mkdir(exist_ok=True)
            
            session_data = {
                'session_token': self.auth_controller.session_token
            }
            
            try:
                with open(session_file, 'w') as f:
                    json.dump(session_data, f)
            except Exception as e:
                print(f"Ошибка сохранения сессии: {e}")
    
    def handle_login_required(self):
        """Обработка требования входа"""
        self.view.show_login()
    
    def handle_user_changed(self, user_data):
        """Обработка смены пользователя"""
        if user_data:
            self.save_session()