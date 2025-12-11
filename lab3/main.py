from abc import ABC, abstractmethod
from enum import Enum
import re
import socket
import os
import tempfile
from ftplib import FTP
from datetime import datetime
from warnings import filters


class LogLevel(Enum):
    WARN = "WARN"
    INFO = "INFO"
    ERROR = "ERROR"


# FILTERS ================================================
class LogFilterProtocol(ABC):
    @abstractmethod
    def match(self, log_level: LogLevel, text: str) -> bool:
        pass

class SimpleLogFilter(LogFilterProtocol):
    def __init__(self, match_text: str) -> None:
        self.match_text = match_text
    
    def match(self, log_level, text):
        return self.match_text in text
    
class ReLogFilter(LogFilterProtocol):
    def __init__(self, pattern: str):
        self.pattern = pattern
    
    def match(self, log_level: LogLevel, text: str):
        return re.match(self.pattern, text)

class LevelFilter(LogFilterProtocol):
    def __init__(self, log_level: LogLevel):
        self.log_level = log_level
    
    def match(self, log_level: LogLevel, text: str):
        return self.log_level == log_level


# HANDLERS ======================================================
class LogHandlerProtocol(ABC):
    @abstractmethod
    def handle(self, log_level: LogLevel, text: str):
        pass

class FileHandler(LogHandlerProtocol):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def handle(self, log_level: LogLevel, text: str):
        try:
            with open(self.file_path, 'a', encoding="utf-8") as file:
                file.write(text)
        except Exception as e:
            pass

class SocketHandler(LogHandlerProtocol):
    def __init__(self, host: str, port: str) -> None:
        self.host = host
        self.port = port
        
    def handle(self, log_level: LogLevel, text: str) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.host, self.port))
                client.sendall(text.encode("utf-8"))
        except Exception as e:
            pass


class ConsoleHandler(LogHandlerProtocol):
    def handle(self, log_level: LogLevel, text: str) -> None:
        print(text)

class SyslogHandler(LogHandlerProtocol):
    def __init__(self, log_dir: str = "/var/log/myapp", app_name: str = "app") -> None:
        self.log_dir = log_dir
        self.app_name = app_name
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"{app_name}.log")

        
    def handle(self, log_level: LogLevel, text: str) -> None:
        try:
            with open(self.log_file, 'a', encoding="utf-8") as f:
                f.write(text + "\n")
        except Exception as e:
           print(f"Syslog couldn`t write file: {e}")
           pass

class FtpHandler(LogHandlerProtocol):
    def __init__(self, host: str, username: str, password: str) -> None:
        self.host       = host
        self.username   = username
        self.password   = password

        
    def handle(self, log_level: LogLevel, text: str) -> None:
        try:
            with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as tmp:
                tmp.write(text)
                tmp.flush()
                tmp_name = tmp.name

            ftp = FTP(self.host)
            ftp.login(self.username, self.password)
            ftp.cwd("/logs")

            with open(tmp_name, 'rb') as f:
                ftp.storbinary(f"STOR log_{os.path.basename}.txt", f)
            ftp.quit()
            os.remove(tmp_name)
        except Exception as e:
           pass


# FORMATTERS ====================================
class LogFormatterProtocol(ABC):
    @abstractmethod
    def format(self, log_level: LogLevel, text: str) -> str:
        pass

class LevelAndTimeFormatter(LogFormatterProtocol):
    def format(self, log_level: LogLevel, text: str) -> str:
        now = datetime.now()
        data = now.strftime("%Y.%m.%d %H:%M:%S")
        return f"[{log_level}][data:{data}] {text}"


# LOGGER ========================================
class Logger():
    def __init__(self, filters: list[LogFilterProtocol], handlers: list[LogHandlerProtocol], formatters: list[LogFormatterProtocol]) -> None:
        self.filters = filters
        self.handlers = handlers
        self.formatters = formatters
    
    def log(self, log_level: LogLevel, text: str) -> None:
        if not all(filter.match(log_level, text) for filter in self.filters):
            return
        
        for formatter in self.formatters:
            text = formatter.format(log_level, text)
        
        for handler in self.handlers:
            handler.handle(log_level, text)
        
    def log_info(self, text: str) -> None:
        self.log(LogLevel.INFO, text)
    
    def log_warn(self, text: str) -> None:
        self.log(LogLevel.WARN, text)

    def log_error(self, text: str) -> None:
        self.log(LogLevel.ERROR, text)
    
    def add_log_filter(self, log_filter: LogFilterProtocol) -> None:
        self.log_filters.append(log_filter)

    def add_log_formatter(self, log_formatter: LogFormatterProtocol) -> None:
        self.log_formatters.append(log_formatter)

    def add_log_handler(self, log_handler: LogHandlerProtocol) -> None:
        self.log_handlers.append(log_handler)

    def remove_log_filter(self, log_filter: LogFilterProtocol) -> None:
        self.log_filters.remove(log_filter)

    def remove_log_formatter(self, log_formatter: LogFormatterProtocol) -> None:
        self.log_formatters.remove(log_formatter)

    def remove_log_handler(self, log_handler: LogHandlerProtocol) -> None:
        self.log_handlers.remove(log_handler)

        

# Фильтры
filters = [
    LevelFilter(LogLevel.WARN),        # только WARN
    SimpleLogFilter("disk"),           # только если есть "disk"
    ReLogFilter(r".*full.*")           # и содержит "full"
]

# Хэндлеры
handlers = [
    SyslogHandler(),
    ConsoleHandler(),
    FileHandler("log_demo_extended.txt")
]

# Форматтер
formatters = [LevelAndTimeFormatter()]

# Logger
logger = Logger(filters, handlers, formatters)

# Тестовые логи
test_messages = [
    (LogLevel.INFO, "disk space ok"),            # не пройдет (INFO)
    (LogLevel.WARN, "disk almost full"),        # пройдет
    (LogLevel.WARN, "disk usage high"),         # не пройдет (нет "full")
    (LogLevel.WARN, "memory full"),             # не пройдет (нет "disk")
    (LogLevel.ERROR, "disk almost full"),       # не пройдет (ERROR)
    (LogLevel.WARN, "disk full backup"),        # пройдет
]

for level, msg in test_messages:
    logger.log(level, msg)