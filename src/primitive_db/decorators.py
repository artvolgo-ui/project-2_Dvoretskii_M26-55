import functools
import time


def handle_db_errors(func):
    """Перехватывает исключения базы данных и выводит понятные сообщения."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name: str):
    """Запрашивает у пользователя подтверждение перед выполнением действия."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.lower() == 'y':
                return func(*args, **kwargs)
            else:
                print("Операция отменена.")
                return args[0] if args else None
        return wrapper
    return decorator


def log_time(func):
    """Замеряет и выводит время выполнения функции."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    """Создает функцию для кэширования результатов с возможностью очистки."""
    cache = {}
    
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result
        
    cache_result.clear = cache.clear
    return cache_result