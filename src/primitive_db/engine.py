import shlex

from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_set, parse_values, parse_where
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

DB_FILE = "db_meta.json"
cache = create_cacher()


def print_help():
    """Выводит справку по всем доступным командам."""
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"
        " - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение>"
        " - прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1>"
        " where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение>"
        " - удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Запускает главный цикл приложения для обработки команд пользователя."""
    print("\n***База данных***")
    print_help()

    while True:
        try:
            user_input = input(">>> Введите команду: ").strip()
            if not user_input:
                continue

            args = shlex.split(user_input, posix=False)
            command = args[0].lower()

            metadata = load_metadata(DB_FILE)

            if command == "exit":
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
                    continue
                table_name = args[1]
                columns = args[2:]
                new_metadata = create_table(metadata, table_name, columns)
                if new_metadata is not None:
                    save_metadata(DB_FILE, new_metadata)
                
            elif command == "drop_table":
                if len(args) < 2:
                    continue
                table_name = args[1]
                new_metadata = drop_table(metadata, table_name)
                if new_metadata is not None:
                    save_metadata(DB_FILE, new_metadata)
                    cache.clear()
                
            elif command == "info":
                table_name = args[1]
                if table_name in metadata:
                    cols = ", ".join(metadata[table_name]["columns"])
                    data = load_table_data(table_name)
                    print(f"Таблица: {table_name}")
                    print(f"Столбцы: {cols}")
                    print(f"Количество записей: {len(data)}")
                else:
                    print(f'Ошибка: Таблицы "{table_name}" не существует.')

            elif command == "insert":
                try:
                    table_name = user_input.split("into")[1].split("values")[0].strip()
                except IndexError:
                    print("Ошибка: неверный синтаксис insert.")
                    continue

                start_idx = user_input.find("(")
                end_idx = user_input.rfind(")")
                if start_idx == -1 or end_idx == -1:
                    print("Ошибка: неверный синтаксис insert. Нужны скобки.")
                    continue

                values_str = user_input[start_idx:end_idx+1]
                values = parse_values(values_str)
                
                table_data = insert(metadata, table_name, values)
                
                if table_data is not None:
                    save_table_data(table_name, table_data)
                    cache.clear()

            elif command == "select" and len(args) >= 3 and args[1] == "from":
                table_name = args[2]
                if table_name not in metadata:
                    print(f'Ошибка: Таблицы "{table_name}" не существует.')
                    continue
                
                where_clause = {}
                if "where" in user_input:
                    where_str = user_input.split("where", 1)[1]
                    where_clause = parse_where(where_str)
                
                cache_key = f"{table_name}_{str(where_clause)}"
                
                result = cache(
                    cache_key, 
                    lambda: select(load_table_data(table_name), where_clause)
                )
                
                if not result:
                    print("Записей не найдено.")
                else:
                    pt = PrettyTable()
                    cols = [c.split(":")[0] for c in metadata[table_name]["columns"]]
                    pt.field_names = cols
                    for row in result:
                        pt.add_row([row.get(c) for c in cols])
                    print(pt)

            elif command == "update" and len(args) >= 4:
                table_name = args[1]
                if "set" not in user_input or "where" not in user_input:
                    print("Ошибка: Неверный синтаксис update.")
                    continue
                
                set_str = user_input.split("set", 1)[1].split("where")[0]
                where_str = user_input.split("where", 1)[1]
                
                set_clause = parse_set(set_str)
                where_clause = parse_where(where_str)
                
                table_data = load_table_data(table_name)
                new_data = update(table_data, set_clause, where_clause)
                
                if new_data is not None:
                    save_table_data(table_name, new_data)
                    cache.clear()

            elif command == "delete" and len(args) >= 4 and args[1] == "from":
                table_name = args[2]
                if "where" not in user_input:
                    print("Ошибка: Неверный синтаксис delete.")
                    continue
                
                where_str = user_input.split("where", 1)[1]
                where_clause = parse_where(where_str)
                
                table_data = load_table_data(table_name)
                new_data = delete(table_data, where_clause)
                
                if new_data is not None:
                    save_table_data(table_name, new_data)
                    cache.clear()
                    
            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except (KeyboardInterrupt, EOFError):
            print("\nВыход...")
            break