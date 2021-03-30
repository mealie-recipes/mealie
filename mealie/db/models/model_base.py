import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()


class BaseMixins:
    def _pass_on_me():
        pass
