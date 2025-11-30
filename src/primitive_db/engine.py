import prompt
import shlex
import src.primitive_db.utils as utils
import src.primitive_db.core as core
import src.primitive_db.parser as parser


METADATA_PATH = "src/db_meta.json"
TABLE_DATA_DIR = "data"

def welcome():
    print(
        "\n***База данных***\n"
        "\nФункции:\n"
        "<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу\n"
        "<command> list_tables - показать список всех таблиц\n"
        "<command> drop_table <имя_таблицы> - удалить таблицу\n"
        "<command> exit - выход из программы\n"
        "<command> help - справочная информация"
    )

def run():
    while True:
        metadata = utils.load_metadata(METADATA_PATH)
        user_input = prompt.string("\n>>>Введите команду: ")
        user_args = shlex.split(user_input)
        print(user_args)
        if not user_args:
            # Если пользователь ничего не ввел
            continue
        match user_args[0]:
            case "create_table":
                if len(user_args) > 1:
                    if len(user_args) > 2:
                        metadata = core.create_table(metadata, user_args[1], user_args[2:])
                    else:
                        metadata = core.create_table(metadata, user_args[1])
                else:
                    print("Введите имя создаваемой таблицы.")
            case "list_tables":
                metadata = core.list_tables(metadata)
            case "drop_table":
                if len(user_args) > 1:
                    metadata = core.drop_table(metadata, user_args[1])
                else:
                    print("Введите имя удаляемой таблицы.")


            case "insert":
                if len(user_args) >= 4:
                    if user_args[1] == "into" and user_args[3] == "values":
                        table_name = user_args[2]
                        if len(user_args) > 4:
                            table_values = [val.replace('(', '').replace(')', '').replace(',', '') for val in user_args[5:]]
                            core.insert(metadata, table_name, table_values)
                        else:
                            print("Введите значения записи, которую вы хотите добавить.")
                    else:
                        print("Некорректный синтаксис. Попробуйте снова.")
                else:
                    print("Некорректный синтаксис. Попробуйте снова.")

            case "select":
                if len(user_args) >= 2:
                    if user_args[1] == "from":
                        if len(user_args) >= 3:
                            table_name = user_args[2]
                            if table_name in list(metadata.keys()):
                                table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
                            else:
                                print(f"Ошибка: Таблица '{table_name}' не существует.")
                                continue
                            if len(user_args) >= 4:
                                if user_args[3] == "where":
                                    if len(user_args) >= 7:
                                        if user_args[5] == '=':
                                            col_names = [col.split(sep=':')[0] for col in list(metadata[table_name].keys())]
                                            if user_args[4] not in col_names:
                                                print(f"Столбца {user_args[4]} в таблице {table_name} нет.")
                                            else:
                                                col_index = col_names.index(user_args[4])
                                                preferred_type = list(metadata[table_name].keys())[col_index].split(sep=':')[1]
                                                clause, success = parser.parse(user_args[4] + '=' + user_args[6], preferred_type)
                                                if success:
                                                    table_data = core.select(table_data, clause)
                                                    utils.save_table_data(TABLE_DATA_DIR + "/" + table_name + ".json", table_data)
                                                    core.print_table(metadata, table_name)
                                                else:
                                                    print(f"Значение {user_args[6]} нельзя использовать для столбца типа {preferred_type}.")
                                        else:
                                            print("Некорректный синтаксис. Попробуйте снова.")
                                    else:
                                        print("Введите условие для select.")
                                else:
                                    print("Некорректный синтаксис. Попробуйте снова.")
                            else:
                                table_data = core.select(table_data)
                                utils.save_table_data(TABLE_DATA_DIR + "/" + table_name + ".json", table_data)
                                core.print_table(metadata, table_name)
                        else:
                            print("Введите имя таблицы.")
                    else:
                        print("Некорректный синтаксис. Попробуйте снова.")
                else:
                    print("Некорректный синтаксис. Попробуйте снова.")

            case "update":
                if len(user_args) >= 10:
                    table_name = user_args[1]
                    if table_name in list(metadata.keys()):
                        table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
                    else:
                        print(f"Ошибка: Таблица '{table_name}' не существует.")
                        continue
                    if user_args[2] == "set" and user_args[6] == "where":
                        if user_args[4] == '=' and user_args[8] == '=':
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
                                    table_data = core.update(table_data, set_clause, where_clause)
                                    utils.save_table_data(TABLE_DATA_DIR + "/" + table_name + ".json", table_data)
                        else:
                            print("Некорректный синтаксис. Попробуйте снова.")
                    else:
                        print("Некорректный синтаксис. Попробуйте снова.")
                else:
                    print("Некорректный синтаксис. Попробуйте снова.")

            case "delete":
                if len(user_args) >= 7:
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
                                table_data = core.delete(table_data, clause)
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
