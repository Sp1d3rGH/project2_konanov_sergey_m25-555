import json
import src.decorators as decorators


def show_help():
    print(
        "***Процесс работы с таблицей***\n"
        "Функции:\n"
        "<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу\n"
        "<command> list_tables - показать список всех таблиц\n"
        "<command> drop_table <имя_таблицы> - удалить таблицу\n"
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.\n"
        "<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.\n"
        "<command> select from <имя_таблицы> - прочитать все записи.\n"
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.\n"
        "<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.\n"
        "<command> info <имя_таблицы> - вывести информацию о таблице.\n"
        "<command> exit - выход из программы\n"
        "<command> help - справочная информация"
    )

@decorators.handle_db_errors
def load_metadata(filepath):
    with open(filepath) as f:
        data = json.load(f)
        return data

@decorators.handle_db_errors
def save_metadata(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)

@decorators.handle_db_errors
def load_table_data(table_path):
    with open(table_path) as f:
        data = json.load(f)
        return data

@decorators.handle_db_errors
def save_table_data(table_path, data):
    with open(table_path, 'w') as f:
        json.dump(data, f)
