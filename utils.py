def type_convert(value, type_name):
    if not type_name:
        return value
    if type_name == "str":
        return str(value)
    if type_name == "int":
        return int(value)
    if type_name == "num" or type_name == "float":
        return float(value)
