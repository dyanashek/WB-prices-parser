def numbers_format(value):
    """Makes a good looking numbers format."""

    return '{:,}'.format(value).replace(',', ' ')


def vendor_validator(text):
    """Validates if text is a vender."""

    try:
        int(text)
        return True
    
    except:
        return False