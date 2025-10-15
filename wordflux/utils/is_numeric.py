def is_numeric(text):
    """Kiểm tra xem text có phải là số không."""
    try:
        float(text)
        return True
    except ValueError:
        return False