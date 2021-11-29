import datetime
import shutil
import zipfile
from pathlib import Path
from uuid import UUID, uuid4

from mealie.db.database import Database
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.user import GroupInDB
from mealie.utils.fs_stats import pretty_size

from .._base_service import BaseService
from ._abc_exporter import ABCExporter


class Exporter(BaseService):
    def __init__(self, group_id: UUID, temp_zip: Path, exporters: list[ABCExporter]) -> None:
        super().__init__()

        self.group_id = group_id
        self.temp_path = temp_zip
        self.exporters = exporters

    def run(self, db: Database) -> GroupDataExport:
        # Create Zip File
        self.temp_path.touch()

        # Open Zip File
        with zipfile.ZipFile(self.temp_path, "w") as zip:
            for exporter in self.exporters:
                exporter.export(zip)

        export_id = uuid4()

        export_path = GroupInDB.get_export_directory(self.group_id) / f"{export_id}.zip"

        shutil.copy(self.temp_path, export_path)

        group_data_export = GroupDataExport(
            id=export_id,
            group_id=self.group_id,
            path=str(export_path),
            name="Data Export",
            size=pretty_size(export_path.stat().st_size),
            filename=export_path.name,
            expires=datetime.datetime.now() + datetime.timedelta(days=1),
        )

        db.group_exports.create(group_data_export)

        return group_data_export
