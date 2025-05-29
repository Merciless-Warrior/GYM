def get_level_by_count(count):
    if count <= 3:
        return 1
    elif count <= 5:
        return 2
    elif count <= 10:
        return 3
    elif count <= 16:
        return 4
    elif count <= 21:
        return 5
    elif count <= 25:
        return 6
    elif count <= 30:
        return 7
    elif count <= 35:
        return 8
    elif count <= 40:
        return 9
    elif count <= 45:
        return 10
    return 11
