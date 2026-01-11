# src/views/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMenuBar, QMenu, QStatusBar,
    QMessageBox, QTabWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from config import Config

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    login_required = pyqtSignal()
    user_changed = pyqtSignal(dict)  # Сигнал при смене пользователя
    
    def __init__(self, auth_controller, workout_controller):
        super().__init__()
        self.auth_controller = auth_controller
        self.workout_controller = workout_controller
        self.current_user = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Tabata Timer")
        self.setGeometry(100, 100, 800, 600)
        
        # Меню
        self.setup_menu()
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Панель пользователя
        self.user_panel = QHBoxLayout()
        self.user_label = QLabel("Не авторизован")
        self.user_label.setStyleSheet("font-weight: bold;")
        
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.show_login)
        
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.handle_logout)
        self.logout_button.setVisible(False)
        
        self.user_panel.addWidget(self.user_label)
        self.user_panel.addStretch()
        self.user_panel.addWidget(self.login_button)
        self.user_panel.addWidget(self.logout_button)
        
        main_layout.addLayout(self.user_panel)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        
        # Вкладка с моими тренировками
        self.my_workouts_widget = QWidget()
        self.setup_my_workouts_tab()
        self.tab_widget.addTab(self.my_workouts_widget, "Мои тренировки")
        
        # # Вкладка с публичными тренировками
        # self.public_workouts_widget = QWidget()
        # self.setup_public_workouts_tab()
        # self.tab_widget.addTab(self.public_workouts_widget, "Публичные тренировки")
        
        main_layout.addWidget(self.tab_widget)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")
    
    def setup_menu(self):
        """Настройка меню"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        
        login_action = QAction("Вход", self)
        login_action.triggered.connect(self.show_login)
        file_menu.addAction(login_action)
        
        register_action = QAction("Регистрация", self)
        register_action.triggered.connect(self.show_register)
        file_menu.addAction(register_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Тренировки (только для авторизованных)
        self.workout_menu = menubar.addMenu("Тренировки")
        self.setup_workout_menu()
    
    def setup_workout_menu(self):
        """Настройка меню тренировок"""
        self.workout_menu.clear()
        
        if self.current_user:
            new_workout_action = QAction("Новая тренировка", self)
            new_workout_action.triggered.connect(self.create_new_workout)
            self.workout_menu.addAction(new_workout_action)
            
        #     import_workout_action = QAction("Импортировать", self)
        #     import_workout_action.triggered.connect(self.import_workout)
        #     self.workout_menu.addAction(import_workout_action)
            
            self.workout_menu.addSeparator()
            
            stats_action = QAction("Статистика", self)
            # stats_action.triggered.connect(self.show_stats)
            self.workout_menu.addAction(stats_action)
    
    def setup_my_workouts_tab(self):
        """Настройка вкладки с моими тренировками"""
        layout = QVBoxLayout(self.my_workouts_widget)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.new_workout_btn = QPushButton("Новая тренировка")
        self.new_workout_btn.clicked.connect(self.create_new_workout)
        buttons_layout.addWidget(self.new_workout_btn)
        
        self.edit_workout_btn = QPushButton("Редактировать")
        # self.edit_workout_btn.clicked.connect(self.edit_workout)
        buttons_layout.addWidget(self.edit_workout_btn)
        
        self.delete_workout_btn = QPushButton("Удалить")
        # self.delete_workout_btn.clicked.connect(self.delete_workout)
        buttons_layout.addWidget(self.delete_workout_btn)
        
        layout.addLayout(buttons_layout)
        
        # Список тренировок
        self.my_workouts_list = QListWidget()
        # self.my_workouts_list.itemDoubleClicked.connect(self.start_workout)
        layout.addWidget(self.my_workouts_list)
    
    # def setup_public_workouts_tab(self):
    #     """Настройка вкладки с публичными тренировками"""
    #     layout = QVBoxLayout(self.public_workouts_widget)
        
    #     # Список публичных тренировок
    #     self.public_workouts_list = QListWidget()
    #     self.public_workouts_list.itemDoubleClicked.connect(self.import_public_workout)
    #     layout.addWidget(self.public_workouts_list)
    
    def update_user_display(self):
        """Обновление отображения информации о пользователе"""
        if self.current_user:
            self.user_label.setText(f"Пользователь: {self.current_user['username']}")
            self.login_button.setVisible(False)
            self.logout_button.setVisible(True)
            
            # Обновляем меню
            self.setup_workout_menu()
            
            # Загружаем тренировки пользователя
            self.load_user_workouts()
            
        else:
            self.user_label.setText("Не авторизован")
            self.login_button.setVisible(True)
            self.logout_button.setVisible(False)
            self.my_workouts_list.clear()
            self.setup_workout_menu()
    
    def show_login(self):
        """Показать диалог входа"""
        from views.login_dialog import LoginDialog
        dialog = LoginDialog(self.auth_controller, self)
        if dialog.exec():
            self.current_user = self.auth_controller.get_current_user()
            self.update_user_display()
            self.user_changed.emit(self.current_user)
    
    def show_register(self):
        """Показать диалог регистрации"""
        from views.register_dialog import RegisterDialog
        dialog = RegisterDialog(self.auth_controller, self)
        if dialog.exec():
            self.current_user = self.auth_controller.get_current_user()
            self.update_user_display()
            self.user_changed.emit(self.current_user)
    
    def handle_logout(self):
        """Обработка выхода"""
        reply = QMessageBox.question(self, 'Подтверждение',
            'Вы уверены, что хотите выйти?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.auth_controller.logout()
            self.current_user = None
            self.update_user_display()
            self.user_changed.emit({})
    
    def load_user_workouts(self):
        """Загрузка тренировок пользователя"""
        if not self.current_user:
            return
        
        workouts = self.workout_controller.get_user_workouts(self.current_user['id'])
        self.my_workouts_list.clear()
        
        for workout in workouts['workouts']:
            item_text = f"{workout['name']} - {workout['work_time']}/{workout['rest_time']} сек, {workout['cycles']} циклов"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, workout['id'])
            self.my_workouts_list.addItem(item)

    def create_new_workout(self):
        """Создание новой тренировки"""
        if not self.current_user:
            QMessageBox.warning(self, "Ошибка", "Для создания тренировки необходимо войти в систему")
            return
        self.workout_controller.create_workout(self.current_user['id'], 'test') 

        # from views.workout_dialog import WorkoutDialog
        # dialog = WorkoutDialog(self.workout_controller, self.current_user['id'], self)
        # if dialog.exec():
        #     self.load_user_workouts()
