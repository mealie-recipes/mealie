import operator

from mealie.schema.admin.backup import AllBackups, BackupFile, CreateBackup
from mealie.services._base_http_service import AdminHttpService
from mealie.services.events import create_backup_event

from .exporter import Exporter


class BackupHttpService(AdminHttpService):
    event_func = create_backup_event

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.exporter = Exporter()

    def get_all(self) -> AllBackups:
        imports = []
        for archive in self.app_dirs.BACKUP_DIR.glob("*.zip"):
            backup = BackupFile(name=archive.name, date=archive.stat().st_ctime)
            imports.append(backup)

        templates = [template.name for template in self.app_dirs.TEMPLATE_DIR.glob("*.*")]
        imports.sort(key=operator.attrgetter("date"), reverse=True)

        return AllBackups(imports=imports, templates=templates)

    def create_one(self, options: CreateBackup):
        pass

    def delete_one(self):
        pass


class BackupService:
    pass
