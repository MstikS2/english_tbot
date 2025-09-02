def field_or_unknown(field):
    """Returns the obj field it its not empty or a string if it is empty."""
    return field if field else 'не указано'
