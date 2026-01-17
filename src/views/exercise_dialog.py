# src/views/exercise_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QSpinBox, QCheckBox,
    QPushButton, QGroupBox, QMessageBox, QComboBox,
    QTabWidget, QWidget, QTextEdit, QFrame, QSlider,
    # QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
import logging
# from datetime import datetime

logger = logging.getLogger(__name__)


class exerciseDialog(QDialog):
    """Диалог для создания/редактирования тренировки"""
    
    exercise_saved = pyqtSignal(dict)  # Сигнал при сохранении тренировки
    
    def __init__(self, exercise_controller, user_id: int, 
                 exercise_data: dict = None, parent=None):
        """
        Инициализация диалога
        
        Args:
            exercise_controller: Контроллер тренировок
            user_id: ID текущего пользователя
            exercise_data: Данные для редактирования (если None - создание)
            parent: Родительское окно
        """
        super().__init__(parent)
        self.exercise_controller = exercise_controller
        self.user_id = user_id
        self.exercise_data = exercise_data
        self.exercise_id = exercise_data.get('id') if exercise_data else None
        
        self.setup_ui()
        self.setup_connections()
        
        # Заполняем данные, если редактирование
        if self.exercise_data:
            self.load_exercise_data()
        
        # Рассчитываем и обновляем общее время
        # self.calculate_total_time()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle(
            "Редактировать тренировку" if self.exercise_data 
            else "Новая тренировка"
        )
        self.setMinimumSize(550, 400)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # === ВКЛАДКИ ===
        self.tab_widget = QTabWidget()
        
        # Вкладка 1: Основные параметры
        self.basic_tab = self.create_basic_tab()
        self.tab_widget.addTab(self.basic_tab, "Основные")
        
        # # Вкладка 2: Расширенные параметры
        # self.advanced_tab = self.create_advanced_tab()
        # self.tab_widget.addTab(self.advanced_tab, "Расширенные")
        
        # # Вкладка 3: Предпросмотр
        # self.preview_tab = self.create_preview_tab()
        # self.tab_widget.addTab(self.preview_tab, "Предпросмотр")
        
        main_layout.addWidget(self.tab_widget)
        
        # # === ИНФОРМАЦИОННАЯ ПАНЕЛЬ ===
        # self.info_panel = self.create_info_panel()
        # main_layout.addWidget(self.info_panel)
        
        # === КНОПКИ ===
        self.create_buttons(main_layout)
    
    def create_basic_tab(self) -> QWidget:
        """Создание вкладки с основными параметрами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # === ОСНОВНЫЕ ПАРАМЕТРЫ ===
        basic_group = QGroupBox("Основные параметры")
        basic_layout = QGridLayout()
        basic_layout.setSpacing(10)
        basic_layout.setContentsMargins(10, 15, 10, 10)
        
        # Название тренировки
        basic_layout.addWidget(QLabel("Название упражнения:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: отжимания")
        self.name_input.setMinimumWidth(300)
        basic_layout.addWidget(self.name_input, 0, 1, 1, 2)
        
        # Описание
        basic_layout.addWidget(QLabel("Описание:"), 1, 0)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Краткое описание упражнения...")
        basic_layout.addWidget(self.description_input, 1, 1, 1, 2)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # === ПАРАМЕТРЫ тренировки ===
        tabata_group = QGroupBox("Параметры тренировки")
        tabata_layout = QGridLayout()
        tabata_layout.setSpacing(15)
        tabata_layout.setContentsMargins(10, 15, 10, 10)        
       
        # Количество подходов
        tabata_layout.addWidget(QLabel("Количество подходов:"), 0, 0)
        self.sets_input = QSpinBox()
        self.sets_input.setRange(1, 20)
        self.sets_input.setValue(5)
        self.sets_input.setMinimumWidth(120)
        tabata_layout.addWidget(self.sets_input, 0, 1)
        
        # Количество повторений
        tabata_layout.addWidget(QLabel("Повторений в подходе:"), 1, 0)
        self.cycles_input = QSpinBox()
        self.cycles_input.setRange(1, 100)
        self.cycles_input.setValue(20)
        self.cycles_input.setMinimumWidth(120)
        tabata_layout.addWidget(self.cycles_input, 1, 1)      

        # Время отдыха между подходами
        tabata_layout.addWidget(QLabel("Отдых между подходами:"), 2, 0)
        self.rest_time_input = QSpinBox()
        self.rest_time_input.setRange(0, 600)
        self.rest_time_input.setValue(60)
        self.rest_time_input.setSuffix(" сек")
        self.rest_time_input.setMinimumWidth(120)
        tabata_layout.addWidget(self.rest_time_input, 2, 1)

        # Время подготовительное
        tabata_layout.addWidget(QLabel("Время на подготовку:"), 3, 0)
        self.prepare_time_input = QSpinBox()
        self.prepare_time_input.setRange(1, 30)
        self.prepare_time_input.setValue(10)
        self.prepare_time_input.setSuffix(" сек")
        self.prepare_time_input.setMinimumWidth(120)
        tabata_layout.addWidget(self.prepare_time_input, 3, 1)

        tabata_group.setLayout(tabata_layout)
        layout.addWidget(tabata_group)        
       
        layout.addStretch()
        return widget
    
    def create_advanced_tab(self) -> QWidget:
        """Создание вкладки с расширенными параметрами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # === ЦВЕТА И КАТЕГОРИИ ===
        categories_group = QGroupBox("Категории и цвета")
        categories_layout = QGridLayout()
        categories_layout.setSpacing(10)
        categories_layout.setContentsMargins(10, 15, 10, 10)
        
        # Категория
        categories_layout.addWidget(QLabel("Категория:"), 0, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Общая тренировка",
            "Кардио",
            "Силовая",
            "Разминка",
            "Растяжка",
            "Интервальная",
            "Выносливость"
        ])
        categories_layout.addWidget(self.category_combo, 0, 1)
        
        # Цвет тренировки
        categories_layout.addWidget(QLabel("Цвет метки:"), 1, 0)
        self.color_combo = QComboBox()
        self.color_combo.addItems([
            "Синий (#4299e1)",
            "Зеленый (#48bb78)",
            "Красный (#f56565)",
            "Желтый (#ecc94b)",
            "Фиолетовый (#9f7aea)",
            "Розовый (#ed64a6)",
            "Оранжевый (#ed8936)",
            "Бирюзовый (#38b2ac)"
        ])
        categories_layout.addWidget(self.color_combo, 1, 1)
        
        # Уровень сложности
        categories_layout.addWidget(QLabel("Сложность:"), 2, 0)
        self.difficulty_slider = QSlider(Qt.Orientation.Horizontal)
        self.difficulty_slider.setRange(1, 5)
        self.difficulty_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.difficulty_slider.setTickInterval(1)
        self.difficulty_slider.setValue(3)
        
        difficulty_layout = QHBoxLayout()
        difficulty_layout.addWidget(QLabel("Лёгкая"))
        difficulty_layout.addWidget(self.difficulty_slider)
        difficulty_layout.addWidget(QLabel("Сложная"))
        categories_layout.addLayout(difficulty_layout, 2, 1)
        
        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)
        
        # === ПОВТОРЕНИЯ И НАПОМИНАНИЯ ===
        reminders_group = QGroupBox("Повторения и напоминания")
        reminders_layout = QGridLayout()
        reminders_layout.setSpacing(10)
        reminders_layout.setContentsMargins(10, 15, 10, 10)
        
        # Любимая тренировка
        self.favorite_checkbox = QCheckBox("Добавить в избранное")
        reminders_layout.addWidget(self.favorite_checkbox, 0, 0, 1, 2)
        
        # Напоминание о тренировке
        self.reminder_checkbox = QCheckBox("Напоминать о тренировке")
        reminders_layout.addWidget(self.reminder_checkbox, 1, 0, 1, 2)
        
        # Дни недели для напоминания
        reminders_layout.addWidget(QLabel("Дни для напоминания:"), 2, 0)
        self.days_widget = self.create_days_widget()
        reminders_layout.addWidget(self.days_widget, 2, 1)
        
        # Время напоминания
        reminders_layout.addWidget(QLabel("Время напоминания:"), 3, 0)
        self.reminder_time = QComboBox()
        times = []
        for hour in range(6, 23):
            for minute in [0, 30]:
                times.append(f"{hour:02d}:{minute:02d}")
        self.reminder_time.addItems(times)
        self.reminder_time.setCurrentText("18:00")
        reminders_layout.addWidget(self.reminder_time, 3, 1)
        
        reminders_group.setLayout(reminders_layout)
        layout.addWidget(reminders_group)
        
        # === ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ===
        additional_group = QGroupBox("Дополнительные настройки")
        additional_layout = QVBoxLayout()
        
        # Звуковые сигналы
        self.enable_sounds = QCheckBox("Включить звуковые сигналы")
        additional_layout.addWidget(self.enable_sounds)
        
        # Вибрация (если поддерживается)
        self.enable_vibration = QCheckBox("Включить вибрацию")
        additional_layout.addWidget(self.enable_vibration)
        
        # Автозапуск следующего сета
        self.auto_start_next = QCheckBox("Автоматически начинать следующий сет")
        additional_layout.addWidget(self.auto_start_next)
        
        # Показывать таймер в полноэкранном режиме
        self.fullscreen_timer = QCheckBox("Показывать таймер в полноэкранном режиме")
        additional_layout.addWidget(self.fullscreen_timer)
        
        additional_group.setLayout(additional_layout)
        layout.addWidget(additional_group)
        
        layout.addStretch()
        return widget
    
    def create_preview_tab(self) -> QWidget:
        """Создание вкладки предпросмотра"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # === ПРЕДПРОСМОТР ТРЕНИРОВКИ ===
        preview_group = QGroupBox("Предпросмотр тренировки")
        preview_layout = QVBoxLayout()
        preview_layout.setSpacing(10)
        preview_layout.setContentsMargins(10, 15, 10, 10)
        
        # Название тренировки в предпросмотре
        self.preview_title = QLabel("Название тренировки")
        self.preview_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_title)
        
        # Описание в предпросмотре
        self.preview_description = QLabel("Описание тренировки будет отображено здесь")
        self.preview_description.setWordWrap(True)
        self.preview_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_description)
        
        # === ПАРАМЕТРЫ В ПРЕДПРОСМОТРЕ ===
        params_layout = QGridLayout()
        params_layout.setSpacing(10)
        
        self.preview_work_time = self.create_preview_card("Время работы", "20 сек", "#4299e1")
        self.preview_rest_time = self.create_preview_card("Время отдыха", "10 сек", "#38a169")
        self.preview_cycles = self.create_preview_card("Циклов", "8", "#ed8936")
        self.preview_sets = self.create_preview_card("Сетов", "1", "#9f7aea")
        self.preview_total_time = self.create_preview_card("Общее время", "2:30", "#3182ce")
        
        params_layout.addWidget(self.preview_work_time, 0, 0)
        params_layout.addWidget(self.preview_rest_time, 0, 1)
        params_layout.addWidget(self.preview_cycles, 1, 0)
        params_layout.addWidget(self.preview_sets, 1, 1)
        params_layout.addWidget(self.preview_total_time, 2, 0, 1, 2)
        
        preview_layout.addLayout(params_layout)
        
        # === РАСПИСАНИЕ ТРЕНИРОВКИ ===
        schedule_label = QLabel("Расписание тренировки:")
        schedule_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        preview_layout.addWidget(schedule_label)
        
        self.preview_schedule = QTextEdit()
        self.preview_schedule.setMaximumHeight(150)
        self.preview_schedule.setReadOnly(True)
        preview_layout.addWidget(self.preview_schedule)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # === СТАТИСТИКА ===
        stats_group = QGroupBox("Статистика тренировки")
        stats_layout = QVBoxLayout()
        
        self.preview_stats = QLabel("Интенсивность: средняя\nСожжено калорий: ~150 ккал")
        self.preview_stats.setWordWrap(True)
        stats_layout.addWidget(self.preview_stats)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        return widget
    
    def create_info_panel(self) -> QGroupBox:
        """Создание информационной панели"""
        panel = QGroupBox("Информация о тренировке")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Общее время
        self.total_time_label = QLabel()
        self.total_time_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Разбивка по времени
        self.breakdown_label = QLabel()
        self.breakdown_label.setWordWrap(True)
        self.breakdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.total_time_label)
        layout.addWidget(self.breakdown_label)
        
        panel.setLayout(layout)
        return panel
    
    def create_buttons(self, parent_layout):
        """Создание кнопок управления"""
        buttons_layout = QHBoxLayout()
        
        if self.exercise_data:
            # # Для редактирования: кнопка "Дублировать"
            # self.duplicate_button = QPushButton("Дублировать")
            # self.duplicate_button.setToolTip("Создать копию этой тренировки")
            # buttons_layout.addWidget(self.duplicate_button)
            
            # Кнопка удаления
            self.delete_button = QPushButton("Удалить")
            self.delete_button.setToolTip("Удалить эту тренировку")
            self.delete_button.setStyleSheet("background-color: #f56565; color: white;")
            buttons_layout.addWidget(self.delete_button)
        
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton(
            "Сохранить изменения" if self.exercise_data else "Создать тренировку"
        )
        self.save_button.setDefault(True)
        buttons_layout.addWidget(self.save_button)
        
        parent_layout.addLayout(buttons_layout)
    
    def create_days_widget(self) -> QWidget:
        """Создание виджета выбора дней недели"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(5)
        
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        self.day_checkboxes = []
        
        for day in days:
            checkbox = QCheckBox(day)
            checkbox.setMaximumWidth(40)
            layout.addWidget(checkbox)
            self.day_checkboxes.append(checkbox)
        
        return widget
    
    def create_preview_card(self, title: str, value: str, color: str) -> QWidget:
        """Создание карточки для предпросмотра"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setLineWidth(1)
        card.setStyleSheet(f"QFrame {{ border-color: {color}; border-radius: 5px; padding: 5px; }}")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"QLabel {{ color: {color}; font-weight: bold; }}")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def setup_connections(self):
        """Настройка соединений сигналов"""
        # При изменении любого параметра пересчитываем время и обновляем предпросмотр
        # self.work_time_input.valueChanged.connect(self.update_exercise)
        self.prepare_time_input.valueChanged.connect(self.update_exercise)
        self.cycles_input.valueChanged.connect(self.update_exercise)
        self.sets_input.valueChanged.connect(self.update_exercise)
        self.rest_time_input.valueChanged.connect(self.update_exercise)
        # self.name_input.textChanged.connect(self.update_preview)
        # self.description_input.textChanged.connect(self.update_preview)
        
        # Предустановки
        # self.preset_combo.currentTextChanged.connect(self.apply_preset)
        
        # Кнопки
        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject)
        
        if self.exercise_data:
            # self.duplicate_button.clicked.connect(self.handle_duplicate)
            self.delete_button.clicked.connect(self.handle_delete)
        
        # Обновление предпросмотра при изменении категорий
        # self.category_combo.currentTextChanged.connect(self.update_preview)
        # self.color_combo.currentTextChanged.connect(self.update_preview)
        # self.difficulty_slider.valueChanged.connect(self.update_preview)
    
    def load_exercise_data(self):
        """Загрузка данных тренировки для редактирования"""
        self.name_input.setText(self.exercise_data.get('name', ''))
        
        description = self.exercise_data.get('description', '')
        self.description_input.setPlainText(description)
        
        # self.work_time_input.setValue(self.exercise_data.get('work_time', 20))
        self.prepare_time_input.setValue(self.exercise_data.get('prepare_time', 10))
        self.cycles_input.setValue(self.exercise_data.get('reps', 8))
        self.sets_input.setValue(self.exercise_data.get('sets', 1))
        self.rest_time_input.setValue(self.exercise_data.get('rest_time', 60))
    
    def update_exercise(self):
        """Обновление расчетов тренировки"""
        # self.calculate_total_time()
        # self.update_preview()
    
    def calculate_total_time(self):
        """Расчет и отображение общего времени тренировки"""
        # work_time = 0   # self.work_time_input.value()
        # prepare_time = self.prepare_time_input.value()
        cycles = self.cycles_input.value()
        sets = self.sets_input.value()
        rest_time = self.rest_time_input.value()
        
        # Расчет общей продолжительности тренировки
        cycle_time = work_time + rest_time
        total_cycles = cycles * sets
        
        if total_cycles > 0:
            # Общее время = (время цикла * общее количество циклов) - последний отдых + отдых между сетами
            total_time = (cycle_time * total_cycles) - rest_time
            
            # Добавляем отдых между сетами (кроме последнего сета)
            if sets > 1:
                total_time += rest_between_sets * (sets - 1)
            
            # Форматируем время
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            seconds = total_time % 60
            
            if hours > 0:
                time_str = f"{hours} ч {minutes} мин {seconds} сек"
            elif minutes > 0:
                time_str = f"{minutes} мин {seconds} сек"
            else:
                time_str = f"{seconds} сек"
            
            # Обновляем метки
            self.total_time_label.setText(
                f"<span style='color: #2c3e50;'>Общее время: "
                f"<b>{time_str}</b> ({total_time} сек)</span>"
            )
            
            # Детальная разбивка
            breakdown = (
                f"• Работа: {work_time} сек × {cycles} циклов × {sets} сетов = "
                f"<b>{work_time * cycles * sets} сек</b><br>"
                f"• Отдых: {rest_time} сек × {cycles} циклов × {sets} сетов = "
                f"<b>{rest_time * cycles * sets} сек</b><br>"
            )
            
            if sets > 1:
                breakdown += f"• Отдых между сетами: {rest_between_sets} сек × {sets - 1} = "
                breakdown += f"<b>{rest_between_sets * (sets - 1)} сек</b><br>"
            
            breakdown += f"• Итого: <b>{total_time} сек</b>"
            self.breakdown_label.setText(breakdown)
    
    def update_preview(self):
        """Обновление предпросмотра тренировки"""
        # Обновляем название и описание
        name = self.name_input.text().strip()
        if name:
            self.preview_title.setText(name)
        else:
            self.preview_title.setText("Новая тренировка")
        
        description = self.description_input.toPlainText().strip()
        if description:
            self.preview_description.setText(description)
        else:
            self.preview_description.setText("Описание тренировки")
        
        # Обновляем параметры в предпросмотре
        total_time = self.calculate_preview_total_time()
        minutes = total_time // 60
        seconds = total_time % 60
        
        # Обновляем карточки предпросмотра
        # self.update_preview_card(self.preview_work_time, "Время работы", f"{self.work_time_input.value()} сек")
        self.update_preview_card(self.preview_rest_time, "Время отдыха", f"{self.prepare_time_input.value()} сек")
        self.update_preview_card(self.preview_cycles, "Циклов", str(self.cycles_input.value()))
        self.update_preview_card(self.preview_sets, "Сетов", str(self.sets_input.value()))
        self.update_preview_card(self.preview_total_time, "Общее время", f"{minutes}:{seconds:02d}")
        
        # Обновляем расписание
        self.update_schedule_preview()
        
        # Обновляем статистику
        self.update_stats_preview()
    
    def update_preview_card(self, card: QWidget, title: str, value: str):
        """Обновление карточки предпросмотра"""
        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[0].setText(title)
            labels[1].setText(value)
    
    def calculate_preview_total_time(self) -> int:
        """Расчет общего времени для предпросмотра"""
        work_time = 0   # self.work_time_input.value()
        rest_time = self.prepare_time_input.value()
        cycles = self.cycles_input.value()
        sets = self.sets_input.value()
        rest_between_sets = self.rest_time_input.value()
        
        cycle_time = work_time + rest_time
        total_cycles = cycles * sets
        
        if total_cycles > 0:
            total_time = (cycle_time * total_cycles) - rest_time
            
            if sets > 1:
                total_time += rest_between_sets * (sets - 1)
            
            return total_time
        return 0
    
    def update_schedule_preview(self):
        """Обновление расписания в предпросмотре"""
        work_time = self.work_time_input.value()
        rest_time = self.prepare_time_input.value()
        cycles = self.cycles_input.value()
        sets = self.sets_input.value()
        rest_between_sets = self.rest_time_input.value()
        
        schedule_text = "Расписание тренировки:\n\n"
        
        for set_num in range(1, sets + 1):
            schedule_text += f"Сет {set_num}:\n"
            
            for cycle_num in range(1, cycles + 1):
                schedule_text += f"  Цикл {cycle_num}: работа {work_time} сек, отдых {rest_time} сек\n"
            
            if set_num < sets:
                schedule_text += f"  Отдых между сетами: {rest_between_sets} сек\n\n"
        
        self.preview_schedule.setPlainText(schedule_text)
    
    def update_stats_preview(self):
        """Обновление статистики в предпросмотре"""
        work_time = self.work_time_input.value()
        cycles = self.cycles_input.value()
        sets = self.sets_input.value()
        difficulty = self.difficulty_slider.value()
        
        # Расчет примерного количества калорий
        # Базовая формула: 0.1 калорий на секунду интенсивной работы
        total_work_time = work_time * cycles * sets
        estimated_calories = int(total_work_time * 0.1)
        
        # Определение интенсивности
        if difficulty >= 4:
            intensity = "высокая"
        elif difficulty >= 3:
            intensity = "средняя"
        else:
            intensity = "низкая"
        
        stats_text = (
            f"Интенсивность: {intensity}\n"
            f"Сложность: {difficulty}/5\n"
            f"Примерное время тренировки: {self.format_time(self.calculate_preview_total_time())}\n"
            f"Сожжено калорий: ~{estimated_calories} ккал\n"
            f"Категория: {self.category_combo.currentText()}"
        )
        
        self.preview_stats.setText(stats_text)
    
    def format_time(self, seconds: int) -> str:
        """Форматирование времени в читаемый вид"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours} ч {minutes} мин"
        elif minutes > 0:
            return f"{minutes} мин {secs} сек"
        else:
            return f"{secs} сек"
    
    def apply_preset(self, preset_name: str):
        """Применение предустановленных настроек"""
        if preset_name == "-- Выберите шаблон --":
            return
        
        presets = {
            "Классический Tabata (20/10, 8 циклов)": (20, 10, 8, 1, 60),
            "Интенсивный (30/15, 8 циклов)": (30, 15, 8, 1, 60),
            "Выносливость (45/15, 5 циклов)": (45, 15, 5, 1, 60),
            "Для начинающих (15/30, 5 циклов)": (15, 30, 5, 1, 90),
            "Интервалы (60/30, 4 цикла)": (60, 30, 4, 1, 120),
            "Короткая разминка (20/10, 4 цикла)": (20, 10, 4, 1, 30),
            "Длинная тренировка (40/20, 10 циклов, 2 сета)": (40, 20, 10, 2, 180)
        }
        
        if preset_name in presets:
            work, rest, cycles, sets, rest_between = presets[preset_name]
            
            # Временно отключаем сигналы
            # self.work_time_input.blockSignals(True)
            self.prepare_time_input.blockSignals(True)
            self.cycles_input.blockSignals(True)
            self.sets_input.blockSignals(True)
            self.rest_time_input.blockSignals(True)
            
            # self.work_time_input.setValue(work)
            self.prepare_time_input.setValue(rest)
            self.cycles_input.setValue(cycles)
            self.sets_input.setValue(sets)
            self.rest_time_input.setValue(rest_between)
            
            # Включаем сигналы обратно
            # self.work_time_input.blockSignals(False)
            self.prepare_time_input.blockSignals(False)
            self.cycles_input.blockSignals(False)
            self.sets_input.blockSignals(False)
            self.rest_time_input.blockSignals(False)
            
            # Однократное обновление
            self.update_exercise()
    
    def validate_inputs(self) -> tuple:
        """
        Валидация введенных данных
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Проверка названия
        name = self.name_input.text().strip()
        if not name:
            return False, "Введите название тренировки"
        
        if len(name) < 3:
            return False, "Название должно содержать минимум 3 символа"
        
        if len(name) > 100:
            return False, "Название слишком длинное (макс. 100 символов)"
        
        # Проверка параметров
        work_time = 0   # self.work_time_input.value()
        rest_time = self.prepare_time_input.value()
        cycles = self.cycles_input.value()
        sets = self.sets_input.value()
        rest_between_sets = self.rest_time_input.value()
        
        # if work_time < 1 or work_time > 300:
        #     return False, "Время работы должно быть от 1 до 300 секунд"
        
        if rest_time < 1 or rest_time > 300:
            return False, "Время отдыха должно быть от 1 до 300 секунд"
        
        if cycles < 1 or cycles > 1000:
            return False, "Количество повторений должно быть от 1 до 1000"
        
        if sets < 1 or sets > 20:
            return False, "Количество подходов должно быть от 1 до 20"
        
        # if rest_between_sets < 0 or rest_between_sets > 600:
        #     return False, "Отдых между сетами должен быть от 0 до 600 секунд"
        
        # # Проверка общего времени (не более 4 часов)
        # total_time = self.calculate_preview_total_time()
        # if total_time > 14400:  # 4 часа
        #     return False, "Общее время тренировки не должно превышать 4 часов"
        
        return True, ""
    
    def handle_save(self):
        """Обработка сохранения тренировки"""
        # Валидация
        is_valid, error_message = self.validate_inputs()
        if not is_valid:
            QMessageBox.warning(self, "Ошибка ввода", error_message)
            return
        
        # Сбор данных
        exercise_data = {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'reps': self.cycles_input.value(),
            'sets': self.sets_input.value(),
            'prepare_time': self.prepare_time_input.value(),
            'rest_time': self.rest_time_input.value(),
        }
        
        # # Извлекаем цвет из строки
        # color_text = self.color_combo.currentText()
        # if '#' in color_text:
        #     exercise_data['color'] = color_text.split('#')[1][:6]
        
        # # Дни напоминания
        # if self.reminder_checkbox.isChecked():
        #     selected_days = []
        #     for i, checkbox in enumerate(self.day_checkboxes):
        #         if checkbox.isChecked():
        #             selected_days.append(i)  # 0=Понедельник, 6=Воскресенье
            
        #     exercise_data['reminder_days'] = selected_days
        #     exercise_data['reminder_time'] = self.reminder_time.currentText()
        
        try:
            if self.exercise_data:
                # Редактирование существующей тренировки
                result = self.exercise_controller.update_exercise(
                    exercise_id=self.exercise_id,
                    user_id=self.user_id,
                    **exercise_data
                )
            else:
                # Создание новой тренировки
                result = self.exercise_controller.create_exercise(
                    user_id=self.user_id,
                    **exercise_data
                )
            
            if result["success"]:
                # Отправляем сигнал с данными тренировки
                self.exercise_saved.emit(result.get("exercise", {}))
                
                logger.info(f"Тренировка сохранена: {exercise_data['name']}")
                QMessageBox.information(
                    self, 
                    "Успешно", 
                    result.get("message", "Тренировка сохранена")
                )
                self.accept()
            else:
                logger.error(f"Ошибка сохранения тренировки: {result.get('message')}")
                QMessageBox.warning(
                    self, 
                    "Ошибка", 
                    result.get("message", "Не удалось сохранить тренировку")
                )
                
        except Exception as e:
            logger.error(f"Критическая ошибка при сохранении тренировки: {e}")
            QMessageBox.critical(
                self, 
                "Критическая ошибка", 
                f"Произошла ошибка: {str(e)}"
            )
    
    # def handle_duplicate(self):
    #     """Дублирование текущей тренировки"""
    #     reply = QMessageBox.question(
    #         self,
    #         "Дублировать тренировку",
    #         "Создать копию этой тренировки?",
    #         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    #     )
        
    #     if reply == QMessageBox.StandardButton.Yes:
    #         # Создаем копию с измененным названием
    #         original_name = self.name_input.text().strip()
    #         new_name = f"{original_name} (Копия)"
            
    #         # Закрываем текущий диалог
    #         self.reject()
            
    #         # Открываем новый диалог с данными копии
    #         duplicate_data = {
    #             'name': new_name,
    #             'description': self.description_input.toPlainText().strip(),
    #             # 'work_time': self.work_time_input.value(),
    #             'rest_time': self.prepare_time_input.value(),
    #             'cycles': self.cycles_input.value(),
    #             'sets': self.sets_input.value(),
    #             'rest_between_sets': self.rest_time_input.value(),
    #             'category': self.category_combo.currentText(),
    #             'difficulty': self.difficulty_slider.value(),
    #         }
            
    #         duplicate_dialog = exerciseDialog(
    #             exercise_controller=self.exercise_controller,
    #             user_id=self.user_id,
    #             exercise_data=duplicate_data,
    #             parent=self.parent()
    #         )
            
    #         # Подключаем сигнал, чтобы обновить список тренировок в родительском окне
    #         if self.parent():
    #             duplicate_dialog.exercise_saved.connect(
    #                 getattr(self.parent(), 'on_exercise_saved', lambda x: None)
    #             )
            
    #         duplicate_dialog.exec()
    
    def handle_delete(self):
        """Удаление тренировки"""
        if not self.exercise_data:
            return
        
        exercise_name = self.exercise_data.get('name', 'эту тренировку')
        
        reply = QMessageBox.warning(
            self,
            "Удаление тренировки",
            f"Вы уверены, что хотите удалить тренировку '{exercise_name}'?\n\n"
            f"Это действие нельзя отменить!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                result = self.exercise_controller.delete_exercise(
                    exercise_id=self.exercise_id,
                    user_id=self.user_id
                )
                
                if result["success"]:
                    QMessageBox.information(
                        self,
                        "Удалено",
                        result.get("message", "Тренировка удалена")
                    )
                    self.reject()  # Закрываем диалог
                else:
                    QMessageBox.warning(
                        self,
                        "Ошибка",
                        result.get("message", "Не удалось удалить тренировку")
                    )
                    
            except Exception as e:
                logger.error(f"Ошибка удаления тренировки: {e}")
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить тренировку: {str(e)}"
                )
    
    def get_exercise_data(self) -> dict:
        """Получение данных из диалога"""
        data = {
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            # 'work_time': self.work_time_input.value(),
            'rest_time': self.prepare_time_input.value(),
            'reps': self.cycles_input.value(),
            'sets': self.sets_input.value(),
            'rest_between_sets': self.rest_time_input.value(),
            'category': self.category_combo.currentText(),
            'difficulty': self.difficulty_slider.value(),
            'favorite': self.favorite_checkbox.isChecked(),
        }
        
        # Извлекаем цвет из строки
        color_text = self.color_combo.currentText()
        if '#' in color_text:
            data['color'] = color_text.split('#')[1][:6]
        
        return data


class QuickexerciseDialog(QDialog):
    """Упрощенный диалог для быстрого создания тренировки"""
    
    exercise_created = pyqtSignal(dict)
    
    def __init__(self, exercise_controller, user_id: int, parent=None):
        super().__init__(parent)
        self.exercise_controller = exercise_controller
        self.user_id = user_id
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Быстрая тренировка")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("Быстрая тренировка")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Поле для названия
        layout.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Утренняя разминка")
        layout.addWidget(self.name_input)
        
        # Параметры в сетке
        params_layout = QGridLayout()
        params_layout.setSpacing(10)
        
        # # Время работы
        # params_layout.addWidget(QLabel("Работа:"), 0, 0)
        # # self.work_time_input = QSpinBox()
        # self.work_time_input.setRange(10, 60)
        # self.work_time_input.setValue(30)
        # self.work_time_input.setSuffix(" сек")
        # params_layout.addWidget(self.work_time_input, 0, 1)
        
        # Время отдыха
        params_layout.addWidget(QLabel("Отдых:"), 1, 0)
        self.rest_time_input = QSpinBox()
        self.rest_time_input.setRange(5, 30)
        self.rest_time_input.setValue(15)
        self.rest_time_input.setSuffix(" сек")
        params_layout.addWidget(self.rest_time_input, 1, 1)
        
        # Количество циклов
        params_layout.addWidget(QLabel("Циклы:"), 2, 0)
        self.cycles_input = QSpinBox()
        self.cycles_input.setRange(4, 12)
        self.cycles_input.setValue(8)
        params_layout.addWidget(self.cycles_input, 2, 1)
        
        # Количество сетов
        params_layout.addWidget(QLabel("Сеты:"), 3, 0)
        self.sets_input = QSpinBox()
        self.sets_input.setRange(1, 3)
        self.sets_input.setValue(1)
        params_layout.addWidget(self.sets_input, 3, 1)
        
        layout.addLayout(params_layout)
        
        # Информация о времени
        self.time_info = QLabel()
        self.time_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_info)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(self.cancel_button)
        
        buttons_layout.addStretch()
        
        self.create_button = QPushButton("Создать и начать")
        self.create_button.setDefault(True)
        buttons_layout.addWidget(self.create_button)
        
        layout.addLayout(buttons_layout)
        
        # Обновляем информацию о времени
        self.update_time_info()
    
    def setup_connections(self):
        """Настройка соединений"""
        self.work_time_input.valueChanged.connect(self.update_time_info)
        self.rest_time_input.valueChanged.connect(self.update_time_info)
        self.cycles_input.valueChanged.connect(self.update_time_info)
        self.sets_input.valueChanged.connect(self.update_time_info)
        
        self.cancel_button.clicked.connect(self.reject)
        self.create_button.clicked.connect(self.handle_create)
    
    def update_time_info(self):
        """Обновление информации о времени тренировки"""
        work_time = self.work_time_input.value()
        rest_time = self.rest_time_input.value()
        cycles = self.cycles_input.value()
        sets = self.sets_input.value()
        
        cycle_time = work_time + rest_time
        total_cycles = cycles * sets
        total_time = (cycle_time * total_cycles) - rest_time
        
        minutes = total_time // 60
        seconds = total_time % 60
        
        if minutes > 0:
            time_str = f"{minutes} мин {seconds} сек"
        else:
            time_str = f"{seconds} сек"
        
        self.time_info.setText(f"Общее время: <b>{time_str}</b>")
    
    def handle_create(self):
        """Создание быстрой тренировки"""
        name = self.name_input.text().strip()
        if not name:
            name = "Быстрая тренировка"
        
        result = self.exercise_controller.create_exercise(
            user_id=self.user_id,
            name=name,
            work_time=self.work_time_input.value(),
            rest_time=self.rest_time_input.value(),
            reps=self.cycles_input.value(),
            sets=self.sets_input.value()
        )
        
        if result["success"]:
            self.exercise_created.emit(result.get("exercise", {}))
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", result.get("message", ""))