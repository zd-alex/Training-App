# src/models/repositories/user_repository.py
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
from .base_repository import BaseRepository

class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями"""
    
    def table_name(self):
        return "users"
    
    def create_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Создание нового пользователя"""
        # Проверяем, существует ли пользователь
        if self.get_by_email(email):
            raise ValueError("Пользователь с таким email уже существует")
        
        if self.get_by_username(username):
            raise ValueError("Пользователь с таким именем уже существует")
        
        # Хешируем пароль
        password_hash = self._hash_password(password)
        
        query = f"""
            INSERT INTO {self.table_name()} (username, email, password_hash)
            VALUES (?, ?, ?)
        """
        
        user_id = self.execute_update(query, (username, email, password_hash))
        
        # Возвращаем созданного пользователя
        return self.get_by_id(user_id)
    
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение пользователя по ID (без пароля)"""
        query = """
            SELECT id, username, email, created_at, is_active, last_login
            FROM users 
            WHERE id = ?
        """
        results = self.execute_select(query, (user_id,))
        return results[0] if results else None
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по email (с паролем для аутентификации)"""
        query = "SELECT * FROM users WHERE email = ?"
        results = self.execute_select(query, (email,))
        return results[0] if results else None
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по имени пользователя"""
        query = """
            SELECT id, username, email, created_at, is_active
            FROM users 
            WHERE username = ?
        """
        results = self.execute_select(query, (username,))
        return results[0] if results else None
    
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Аутентификация пользователя"""
        user = self.get_by_email(email)
        if not user:
            return None
        
        # Проверяем пароль
        if self._verify_password(password, user['password_hash']) and user['is_active']:
            # Обновляем время последнего входа
            self.update_last_login(user['id'])
            
            # Возвращаем пользователя без пароля
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at'],
                'is_active': user['is_active']
            }
        return None
    
    def update_last_login(self, user_id: int):
        """Обновление времени последнего входа"""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        self.execute_update(query, (user_id,))
    
    def update_password(self, user_id: int, new_password: str):
        """Обновление пароля"""
        password_hash = self._hash_password(new_password)
        query = "UPDATE users SET password_hash = ? WHERE id = ?"
        self.execute_update(query, (password_hash, user_id))
    
    def update_profile(self, user_id: int, **kwargs) -> bool:
        """Обновление профиля пользователя"""
        allowed_fields = ['username', 'email']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(user_id)
        
        query = f"UPDATE users SET {set_clause} WHERE id = ?"
        self.execute_update(query, tuple(values))
        return True
    
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
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Хеширование пароля"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """Проверка пароля"""
        return UserRepository._hash_password(password) == password_hash