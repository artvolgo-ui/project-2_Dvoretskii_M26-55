import re


def parse_values(values_str: str) -> list:
    inner = values_str.strip("()")
    
    raw_values = re.findall(r'"[^"]*"|\S+', inner)
    
    result = []
    for val in raw_values:
        val = val.strip().strip(",")
        if not val:
            continue
        if val.lower() == "true":
            result.append(True)
        elif val.lower() == "false":
            result.append(False)
        elif val.startswith('"') and val.endswith('"'):
            result.append(val[1:-1])  
        else:
            try:
                result.append(int(val))
            except ValueError:
                result.append(val)
    return result


def parse_where(where_str: str) -> dict:
    if not where_str:
        return {}
    
    match = re.match(r"(\w+)\s*=\s*(.+)", where_str.strip())
    if not match:
        raise ValueError("Некорректное условие where")
    
    col, val = match.groups()
    val = val.strip()
    
    if val.lower() == "true":
        val = True
    elif val.lower() == "false":
        val = False
    elif val.startswith('"') and val.endswith('"'):
        val = val[1:-1]
    else:
        try:
            val = int(val)
        except ValueError:
            pass
            
    return {col: val}


def parse_set(set_str: str) -> dict:
    parts = set_str.split(",")
    result = {}
    for part in parts:
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip()
        v = v.strip()
        
        if v.lower() == "true":
            v = True
        elif v.lower() == "false":
            v = False
        elif v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        else:
            try:
                v = int(v)
            except ValueError:
                pass
        result[k] = v
    return result