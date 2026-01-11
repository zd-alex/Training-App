# src/views/auth/login_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt

class LoginDialog(QDialog):
    """Диалог входа"""
    
    def __init__(self, auth_controller, parent=None):
        super().__init__(parent)
        self.auth_controller = auth_controller
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(350, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("Вход в Tabata Timer")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Поле для email
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@email.com")
        layout.addWidget(self.email_input)
        
        # Поле для пароля
        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Запомнить меня
        self.remember_checkbox = QCheckBox("Запомнить меня")
        layout.addWidget(self.remember_checkbox)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Ссылка на регистрацию
        footer_layout = QHBoxLayout()
        footer_layout.addWidget(QLabel("Нет аккаунта?"))
        self.register_link = QPushButton("Зарегистрироваться")
        self.register_link.setStyleSheet("border: none; color: blue; text-decoration: underline;")
        self.register_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_link.clicked.connect(self.show_register)
        footer_layout.addWidget(self.register_link)
        footer_layout.addStretch()
        
        layout.addLayout(footer_layout)
        self.setLayout(layout)
    
    def handle_login(self):
        """Обработка входа"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        remember_me = self.remember_checkbox.isChecked()
        
        result = self.auth_controller.login(email, password, remember_me)
        
        if result["success"]:
            QMessageBox.information(self, "Успешно", result["message"])
            self.accept()  # Закрываем диалог с успехом
        else:
            QMessageBox.warning(self, "Ошибка", result["message"])
    
    def show_register(self):
        """Показать форму регистрации"""
        from .register_dialog import RegisterDialog
        register_dialog = RegisterDialog(self.auth_controller, self)
        self.reject()  # Закрываем текущее окно
        register_dialog.exec()