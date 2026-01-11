# src/views/auth/register_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt

class RegisterDialog(QDialog):
    """Диалог регистрации"""
    
    def __init__(self, auth_controller, parent=None):
        super().__init__(parent)
        self.auth_controller = auth_controller
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Регистрация")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("Создание аккаунта")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Поле для имени пользователя
        layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        layout.addWidget(self.username_input)
        
        # Поле для email
        layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@email.com")
        layout.addWidget(self.email_input)
        
        # Поле для пароля
        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Минимум 6 символов")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        # Подтверждение пароля
        layout.addWidget(QLabel("Подтвердите пароль:"))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Повторите пароль")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)
        
        # # Запомнить меня
        # self.remember_checkbox = QCheckBox("Запомнить меня")
        # layout.addWidget(self.remember_checkbox)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.handle_register)
        buttons_layout.addWidget(self.register_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Ссылка на вход
        footer_layout = QHBoxLayout()
        footer_layout.addWidget(QLabel("Уже есть аккаунт?"))
        self.login_link = QPushButton("Войти")
        self.login_link.setStyleSheet("border: none; color: blue; text-decoration: underline;")
        self.login_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_link.clicked.connect(self.show_login)
        footer_layout.addWidget(self.login_link)
        footer_layout.addStretch()
        
        layout.addLayout(footer_layout)
        self.setLayout(layout)
    
    def handle_register(self):
        """Обработка регистрации"""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        # remember_me = self.remember_checkbox.isChecked()
        
        result = self.auth_controller.register(username, email, password, confirm_password)
        
        if result["success"]:
            QMessageBox.information(self, "Успешно", result["message"])
            self.accept()  # Закрываем диалог с успехом
        else:
            QMessageBox.warning(self, "Ошибка", result["message"])
    
    def show_login(self):
        """Показать форму входа"""
        from .login_dialog import LoginDialog
        login_dialog = LoginDialog(self.auth_controller, self)
        self.reject()  # Закрываем текущее окно
        login_dialog.exec()