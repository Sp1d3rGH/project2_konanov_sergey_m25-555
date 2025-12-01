import time
import prompt
import shlex


def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. База данных или файл таблицы не инициализированы.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper

def confirm_action(action_name=""):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            if action_name == "удаление таблицы":
                print(f"Вы уверены, что хотите выполнить {action_name}? [y/n]:", end='')
            else:
                print("Вы уверены, что хотите выполнить это действие? [y/n]:", end='')
            user_input = prompt.string()
            user_input = shlex.split(user_input)
            if not user_input:
                return None
            if user_input[0].lower() in ['y', 'yes', 'да']:
                return func(*args, **kwargs)
            else:
                return None
        return wrapper
    return real_decorator

def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {round(end_time - start_time, 3)} секунд")
        return result
    return wrapper
