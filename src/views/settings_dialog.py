# src/views/settings_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QPushButton, QCheckBox, QSpinBox, QDoubleSpinBox,
    QComboBox, QLineEdit, QGroupBox, QFormLayout, QListWidget,
    QListWidgetItem, QMessageBox, QFileDialog, QGridLayout,
    QSlider, QProgressBar, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QTimer
from PyQt6.QtGui import QFont, QIcon, QIntValidator, QDoubleValidator
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    
    settings_changed = pyqtSignal(dict)  # Сигнал при изменении настроек
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.settings = QSettings(config.ORGANIZATION, config.APP_NAME)
        self.original_settings = self.load_settings()
        
        self.setup_ui()
        self.load_current_settings()
        self.setup_connections()
    
    def setup_ui(self):
        """Настройка интерфейса диалога"""
        self.setWindowTitle("Настройки")
        self.setMinimumSize(700, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Вкладки настроек
        self.tab_widget = QTabWidget()
        
        # Основные настройки
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "Основные")
        
        # Настройки тренировок
        self.workout_tab = self.create_workout_tab()
        self.tab_widget.addTab(self.workout_tab, "Тренировки")
        
        # Настройки таймера
        self.timer_tab = self.create_timer_tab()
        self.tab_widget.addTab(self.timer_tab, "Таймер")
        
        # Настройки внешнего вида
        self.appearance_tab = self.create_appearance_tab()
        self.tab_widget.addTab(self.appearance_tab, "Внешний вид")
        
        # Расширенные настройки
        self.advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "Расширенные")
        
        main_layout.addWidget(self.tab_widget)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Сброс")
        self.reset_button.setToolTip("Сбросить настройки к значениям по умолчанию")
        buttons_layout.addWidget(self.reset_button)
        
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.setDefault(True)
        buttons_layout.addWidget(self.save_button)
        
        self.apply_button = QPushButton("Применить")
        buttons_layout.addWidget(self.apply_button)
        
        main_layout.addLayout(buttons_layout)
    
    def create_general_tab(self) -> QWidget:
        """Создание вкладки основных настроек"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Группа: Общие настройки
        general_group = QGroupBox("Общие настройки")
        general_layout = QFormLayout()
        general_layout.setSpacing(10)
        
        # Язык интерфейса
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский", "English", "Deutsch", "Français"])
        general_layout.addRow("Язык:", self.language_combo)
        
        # Тема приложения
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Авто", "Светлая", "Темная"])
        general_layout.addRow("Тема:", self.theme_combo)
        
        # Запуск при старте системы
        self.startup_checkbox = QCheckBox("Запускать при старте системы")
        general_layout.addRow(self.startup_checkbox)
        
        # Сворачивать в трей
        self.minimize_to_tray = QCheckBox("Сворачивать в системный трей")
        general_layout.addRow(self.minimize_to_tray)
        
        # Проверять обновления
        self.check_updates = QCheckBox("Автоматически проверять обновления")
        general_layout.addRow(self.check_updates)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Группа: Уведомления
        notifications_group = QGroupBox("Уведомления")
        notifications_layout = QVBoxLayout()
        
        self.enable_notifications = QCheckBox("Включить уведомления")
        notifications_layout.addWidget(self.enable_notifications)
        
        # Типы уведомлений
        self.sound_notifications = QCheckBox("Звуковые уведомления")
        self.sound_notifications.setEnabled(False)
        notifications_layout.addWidget(self.sound_notifications)
        
        self.desktop_notifications = QCheckBox("Всплывающие уведомления")
        self.desktop_notifications.setEnabled(False)
        notifications_layout.addWidget(self.desktop_notifications)
        
        notifications_group.setLayout(notifications_layout)
        layout.addWidget(notifications_group)
        
        layout.addStretch()
        return widget
    
    def create_workout_tab(self) -> QWidget:
        """Создание вкладки настроек тренировок"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Группа: Параметры по умолчанию
        defaults_group = QGroupBox("Параметры тренировок по умолчанию")
        defaults_layout = QFormLayout()
        defaults_layout.setSpacing(10)
        
        # Время работы по умолчанию
        self.default_work_time = QSpinBox()
        self.default_work_time.setRange(1, 300)
        self.default_work_time.setSuffix(" сек")
        defaults_layout.addRow("Время работы:", self.default_work_time)
        
        # Время отдыха по умолчанию
        self.default_rest_time = QSpinBox()
        self.default_rest_time.setRange(1, 300)
        self.default_rest_time.setSuffix(" сек")
        defaults_layout.addRow("Время отдыха:", self.default_rest_time)
        
        # Количество циклов по умолчанию
        self.default_cycles = QSpinBox()
        self.default_cycles.setRange(1, 100)
        defaults_layout.addRow("Количество циклов:", self.default_cycles)
        
        # Количество сетов по умолчанию
        self.default_sets = QSpinBox()
        self.default_sets.setRange(1, 20)
        defaults_layout.addRow("Количество сетов:", self.default_sets)
        
        defaults_group.setLayout(defaults_layout)
        layout.addWidget(defaults_group)
        
        # Группа: Автоматизация
        automation_group = QGroupBox("Автоматизация")
        automation_layout = QVBoxLayout()
        
        self.auto_save_workouts = QCheckBox("Автоматически сохранять тренировки")
        automation_layout.addWidget(self.auto_save_workouts)
        
        self.auto_backup = QCheckBox("Создавать резервные копии тренировок")
        automation_layout.addWidget(self.auto_backup)
        
        self.auto_export = QCheckBox("Автоматически экспортировать статистику")
        automation_layout.addWidget(self.auto_export)
        
        automation_group.setLayout(automation_layout)
        layout.addWidget(automation_group)
        
        # Группа: Публичные тренировки
        public_group = QGroupBox("Публичные тренировки")
        public_layout = QVBoxLayout()
        
        self.allow_public = QCheckBox("Разрешить публикацию тренировок")
        public_layout.addWidget(self.allow_public)
        
        self.auto_import = QCheckBox("Автоматически обновлять публичные тренировки")
        public_layout.addWidget(self.auto_import)
        
        public_group.setLayout(public_layout)
        layout.addWidget(public_group)
        
        layout.addStretch()
        return widget
    
    def create_timer_tab(self) -> QWidget:
        """Создание вкладки настроек таймера"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Группа: Звуковые сигналы
        sound_group = QGroupBox("Звуковые сигналы")
        sound_layout = QFormLayout()
        sound_layout.setSpacing(10)
        
        # Включение звуков
        self.enable_sounds = QCheckBox("Включить звуковые сигналы")
        sound_layout.addRow(self.enable_sounds)
        
        # Громкость
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.volume_slider.setTickInterval(10)
        sound_layout.addRow("Громкость:", self.volume_slider)
        
        # Тип звука
        self.sound_type = QComboBox()
        self.sound_type.addItems(["Бип", "Звонок", "Голос", "Музыка"])
        sound_layout.addRow("Тип звука:", self.sound_type)
        
        # Тест звука
        self.test_sound_button = QPushButton("Тест звука")
        sound_layout.addRow("", self.test_sound_button)
        
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)
        
        # Группа: Отображение таймера
        display_group = QGroupBox("Отображение таймера")
        display_layout = QFormLayout()
        display_layout.setSpacing(10)
        
        # Формат времени
        self.time_format = QComboBox()
        self.time_format.addItems(["MM:SS", "Минуты:Секунды", "Только секунды"])
        display_layout.addRow("Формат времени:", self.time_format)
        
        # Показывать прогресс
        self.show_progress = QCheckBox("Показывать прогресс-бар")
        display_layout.addRow(self.show_progress)
        
        # Показывать этапы
        self.show_stages = QCheckBox("Показывать этапы тренировки")
        display_layout.addRow(self.show_stages)
        
        # Время подготовки
        self.preparation_time = QSpinBox()
        self.preparation_time.setRange(0, 60)
        self.preparation_time.setSuffix(" сек")
        display_layout.addRow("Время подготовки:", self.preparation_time)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Группа: Поведение таймера
        behavior_group = QGroupBox("Поведение таймера")
        behavior_layout = QVBoxLayout()
        
        self.auto_start_next = QCheckBox("Автоматически начинать следующий сет")
        behavior_layout.addWidget(self.auto_start_next)
        
        self.pause_between_sets = QCheckBox("Пауза между сетами")
        behavior_layout.addWidget(self.pause_between_sets)
        
        self.countdown_preparation = QCheckBox("Обратный отсчет перед началом")
        behavior_layout.addWidget(self.countdown_preparation)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        layout.addStretch()
        return widget
    
    def create_appearance_tab(self) -> QWidget:
        """Создание вкладки настроек внешнего вида"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Группа: Темы
        themes_group = QGroupBox("Темы оформления")
        themes_layout = QVBoxLayout()
        
        self.theme_list = QListWidget()
        self.theme_list.addItems([
            "Системная",
            "Светлая", 
            "Темная",
            "Синяя",
            "Зеленая",
            "Оранжевая"
        ])
        themes_layout.addWidget(self.theme_list)
        
        themes_group.setLayout(themes_layout)
        layout.addWidget(themes_group)
        
        # Группа: Шрифты
        fonts_group = QGroupBox("Шрифты")
        fonts_layout = QFormLayout()
        fonts_layout.setSpacing(10)
        
        self.font_family = QComboBox()
        self.font_family.addItems(["Arial", "Segoe UI", "Helvetica", "Verdana", "Tahoma"])
        fonts_layout.addRow("Шрифт:", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 20)
        fonts_layout.addRow("Размер шрифта:", self.font_size)
        
        self.font_preview = QLabel("Пример текста: 123 ABC абв")
        self.font_preview.setFrameStyle(QFrame.Shape.Box)
        self.font_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fonts_layout.addRow("Предпросмотр:", self.font_preview)
        
        fonts_group.setLayout(fonts_layout)
        layout.addWidget(fonts_group)
        
        # Группа: Прозрачность
        transparency_group = QGroupBox("Прозрачность окна")
        transparency_layout = QVBoxLayout()
        
        self.window_opacity = QSlider(Qt.Orientation.Horizontal)
        self.window_opacity.setRange(30, 100)
        self.window_opacity.setValue(100)
        self.window_opacity.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.window_opacity.setTickInterval(10)
        
        self.opacity_label = QLabel("100%")
        self.opacity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        transparency_layout.addWidget(QLabel("Непрозрачность:"))
        transparency_layout.addWidget(self.window_opacity)
        transparency_layout.addWidget(self.opacity_label)
        
        transparency_group.setLayout(transparency_layout)
        layout.addWidget(transparency_group)
        
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self) -> QWidget:
        """Создание вкладки расширенных настроек"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Группа: База данных
        database_group = QGroupBox("База данных")
        database_layout = QFormLayout()
        database_layout.setSpacing(10)
        
        # Путь к базе данных
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)
        self.browse_db_button = QPushButton("Обзор...")
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(self.db_path_edit)
        db_path_layout.addWidget(self.browse_db_button)
        database_layout.addRow("Путь к БД:", db_path_layout)
        
        # Создать резервную копию
        self.backup_button = QPushButton("Создать резервную копию БД")
        database_layout.addRow("", self.backup_button)
        
        # Восстановить из резервной копии
        self.restore_button = QPushButton("Восстановить БД из копии")
        database_layout.addRow("", self.restore_button)
        
        database_group.setLayout(database_layout)
        layout.addWidget(database_group)
        
        # Группа: Логирование
        logging_group = QGroupBox("Логирование")
        logging_layout = QFormLayout()
        logging_layout.setSpacing(10)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("Уровень логирования:", self.log_level)
        
        self.enable_file_logging = QCheckBox("Вести лог в файл")
        logging_layout.addRow(self.enable_file_logging)
        
        self.enable_console_logging = QCheckBox("Выводить лог в консоль")
        logging_layout.addRow(self.enable_console_logging)
        
        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)
        
        # Группа: Производительность
        performance_group = QGroupBox("Производительность")
        performance_layout = QFormLayout()
        performance_layout.setSpacing(10)
        
        self.cache_size = QSpinBox()
        self.cache_size.setRange(10, 1000)
        self.cache_size.setSuffix(" MB")
        performance_layout.addRow("Размер кэша:", self.cache_size)
        
        self.update_interval = QSpinBox()
        self.update_interval.setRange(100, 5000)
        self.update_interval.setSuffix(" мс")
        performance_layout.addRow("Интервал обновления:", self.update_interval)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        # Группа: Сброс настроек
        reset_group = QGroupBox("Опасная зона")
        reset_layout = QVBoxLayout()
        
        self.reset_all_button = QPushButton("Сбросить ВСЕ настройки")
        self.reset_all_button.setStyleSheet("background-color: #f56565; color: white;")
        reset_layout.addWidget(self.reset_all_button)
        
        self.export_settings_button = QPushButton("Экспортировать настройки")
        reset_layout.addWidget(self.export_settings_button)
        
        self.import_settings_button = QPushButton("Импортировать настройки")
        reset_layout.addWidget(self.import_settings_button)
        
        reset_group.setLayout(reset_layout)
        layout.addWidget(reset_group)
        
        layout.addStretch()
        return widget
    
    def setup_connections(self):
        """Настройка соединений сигналов и слотов"""
        # Кнопки
        self.save_button.clicked.connect(self.save_settings)
        self.apply_button.clicked.connect(self.apply_settings)
        self.reset_button.clicked.connect(self.reset_to_defaults)
        self.cancel_button.clicked.connect(self.reject)
        
        # Звук
        self.enable_sounds.stateChanged.connect(
            lambda state: self.set_sound_widgets_enabled(state == Qt.CheckState.Checked.value)
        )
        self.test_sound_button.clicked.connect(self.test_sound)
        
        # Уведомления
        self.enable_notifications.stateChanged.connect(
            lambda state: self.set_notification_widgets_enabled(state == Qt.CheckState.Checked.value)
        )
        
        # Шрифты
        self.font_family.currentTextChanged.connect(self.update_font_preview)
        self.font_size.valueChanged.connect(self.update_font_preview)
        
        # Прозрачность
        self.window_opacity.valueChanged.connect(
            lambda value: self.opacity_label.setText(f"{value}%")
        )
        
        # База данных
        self.browse_db_button.clicked.connect(self.browse_database_path)
        self.backup_button.clicked.connect(self.backup_database)
        self.restore_button.clicked.connect(self.restore_database)
        
        # Расширенные
        self.reset_all_button.clicked.connect(self.reset_all_settings)
        self.export_settings_button.clicked.connect(self.export_settings)
        self.import_settings_button.clicked.connect(self.import_settings)
        
        # Темы
        self.theme_list.itemSelectionChanged.connect(self.preview_theme)
    
    def load_settings(self) -> dict:
        """Загрузка текущих настроек"""
        settings_dict = {}
        
        # Общие настройки
        settings_dict['language'] = self.settings.value('general/language', 'Русский')
        settings_dict['theme'] = self.settings.value('general/theme', 'Авто')
        settings_dict['startup'] = self.settings.value('general/startup', False, type=bool)
        settings_dict['minimize_to_tray'] = self.settings.value('general/minimize_to_tray', False, type=bool)
        settings_dict['check_updates'] = self.settings.value('general/check_updates', True, type=bool)
        
        # Уведомления
        settings_dict['enable_notifications'] = self.settings.value('notifications/enabled', True, type=bool)
        settings_dict['sound_notifications'] = self.settings.value('notifications/sound', True, type=bool)
        settings_dict['desktop_notifications'] = self.settings.value('notifications/desktop', True, type=bool)
        
        # Тренировки
        settings_dict['default_work_time'] = self.settings.value('workouts/default_work_time', 
                                                                self.config.DEFAULT_WORK_TIME, type=int)
        settings_dict['default_rest_time'] = self.settings.value('workouts/default_rest_time', 
                                                                self.config.DEFAULT_REST_TIME, type=int)
        settings_dict['default_cycles'] = self.settings.value('workouts/default_cycles', 
                                                             self.config.DEFAULT_CYCLES, type=int)
        settings_dict['default_sets'] = self.settings.value('workouts/default_sets', 
                                                           self.config.DEFAULT_SETS, type=int)
        settings_dict['auto_save_workouts'] = self.settings.value('workouts/auto_save', True, type=bool)
        settings_dict['auto_backup'] = self.settings.value('workouts/auto_backup', False, type=bool)
        settings_dict['allow_public'] = self.settings.value('workouts/allow_public', True, type=bool)
        
        # Таймер
        settings_dict['enable_sounds'] = self.settings.value('timer/enable_sounds', True, type=bool)
        settings_dict['volume'] = self.settings.value('timer/volume', 80, type=int)
        settings_dict['sound_type'] = self.settings.value('timer/sound_type', 'Бип')
        settings_dict['time_format'] = self.settings.value('timer/time_format', 'MM:SS')
        settings_dict['show_progress'] = self.settings.value('timer/show_progress', True, type=bool)
        settings_dict['show_stages'] = self.settings.value('timer/show_stages', True, type=bool)
        settings_dict['preparation_time'] = self.settings.value('timer/preparation_time', 
                                                               self.config.PREPARATION_TIME, type=int)
        settings_dict['auto_start_next'] = self.settings.value('timer/auto_start_next', False, type=bool)
        
        # Внешний вид
        settings_dict['font_family'] = self.settings.value('appearance/font_family', 'Arial')
        settings_dict['font_size'] = self.settings.value('appearance/font_size', 10, type=int)
        settings_dict['window_opacity'] = self.settings.value('appearance/window_opacity', 100, type=int)
        settings_dict['selected_theme'] = self.settings.value('appearance/theme', 'Системная')
        
        # Расширенные
        settings_dict['db_path'] = self.settings.value('advanced/db_path', str(self.config.DB_PATH))
        settings_dict['log_level'] = self.settings.value('advanced/log_level', 'INFO')
        settings_dict['enable_file_logging'] = self.settings.value('advanced/enable_file_logging', True, type=bool)
        settings_dict['enable_console_logging'] = self.settings.value('advanced/enable_console_logging', True, type=bool)
        settings_dict['cache_size'] = self.settings.value('advanced/cache_size', 100, type=int)
        settings_dict['update_interval'] = self.settings.value('advanced/update_interval', 
                                                              self.config.TIMER_UPDATE_INTERVAL, type=int)
        
        return settings_dict
    
    def load_current_settings(self):
        """Загрузка текущих настроек в виджеты"""
        settings = self.original_settings
        
        # Общие
        self.language_combo.setCurrentText(settings['language'])
        self.theme_combo.setCurrentText(settings['theme'])
        self.startup_checkbox.setChecked(settings['startup'])
        self.minimize_to_tray.setChecked(settings['minimize_to_tray'])
        self.check_updates.setChecked(settings['check_updates'])
        
        # Уведомления
        self.enable_notifications.setChecked(settings['enable_notifications'])
        self.sound_notifications.setChecked(settings['sound_notifications'])
        self.desktop_notifications.setChecked(settings['desktop_notifications'])
        self.set_notification_widgets_enabled(settings['enable_notifications'])
        
        # Тренировки
        self.default_work_time.setValue(settings['default_work_time'])
        self.default_rest_time.setValue(settings['default_rest_time'])
        self.default_cycles.setValue(settings['default_cycles'])
        self.default_sets.setValue(settings['default_sets'])
        self.auto_save_workouts.setChecked(settings['auto_save_workouts'])
        self.auto_backup.setChecked(settings['auto_backup'])
        self.allow_public.setChecked(settings['allow_public'])
        
        # Таймер
        self.enable_sounds.setChecked(settings['enable_sounds'])
        self.volume_slider.setValue(settings['volume'])
        self.sound_type.setCurrentText(settings['sound_type'])
        self.time_format.setCurrentText(settings['time_format'])
        self.show_progress.setChecked(settings['show_progress'])
        self.show_stages.setChecked(settings['show_stages'])
        self.preparation_time.setValue(settings['preparation_time'])
        self.auto_start_next.setChecked(settings['auto_start_next'])
        self.set_sound_widgets_enabled(settings['enable_sounds'])
        
        # Внешний вид
        self.font_family.setCurrentText(settings['font_family'])
        self.font_size.setValue(settings['font_size'])
        self.window_opacity.setValue(settings['window_opacity'])
        self.opacity_label.setText(f"{settings['window_opacity']}%")
        
        # Выбор темы в списке
        items = self.theme_list.findItems(settings['selected_theme'], Qt.MatchFlag.MatchExactly)
        if items:
            self.theme_list.setCurrentItem(items[0])
        
        # Расширенные
        self.db_path_edit.setText(settings['db_path'])
        self.log_level.setCurrentText(settings['log_level'])
        self.enable_file_logging.setChecked(settings['enable_file_logging'])
        self.enable_console_logging.setChecked(settings['enable_console_logging'])
        self.cache_size.setValue(settings['cache_size'])
        self.update_interval.setValue(settings['update_interval'])
    
    def get_current_settings(self) -> dict:
        """Получение текущих настроек из виджетов"""
        settings = {}
        
        # Общие
        settings['language'] = self.language_combo.currentText()
        settings['theme'] = self.theme_combo.currentText()
        settings['startup'] = self.startup_checkbox.isChecked()
        settings['minimize_to_tray'] = self.minimize_to_tray.isChecked()
        settings['check_updates'] = self.check_updates.isChecked()
        
        # Уведомления
        settings['enable_notifications'] = self.enable_notifications.isChecked()
        settings['sound_notifications'] = self.sound_notifications.isChecked()
        settings['desktop_notifications'] = self.desktop_notifications.isChecked()
        
        # Тренировки
        settings['default_work_time'] = self.default_work_time.value()
        settings['default_rest_time'] = self.default_rest_time.value()
        settings['default_cycles'] = self.default_cycles.value()
        settings['default_sets'] = self.default_sets.value()
        settings['auto_save_workouts'] = self.auto_save_workouts.isChecked()
        settings['auto_backup'] = self.auto_backup.isChecked()
        settings['allow_public'] = self.allow_public.isChecked()
        
        # Таймер
        settings['enable_sounds'] = self.enable_sounds.isChecked()
        settings['volume'] = self.volume_slider.value()
        settings['sound_type'] = self.sound_type.currentText()
        settings['time_format'] = self.time_format.currentText()
        settings['show_progress'] = self.show_progress.isChecked()
        settings['show_stages'] = self.show_stages.isChecked()
        settings['preparation_time'] = self.preparation_time.value()
        settings['auto_start_next'] = self.auto_start_next.isChecked()
        
        # Внешний вид
        settings['font_family'] = self.font_family.currentText()
        settings['font_size'] = self.font_size.value()
        settings['window_opacity'] = self.window_opacity.value()
        
        # Выбранная тема
        selected_items = self.theme_list.selectedItems()
        settings['selected_theme'] = selected_items[0].text() if selected_items else 'Системная'
        
        # Расширенные
        settings['db_path'] = self.db_path_edit.text()
        settings['log_level'] = self.log_level.currentText()
        settings['enable_file_logging'] = self.enable_file_logging.isChecked()
        settings['enable_console_logging'] = self.enable_console_logging.isChecked()
        settings['cache_size'] = self.cache_size.value()
        settings['update_interval'] = self.update_interval.value()
        
        return settings
    
    def save_settings_to_storage(self, settings: dict):
        """Сохранение настроек в хранилище"""
        # Общие
        self.settings.setValue('general/language', settings['language'])
        self.settings.setValue('general/theme', settings['theme'])
        self.settings.setValue('general/startup', settings['startup'])
        self.settings.setValue('general/minimize_to_tray', settings['minimize_to_tray'])
        self.settings.setValue('general/check_updates', settings['check_updates'])
        
        # Уведомления
        self.settings.setValue('notifications/enabled', settings['enable_notifications'])
        self.settings.setValue('notifications/sound', settings['sound_notifications'])
        self.settings.setValue('notifications/desktop', settings['desktop_notifications'])
        
        # Тренировки
        self.settings.setValue('workouts/default_work_time', settings['default_work_time'])
        self.settings.setValue('workouts/default_rest_time', settings['default_rest_time'])
        self.settings.setValue('workouts/default_cycles', settings['default_cycles'])
        self.settings.setValue('workouts/default_sets', settings['default_sets'])
        self.settings.setValue('workouts/auto_save', settings['auto_save_workouts'])
        self.settings.setValue('workouts/auto_backup', settings['auto_backup'])
        self.settings.setValue('workouts/allow_public', settings['allow_public'])
        
        # Таймер
        self.settings.setValue('timer/enable_sounds', settings['enable_sounds'])
        self.settings.setValue('timer/volume', settings['volume'])
        self.settings.setValue('timer/sound_type', settings['sound_type'])
        self.settings.setValue('timer/time_format', settings['time_format'])
        self.settings.setValue('timer/show_progress', settings['show_progress'])
        self.settings.setValue('timer/show_stages', settings['show_stages'])
        self.settings.setValue('timer/preparation_time', settings['preparation_time'])
        self.settings.setValue('timer/auto_start_next', settings['auto_start_next'])
        
        # Внешний вид
        self.settings.setValue('appearance/font_family', settings['font_family'])
        self.settings.setValue('appearance/font_size', settings['font_size'])
        self.settings.setValue('appearance/window_opacity', settings['window_opacity'])
        self.settings.setValue('appearance/theme', settings['selected_theme'])
        
        # Расширенные
        self.settings.setValue('advanced/db_path', settings['db_path'])
        self.settings.setValue('advanced/log_level', settings['log_level'])
        self.settings.setValue('advanced/enable_file_logging', settings['enable_file_logging'])
        self.settings.setValue('advanced/enable_console_logging', settings['enable_console_logging'])
        self.settings.setValue('advanced/cache_size', settings['cache_size'])
        self.settings.setValue('advanced/update_interval', settings['update_interval'])
        
        self.settings.sync()
    
    def save_settings(self):
        """Сохранение настроек и закрытие диалога"""
        try:
            settings = self.get_current_settings()
            self.save_settings_to_storage(settings)
            
            # Отправляем сигнал об изменении настроек
            self.settings_changed.emit(settings)
            
            logger.info("Настройки сохранены")
            QMessageBox.information(self, "Сохранено", "Настройки успешно сохранены.")
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def apply_settings(self):
        """Применение настроек без закрытия диалога"""
        try:
            settings = self.get_current_settings()
            self.save_settings_to_storage(settings)
            
            # Отправляем сигнал об изменении настроек
            self.settings_changed.emit(settings)
            
            logger.info("Настройки применены")
            QMessageBox.information(self, "Применено", "Настройки успешно применены.")
            
        except Exception as e:
            logger.error(f"Ошибка применения настроек: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось применить настройки: {e}")
    
    def reset_to_defaults(self):
        """Сброс настроек к значениям по умолчанию"""
        reply = QMessageBox.question(
            self,
            "Сброс настроек",
            "Сбросить настройки к значениям по умолчанию?\n\n"
            "Это не затронет ваши тренировки и данные пользователей.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Сбрасываем значения в виджетах
            self.default_work_time.setValue(self.config.DEFAULT_WORK_TIME)
            self.default_rest_time.setValue(self.config.DEFAULT_REST_TIME)
            self.default_cycles.setValue(self.config.DEFAULT_CYCLES)
            self.default_sets.setValue(self.config.DEFAULT_SETS)
            
            # Сбрасываем другие настройки
            self.enable_sounds.setChecked(True)
            self.volume_slider.setValue(80)
            self.preparation_time.setValue(self.config.PREPARATION_TIME)
            
            logger.info("Настройки сброшены к значениям по умолчанию")
    
    def reset_all_settings(self):
        """Сброс ВСЕХ настроек (опасная операция)"""
        reply = QMessageBox.warning(
            self,
            "ВНИМАНИЕ!",
            "Вы уверены, что хотите сбросить ВСЕ настройки?\n\n"
            "Это действие невозможно отменить!\n"
            "Будут сброшены:\n"
            "• Все пользовательские настройки\n"
            "• Настройки внешнего вида\n"
            "• Настройки тренировок\n"
            "• Настройки таймера\n\n"
            "Ваши тренировки и данные пользователей НЕ будут затронуты.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Удаляем все настройки
            self.settings.clear()
            
            # Перезагружаем настройки по умолчанию
            self.load_current_settings()
            
            logger.warning("ВСЕ настройки сброшены")
            QMessageBox.information(self, "Сброс завершен", "Все настройки сброшены к значениям по умолчанию.")
    
    def set_sound_widgets_enabled(self, enabled: bool):
        """Включение/выключение виджетов настроек звука"""
        self.volume_slider.setEnabled(enabled)
        self.sound_type.setEnabled(enabled)
        self.test_sound_button.setEnabled(enabled)
    
    def set_notification_widgets_enabled(self, enabled: bool):
        """Включение/выключение виджетов уведомлений"""
        self.sound_notifications.setEnabled(enabled)
        self.desktop_notifications.setEnabled(enabled)
    
    def update_font_preview(self):
        """Обновление предпросмотра шрифта"""
        font = QFont(self.font_family.currentText(), self.font_size.value())
        self.font_preview.setFont(font)
    
    def preview_theme(self):
        """Предпросмотр выбранной темы"""
        selected_items = self.theme_list.selectedItems()
        if selected_items:
            theme = selected_items[0].text()
            # Здесь можно добавить логику предпросмотра темы
            logger.debug(f"Предпросмотр темы: {theme}")
    
    def test_sound(self):
        """Тест звукового сигнала"""
        try:
            # Здесь будет логика воспроизведения тестового звука
            logger.info("Воспроизведение тестового звука")
            QMessageBox.information(self, "Тест звука", "Звуковой сигнал воспроизведен.")
        except Exception as e:
            logger.error(f"Ошибка воспроизведения звука: {e}")
            QMessageBox.warning(self, "Ошибка", "Не удалось воспроизвести звук.")
    
    def browse_database_path(self):
        """Выбор пути к базе данных"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Выберите путь к базе данных",
            str(self.config.DB_PATH.parent),
            "SQLite Database (*.db *.sqlite);;All Files (*)"
        )
        
        if file_path:
            self.db_path_edit.setText(file_path)
    
    def backup_database(self):
        """Создание резервной копии базы данных"""
        try:
            from models.database import get_database
            
            db = get_database()
            backup_path = db.backup_database()
            
            if backup_path:
                QMessageBox.information(
                    self,
                    "Резервная копия создана",
                    f"Резервная копия базы данных успешно создана:\n{backup_path}"
                )
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось создать резервную копию.")
                
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать резервную копию: {e}")
    
    def restore_database(self):
        """Восстановление базы данных из резервной копии"""
        reply = QMessageBox.warning(
            self,
            "ВНИМАНИЕ!",
            "Вы уверены, что хотите восстановить базу данных из резервной копии?\n\n"
            "Текущая база данных будет заменена.\n"
            "Это действие невозможно отменить!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите резервную копию базы данных",
                str(self.config.DB_PATH.parent),
                "SQLite Database (*.db *.sqlite);;All Files (*)"
            )
            
            if file_path:
                try:
                    import shutil
                    import os
                    
                    # Создаем резервную копию текущей БД
                    current_db = Path(self.config.DB_PATH)
                    if current_db.exists():
                        timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
                        backup_name = f"{current_db.stem}_before_restore_{timestamp}{current_db.suffix}"
                        backup_path = current_db.parent / backup_name
                        shutil.copy2(current_db, backup_path)
                    
                    # Копируем выбранную резервную копию
                    shutil.copy2(file_path, current_db)
                    
                    QMessageBox.information(
                        self,
                        "Восстановление завершено",
                        f"База данных успешно восстановлена из:\n{file_path}\n\n"
                        f"Текущая БД сохранена как:\n{backup_path}"
                    )
                    
                    # Требуем перезапуск приложения
                    QMessageBox.warning(
                        self,
                        "Перезапуск требуется",
                        "Для применения изменений требуется перезапуск приложения."
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка восстановления БД: {e}")
                    QMessageBox.critical(self, "Ошибка", f"Не удалось восстановить БД: {e}")
    
    def export_settings(self):
        """Экспорт настроек в файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт настроек",
            str(Path.home() / f"{self.config.APP_NAME}_settings.json"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                settings = self.get_current_settings()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(
                    self,
                    "Экспорт завершен",
                    f"Настройки успешно экспортированы в:\n{file_path}"
                )
                
            except Exception as e:
                logger.error(f"Ошибка экспорта настроек: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать настройки: {e}")
    
    def import_settings(self):
        """Импорт настроек из файла"""
        reply = QMessageBox.question(
            self,
            "Импорт настроек",
            "Импортировать настройки из файла?\n\n"
            "Текущие настройки будут заменены.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите файл настроек",
                str(Path.home()),
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    # Загружаем настройки в виджеты
                    self.load_settings_into_widgets(settings)
                    
                    QMessageBox.information(
                        self,
                        "Импорт завершен",
                        "Настройки успешно импортированы."
                    )
                    
                except Exception as e:
                    logger.error(f"Ошибка импорта настроек: {e}")
                    QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать настройки: {e}")
    
    def load_settings_into_widgets(self, settings: dict):
        """Загрузка настроек в виджеты из словаря"""
        # Эта функция должна быть реализована для корректной загрузки
        # всех настроек из словаря в соответствующие виджеты
        pass
    
    def closeEvent(self, event):
        """Обработка закрытия диалога"""
        current_settings = self.get_current_settings()
        
        # Проверяем, изменились ли настройки
        if current_settings != self.original_settings:
            reply = QMessageBox.question(
                self,
                "Несохраненные изменения",
                "У вас есть несохраненные изменения. Сохранить?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_settings()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()