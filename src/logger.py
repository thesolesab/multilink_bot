import logging
import time
from functools import wraps

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Отключаем подробные логи httpx (запросы polling)
logging.getLogger('httpx').setLevel(logging.WARNING)

def log_method(func):
    """Декоратор для логирования вызовов методов"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__module__)
        
        # Логируем вызов
        logger.info(f"Вызов метода {func.__name__} с args={args[1:]}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Метод {func.__name__} выполнен за {execution_time:.2f} сек")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Ошибка в методе {func.__name__} за {execution_time:.2f} сек: {e}")
            raise
    
    return wrapper

# Для асинхронных методов
def log_async_method(func):
    """Декоратор для логирования асинхронных методов"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(func.__module__)
        
        logger.info(f"Асинхронный вызов метода {func.__name__} с args={args[1:]}, kwargs={kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Асинхронный метод {func.__name__} выполнен за {execution_time:.2f} сек")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Ошибка в асинхронном методе {func.__name__} за {execution_time:.2f} сек: {e}")
            raise
    
    return wrapper