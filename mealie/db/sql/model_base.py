import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()


class BaseMixins:
    @staticmethod
    def _sql_remove_list(session, list_of_tables: list, parent_id):
        """
        docstring
        """
        for table in list_of_tables:
            session.query(table).filter_by(parent_id=parent_id).delete()

    @staticmethod
    def _flatten_dict(list_of_dict: list[dict]):
        finalMap = {}
        for d in list_of_dict:

            finalMap.update(d.dict())

        return finalMap
