import random
import string


def new_key(length=4) -> str:
    """returns a 4 character string to be used as a cache key for frontend data"""
    options = string.ascii_letters + string.digits
    return "".join(random.choices(options, k=length))
