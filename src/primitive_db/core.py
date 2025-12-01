import src.primitive_db.utils as utils
import os
import src.decorators as decorators
from prettytable import PrettyTable


TABLE_DATA_DIR = "data"

@decorators.handle_db_errors
def create_table(metadata, table_name, columns=None):
    # metadata - словарь
    # metadata = {
    #   'table1': {'ID:int': [], 'column1:str': []},
    #   'table2': {'ID:int': [], 'column1:str': []} 
    #   }
    if table_name not in list(metadata.keys()):
        table_data = {}
        table_data["ID:int"] = []
        if columns:
            count_columns = 0 # Для безымянных колонн
            for column in columns:
                count_columns += 1
                # column = "name:type"
                if columns.count(column) > 1: # Дубликаты столбцов
                    print(f"Ошибка: Идентичные столбцы {column}. Попробуйте снова.")
                    return metadata
                if ':' in column:
                    col_name, col_type = column.split(sep=':')[0], column.split(sep=':')[1]
                    if not col_name:
                        col_name = "col" + str(count_columns)
                    if '=' in col_name:
                        print(f"Недопустимый символ '=' в имени столбца: {col_name}. Попробуйте снова.")
                        return metadata
                    if col_type not in ["int", "str", "bool"]:
                        print(f"Некорректное значение: {col_type}. Попробуйте снова.")
                        return metadata
                    else:
                        table_data[col_name + ':' + col_type] = []
                else:
                    print(f"Некорректная инициализация столбца: {column}.")
                    return metadata
        print(f"Таблица '{table_name}' успешно создана со столбцами: {[col_name for col_name in list(table_data.keys())]}")
        metadata[table_name] = table_data
        os.makedirs(TABLE_DATA_DIR, exist_ok=True)
        with open(TABLE_DATA_DIR + "/" + table_name + ".json", "w") as file:
            file.write(str(dict()))
        return metadata
    else:
        print(f"Ошибка: Таблица '{table_name}' уже существует.")
        return metadata

@decorators.handle_db_errors
def list_tables(metadata):
    for table_name in list(metadata.keys()):
        print(f"- {table_name}")
    return metadata

@decorators.handle_db_errors
@decorators.confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in list(metadata.keys()):
        print(f"Ошибка: Таблица '{table_name}' не существует.")
        return metadata
    else:
        print(f"Таблица {table_name} успешно удалена.")
        metadata.pop(table_name)
        os.remove(TABLE_DATA_DIR + "/" + table_name + ".json")
        return metadata

@decorators.handle_db_errors
@decorators.log_time
def insert(metadata, table_name, values):
    # <table_name>.json:
    # {
    #   '1': {'column1': <str>, 'column2': <int>},
    #   '2': {'column1': <str>, 'column2': <int>} 
    # }
    if table_name not in list(metadata.keys()):
        print(f"Ошибка: Таблица '{table_name}' не существует.")
        return {}
    else:
        table_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
        if len(list(metadata[table_name].keys())) - 1 == len(values):
            table_entry = {}
            id_entry = str(len(table_data) + 1)
            columns = list(metadata[table_name].keys())
            columns.pop(0) # Игнорируем ID:int
            for i in range(len(columns)):
                col_name = columns[i].split(sep=':')[0]
                col_type = columns[i].split(sep=':')[1]
                match col_type:
                    case "int":
                        if not isinstance(values[i], int):
                            print(f"Ошибка: тип переменной {values[i]} не соответствует типу столбца {col_name + ":" + col_type}.")
                            return table_data
                    case "str":
                        if not isinstance(values[i], str):
                            print(f"Ошибка: тип переменной {values[i]} не соответствует типу столбца {col_name + ":" + col_type}.")
                            return table_data
                    case "bool":
                        if not isinstance(values[i], bool):
                            print(f"Ошибка: тип переменной {values[i]} не соответствует типу столбца {col_name + ":" + col_type}.")
                            return table_data
                table_entry[col_name] = values[i]
            table_data[id_entry] = table_entry
            utils.save_table_data(TABLE_DATA_DIR + "/" + table_name + ".json", table_data)
            print(f"Запись с ID={id_entry} успешно добавлена в таблицу {table_name}.")
            return table_data
        else:
            print("Ошибка: Число переменных не соответствует числу столбцов.")
            return table_data

@decorators.handle_db_errors
@decorators.log_time
def select(table_data, where_clause=None):
    if where_clause:
        select_data = {}
        col_name = list(where_clause.keys())[0]
        col_value = where_clause[col_name]
        if col_name == "ID":
            for key in list(table_data.keys()):
                if int(key) == col_value:
                    select_data[key] = table_data[key]
            return select_data
        else:
            for key in list(table_data.keys()):
                if table_data[key][col_name] == col_value:
                    select_data[key] = table_data[key]
            return select_data
    else:
        return table_data

@decorators.handle_db_errors
def update(table_data, set_clause, where_clause):
    set_name = list(set_clause.keys())[0]
    set_value = set_clause[set_name]
    where_name = list(where_clause.keys())[0]
    where_value = where_clause[where_name]
    if set_name == "ID":
        print(f"Столбец {set_name} нельзя изменить.")
        return table_data
    elif where_name == "ID":
        for key in list(table_data.keys()):
            if int(key) == where_value:
                print(f"Запись с ID={key} в таблице успешно обновлена.")
                table_data[key][set_name] = set_value
        return table_data
    else:
        ids_to_update = []
        for key in list(table_data.keys()):
            if table_data[key][where_name] == where_value:
                ids_to_update.append(key)
        for key in ids_to_update:
            print(f"Запись с ID={key} в таблице успешно обновлена.")
            table_data[key][set_name] = set_value
        return table_data

@decorators.handle_db_errors
@decorators.confirm_action("удаление записи")
def delete(table_data, where_clause):
    col_name = list(where_clause.keys())[0]
    col_value = where_clause[col_name]
    if col_name == "ID":
        for key in list(table_data.keys()):
            if int(key) == col_value:
                print(f"Запись с ID={key} в таблице успешно удалена.")
                del table_data[key]
        return table_data
    else:
        ids_to_delete = []
        for key in list(table_data.keys()):
            if table_data[key][col_name] == col_value:
                ids_to_delete.append(key)
        for key in ids_to_delete:
            print(f"Запись с ID={key} в таблице успешно удалена.")
            del table_data[key]
        return table_data

@decorators.handle_db_errors
def print_table(metadata, table_name, selected_data=None):
    output_table = PrettyTable()
    if table_name not in list(metadata.keys()):
        print(f"Ошибка: Таблица '{table_name}' не существует.")
    else:
        columns = [col.split(sep=':')[0] for col in list(metadata[table_name].keys())] 
        output_table.field_names = columns
        if not selected_data:
            selected_data = utils.load_table_data(TABLE_DATA_DIR + "/" + table_name + ".json")
        for id in list(selected_data.keys()):
            row = [id]
            for column in columns:
                if column != "ID":
                    row.append(selected_data[id][column])
            output_table.add_row(row)
        print(output_table)
