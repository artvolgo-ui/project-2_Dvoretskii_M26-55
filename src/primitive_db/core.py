from primitive_db.utils import load_table_data


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    valid_types = {"int", "str", "bool"}
    parsed_columns = []
    
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        
        col_name, col_type = col.split(":", 1)
        
        if col_type not in valid_types:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
            
        parsed_columns.append(f"{col_name}:{col_type}")

    parsed_columns.insert(0, "ID:int")
    
    metadata[table_name] = {"columns": parsed_columns}
    
    cols_str = ", ".join(parsed_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata



def insert(metadata: dict, table_name: str, values: list) -> list:
    if table_name not in metadata:
        print(f'Ошибка: Таблицы "{table_name}" не существует.')
        return []

    table_data = load_table_data(table_name)
    columns = metadata[table_name]["columns"]
    
    data_columns = columns[1:]
    
    if len(values) != len(data_columns):
        print(f"Ошибка: Ожидалось {len(data_columns)} значений, "
              f"получено {len(values)}.")
        return table_data

    record = {}
    for i, col_def in enumerate(data_columns):
        col_name, col_type = col_def.split(":")
        val = values[i]
        
        if col_type == "int" and not isinstance(val, int):
            print(f"Ошибка типа: столбец {col_name} ожидает int.")
            return table_data
        if col_type == "str" and not isinstance(val, str):
            print(f"Ошибка типа: столбец {col_name} ожидает str.")
            return table_data
        if col_type == "bool" and not isinstance(val, bool):
            print(f"Ошибка типа: столбец {col_name} ожидает bool.")
            return table_data
            
        record[col_name] = val

    new_id = 1
    if table_data:
        new_id = max(r.get("ID", 0) for r in table_data) + 1
    record["ID"] = new_id

    table_data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_data: list, where_clause: dict = None) -> list:
    if not where_clause:
        return table_data
    return [
        row for row in table_data 
        if all(row.get(k) == v for k, v in where_clause.items())
    ]



def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    updated_count = 0
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            row.update(set_clause)
            updated_count += 1
    
    if updated_count > 0:
        print("Запись успешно обновлена.")
    else:
        print("Записей, подходящих под условие, не найдено.")
    return table_data


def delete(table_data: list, where_clause: dict) -> list:
    new_data = []
    deleted_count = 0
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            deleted_count += 1
            print(f'Запись с ID={row.get("ID")} успешно удалена из таблицы.')
        else:
            new_data.append(row)
            
    if deleted_count == 0:
        print("Записей, подходящих под условие, не найдено.")
    return new_data