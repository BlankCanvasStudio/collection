#!/bin/python3

def find_size(val):
    size = 0

    if isinstance(val, str):
        size = len(val.encode('utf-8'))  # Size of the string in bytes
    elif isinstance(val, int):
        size = 1
    elif isinstance(val, float):
        size = 8  # Floats are typically 8 bytes
    elif isinstance(val, bool):
        size = 1
    elif val == None:
        size = 1
    else:
        size = 8 # assume worst case

    return size

def valid_column(key):
    if key == "_start":
        return False
    elif key == "_stop":
        return False
    elif key == "result":
        return False
    elif key == "table":
        return False
    elif key == "_measurement":
        return False

    return True

