import os

from primitive_db.constants import DATA_DIR, VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создает новую таблицу в метаданных, проверяя типы и добавляя ID."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    parsed_columns = []
    
    for col in columns:
        if ":" not in col:
            raise ValueError(f"Некорректное значение: {col}.")
        
        col_name, col_type = col.split(":", 1)
        
        if col_type not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {col}.")
            
        parsed_columns.append(f"{col_name}:{col_type}")

    parsed_columns.insert(0, "ID:int")
    
    metadata[table_name] = {"columns": parsed_columns}
    
    table_filepath = f"{DATA_DIR}/{table_name}.json"
    if os.path.exists(table_filepath):
        os.remove(table_filepath)
    
    cols_str = ", ".join(parsed_columns)
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных и стирает её файл данных."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    
    table_filepath = f"{DATA_DIR}/{table_name}.json"
    if os.path.exists(table_filepath):
        os.remove(table_filepath)
        
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list) -> list:
    """Добавляет новую запись в таблицу, валидируя типы данных и генерируя ID."""
    if table_name not in metadata:
        raise KeyError(f'Таблицы "{table_name}" не существует.')

    table_data = load_table_data(table_name)
    columns = metadata[table_name]["columns"]
    
    data_columns = columns[1:]
    
    if len(values) != len(data_columns):
        raise ValueError(
            f"Ожидалось {len(data_columns)} значений, получено {len(values)}."
        )

    record = {}
    for i, col_def in enumerate(data_columns):
        col_name, col_type = col_def.split(":")
        val = values[i]
        
        if col_type == "int" and not isinstance(val, int):
            raise ValueError(f"Столбец {col_name} ожидает int.")
        if col_type == "str" and not isinstance(val, str):
            raise ValueError(f"Столбец {col_name} ожидает str.")
        if col_type == "bool" and not isinstance(val, bool):
            raise ValueError(f"Столбец {col_name} ожидает bool.")
            
        record[col_name] = val

    new_id = 1
    if table_data:
        new_id = max(r.get("ID", 0) for r in table_data) + 1
    record["ID"] = new_id

    table_data.append(record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_data: list, where_clause: dict = None) -> list:
    """Возвращает записи таблицы, опционально фильтруя их по условию."""
    if not where_clause:
        return table_data
    return [
        row for row in table_data 
        if all(row.get(k) == v for k, v in where_clause.items())
    ]


@handle_db_errors
def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """Обновляет значения в записях, которые соответствуют условию."""
    updated_count = 0
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            row.update(set_clause)
            updated_count += 1
    
    if updated_count > 0:
        print("Запись успешно обновлена.")
    else:
        raise ValueError("Записей, подходящих под условие, не найдено.")
    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: list, where_clause: dict) -> list:
    """Удаляет записи, соответствующие условию, после подтверждения."""
    new_data = []
    deleted_count = 0
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            deleted_count += 1
            print(f'Запись с ID={row.get("ID")} успешно удалена из таблицы.')
        else:
            new_data.append(row)
            
    if deleted_count == 0:
        raise ValueError("Записей, подходящих под условие, не найдено.")
    return new_data