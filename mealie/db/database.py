from functools import lru_cache

from .data_access_layer import DatabaseAccessLayer

db = DatabaseAccessLayer()


@lru_cache
def get_database():
    return db
