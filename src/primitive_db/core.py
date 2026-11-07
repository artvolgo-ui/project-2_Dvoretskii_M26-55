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
    
    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(parsed_columns)}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata