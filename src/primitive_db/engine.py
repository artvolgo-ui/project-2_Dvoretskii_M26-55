import shlex
from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

DB_FILE = "db_meta.json"


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print("\n***База данных***")
    print_help()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
            if not user_input:
                continue

            args = shlex.split(user_input, posix=False)
            command = args[0].lower()

            metadata = load_metadata(DB_FILE)

            if command == "exit":
                print("Выход из программы.")
                break
            elif command == "help":
                print_help()
            elif command == "list_tables":
                if not metadata:
                    print("Список таблиц пуст.")
                else:
                    for table_name in metadata.keys():
                        print(f"- {table_name}")
            elif command == "create_table":
                if len(args) < 3:
                    print("Ошибка: Недостаточно аргументов для create_table.")
                    continue
                table_name = args[1]
                columns = args[2:]
                new_metadata = create_table(metadata, table_name, columns)
                if new_metadata != metadata or table_name in new_metadata:
                    save_metadata(DB_FILE, new_metadata)
            elif command == "drop_table":
                if len(args) < 2:
                    print("Ошибка: Недостаточно аргументов для drop_table.")
                    continue
                table_name = args[1]
                new_metadata = drop_table(metadata, table_name)
                save_metadata(DB_FILE, new_metadata)
            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except (KeyboardInterrupt, EOFError):
            print("\nВыход...")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")