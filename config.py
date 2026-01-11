import os
import sys
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Optional


class Config:
    """Класс конфигурации приложения (синглтон)"""    
    _instance = None    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._setup()
    
    def _setup(self):
        """Настройка конфигурации"""
        # Основные настройки
        self.APP_NAME = "Training App"
        self.APP_VERSION = "1.0.0"
        
        # Определяем режим работы
        self.ENVIRONMENT = os.environ.get('TABATA_ENV', 'production').lower()
        self.DEBUG = True   #self.ENVIRONMENT in ['development', 'dev', 'test']
        
        # Пути
        self.BASE_DIR = self._get_base_dir()
        self.DATA_DIR = self.BASE_DIR / "data"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.RESOURCES_DIR = self.BASE_DIR / "resources"
        
        # База данных
        # self.DB_PATH = self.DATA_DIR / "database" / "test.db"
        self.DB_PATH = self.DATA_DIR / "database" / "fitness.db"
        
        # Интерфейс
        self.WINDOW_TITLE = f"{self.APP_NAME} v{self.APP_VERSION}"
        self.WINDOW_SIZE = (1024, 768) if not self.DEBUG else (800, 600)
        self.WINDOW_MIN_SIZE = (800, 600)
        
        # Логирование
        self.LOG_LEVEL = logging.DEBUG if self.DEBUG else logging.INFO
        self.LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        self.LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        self.LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
        self.LOG_BACKUP_COUNT = 5
        self.LOG_FILE = self.LOGS_DIR / f"{self.APP_NAME.lower().replace(' ', '_')}.log"
        
        # Настройки таймера
        self.TIMER_UPDATE_INTERVAL = 1000  # мс
        self.PREPARATION_TIME = 5  # секунд подготовки
        self.BEEP_ENABLED = True
        self.BEEP_VOLUME = 80  # %
        
        # Настройки тренировок
        self.DEFAULT_REST_TIME = 10
        self.DEFAULT_CYCLES = 8
        self.DEFAULT_SETS = 1
        
        # Настройки пользователя
        self.SESSION_TIMEOUT = 24 * 60 * 60  # 1 день в секундах для "запомнить меня"
        
        # Создаем директории
        self._create_directories()
    
    def _get_base_dir(self) -> Path:
        """Получение базовой директории"""
        # Для frozen приложений (PyInstaller)
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent.absolute()
        
        return base_dir
    
    def _create_directories(self):
        """Создание необходимых директорий"""
        directories = [
            self.DATA_DIR,
            self.DATA_DIR / "database",
            self.LOGS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Безопасное получение значения"""
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any):
        """Установка значения конфигурации"""
        setattr(self, key, value)
    
    def to_dict(self) -> dict:
        """Преобразование конфигурации в словарь (без приватных атрибутов)"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_') and not callable(value):
                # Преобразуем Path в строку для сериализации
                if isinstance(value, Path):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result    
    
    def print_config(self):
        """Вывод конфигурации в консоль"""
        print("=" * 50)
        print(f"Конфигурация {self.APP_NAME}")
        print("=" * 50)
        
        config_dict = self.to_dict()
        for key, value in config_dict.items():
            if isinstance(value, Path):
                value = str(value)
            print(f"{key:30} : {value}")
        
        print("=" * 50)


def setup_logging(config: Optional[Config] = None):
    """
    Настройка системы логирования
    
    Args:
        config: Экземпляр Config (если None, создается новый)
    """
    if config is None:
        config = Config()
    
    # Создаем директорию для логов, если не существует
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Создаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(config.LOG_LEVEL)
    
    # Удаляем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Форматтер для логов
    formatter = logging.Formatter(
        fmt=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )
    
    # Обработчик для файла (ротация логов)
    file_handler = RotatingFileHandler(
        filename=config.LOG_FILE,
        maxBytes=config.LOG_MAX_SIZE,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(config.LOG_LEVEL)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    
    if config.DEBUG:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики к корневому логгеру
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Отключаем логирование некоторых библиотек
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Логируем начало сессии
    logger = logging.getLogger(__name__)
    logger.info(f"Запуск {config.APP_NAME} v{config.APP_VERSION}")
    if config.DEBUG:
        logger.info(f"Платформа: {sys.platform}")
        logger.info(f"Python: {sys.version}")
        config.print_config()
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Получение именованного логгера
    
    Args:
        name: Имя логгера (обычно __name__)
        
    Returns:
        Настроенный логгер
    """
    return logging.getLogger(name)


# Глобальный экземпляр для удобного доступа
config = Config()

