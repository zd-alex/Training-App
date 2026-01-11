# src/models/repositories/session_repository.py
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from .base_repository import BaseRepository

class SessionRepository(BaseRepository):
    """Репозиторий для управления сессиями"""
    
    def table_name(self):
        return "user_sessions"
    
    def create_session(self, user_id: int, remember_me: bool = False) -> str:
        """Создание новой сессии"""

        # удаляем старые сессии пользователя
        self.execute_update(
            f"DELETE FROM {self.table_name()} WHERE user_id = ? AND (expires_at < ? OR expires_at IS NULL)",
            (user_id, datetime.now())
        )

        # Генерируем токен
        token = secrets.token_urlsafe(32)
        
        now_utc = datetime.now(timezone.utc)
        # Устанавливаем срок действия
        expires_at = None
        if remember_me:
            expires_at = now_utc + timedelta(days=30)
        else:
            expires_at = now_utc + timedelta(minutes=15)
        
        query = f"""
            INSERT INTO {self.table_name()} (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        """
        self.execute_update(query, (user_id, token, expires_at))
        
        return token
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Валидация сессии и получение пользователя"""
        query = f"""
            SELECT u.id, u.username, u.email, u.is_active
            FROM {self.table_name()} s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ? 
            AND u.is_active = 1
            AND (s.expires_at IS NULL OR s.expires_at > CURRENT_TIMESTAMP)
        """
        
        results = self.execute_select(query, (session_token,))
        if results:
            # Обновляем время действия сессии
            # self._update_session(session_token)
            return results[0]
        return None
    
    def delete_session(self, session_token: str):
        """Удаление сессии"""
        query = f"DELETE FROM {self.table_name()} WHERE session_token = ?"
        self.execute_update(query, (session_token,))
    
    def delete_user_sessions(self, user_id: int):
        """Удаление всех сессий пользователя"""
        query = f"DELETE FROM {self.table_name()} WHERE user_id = ?"
        self.execute_update(query, (user_id,))
    
    def _update_session(self, session_token: str):
        """Обновление времени сессии"""
        query = f"""
            UPDATE {self.table_name()} 
            SET expires_at = DATETIME(CURRENT_TIMESTAMP, '+30 days')
            WHERE session_token = ? AND expires_at IS NOT NULL
        """
        self.execute_update(query, (session_token,))