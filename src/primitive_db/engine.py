import prompt


def welcome():
    user_command = prompt.string(
        "\n***\n"
        "<command> exit - выйти из программы\n"
        "<command> help - справочная информация\n"
        "Введите команду: ")
    return user_command
