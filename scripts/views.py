def field_or_unknown(field):
    """Returns the obj field it its not empty or a string if it is empty."""
    return field if field else 'не указано'


def list_names(objs):
    """Gets a list of db objects and returns a str of objects's names."""
    name_list = ''
    for number, obj in enumerate(objs):
        name_list += f'{number + 1}) {obj.name}\n'
    return name_list
