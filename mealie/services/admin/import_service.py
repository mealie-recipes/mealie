from mealie.services._base_http_service import AdminHttpService

from .importer import Importer


class ImportHttpService(AdminHttpService):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.exporter = Importer()

    def get_all(self):
        pass

    def get_one(self):
        pass

    def create(self):
        pass

    def delete_one(self):
        pass
