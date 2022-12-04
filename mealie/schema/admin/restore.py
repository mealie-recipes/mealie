from pydantic.main import BaseModel


class ImportBase(BaseModel):
    name: str
    status: bool
    exception: str | None


class RecipeImport(ImportBase):
    slug: str | None


class CommentImport(ImportBase):
    pass


class SettingsImport(ImportBase):
    pass


class GroupImport(ImportBase):
    pass


class UserImport(ImportBase):
    pass


class CustomPageImport(ImportBase):
    pass


class NotificationImport(ImportBase):
    pass
