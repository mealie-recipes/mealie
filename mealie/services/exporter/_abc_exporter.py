import zipfile
from abc import abstractmethod, abstractproperty
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from uuid import UUID

from pydantic import BaseModel

from mealie.core.root_logger import get_logger
from mealie.repos.all_repositories import AllRepositories
from mealie.schema.reports.reports import ReportEntryCreate

from .._base_service import BaseService


@dataclass
class ExportedItem:
    """
    Exported items are the items provided by items() call in an concrete exporter class
    Where the items are used to write data to the zip file. Models should derive from the
    BaseModel class OR provide a .json method that returns a json string.
    """

    model: BaseModel
    name: str


class ABCExporter(BaseService):
    write_dir_to_zip: Callable[[Path, str, Optional[set[str]]], None] | None

    def __init__(self, db: AllRepositories, group_id: UUID) -> None:
        self.logger = get_logger()
        self.db = db
        self.group_id = group_id

        super().__init__()

    @abstractproperty
    def destination_dir(self) -> str:
        ...

    @abstractmethod
    def items(self) -> Iterator[ExportedItem]:
        ...

    def _post_export_hook(self, _: BaseModel) -> None:
        pass

    def export(self, zip: zipfile.ZipFile) -> list[ReportEntryCreate]:  # type: ignore
        """
        Export takes in a zip file and exports the recipes to it. Note that the zip
        file open/close is NOT handled by this method. You must handle it yourself.

        Args:
            zip (zipfile.ZipFile): Zip file destination

        Returns:
            list[ReportEntryCreate]:
        """
        self.write_dir_to_zip = self.write_dir_to_zip_func(zip)

        for item in self.items():
            if item is None:
                self.logger.error("Failed to export item. no item found")
                continue

            zip.writestr(f"{self.destination_dir}/{item.name}/{item.name}.json", item.model.json())

            self._post_export_hook(item.model)

        self.write_dir_to_zip = None

    def write_dir_to_zip_func(self, zip: zipfile.ZipFile):
        """Returns a recursive function that writes a directory to a zip file.

        Args:
            zip (zipfile.ZipFile):
        """

        def func(source_dir: Path, dest_dir: str, ignore_ext: set[str] = None) -> None:
            ignore_ext = ignore_ext or set()

            for source_file in source_dir.iterdir():
                if source_file.is_dir():
                    func(source_file, f"{dest_dir}/{source_file.name}")
                elif source_file.suffix not in ignore_ext:
                    zip.write(source_file, f"{dest_dir}/{source_file.name}")

        return func
