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
                if ':' in column:
                    col_name, col_type = column.split(sep=':')[0], column.split(sep=':')[1]
                    if not col_name:
                        col_name = "col" + str(count_columns)
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
        return metadata
    else:
        print(f"Ошибка: Таблица '{table_name}' уже существует.")
        return metadata

def list_tables(metadata):
    for table_name in list(metadata.keys()):
        print(f"- {table_name}")
    return metadata

def drop_table(metadata, table_name):
    if table_name not in list(metadata.keys()):
        print(f"Ошибка: Таблица '{table_name}' не существует.")
        return metadata
    else:
        print(f"Таблица {table_name} успешно удалена.")
        metadata.pop(table_name)
        return metadata
