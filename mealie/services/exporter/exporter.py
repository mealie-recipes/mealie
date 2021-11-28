import shutil
import zipfile
from pathlib import Path
from uuid import UUID, uuid4

from mealie.schema.user import GroupInDB

from .._base_service import BaseService
from ._abc_exporter import ABCExporter


class Exporter(BaseService):
    def __init__(self, group_id: UUID, temp_zip: Path, exporters: list[ABCExporter]) -> None:
        super().__init__()

        self.group_id = group_id
        self.temp_path = temp_zip
        self.exporters = exporters

    def run(self) -> Path:
        # Create Zip File
        self.temp_path.touch()

        # Open Zip File
        with zipfile.ZipFile(self.temp_path, "w") as zip:
            for exporter in self.exporters:
                exporter.export(zip)

        export_path = GroupInDB.get_export_directory(self.group_id) / f"{uuid4()}.zip"

        shutil.copy(self.temp_path, export_path)

        return Path
