def parse(expression, preferred_type="str"):
    '''
    На вход:
    строка "col_name = col_value"
    или "col_name=col_value"
    На выход: 
    {"col_name": col_value}, parse_success
    '''
    col_name = expression.split('=')[0]
    col_value = expression.split('=')[1]
    parse_success = True
    match preferred_type:
        case "int":
            try:
                col_value = int(col_value)
            except ValueError:
                parse_success = False
        case "bool":
            if col_value.lower() == "true":
                col_value = True
            elif col_value.lower() == "false":
                col_value = False
            else:
                parse_success = False
        case "str":
            pass

    return {col_name: col_value}, parse_success

def parse_values(values, columns):
    '''
    In:  ['123', ...], ['col1:int', ...]
    Out: [123, ...]
    '''
    parsed_values = []
    for i in range(len(values)):
        preferred_type = columns[i].split(sep=':')[1]
        match preferred_type:
            case "int":
                try:
                    parsed_values.append(int(values[i]))
                except ValueError:
                    parsed_values.append(values[i])
            case "bool":
                if values[i].lower() == "true":
                    parsed_values.append(True)
                elif values[i].lower() == "false":
                    parsed_values.append(False)
                else:
                    parsed_values.append(values[i])
            case "str":
                parsed_values.append(values[i])
    return parsed_values
