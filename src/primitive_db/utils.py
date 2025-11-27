import json


def show_help():
    print(
        "***Процесс работы с таблицей***\n"
        "Функции:\n"
        "<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу\n"
        "<command> list_tables - показать список всех таблиц\n"
        "<command> drop_table <имя_таблицы> - удалить таблицу\n"
        "<command> exit - выход из программы\n"
        "<command> help - справочная информация"
    )

def load_metadata(filepath):
    try:
        with open(filepath) as f:
            # Возвращает json как словарь
            data = json.load(f)
            #print(f"Загрузка данных из {filepath}.")
            return data
    except FileNotFoundError:
        print(f"Не найден файл {filepath}.")
        return {}

def save_metadata(filepath, data):
    try:
        with open(filepath, 'w') as f:
            # Записывает словарь в существующий json
            #print(f"Запись в существующий файл: {filepath}.")
            json.dump(data, f)
    except FileNotFoundError:
        with open(filepath, 'w') as f:
            # Записывает словарь в новый json
            #print(f"Запись в новый файл: {filepath}.")
            json.dump(data, f)
