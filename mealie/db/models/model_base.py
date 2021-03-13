from typing import List

import sqlalchemy.ext.declarative as dec
from sqlalchemy.orm.session import Session

SqlAlchemyBase = dec.declarative_base()


class BaseMixins:
    @staticmethod
    def _sql_remove_list(session: Session, list_of_tables: list, parent_id):
        for table in list_of_tables:
            session.query(table).filter(parent_id == parent_id).delete()

    @staticmethod
    def _flatten_dict(list_of_dict: List[dict]):
        finalMap = {}
        for d in list_of_dict:

            finalMap.update(d.dict())

        return finalMap


# ! Don't use!
def update_generics(func):
    """An experimental function that does the initial work of updating attributes on a class
    and passing "complex" data types recuresively to an "self.update()" function if one exists.

    Args:
        func ([type]): [description]
    """

    def wrapper(class_object, session, new_data: dict):
        complex_attributed = {}
        for key, value in new_data.items():

            attribute = getattr(class_object, key, None)

            if attribute and isinstance(attribute, SqlAlchemyBase):
                attribute.update(session, value)

            elif attribute:
                setattr(class_object, key, value)
        print("Complex", complex_attributed)
        func(class_object, complex_attributed)

    return wrapper
