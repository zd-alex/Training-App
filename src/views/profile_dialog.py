# src/views/profile_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QFormLayout, QTabWidget, QWidget,
    QComboBox, QSpinBox, QCheckBox, QTextEdit,
    QDateEdit, QTimeEdit, QListWidget, QListWidgetItem,
    QStackedWidget, QScrollArea, QFrame, QProgressBar,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog
)

from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime, QDateTime
from PyQt6.QtGui import QFont, QIcon, QPixmap, QIntValidator, QDoubleValidator
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class ProfileDialog(QDialog):
    """Диалог редактирования профиля пользователя"""
    
    profile_updated = pyqtSignal(dict)  # Сигнал при обновлении профиля
    password_changed = pyqtSignal()      # Сигнал при изменении пароля
    
    def __init__(self, auth_controller, workout_controller, user_data: dict, parent=None):
        """
        Инициализация диалога профиля
        
        Args:
            auth_controller: Контроллер аутентификации
            user_data: Данные текущего пользователя
            parent: Родительское окно
        """
        super().__init__(parent)
        self.auth_controller = auth_controller
        self.workout_controller = workout_controller
        self.user_data = user_data.copy()  # Копируем данные
        self.original_user_data = user_data.copy()

        self.current_user_id = self.auth_controller.current_user['id']
        
        self.stats_widgets = {}  # Словарь для хранения виджетов статистики
        self.setup_ui()
        self.load_user_data()
        self.setup_connections()

        self.move(parent.window().frameGeometry().center() - self.rect().center())
        self.load_workout_history()
        self.load_user_stats()
    
    def setup_ui(self):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("Профиль пользователя")
        self.setMinimumSize(650, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # === ЗАГОЛОВОК ===
        header_layout = QHBoxLayout()
       
        main_layout.addLayout(header_layout)
        
        # === ВКЛАДКИ ПРОФИЛЯ ===
        self.tab_widget = QTabWidget()
        
        # Вкладка 1: Основная информация
        self.basic_info_tab = self.create_basic_info_tab()
        self.tab_widget.addTab(self.basic_info_tab, "Основное")        
       
        # Вкладка 2: Статистика
        self.stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "Статистика")
        
        main_layout.addWidget(self.tab_widget)
        
        # === КНОПКИ ===
        self.create_buttons(main_layout)
    
    def create_basic_info_tab(self) -> QWidget:
        """Создание вкладки с основной информацией"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # === ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ ===
        info_group = QGroupBox("Личная информация")
        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        info_layout.setContentsMargins(10, 15, 10, 10)
        
        # Имя пользователя
        info_layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        info_layout.addRow(self.username_input)
        
        # Email
        info_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@email.com")
        info_layout.addRow(self.email_input)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # === СМЕНА ПАРОЛЯ ===
        password_group = QGroupBox("Смена пароля")
        password_layout = QFormLayout()
        password_layout.setSpacing(10)
        # password_layout.setContentsMargins(10, 15, 10, 10)
        
        # Текущий пароль
        password_layout.addWidget(QLabel("Текущий пароль:"))
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addRow(self.current_password_input)
        
        # Новый пароль
        password_layout.addWidget(QLabel("Новый пароль:"))
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Минимум 8 символов")
        password_layout.addRow(self.new_password_input)
        
        # Подтверждение пароля
        password_layout.addWidget(QLabel("Подтвердите пароль:"))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addRow(self.confirm_password_input)
              
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)    
        
        layout.addStretch()
        return widget
    
           
    def create_stats_tab(self) -> QWidget:
        """Создание вкладки статистики"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # === ОБЩАЯ СТАТИСТИКА ===
        general_stats_group = QGroupBox("Общая статистика")
        general_layout = QGridLayout()
        general_layout.setSpacing(10)
        
        # Создаем карточки статистики
        stats_cards = [
            ("Всего тренировок", "0", "#4299e1"),
            ("Общее время", "0 ч", "#48bb78"),
            # ("Дней подряд", "0", "#ed8936"),
            # ("Средняя оценка", "0.0", "#9f7aea"),
            # ("Сожжено калорий", "0", "#f56565"),
            # ("Любимая тренировка", "Нет", "#38b2ac")
        ]
        
        row, col = 0, 0
        for title, value, color in stats_cards:
            card = self.create_stat_card(title, value, color)
            general_layout.addWidget(card, row, col)
            self.stats_widgets[title] = card    # сохраняем ссылку на карточку
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        general_stats_group.setLayout(general_layout)
        scroll_layout.addWidget(general_stats_group)
        
        # # === ДОСТИЖЕНИЯ ===
        # achievements_group = QGroupBox("Достижения")
        # achievements_layout = QVBoxLayout()
        
        # self.achievements_list = QListWidget()
        # achievements = [
        #     "🎯 Первая тренировка",
        #     "🔥 10 тренировок",
        #     "🏆 50 тренировок",
        #     "💯 100 тренировок",
        #     "⚡ Неделя подряд",
        #     "🌟 Месяц подряд",
        #     "🚀 5 различных тренировок",
        #     "💪 10 различных тренировок"
        # ]
        
        # for achievement in achievements:
        #     item = QListWidgetItem(achievement)
        #     self.achievements_list.addItem(item)
        
        # achievements_layout.addWidget(self.achievements_list)
        # achievements_group.setLayout(achievements_layout)
        # scroll_layout.addWidget(achievements_group)
        
        # === ИСТОРИЯ АКТИВНОСТИ ===
        activity_group = QGroupBox("История активности")
        activity_layout = QVBoxLayout()
        
        self.activity_table = self.create_activity_table()
        activity_layout.addWidget(self.activity_table)
        
        activity_group.setLayout(activity_layout)
        scroll_layout.addWidget(activity_group)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        return widget
    
    def create_stat_card(self, title: str, value: str, color: str) -> QWidget:
        """Создание карточки статистики"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setLineWidth(1)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"QLabel {{ color: {color}; font-weight: bold; }}")
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; }")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def create_activity_table(self) -> QWidget:
        """Создание таблицы активности"""
      
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Дата/время", "Наименование", "Подходов", "Всего повторений", "Длительность"])
        # table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Минимальные ширины для каждой колонки (в пикселях)
        min_widths = [100, 150, 50, 110, 100]  # для каждой колонки
    
        header = table.horizontalHeader()
        # Установить минимальные ширины
        for i, min_width in enumerate(min_widths):
            header.setMinimumSectionSize(min_width)
        
        # Установить начальные ширины (равны минимальным или больше)
        for i in range(table.columnCount()):
            table.setColumnWidth(i, min_widths[i])
        
        for i in range(table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)

        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)    
        return table
    
    def create_buttons(self, parent_layout):
        """Создание кнопок управления"""
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(self.cancel_button)
        
        buttons_layout.addStretch()
        
        self.save_button = QPushButton("Сохранить изменения")
        self.save_button.setDefault(True)
        buttons_layout.addWidget(self.save_button)
        
        parent_layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """Настройка соединений сигналов"""
        # Кнопки
        self.save_button.clicked.connect(self.save_profile)
        self.cancel_button.clicked.connect(self.close)        
   
    def load_user_data(self):
        """Загрузка данных пользователя в форму"""
        # Основная информация
        self.username_input.setText(self.user_data.get('username', ''))
        self.email_input.setText(self.user_data.get('email', ''))    
       
    def validate_email(self, email: str) -> bool:
        """Проверка валидности email"""
        if '@' not in email or '.' not in email:
            return False
        return True
    
    def check_password_strength(self, password: str):
        """Проверка сложности пароля"""
        if not password:
            self.password_strength.setValue(0)
            return
        
        score = 0
        
        # Длина пароля
        if len(password) >= 8:
            score += 25
        if len(password) >= 12:
            score += 15
        
        # Наличие цифр
        if any(char.isdigit() for char in password):
            score += 15
        
        # Наличие букв в разных регистрах
        if any(char.islower() for char in password) and any(char.isupper() for char in password):
            score += 20
        
        # Наличие специальных символов
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(char in special_chars for char in password):
            score += 25
        
        self.password_strength.setValue(min(score, 100))
        
        # Цвет индикатора в зависимости от сложности
        if score < 40:
            color = "#f56565"  # Красный
        elif score < 70:
            color = "#ecc94b"  # Желтый
        else:
            color = "#48bb78"  # Зеленый
        
        self.password_strength.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
    
    def get_profile_data(self) -> dict:
        """Получение данных профиля из формы"""
        data = {
            'username': self.username_input.text().strip(),
            'email': self.email_input.text().strip(),
            'password': self.current_password_input.text().strip(),
            'confirm_password': self.confirm_password_input.text().strip(),

            # Метаданные
            'updated_at': datetime.now().isoformat()
        }
        
        # Удаляем пустые строки
        data = {k: v for k, v in data.items() if v or isinstance(v, bool)}
        
        return data
    
    def validate_profile_data(self, data: dict) -> tuple:
        """
        Валидация данных профиля
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Проверка имени пользователя
        username = data.get('username', '').strip()
        if not username:
            return False, "Введите имя пользователя"
        
        if len(username) < 3:
            return False, "Имя пользователя должно содержать минимум 3 символа"
        
        if len(username) > 50:
            return False, "Имя пользователя слишком длинное (макс. 50 символов)"
        
        # Проверка email
        email = data.get('email', '').strip()
        if not email:
            return False, "Введите email"
        
        if not self.validate_email(email):
            return False, "Введите корректный email адрес"
        
        # Проверка имени и фамилии
        first_name = data.get('first_name', '').strip()
        if first_name and len(first_name) > 50:
            return False, "Имя слишком длинное (макс. 50 символов)"

        return True, ""
    
    def save_profile(self) -> dict:
        """Сохранение профиля"""
        # Получаем данные из формы
        profile_data = self.get_profile_data()
        
        # Валидация
        is_valid, error_message = self.validate_profile_data(profile_data)
        if not is_valid:
            QMessageBox.warning(self, "Ошибка валидации", error_message)
            return {"success": False, "message": error_message}            
        
        # Проверяем, изменился ли пароль
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if new_password:
            # Пытаемся изменить пароль
            password_result = self.change_password(current_password, new_password, confirm_password)
            if not password_result["success"]:
                QMessageBox.warning(self, "Ошибка смены пароля", password_result["message"])
                return {"success": False, "message": password_result["message"]}                
        
        try:
            # Обновляем профиль через контроллер аутентификации
            result = self.auth_controller.update_profile(**profile_data)
            
            if result["success"]:
                # Обновляем данные пользователя
                self.user_data.update(profile_data)
                
                # Отправляем сигнал об обновлении профиля
                self.profile_updated.emit(self.user_data)
                
                logger.info(f"Профиль обновлен: {self.user_data['username']}")
                QMessageBox.information(
                    self, 
                    "Успешно", 
                    result.get("message", "Профиль успешно обновлен")
                )
                self.accept()
                return {"success": True, "message": "Профиль успешно обновлен"}  
            else:
                logger.error(f"Ошибка обновления профиля: {result.get('message')}")
                QMessageBox.warning(
                    self, 
                    "Ошибка", 
                    result.get("message", "Не удалось обновить профиль")
                )
                return {"success": False, "message": "Не удалось обновить профиль"} 
                
        except Exception as e:
            logger.error(f"Критическая ошибка при обновлении профиля: {e}")
            QMessageBox.critical(
                self, 
                "Критическая ошибка", 
                f"Произошла ошибка: {str(e)}"
            )
            return {"success": False, "message": "Критическая ошибка при обновлении профиля"} 
    
    def change_password(self, current_password: str, new_password: str, confirm_password: str) -> dict:
        """
        Смена пароля
        
        Returns:
            dict: Результат операции
        """
        if not current_password:
            return {"success": False, "message": "Введите текущий пароль"}
        
        if not new_password:
            return {"success": False, "message": "Введите новый пароль"}
        
        if len(new_password) < 8:
            return {"success": False, "message": "Новый пароль должен содержать минимум 8 символов"}
        
        if new_password != confirm_password:
            return {"success": False, "message": "Пароли не совпадают"}
        
        if new_password == current_password:
            return {"success": False, "message": "Новый пароль не должен совпадать со старым"}
        
        try:
            # Используем метод контроллера для смены пароля
            result = self.auth_controller.change_password(
                current_password=current_password,
                new_password=new_password,
                confirm_password=confirm_password
            )
            
            if result["success"]:
                # Очищаем поля пароля
                self.current_password_input.clear()
                self.new_password_input.clear()
                self.confirm_password_input.clear()
                # self.password_strength.setValue(0)
                
                # Отправляем сигнал об изменении пароля
                self.password_changed.emit()
                
                logger.info("Пароль успешно изменен")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка смены пароля: {e}")
            return {"success": False, "message": f"Ошибка смены пароля: {str(e)}"}
    
    
    def deactivate_account(self):
        """Деактивация аккаунта"""
        reply = QMessageBox.warning(
            self,
            "Деактивация аккаунта",
            "Вы уверены, что хотите деактивировать свой аккаунт?\n\n"
            "При деактивации:\n"
            "• Ваши данные будут скрыты\n"
            "• Вы не сможете входить в систему\n"
            "• Ваши тренировки сохранятся\n"
            "• Вы сможете восстановить аккаунт позже\n\n"
            "Для подтверждения введите ваш пароль:",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Запрашиваем пароль
            password, ok = QInputDialog.getText(
                self,
                "Подтверждение",
                "Введите ваш пароль для деактивации:",
                QLineEdit.EchoMode.Password
            )
            
            if ok and password:
                try:
                    # Деактивируем аккаунт через контроллер
                    result = self.auth_controller.deactivate_account(password)
                    
                    if result["success"]:
                        QMessageBox.information(
                            self,
                            "Аккаунт деактивирован",
                            "Ваш аккаунт успешно деактивирован.\n\n"
                            "Для восстановления обратитесь в поддержку."
                        )
                        self.reject()
                    else:
                        QMessageBox.warning(
                            self,
                            "Ошибка",
                            result.get("message", "Не удалось деактивировать аккаунт")
                        )
                        
                except Exception as e:
                    logger.error(f"Ошибка деактивации аккаунта: {e}")
                    QMessageBox.critical(
                        self,
                        "Ошибка",
                        f"Не удалось деактивировать аккаунт: {str(e)}"
                    )
    
    def delete_account(self):
        """Удаление аккаунта"""
        reply = QMessageBox.critical(
            self,
            "УДАЛЕНИЕ АККАУНТА",
            "<b>ВНИМАНИЕ! Это действие НЕОБРАТИМО!</b>\n\n"
            "При удалении аккаунта:\n"
            "• Все ваши данные будут БЕЗВОЗВРАТНО удалены\n"
            "• Все тренировки будут удалены\n"
            "• Вся статистика будет потеряна\n"
            "• Восстановление будет НЕВОЗМОЖНО\n\n"
            "Для подтверждения введите 'УДАЛИТЬ' в поле ниже:",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Запрашиваем подтверждение
            confirmation, ok = QInputDialog.getText(
                self,
                "Подтверждение удаления",
                "Введите 'УДАЛИТЬ' для подтверждения:"
            )
            
            if ok and confirmation == "УДАЛИТЬ":
                # Запрашиваем пароль
                password, ok = QInputDialog.getText(
                    self,
                    "Подтверждение пароля",
                    "Введите ваш пароль для удаления аккаунта:",
                    QLineEdit.EchoMode.Password
                )
                
                if ok and password:
                    try:
                        # Удаляем аккаунт через контроллер
                        result = self.auth_controller.delete_account(password)
                        
                        if result["success"]:
                            QMessageBox.information(
                                self,
                                "Аккаунт удален",
                                "Ваш аккаунт и все данные успешно удалены."
                            )
                            self.reject()
                        else:
                            QMessageBox.warning(
                                self,
                                "Ошибка",
                                result.get("message", "Не удалось удалить аккаунт")
                            )
                            
                    except Exception as e:
                        logger.error(f"Ошибка удаления аккаунта: {e}")
                        QMessageBox.critical(
                            self,
                            "Ошибка",
                            f"Не удалось удалить аккаунт: {str(e)}"
                        )
    
    def closeEvent(self, event):
        """Обработка закрытия диалога"""
            
        current_data = self.get_profile_data()
        
        # Проверяем, изменились ли данные
        has_changes = False
        for key in current_data:
            if key in self.original_user_data:
                if current_data[key] != self.original_user_data[key]:
                    has_changes = True
                    break
        
        # Проверяем, изменился ли пароль
        if self.new_password_input.text():
            has_changes = True
        
        if has_changes:
            reply = QMessageBox.question(
                self,
                "Несохраненные изменения",
                "У вас есть несохраненные изменения. Сохранить?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                result = self.save_profile()
                if result["success"]:
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()



    def update_stat_card(self, title, new_value):
        """Обновить значение в карточке статистики"""
        if title in self.stats_widgets:
            card = self.stats_widgets[title]
            
            # Находим QLabel с значением (предполагаем, что это второй QLabel в карточке)
            value_label = card.findChild(QLabel, "value_label")
            if value_label:
                value_label.setText(new_value)
            
            # Или если у вас нет установленного objectName, можно искать по индексу:
            # layout = card.layout()
            # if layout and layout.count() > 1:
            #     value_widget = layout.itemAt(1).widget()
            #     if isinstance(value_widget, QLabel):
            #         value_widget.setText(new_value)

    def update_activity_table(self, history):
        """Обновление таблицы активности"""
        self.activity_table.setRowCount(len(history))
        
        for row, record in enumerate(history):
            # Дата
            utc_time_str = record.get('created_at', '')
             # Парсим UTC время
            utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)
            
            # Конвертируем в локальное
            local_dt = utc_dt.astimezone()
            
            # Форматируем для отображения
            display_time = local_dt.strftime("%d.%m.%Y %H:%M")

            date_item = QTableWidgetItem(display_time)
            self.activity_table.setItem(row, 0, date_item)            
           
            # Наименование тренировки
            name_item = QTableWidgetItem(record.get('name', ''))
            self.activity_table.setItem(row, 1, name_item)

            # Число подходов
            sets_item = QTableWidgetItem(str(record.get('sets', '')))
            sets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.activity_table.setItem(row, 2, sets_item)

            # Число повторений
            reps_item = QTableWidgetItem(str(record.get('reps', '')))
            reps_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.activity_table.setItem(row, 3, reps_item)

            # Длительность
            duration = record.get('work_time', 0)
            minutes = duration // 60
            seconds = duration % 60
            duration_item = QTableWidgetItem(f"{minutes}:{seconds:02d}")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.activity_table.setItem(row, 4, duration_item)

    def load_workout_history(self):
        """Загрузка истории тренировок"""
        result = self.workout_controller.get_workout_history(self.current_user_id)
        
        if result["success"]:
            self.update_activity_table(result["history"])
        else:
            self.parent().show_error_message("Ошибка загрузки истории тренировок", result["message"])
        
    def load_user_stats(self):
        """Загрузка статистики"""
        result = self.workout_controller.get_user_stats(self.current_user_id)

        if result["success"]:
            self.update_stat_card("Всего тренировок", str(result["stats"]["Всего тренировок"]))
            res = result["stats"]["Общее время"]
            formatted_time = self.seconds_to_hms(res)
            self.update_stat_card("Общее время", formatted_time)
        else:
            self.parent().show_error_message("Ошибка загрузки статистики тренировок", result["message"])

    @staticmethod
    def seconds_to_hms(seconds: int) -> str:
        """Конвертировать секунды в формат чч:мм:сс"""
        if not seconds:
            return "00:00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

