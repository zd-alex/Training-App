# src/views/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QMenuBar, QMenu, QStatusBar, QToolBar,
    QMessageBox, QTabWidget, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QTextEdit, QFrame, QGroupBox, QSizePolicy, QSpacerItem,
    QDialog, QApplication, QStackedWidget, QLineEdit, QSpinBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QSettings, QThread
from PyQt6.QtGui import QAction, QIcon, QFont, QColor, QPixmap

import sys
from datetime import datetime, timezone
from pathlib import Path
import threading
import winsound

# Добавляем путь для импорта config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    # Сигналы
    login_required = pyqtSignal()
    user_changed = pyqtSignal(dict)
    exercise_selected = pyqtSignal(dict)
    exercise_started = pyqtSignal(dict)
    workout_finished = pyqtSignal()
    
    def __init__(self, auth_controller, exercise_controller, workout_controller):
        super().__init__()
        self.config = Config()
        self.auth_controller = auth_controller
        self.exercise_controller = exercise_controller
        self.workout_controller = workout_controller
        self.current_user = None
        self.current_exercise = None
        self.current_workout = None
        self.beep_thread = BeepThread(frequency=1000, duration=200)
        self.last_reps = 0
        self.workout_history = None
        
        # Настройки приложения
        self.settings = QSettings("TrainingApp", "TrainingApp")
        
        # Инициализация UI
        self.setup_ui()
        self.setup_menu()
        # self.setup_toolbar()
        self.setup_connections()
        
        # Восстановление размеров окна
        self.restore_window_state()
        
        # Загрузка данных пользователя, если есть сессия
        if self.auth_controller.is_authenticated():
            self.current_user = self.auth_controller.get_current_user()
            self.update_user_display()
            self.load_user_data()
    
    def setup_ui(self):
        """Настройка основного интерфейса"""
        # Основные настройки окна
        self.setWindowTitle(self.config.WINDOW_TITLE)
        self.setWindowIcon(QIcon(str(self.config.ICON_PATH))) if hasattr(self.config, 'ICON_PATH') else None
        
        # Установка размера из конфига
        width, height = self.config.WINDOW_SIZE
        self.resize(width, height)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # === Панель пользователя ===
        self.user_panel = self.create_user_panel()
        main_layout.addWidget(self.user_panel)
        
        # === Разделитель основного контента ===
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая панель - список тренировок
        self.left_panel = self.create_left_panel()
        splitter.addWidget(self.left_panel)
        
        # Правая панель - детали и управление
        self.right_panel = self.create_right_panel()
        splitter.addWidget(self.right_panel)
        
        # Настройка размеров разделителя
        splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter, 1)  # 1 - коэффициент растяжения
        
        # === Статус бар ===
        self.setup_statusbar()
        
        # Установка стилей
        self.apply_styles()
    
    def create_user_panel(self) -> QWidget:
        """Создание панели пользователя"""
        panel = QWidget()
        panel.setObjectName("userPanel")
        panel.setMaximumHeight(50)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Информация о пользователе
        self.user_info_label = QLabel("Не авторизован")
        self.user_info_label.setObjectName("userInfoLabel")
        
        # Статистика
        self.user_stats_label = QLabel("")
        self.user_stats_label.setObjectName("userStatsLabel")
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("loginButton")
        self.login_button.setMaximumWidth(80)
        
        self.register_button = QPushButton("Регистрация")
        self.register_button.setObjectName("registerButton")
        self.register_button.setMaximumWidth(100)
        
        self.profile_button = QPushButton("Профиль")
        self.profile_button.setObjectName("profileButton")
        self.profile_button.setMaximumWidth(80)
        self.profile_button.setVisible(False)
        
        self.logout_button = QPushButton("Выйти")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.setMaximumWidth(80)
        self.logout_button.setVisible(False)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.profile_button)
        button_layout.addWidget(self.logout_button)
        button_layout.addStretch()
        
        layout.addWidget(self.user_info_label)
        layout.addStretch()
        layout.addWidget(self.user_stats_label)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        return panel
    
    def create_left_panel(self) -> QWidget:
        """Создание левой панели со списком тренировок"""
        panel = QWidget()
        panel.setObjectName("leftPanel")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Заголовок
        title_label = QLabel("Мои упражнения")
        title_label.setObjectName("sectionTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Кнопки управления тренировками
        exercise_buttons_layout = QGridLayout()
        
        self.new_exercise_btn = QPushButton("Добавить")
        self.new_exercise_btn.setObjectName("newExerciseButton")
        self.new_exercise_btn.setIcon(QIcon.fromTheme("document-new"))
        exercise_buttons_layout.addWidget(self.new_exercise_btn, 0, 0)
        
        self.edit_exercise_btn = QPushButton("Изменить")
        self.edit_exercise_btn.setObjectName("editExerciseButton")
        self.edit_exercise_btn.setEnabled(False)
        exercise_buttons_layout.addWidget(self.edit_exercise_btn, 0, 1)
        
        self.delete_exercise_btn = QPushButton("Удалить")
        self.delete_exercise_btn.setObjectName("deleteexerciseButton")
        self.delete_exercise_btn.setEnabled(False)
        exercise_buttons_layout.addWidget(self.delete_exercise_btn, 0, 2)
        
        layout.addLayout(exercise_buttons_layout)
        
        # Список тренировок
        self.exercises_list = QListWidget()
        self.exercises_list.setObjectName("exercisesList")
        self.exercises_list.setAlternatingRowColors(True)
        self.exercises_list.itemSelectionChanged.connect(self.on_exercise_selected)
        self.exercises_list.itemDoubleClicked.connect(self.on_exercise_double_clicked)
        layout.addWidget(self.exercises_list, 1)
        
        # self.exercises_list.setStyleSheet("""
        #     QListWidget {
        #         background-color: black;
        #         color: #333;
        #         font-size: 12px;
        #         border: none;
        #         outline: none;
        #     }
            
        #     QListWidget::item {
        #         padding: 12px 10px;
        #         border-bottom: 1px solid #f0f0f0;
        #     }
            
        #     QListWidget::item:alternate {
        #         background-color: #fafafa;
        #     }
            
        #     QListWidget::item:selected {
        #         background-color: rgba(0, 123, 255, 0.1);
        #         color: #007bff;
        #         border-left: 4px solid #007bff;
        #     }
            
        #     QListWidget::item:hover {
        #         background-color: #f8f9fa;
        #     }
        # """)

        # Фильтр тренировок
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Поиск:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск упражнений...")
        self.search_input.textChanged.connect(self.filter_exercises)
        filter_layout.addWidget(self.search_input)
        
        layout.addLayout(filter_layout)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Создание правой панели с деталями и управлением"""
        panel = QWidget()
        panel.setObjectName("rightPanel")
        self.exercise_title_label = QLabel("Название тренировки")
        self.exercise_title_label.setObjectName("exerciseTitle")
        self.exercise_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exercise_title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        
        # Используем QStackedWidget для переключения между состояниями
        self.stacked_widget = QStackedWidget()
        
        # Виджет 0: Приветствие/Требование входа
        self.welcome_widget = self.create_welcome_widget()
        self.stacked_widget.addWidget(self.welcome_widget)
        
        # Виджет 1: Детали тренировки
        self.details_widget = self.create_details_widget()
        self.stacked_widget.addWidget(self.details_widget)
        
        # Виджет 2: Таймер тренировки
        # self.setup_variables()
        self.timer_widget = self.create_timer_widget()
        self.stacked_widget.addWidget(self.timer_widget)
        
        # Устанавливаем начальный виджет
        self.stacked_widget.setCurrentIndex(0)
        
        layout = QVBoxLayout(panel)
        layout.addWidget(self.exercise_title_label)
        layout.addWidget(self.stacked_widget)
        
        return panel
    


    def create_welcome_widget(self) -> QWidget:
        """Создание виджета приветствия"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Заголовок
        title = QLabel("Добро пожаловать в Training App!")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Описание
        description = QLabel(
            "Для начала работы войдите в систему или зарегистрируйтесь.\n"
            "После входа вы сможете создавать и запускать тренировки"
        )
        description.setObjectName("welcomeDescription")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        login_btn = QPushButton("Войти сейчас")
        login_btn.setObjectName("welcomeLoginButton")
        login_btn.clicked.connect(self.show_login_dialog)
        
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.setObjectName("welcomeRegisterButton")
        register_btn.clicked.connect(self.show_register_dialog)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)
        
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addLayout(button_layout)
        
        return widget
    
    def create_details_widget(self) -> QWidget:
        """Создание виджета деталей тренировки"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Заголовок с названием тренировки
        # self.exercise_title_label = QLabel("Название тренировки")
        # self.exercise_title_label.setObjectName("exerciseTitle")
        # self.exercise_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(self.exercise_title_label)
        
        # Информация о тренировке в виде карточек
        info_group = QGroupBox("Параметры тренировки")
        info_layout = QGridLayout()
        
        # Карточки с параметрами        
        self.rest_time_card = self.create_info_card("Время отдыха", "-", "#f3f99c")
        self.cycles_card = self.create_info_card("Повторений", "-", "#f3f99c")
        self.sets_card = self.create_info_card("Подходов", "-", "#f3f99c")
        self.prepare_time_card = self.create_info_card("Время подготовки", "-", "#f3f99c")
        
        # Размещаем карточки в сетке
        info_layout.addWidget(self.sets_card, 0, 0)
        info_layout.addWidget(self.rest_time_card, 0, 1)
        info_layout.addWidget(self.cycles_card, 1, 0)
        info_layout.addWidget(self.prepare_time_card, 1, 1)
        
        # info_layout.addWidget(self.total_time_card, 2, 0, 1, 2)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Кнопка запуска
        self.start_exercise_btn = QPushButton("Начать тренировку")
        self.start_exercise_btn.setObjectName("startexerciseButton")
        self.start_exercise_btn.setMinimumHeight(50)
        layout.addWidget(self.start_exercise_btn)
        
        # История тренировок
        history_group = QGroupBox("Последние выполнения")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Дата/время", "Наименование", "Подходов", "Всего повторений", "Длительность"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        # self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)


        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        return widget
    
    def create_timer_widget(self) -> QWidget:
        """Создание виджета таймера тренировки"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Таймер
        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setFont(QFont("Arial", 48))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Статус
        self.timer_status_label = QLabel("Готов к запуску")
        self.timer_status_label.setObjectName("timerStatusLabel")
        self.timer_status_label.setFont(QFont("Arial", 16))
        self.timer_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("timerProgressBar")
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setVisible(False)
        
        # Информация о текущем этапе
        self.phase_info_label = QLabel("Этап: Подготовка")
        self.phase_info_label.setObjectName("phaseInfoLabel")
        self.phase_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Кнопки управления таймером
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.start_timer_btn = QPushButton("Старт")
        self.start_timer_btn.setObjectName("startTimerButton")
        self.start_timer_btn.setMinimumWidth(100)
        
        self.execute_btn = QPushButton("Выполнено")
        self.execute_btn.setObjectName("pauseTimerButton")
        self.execute_btn.setMinimumWidth(100)
        self.execute_btn.setEnabled(False)
        
        self.stop_timer_btn = QPushButton("Стоп")
        self.stop_timer_btn.setObjectName("stopTimerButton")
        self.stop_timer_btn.setMinimumWidth(100)
        self.stop_timer_btn.setEnabled(False)
        
        buttons_layout.addWidget(self.start_timer_btn)
        buttons_layout.addWidget(self.execute_btn)
        buttons_layout.addWidget(self.stop_timer_btn)
        
        layout.addWidget(self.timer_label)
        layout.addWidget(self.timer_status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.phase_info_label)
        layout.addLayout(buttons_layout)
        
        return widget
    

    def create_info_card(self, title: str, value: str, color: str) -> QWidget:
        """Создание карточки с информацией"""
        card = QWidget()
        card.setObjectName("infoCard")
        
        # Устанавливаем стили через setStyleSheet
        card.setStyleSheet(f"""
            QWidget#infoCard {{
                border: 2px solid {color};
                border-radius: 8px;
                padding: 10px;
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {color}20,
                    stop: 1 {color}10
                );
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel#cardTitle {{
                color: {color};
                font-weight: bold;
                font-size: 12px;
                padding-bottom: 2px;
            }}
        """)
        
        # sets_input = QSpinBox()
        # sets_input.setRange(1, 20)
        # sets_input.setValue(5)
        # # # self.sets_input.setMinimumWidth(120)
        # sets_input.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)

      

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("""
            QLabel#cardValue {
                color: #2d3748;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        # layout.addWidget(sets_input)
        
        return card
    
    def setup_menu(self):
        """Настройка меню приложения"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("&Файл")
        
        self.login_action = QAction("&Вход", self)
        self.login_action.triggered.connect(self.show_login_dialog)
        file_menu.addAction(self.login_action)
        
        self.register_action = QAction("&Регистрация", self)
        self.register_action.triggered.connect(self.show_register_dialog)
        file_menu.addAction(self.register_action)
        
        file_menu.addSeparator()
        
        self.settings_action = QAction("&Настройки", self)
        self.settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(self.settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Тренировки
        self.exercise_menu = menubar.addMenu("&Тренировки")
        
        self.new_exercise_action = QAction("&Новая тренировка", self)
        self.new_exercise_action.setShortcut("Ctrl+N")
        self.new_exercise_action.triggered.connect(self.create_new_exercise)
        self.exercise_menu.addAction(self.new_exercise_action)
        
        self.edit_exercise_action = QAction("&Изменить тренировку", self)
        self.edit_exercise_action.setShortcut("Ctrl+E")
        self.edit_exercise_action.triggered.connect(self.edit_selected_exercise)
        self.exercise_menu.addAction(self.edit_exercise_action)
        
        # Меню Вид
        view_menu = menubar.addMenu("&Вид")
        
        self.toggle_sidebar_action = QAction("&Скрыть боковую панель", self)
        self.toggle_sidebar_action.setCheckable(True)
        self.toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(self.toggle_sidebar_action)
        
        view_menu.addSeparator()
        
        self.dark_mode_action = QAction("&Темная тема", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.settings.value("dark_mode", False, type=bool))
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)
        
        # Меню Справка
        help_menu = menubar.addMenu("&Справка")
        
        about_action = QAction("&О программе", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        help_action = QAction("&Помощь", self)
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)
    
    def setup_toolbar(self):
        """Настройка панели инструментов"""
        toolbar = QToolBar("Основные инструменты")
        toolbar.setObjectName("mainToolbar")
        self.addToolBar(toolbar)
        
        # Кнопки
        toolbar.addAction(self.new_exercise_action)
        toolbar.addSeparator()
        toolbar.addAction(self.login_action)
        toolbar.addAction(self.register_action)
        toolbar.addSeparator()
        
        # Кнопка статистики
        self.stats_action = QAction("Статистика", self)
        self.stats_action.triggered.connect(self.show_stats_dialog)
        toolbar.addAction(self.stats_action)
    
    def setup_statusbar(self):
        """Настройка статус бара"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Постоянные элементы
        self.status_label = QLabel("Готов")
        self.status_bar.addWidget(self.status_label)
        
        self.status_bar.addPermanentWidget(QLabel("Training App v1.0"))
    
    def setup_connections(self):
        """Настройка соединений сигналов и слотов"""
        # Кнопки пользователя
        self.login_button.clicked.connect(self.show_login_dialog)
        self.register_button.clicked.connect(self.show_register_dialog)
        self.profile_button.clicked.connect(self.show_profile_dialog)
        self.logout_button.clicked.connect(self.handle_logout)
        
        # Кнопки тренировок
        self.new_exercise_btn.clicked.connect(self.create_new_exercise)
        self.edit_exercise_btn.clicked.connect(self.edit_selected_exercise)
        self.delete_exercise_btn.clicked.connect(self.delete_selected_exercise)
        self.start_exercise_btn.clicked.connect(self.start_exercise)
        
        # Таймер
        self.start_timer_btn.clicked.connect(self.start_timer)
        self.execute_btn.clicked.connect(self.execute_action)
        self.stop_timer_btn.clicked.connect(self.handle_stop_workout)
    
    def apply_styles(self):
        """Применение стилей из конфигурации"""
        try:
            # Загрузка стилей из файла, если указан в конфиге
            if hasattr(self.config, 'STYLE_PATH') and self.config.STYLE_PATH.exists():
                with open(self.config.STYLE_PATH, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            else:
                # Использование стилей по умолчанию из конфига
                if hasattr(self.config, 'DEFAULT_STYLE'):
                    self.setStyleSheet(self.config.DEFAULT_STYLE)
        except Exception as e:
            print(f"Ошибка загрузки стилей: {e}")
            # Минимальные стили по умолчанию
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f7fafc;
                }
                QStatusBar {
                    background-color: #edf2f7;
                    color: #4a5568;
                }
            """)
    
    def restore_window_state(self):
        """Восстановление состояния окна из настроек"""
        # Восстановление геометрии
        geometry = self.settings.value("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Восстановление состояния окна
        state = self.settings.value("window_state")
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # Сохранение состояния окна
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        
        # Сохранение текущей темы
        self.settings.setValue("dark_mode", self.dark_mode_action.isChecked())
        
        event.accept()
    
    def update_user_display(self):
        """Обновление отображения информации о пользователе"""
        if self.current_user:
            # Обновляем информацию
            username = self.current_user.get('username', 'Пользователь')
            email = self.current_user.get('email', '')
            
            self.user_info_label.setText(f"👤 {username} ({email})")
            self.user_info_label.setToolTip(f"Зарегистрирован: {self.current_user.get('created_at', '')}")
            
            # Показываем/скрываем кнопки
            self.login_button.setVisible(False)
            self.register_button.setVisible(False)
            self.profile_button.setVisible(True)
            self.logout_button.setVisible(True)
            
            # Обновляем меню
            self.update_menu_for_authenticated_user()
            
            # Переключаем виджет
            self.stacked_widget.setCurrentIndex(1)  # Детали тренировки
            
            # Загружаем статистику
            # self.load_user_stats()
        else:
            self.user_info_label.setText("Не авторизован")
            self.user_stats_label.setText("")
            
            self.login_button.setVisible(True)
            self.register_button.setVisible(True)
            self.profile_button.setVisible(False)
            self.logout_button.setVisible(False)
            
            # Обновляем меню
            self.update_menu_for_anonymous_user()
            
            # Переключаем виджет
            self.stacked_widget.setCurrentIndex(0)  # Приветствие
    
    def update_menu_for_authenticated_user(self):
        """Обновление меню для авторизованного пользователя"""
        self.new_exercise_action.setEnabled(True)
        self.edit_exercise_action.setEnabled(True)
        
        self.login_action.setText("Сменить пользователя")
    
    def update_menu_for_anonymous_user(self):
        """Обновление меню для неавторизованного пользователя"""
        self.new_exercise_action.setEnabled(False)
        self.edit_exercise_action.setEnabled(False)
        
        self.login_action.setText("Вход")
    
    def load_user_data(self):
        """Загрузка данных пользователя"""
        if not self.current_user:
            return
        
        # Загрузка тренировок
        result = self.exercise_controller.get_user_exercises(self.current_user['id'])
        
        if result["success"]:
            self.exercises = result["exercises"]
            self.update_exercises_list()
        else:
            self.show_error_message("Ошибка загрузки тренировок", result["message"])

        self.load_exercise_history()
    
    def update_exercises_list(self):
        """Обновление списка тренировок"""
        self.exercises_list.clear()
        
        for exercise in self.exercises:
            item_text = (
                f"{exercise['name']}\n"
                # f"Работа: {exercise['work_time']}с | Отдых: {exercise['rest_time']}с | "
                # f"Циклов: {exercise['cycles']} | Сетов: {exercise['sets']}"
            )
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, exercise['id'])
            
            # # Разные цвета для разных типов тренировок
            # if exercise.get('is_public'):
            #     item.setBackground(QColor("#e6fffa"))  # Светло-зеленый для публичных
            #     item.setToolTip("Публичная тренировка")
            # else:
            #     item.setBackground(QColor("#fefcbf"))  # Светло-желтый для приватных
            
            self.exercises_list.addItem(item)
    
    def filter_exercises(self):
        """Фильтрация списка тренировок"""
        search_text = self.search_input.text().lower()
        
        for i in range(self.exercises_list.count()):
            item = self.exercises_list.item(i)
            item.setHidden(search_text not in item.text().lower())
    
    def on_exercise_selected(self):
        """Обработка выбора тренировки"""
        selected_items = self.exercises_list.selectedItems()
        
        if selected_items:
            exercise_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.load_exercise_details(exercise_id)
            
            self.edit_exercise_btn.setEnabled(True)
            self.delete_exercise_btn.setEnabled(True)
        else:
            self.edit_exercise_btn.setEnabled(False)
            self.delete_exercise_btn.setEnabled(False)
    
    def on_exercise_double_clicked(self, item):
        """Обработка двойного клика по тренировке"""
        exercise_id = item.data(Qt.ItemDataRole.UserRole)
        self.load_exercise_details(exercise_id)
        self.start_exercise()
    
    def load_exercise_details(self, exercise_id: int):
        """Загрузка деталей выбранной тренировки"""
        result = self.exercise_controller.get_exercise_by_id(
            exercise_id, 
            self.current_user['id']
        )
        
        if result["success"]:
            self.current_exercise = result["exercise"]
            self.update_exercise_details()
            # self.load_exercise_history(exercise_id)
        else:
            self.show_error_message("Ошибка загрузки", result["message"])
    
    def update_exercise_details(self):
        """Обновление отображения деталей тренировки"""
        if not self.current_exercise:
            return
        
        # Заголовок
        self.exercise_title_label.setText(self.current_exercise['name'])
        
        # Обновление карточек
        total_time = self.current_exercise.get('total_time', 0)
        minutes = total_time // 60
        seconds = total_time % 60
        
        self.update_card(self.rest_time_card, "Время отдыха", f"{self.current_exercise['rest_time']} сек")
        self.update_card(self.cycles_card, "Повторений", str(self.current_exercise['reps']))
        self.update_card(self.sets_card, "Подходов", str(self.current_exercise['sets']))
        self.update_card(self.prepare_time_card, "Время подготовки", f"{self.current_exercise['prepare_time']} сек")
        # self.update_card(self.total_time_card, "Общее время", f"{minutes}:{seconds:02d}")
    
    def update_card(self, card: QWidget, title: str, value: str):
        """Обновление карточки"""
        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[0].setText(title)
            labels[1].setText(value)
    
    def load_exercise_history(self):
        """Загрузка истории тренировок"""
        result = self.workout_controller.get_workout_history(
            self.current_user['id'], 
            None, 
            limit=5
        )
        # result = self.exercise_controller.get_exercise_history(
        #     self.current_user['id'], 
        #     exercise_id, 
        #     limit=5
        # )
        
        if result["success"]:
            self.workout_history = result["history"]
            self.update_history_table(result["history"])
    
    def update_history_table(self, history):
        """Обновление таблицы истории"""
        self.history_table.setRowCount(len(history))
        
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
            self.history_table.setItem(row, 0, date_item)            
           
            # Наименование тренировки
            name_item = QTableWidgetItem(record.get('name', ''))
            self.history_table.setItem(row, 1, name_item)

            # Число подходов
            sets_item = QTableWidgetItem(str(record.get('sets', '')))
            sets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_table.setItem(row, 2, sets_item)

            # Число повторений
            reps_item = QTableWidgetItem(str(record.get('reps', '')))
            reps_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_table.setItem(row, 3, reps_item)

            # Длительность
            duration = record.get('work_time', 0)
            minutes = duration // 60
            seconds = duration % 60
            duration_item = QTableWidgetItem(f"{minutes}:{seconds:02d}")
            duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.history_table.setItem(row, 4, duration_item)

    
    def load_user_stats(self):
        """Загрузка статистики пользователя"""
        if not self.current_user:
            return
        
        result = self.exercise_controller.get_user_stats(self.current_user['id'])
        
        if result["success"]:
            stats = result["stats"]["total"]
            total_sessions = stats.get('total_sessions', 0)
            total_time = stats.get('total_time', 0)
            
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            
            self.user_stats_label.setText(
                f"🏃 Тренировок: {total_sessions} | "
                f"⏱️ Время: {hours}ч {minutes}м"
            )
    
    # === Обработчики действий ===
    
    def show_login_dialog(self):
        """Показать диалог входа"""
        from views.login_dialog import LoginDialog
        
        dialog = LoginDialog(self.auth_controller, self)
        if dialog.exec():
            self.current_user = self.auth_controller.get_current_user()
            self.update_user_display()
            self.load_user_data()
            self.user_changed.emit(self.current_user)
    
    def show_register_dialog(self):
        """Показать диалог регистрации"""
        from views.register_dialog import RegisterDialog
        
        dialog = RegisterDialog(self.auth_controller, self)
        if dialog.exec():
            self.current_user = self.auth_controller.get_current_user()
            self.update_user_display()
            self.load_user_data()
            self.user_changed.emit(self.current_user)
    
    def show_profile_dialog(self):
        """Показать диалог профиля"""
        from views.profile_dialog import ProfileDialog
        
        dialog = ProfileDialog(self.auth_controller, self.workout_controller, self.current_user, self)

        if dialog.exec():
            # Обновляем данные пользователя
            self.current_user = self.auth_controller.get_current_user()
            self.update_user_display()
    
    def handle_logout(self):
        """Обработка выхода"""
        reply = QMessageBox.question(
            self, 
            "Подтверждение выхода",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.auth_controller.logout()
            self.current_user = None
            self.current_exercise = None
            self.update_user_display()
            self.exercises_list.clear()
            self.user_changed.emit({})

    def handle_stop_workout(self):
        """Обработка остановки тренировки"""
        reply = QMessageBox.question(
            self, 
            "Остановить тренировку",
            "Вы уверены?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )        
        if reply == QMessageBox.StandardButton.Yes:
            self.stop_timer()
            if self.current_workout['work_time'] == 0:
                result = self.workout_controller.delete_workout(self.current_workout['id'], self.current_user['id'])  
                if result["success"]:
                    self.status_bar.showMessage("Тренировка без выполненных подходов удалена", 3000)
                else:
                    self.show_error_message("Ошибка удаления тренировки", result["message"])

            # self.current_workout = None
            self.workout_finished.emit()
    
    def create_new_exercise(self):
        """Создание новой тренировки"""
        if not self.current_user:
            self.show_login_dialog()
            return
        
        from src.views.exercise_dialog import exerciseDialog
        
        dialog = exerciseDialog(
            exercise_controller=self.exercise_controller,
            user_id=self.current_user['id'],
            parent=self
        )
        
        dialog.exercise_saved.connect(self.on_exercise_saved)
        dialog.exec()
    
    def edit_selected_exercise(self):
        """Редактирование выбранной тренировки"""
        selected_items = self.exercises_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выберите тренировку для редактирования")
            return
        
        exercise_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        result = self.exercise_controller.get_exercise_by_id(
            exercise_id, 
            self.current_user['id']
        )
        
        if result["success"]:
            from src.views.exercise_dialog import exerciseDialog
            
            dialog = exerciseDialog(
                exercise_controller=self.exercise_controller,
                user_id=self.current_user['id'],
                exercise_data=result["exercise"],
                parent=self
            )
            
            dialog.exercise_saved.connect(self.on_exercise_saved)
            dialog.exec()
        else:
            self.show_error_message("Ошибка", result["message"])
    
    def delete_selected_exercise(self):
        """Удаление выбранной тренировки"""
        selected_items = self.exercises_list.selectedItems()
        if not selected_items:
            return
        
        exercise_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        exercise_name = selected_items[0].text().split('\n')[0]
        
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить упражнение '{exercise_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = self.exercise_controller.delete_exercise(
                exercise_id, 
                self.current_user['id']
            )
            
            if result["success"]:
                self.load_user_data()  # Перезагружаем список
                self.status_bar.showMessage("Упражнение удалено", 3000)

            else:
                self.show_error_message("Ошибка удаления", result["message"])
    
       
    def start_exercise(self):
        """Запуск выбранного упражнения"""
        if not self.current_exercise:
            QMessageBox.warning(self, "Внимание", "Выберите упражнение для запуска")
            return
        
        # self.left_panel.setVisible(False)
        # self.resize(500, 300)
        # if self.centralWidget():
        #     content_min_size = self.centralWidget().minimumSizeHint()
        #     print(f"Рекомендуемый размер содержимого: {content_min_size}")
        # self.setMinimumSize(*self.config.WINDOW_MIN_SIZE)
        # Переключаемся на виджет таймера
        
        self.stacked_widget.setCurrentIndex(2)  # Таймер
        self.exercises_list.setEnabled(False)
        
        # Инициализируем таймер
        self.initialize_timer()
        
        # Отправляем сигнал
        self.exercise_started.emit(self.current_exercise)

        # self.create_workout()        
        result = self.workout_controller.create_workout(
            user_id=self.current_user['id'],
            name=self.current_exercise['name'],
            work_time=0,
            rest_time=self.current_exercise['rest_time'],
            reps=self.current_exercise['reps'],
            sets=self.current_exercise['sets']          
        )
        
        if result["success"]:
            self.status_bar.showMessage("Тренировка создана", 3000)
        else:
            self.show_error_message("Ошибка сохранения", result["message"])
        self.current_workout = self.workout_controller.get_current_workout()
    
    def initialize_timer(self):
        """Инициализация таймера"""
        if not self.current_exercise:
            return

        # Инициализируем переменные
        self.total_sets = self.current_exercise['sets']
        self.preparation_time = self.current_exercise['prepare_time']
        self.rest_time = self.current_exercise['rest_time']
        self.current_set = 1
        self.current_time = 10
        self.is_preparation = False
        self.is_resting = False
        self.is_running = False


        # Сброс таймера
        # self.remaining_time = 10
        self.is_running = False
        
        # Обновляем отображение
        self.update_timer_display()
        
        # Настройка кнопок
        self.start_timer_btn.setEnabled(True)
        self.execute_btn.setEnabled(False)
        self.stop_timer_btn.setEnabled(False)

        self.timer_status_label.setText("Готов к запуску")
        self.phase_info_label.setText("Этап: Подготовка")
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
    
    def start_timer(self):
        """Запуск таймера"""
        if not self.is_running:
            self.is_running = True
            self.current_set = 0
            
            # Начинаем с подготовки
            self.is_preparation = True
            self.is_waiting_for_execute = False
            self.is_resting = False
            self.current_time = 10 
            self.current_set += 1
            
            # Создаем таймер
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_timer)
            self.timer.start(1000)  # 1 секунда
            
            # Обновляем кнопки
            self.start_timer_btn.setEnabled(False)
            # self.execute_btn.setEnabled(True)
            self.stop_timer_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
    
    def show_simple_spin_dialog(self, default_value=1):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ввод числа повторений")
        
        layout = QVBoxLayout()
        
        spin_box = QSpinBox()
        spin_box.setRange(1, 1000)
        spin_box.setValue(default_value)
        spin_box.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        spin_box.setFixedHeight(40)


        spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Выравнивание текста по центру

        spin_box.setStyleSheet("""
            QSpinBox {
                font-size: 24px;
                font-weight: bold;
                padding-left: 50px;
                padding-right: 50px;
                border: 3px solid #2196F3;
                border-radius: 5px;
                background-color: #E3F2FD;
                color: #1565C0;
                min-width: 100px;
            }
            
            QSpinBox:focus {
                border-color: #1976D2;
                background-color: #BBDEFB;
            }
            
            /* Левая кнопка */
            QSpinBox::down-button {
                subcontrol-position: left;
                subcontrol-origin: margin;
                width: 45px;
                left: 3px;
                color: white;
                font-size: 28px;
                font-weight: bold;

            }            
            /* Правая кнопка */
            QSpinBox::up-button {
                subcontrol-position: right;
                subcontrol-origin: margin;
                width: 45px;
                right: 3px;
                color: white;
                font-size: 28px;
                font-weight: bold;                           
            }          
        """)
        
        button = QPushButton("Готово")
        button.clicked.connect(dialog.accept)
        
        layout.addWidget(QLabel("Сколько повторений выполнено?"))
        layout.addWidget(spin_box)
        layout.addWidget(button)
        
        dialog.setLayout(layout)
        
        if dialog.exec():   # метод, который показывает диалоговое окно модально
            return spin_box.value() # Выполнится, если диалог закрыт с Accept
        return default_value

    def execute_action(self):
        """Обработка нажатия кнопки 'Выполнено'"""
        if self.is_running:
            new_value = self.last_reps if self.last_reps > 0 else self.current_exercise['reps']           
            reps = self.show_simple_spin_dialog(new_value)

            self.progress_bar.setValue(self.current_set/self.total_sets*100)
            self.save_exercise_result(self.current_set, reps, self.current_time)
            self.last_reps = reps

            if self.current_set + 1 > self.total_sets:
                # Завершаем тренировку
                self.stop_timer()
            elif self.is_waiting_for_execute:
                # Завершаем фазу выполнения и начинаем отдых
                self.current_set += 1
                self.is_waiting_for_execute = False
                self.is_resting = True
                self.current_time = self.rest_time
                
                self.execute_btn.setEnabled(False)
                # self.phase_info_label.setText("Этап: Отдых")                
                # self.update_set_info()
            
            self.execute_btn.setEnabled(False)


   
    # def pause_timer(self):
    #     """Пауза таймера"""
    #     if self.is_running and not self.is_paused:
    #         self.is_paused = True
    #         self.timer.stop()
    #         self.done_btn.setText("Продолжить")
    #         self.timer_status_label.setText("Тренировка на паузе")
    #     elif self.is_paused:
    #         self.is_paused = False
    #         self.timer.start()
    #         self.done_btn.setText("Пауза")
    #         self.timer_status_label.setText("Тренировка выполняется")
    
    def stop_timer(self):
        """Остановка таймера"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            # self.is_paused = False
            
            # Сброс кнопок
            self.start_timer_btn.setEnabled(True)
            self.execute_btn.setEnabled(False)
            self.stop_timer_btn.setEnabled(False)
            # self.execute_btn.setText("Пауза")
            self.exercises_list.setEnabled(True)
            
            self.timer_status_label.setText("Тренировка завершена")
            self.phase_info_label.setText(f"Этап: выполнено {self.current_set} из {self.total_sets}")
            
            # # Сохранение результата
            # self.save_exercise_result(self.current_set, self.current_exercise['cycles'], self.current_time)
            
            # Возврат к деталям тренировки
            QTimer.singleShot(2000, lambda: self.stacked_widget.setCurrentIndex(1))
            
    
    def update_timer(self):
        """Обновление таймера"""
        if not self.is_running:
            return
        self.update_timer_display()

        if self.is_preparation:
            # Фаза подготовки
            if self.current_time > 0:
                self.current_time -= 1
                self.timer_status_label.setText(f"Подготовка...")
                self.phase_info_label.setText(f"Этап: Подготовка к подходу {self.current_set} из {self.total_sets}")
            else:
                # Завершение подготовки, переход к ожиданию выполнения
                self.is_preparation = False
                self.is_waiting_for_execute = True

                self.beep_thread.duration = 600
                self.beep_thread.start()

                self.current_time = 0
                self.execute_btn.setEnabled(True)            
        elif self.is_resting:
            # Фаза отдыха
            if self.current_time > 1:
                if self.preparation_time >= self.current_time:
                    self.beep_thread.duration = 200
                    self.beep_thread.start()
                self.current_time -= 1
                self.timer_status_label.setText(f"Отдых...")
                self.phase_info_label.setText(f"Этап: Подготовка к подходу {self.current_set} из {self.total_sets}")
            else:
                # Завершение отдыха, переход к ожиданию выполнения
                self.beep_thread.duration = 600
                self.beep_thread.start()
               
                self.is_resting = False
                self.is_waiting_for_execute = True
                self.current_time = 0
                self.execute_btn.setEnabled(True)                   
        elif self.is_waiting_for_execute:
            # Время ожидания нажатия кнопки "Выполнено"
            self.current_time += 1  # Увеличиваем время от 0
            self.timer_status_label.setText(f"Сделал - жми 'Выполнено'!")
            self.phase_info_label.setText(f"Этап: тренировка (подход {self.current_set} из {self.total_sets})")            
        # self.update_timer_display()


    def update_timer_display(self):
        """Обновление отображения таймера"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def save_exercise_result(self, current_set, reps, duration):
        """Сохранение результата тренировки"""
        if not self.current_user or not self.current_exercise or not self.current_workout:
            return
        
        result = self.workout_controller.save_workout_result(current_set, reps, duration)
        
        if result["success"]:
            self.status_bar.showMessage("Результат сохранен", 3000)
        else:
            self.show_error_message("Ошибка сохранения", result["message"])

        # Обновляем тренировку
        self.current_workout['work_time'] = self.current_workout['work_time'] + duration
        self.current_workout['reps'] = self.current_workout['reps'] + reps
        self.current_workout['sets'] = self.current_set
        result = self.workout_controller.update_workout(**self.current_workout)

        self.load_exercise_history()
    
    def on_exercise_saved(self, exercise_data):
        """Обработка сохранения тренировки"""
        self.load_user_data()  # Перезагружаем список
        
        if exercise_data:
            # Выбираем сохраненную тренировку в списке
            for i in range(self.exercises_list.count()):
                item = self.exercises_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == exercise_data.get('id'):
                    self.exercises_list.setCurrentItem(item)
                    break
    
    def show_settings_dialog(self):
        """Показать диалог настроек"""
        from views.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            # Применение изменений конфигурации
            self.apply_styles()
    
    def show_stats_dialog(self):
        """Показать диалог статистики"""
        if not self.current_user:
            self.show_login_dialog()
            return
        
        from views.stats_dialog import StatsDialog
        
        dialog = StatsDialog(self.exercise_controller, self.current_user['id'], self)
        dialog.exec()
    
    def show_about_dialog(self):
        """Показать диалог 'О программе'"""
        QMessageBox.about(
            self,
            "О программе Tabata Timer",
            f"""
            <h2>Tabata Timer v1.0</h2>
            <p>Программа для создания и выполнения тренировок по протоколу Tabata.</p>
            
            <h3>Возможности:</h3>
            <ul>
                <li>Создание и редактирование тренировок Tabata</li>
                <li>Учет пользователей и личная статистика</li>
                <li>Публичные тренировки для обмена</li>
                <li>История выполненных тренировок</li>
                <li>Детальная статистика прогресса</li>
            </ul>
            
            <p><b>Конфигурация:</b><br>
            База данных: {self.config.DB_PATH}<br>
            Директория ресурсов: {self.config.RESOURCES_DIR}</p>
            
            <p>© 2024 Tabata Timer. Все права защищены.</p>
            """
        )
    
    def show_help_dialog(self):
        """Показать диалог помощи"""
        QMessageBox.information(
            self,
            "Помощь",
            """
            <h2>Руководство пользователя</h2>
            
            <h3>Основные шаги:</h3>
            <ol>
                <li><b>Регистрация/Вход</b> - создайте аккаунт или войдите в существующий</li>
                <li><b>Создание тренировки</b> - нажмите "Новая тренировка" и задайте параметры</li>
                <li><b>Запуск тренировки</b> - выберите тренировку и нажмите "Начать тренировку"</li>
                <li><b>Просмотр статистики</b> - отслеживайте свой прогресс в разделе "Статистика"</li>
            </ol>
            
            <h3>Горячие клавиши:</h3>
            <ul>
                <li><b>Ctrl+N</b> - новая тренировка</li>
                <li><b>Ctrl+E</b> - изменить тренировку</li>
                <li><b>Ctrl+Q</b> - выход из программы</li>
            </ul>
            
            <h3>Параметры Tabata:</h3>
            <ul>
                <li><b>Время работы</b>: время интенсивного упражнения (20-45 сек)</li>
                <li><b>Время отдыха</b>: время для восстановления (10-30 сек)</li>
                <li><b>Циклы</b>: количество повторений работы и отдыха (6-12)</li>
                <li><b>Сеты</b>: группы циклов с отдыхом между ними (1-3)</li>
            </ul>
            """
        )
    
    def toggle_sidebar(self, checked):
        """Переключение видимости боковой панели"""
        self.left_panel.setVisible(not checked)
        self.toggle_sidebar_action.setText(
            "Показать боковую панель" if checked else "Скрыть боковую панель"
        )
    
    def toggle_dark_mode(self, checked):
        """Переключение темной темы"""
        # Здесь будет логика переключения темной темы
        self.settings.setValue("dark_mode", checked)
        QMessageBox.information(
            self,
            "Перезагрузка",
            "Для применения темы требуется перезапуск приложения"
        )
    
    def show_error_message(self, title: str, message: str):
        """Показать сообщение об ошибке"""
        QMessageBox.warning(self, title, message)
        self.status_bar.showMessage(f"Ошибка: {message}", 5000)
    
    def show_success_message(self, title: str, message: str):
        """Показать сообщение об успехе"""
        QMessageBox.information(self, title, message)
        self.status_bar.showMessage(message, 3000)


class BeepThread(QThread):
    """Поток для воспроизведения звука"""
    # finished = pyqtSignal()
    
    def __init__(self, frequency=1000, duration=500):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def run(self):
        """Основной метод потока"""
        try:
            winsound.Beep(self.frequency, self.duration)
        except Exception as e:
            print(f"Ошибка звука: {e}")
        finally:
            pass
            # self.finished.emit()

# Дополнительные виджеты (должны быть в отдельных файлах, но для краткости здесь)

class QProgressBar(QWidget):
    """Кастомный прогресс-бар"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.maximum = 100
    
    def setValue(self, value):
        self.value = max(0, min(value, self.maximum))
        self.update()
    
    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QPen, QBrush
        painter = QPainter(self)
        
        # Фон
        painter.setBrush(QBrush(QColor("#e2e8f0")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 5, 5)
        
        # Заполнение
        fill_width = int(self.width() * self.value / self.maximum)
        painter.setBrush(QBrush(QColor("#4299e1")))
        painter.drawRoundedRect(0, 0, fill_width, self.height(), 5, 5)


# Экспорт
__all__ = ['MainWindow']