import sqlalchemy.ext.declarative as dec
from requests import Session

SqlAlchemyBase = dec.declarative_base()


class BaseMixins:
    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)

    @classmethod
    def get_ref(cls_type, session: Session, match_value: str, match_attr: str = "id"):
        eff_ref = getattr(cls_type, match_attr)
        return session.query(cls_type).filter(eff_ref == match_value).one_or_none()
