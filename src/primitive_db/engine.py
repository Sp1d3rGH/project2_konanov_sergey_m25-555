import os
import time
import prompt
import shlex
import src.primitive_db.utils as utils
import src.primitive_db.core as core
import src.primitive_db.parser as parser


METADATA_PATH = "src/db_meta.json"
METADATA_DIR = "src"
TABLE_DATA_DIR = "data"

def welcome():
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

def create_cacher(func):
    func_cache = {}
    def cache_result(key, *args, **kwargs):
        start_seek = time.monotonic()
        if key in func_cache:
            stop_seek = time.monotonic()
            result_seek = round(stop_seek - start_seek, 3)
            print(f"Функция выполнилась за {result_seek} секунд")
        else:
            func_cache[key] = func(*args, **kwargs)
        return func_cache[key]
    return cache_result

def run():
    if not os.path.exists(METADATA_PATH):
        os.makedirs(METADATA_DIR, exist_ok=True)
        with open(METADATA_PATH, "w") as file:
            #print(f"Файл с базой данных не найден. Создан файл: {METADATA_PATH}.")
            file.write(str(dict()))
    select_cached = create_cacher(core.select)
    while True:
        metadata = utils.load_metadata(METADATA_PATH)
        user_input = prompt.string("\n>>>Введите команду: ")
        user_args = shlex.split(user_input)
        if not user_args:
            continue
        match user_args[0]:
            case "create_table":
                if len(user_args) > 1:
                    if len(user_args) > 2:
                        new_meta = core.create_table(metadata, user_args[1], user_args[2:])
                        metadata = new_meta if new_meta else metadata
                    else:
                        new_meta = core.create_table(metadata, user_args[1])
                        metadata = new_meta if new_meta else metadata
                else:
                    print("Введите имя создаваемой таблицы.")
            case "list_tables":
                new_meta = core.list_tables(metadata)
                metadata = new_meta if new_meta else metadata
            case "drop_table":
                if len(user_args) > 1:
                    new_meta = core.drop_table(metadata, user_args[1])
                    metadata = new_meta if new_meta else metadata
                else:
                    print("Введите имя удаляемой таблицы.")


            case "insert":
                if len(user_args) > 4:
                    if user_args[1] == "into" and user_args[3] == "values":
                        table_name = user_args[2]
                        table_values = [val.replace('(', '').replace(')', '').replace(',', '') for val in user_args[4:]]
                        if len(table_values) == len(list(metadata[table_name].keys())) - 1:
                            table_values = parser.parse_values(table_values, list(metadata[table_name].keys())[1:])
                            core.insert(metadata, table_name, table_values)
                        else:
                            print("Число переменных не соответствует числу столбцов. Попробуйте снова.")
                    else:
                        print("Некорректный синтаксис. Попробуйте снова.")
                else:
                    print("Некорректный синтаксис. Попробуйте снова.")

            case "select":
                if len(user_args) == 7:
                    # select from where
                    if user_args[1] == "from" and user_args[3] == "where" and user_args[5] == '=':
                        table_name = user_args[2]
                        if table_name in list(metadata.keys()):
                            table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
                        else:
                            print(f"Ошибка: Таблица '{table_name}' не существует.")
                            continue
                        col_names = [col.split(sep=':')[0] for col in list(metadata[table_name].keys())]
                        if user_args[4] not in col_names:
                            print(f"Столбца {user_args[4]} в таблице {table_name} нет.")
                        else:
                            col_index = col_names.index(user_args[4])
                            preferred_type = list(metadata[table_name].keys())[col_index].split(sep=':')[1]
                            clause, success = parser.parse(user_args[4] + '=' + user_args[6], preferred_type)
                            if success:
                                #select_data = core.select(table_data, clause)
                                select_data = select_cached(str(user_args), table_data, clause)
                                core.print_table(metadata, table_name, select_data)
                            else:
                                print(f"Значение {user_args[6]} нельзя использовать для столбца типа {preferred_type}.")
                    else:
                        print("Некорректный синтаксис. Попробуйте снова.")
                elif len(user_args) == 3:
                    # select from
                    table_name = user_args[2]
                    if table_name in list(metadata.keys()):
                        table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
                    else:
                        print(f"Ошибка: Таблица '{table_name}' не существует.")
                        continue
                    #select_data = core.select(table_data)
                    select_data = select_cached(str(user_args), table_data)
                    core.print_table(metadata, table_name)
                else:
                    print("Некорректный синтаксис. Попробуйте снова.")

            case "update":
                if len(user_args) == 10:
                    if user_args[2] == "set" and user_args[4] == '=' and user_args[6] == "where" and user_args[8] == '=':
                        table_name = user_args[1]
                        if table_name in list(metadata.keys()):
                            table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
                        else:
                            print(f"Ошибка: Таблица '{table_name}' не существует.")
                            continue
                        col_names = [col.split(sep=':')[0] for col in list(metadata[table_name].keys())]
                        if user_args[3] not in col_names:
                            print(f"Столбца {user_args[3]} в таблице {table_name} нет.")
                        elif user_args[7] not in col_names:
                            print(f"Столбца {user_args[7]} в таблице {table_name} нет.")
                        else:
                            set_index = col_names.index(user_args[3])
                            preferred_set_type = list(metadata[table_name].keys())[set_index].split(sep=':')[1]
                            set_clause, set_success = parser.parse(user_args[3] + '=' + user_args[5], preferred_set_type)
                            where_index = col_names.index(user_args[7])
                            preferred_where_type = list(metadata[table_name].keys())[where_index].split(sep=':')[1]
                            where_clause, where_success = parser.parse(user_args[7] + '=' + user_args[9], preferred_where_type)
                            if not set_success:
                                print(f"Значение {user_args[3]} нельзя использовать для столбца типа {preferred_set_type}.")
                            elif not where_success:
                                print(f"Значение {user_args[7]} нельзя использовать для столбца типа {preferred_where_type}.")
                            else:
                                new_table_data = core.update(table_data, set_clause, where_clause)
                                table_data = new_table_data if new_table_data else table_data
                                utils.save_table_data(TABLE_DATA_DIR + "/" + table_name + ".json", table_data)
                    else:
                        print("Некорректный синтаксис. Попробуйте снова.")
                else:
                    print("Некорректный синтаксис. Попробуйте снова.")

            case "delete":
                if len(user_args) == 7:
                    if user_args[1] == "from" and user_args[3] == "where" and user_args[5] == '=':
                        table_name = user_args[2]
                        if table_name in list(metadata.keys()):
                            table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
                        else:
                            print(f"Ошибка: Таблица '{table_name}' не существует.")
                            continue
                        col_names = [col.split(sep=':')[0] for col in list(metadata[table_name].keys())]
                        if user_args[4] not in col_names:
                            print(f"Столбца {user_args[4]} в таблице {table_name} нет.")
                        else:
                            col_index = col_names.index(user_args[4])
                            preferred_type = list(metadata[table_name].keys())[col_index].split(sep=':')[1]
                            clause, success = parser.parse(user_args[4] + '=' + user_args[6], preferred_type)
                            if success:
                                new_table_data = core.delete(table_data, clause)
                                table_data = new_table_data if new_table_data else table_data
                                utils.save_table_data(TABLE_DATA_DIR + "/" + table_name + ".json", table_data)
                            else:
                                print(f"Значение {user_args[6]} нельзя использовать для столбца типа {preferred_type}.")
                    else:
                        print("Некорректный синтаксис. Попробуйте снова.")
                else:
                    print("Некорректный синтаксис. Попробуйте снова.")

            case "info":
                if len(user_args) >= 2:
                    table_name = user_args[1]
                    if table_name in list(metadata.keys()):
                        table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
                    else:
                        print(f"Ошибка: Таблица '{table_name}' не существует.")
                        continue
                    print("Таблица: ", table_name)
                    print("Столбцы: ", str(list(metadata[table_name].keys()))[1:-1])
                    table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
                    print("Количество записей: ", len(list(table_data.keys())))
                else:
                    print("Введите имя таблицы.")

            case "exit":
                return None
            case "help":
                utils.show_help()
            case '':
                pass
            case _:
                print(f"Функции {user_args[0]} нет. Попробуйте снова.")
        utils.save_metadata(METADATA_PATH, metadata)
