import prompt
import shlex
import src.primitive_db.utils as utils
import src.primitive_db.core as core


METADATA_PATH = "src/db_meta.json"

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
            case "exit":
                return None
            case "help":
                utils.show_help()
            case '':
                pass
            case _:
                print(f"Функции {user_args[0]} нет. Попробуйте снова.")
        utils.save_metadata(METADATA_PATH, metadata)
