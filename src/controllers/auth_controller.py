# src/controllers/auth_controller.py
from typing import Optional, Dict, Any
from models.database import Database
from models.repositories.user_repository import UserRepository
from models.repositories.session_repository import SessionRepository

class AuthController:
    """Контроллер для управления аутентификацией и пользователями"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database()
        self.user_repo = UserRepository(self.db)
        self.current_user = None
        self.session_token = None
    
    def register(self, username: str, email: str, password: str, confirm_password: str) -> Dict[str, Any]:
        """Регистрация нового пользователя"""
        # Валидация
        if not username or not email or not password:
            return {"success": False, "message": "Все поля обязательны"}
        
        # if len(password) < 6:
        #     return {"success": False, "message": "Пароль должен содержать минимум 6 символов"}
        
        if password != confirm_password:
            return {"success": False, "message": "Пароли не совпадают"}
        
        # if '@' not in email:
        #     return {"success": False, "message": "Некорректный email"}
        
        try:
            # Создаем пользователя
            user = self.user_repo.create_user(username, email, password)
            
            # Автоматически логиним
            return self.login(email, password)
            
        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {"success": False, "message": f"Ошибка регистрации: {str(e)}"}
    
    def login(self, email: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """Вход пользователя"""
        user = self.user_repo.authenticate(email, password)
        
        if user:
            # Создаем сессию
            session_token = self.user_repo.create_session(user['id'], remember_me)
            
            self.current_user = user
            self.session_token = session_token
            
            return {
                "success": True,
                "user": user,
                "session_token": session_token,
                "message": "Вход выполнен успешно"
            }
        else:
            return {
                "success": False,
                "message": "Неверный email или пароль"
            }
    
    def logout(self) -> Dict[str, Any]:
        """Выход пользователя"""
        if self.session_token:
            session_repo = SessionRepository(self.db)
            session_repo.delete_session(self.session_token)
        
        self.current_user = None
        self.session_token = None
        
        return {"success": True, "message": "Выход выполнен"}
    
    def check_session(self, session_token: str) -> bool:
        """Проверка сессии"""
        user = self.user_repo.validate_session(session_token)
        if user:
            self.current_user = user
            self.session_token = session_token
            return True
        return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Получение текущего пользователя"""
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """Проверка аутентификации"""
        return self.current_user is not None
    
    def update_profile(self, **kwargs) -> Dict[str, Any]:
        """Обновление профиля пользователя"""
        if not self.is_authenticated():
            return {"success": False, "message": "Пользователь не аутентифицирован"}
        
        try:
            success = self.user_repo.update_profile(self.current_user['id'], **kwargs)
            if success:
                # Обновляем данные текущего пользователя
                updated_user = self.user_repo.get_by_id(self.current_user['id'])
                self.current_user.update(updated_user)
                return {"success": True, "message": "Профиль обновлен"}
            else:
                return {"success": False, "message": "Нечего обновлять"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка обновления: {str(e)}"}
    
    def change_password(self, current_password: str, new_password: str, confirm_password: str) -> Dict[str, Any]:
        """Смена пароля"""
        if not self.is_authenticated():
            return {"success": False, "message": "Пользователь не аутентифицирован"}
        
        if new_password != confirm_password:
            return {"success": False, "message": "Новые пароли не совпадают"}
        
        if len(new_password) < 6:
            return {"success": False, "message": "Пароль должен содержать минимум 6 символов"}
        
        # Проверяем текущий пароль
        user_with_password = self.user_repo.get_by_email(self.current_user['email'])
        if not UserRepository._verify_password(current_password, user_with_password['password_hash']):
            return {"success": False, "message": "Текущий пароль неверен"}
        
        try:
            self.user_repo.update_password(self.current_user['id'], new_password)
            return {"success": True, "message": "Пароль успешно изменен"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка смены пароля: {str(e)}"}
        
    def create_session(self, user_id: int, remember_me: bool = False) -> str:
        """Создание сессии для пользователя"""
        from models.repositories.session_repository import SessionRepository
        session_repo = SessionRepository(self.db)
        return session_repo.create_session(user_id, remember_me)
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Валидация сессии"""
        from models.repositories.session_repository import SessionRepository
        session_repo = SessionRepository(self.db)
        return session_repo.validate_session(session_token)