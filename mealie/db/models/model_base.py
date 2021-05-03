import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()


class BaseMixins:
    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)
