import gzip
import zipfile
from dataclasses import dataclass
from pathlib import Path


class ArchiveTooLargeError(ValueError):
    pass


@dataclass
class ArchiveBudget:
    """
    What one import may unpack. Pass the same budget to every archive the import opens, nested
    ones included, so a zip of zips cannot multiply the limits.
    """

    bytes_left: int
    entries_left: int
    max_file_size: int
    """
    Upper bound on one unpacked file. Importers parse documents whole (JSON, YAML, HTML), so this
    bounds their memory use.
    """

    def spend(self, zip_file: zipfile.ZipFile) -> int:
        """Charges `zip_file` against the budget and returns its unpacked size.

        Raises ArchiveTooLargeError, before anything is unpacked, when the archive is over any
        limit. The declared member sizes can be trusted for this: zipfile stops reading each
        member at its declared size.
        """
        members = zip_file.infolist()
        if len(members) > self.entries_left:
            raise ArchiveTooLargeError(f"Archive has {len(members)} entries, over the {self.entries_left} entry limit")

        for member in members:
            # Nested archives are only ever unpacked through this budget, never read into memory
            if member.file_size > self.max_file_size and not member.filename.lower().endswith(".zip"):
                raise ArchiveTooLargeError(
                    f"{member.filename} unpacks to {member.file_size} bytes, over the {self.max_file_size} byte limit"
                )

        total = sum(member.file_size for member in members)
        if total > self.bytes_left:
            raise ArchiveTooLargeError(f"Archive unpacks to {total} bytes, over the {self.bytes_left} byte limit")

        self.bytes_left -= total
        self.entries_left -= len(members)
        return total

    def read_gzip(self, path: Path) -> bytes:
        """Decompresses the gzip file at `path` into memory and charges it against the budget.

        Unlike zip, gzip does not record a trustworthy uncompressed size up front, so this reads one
        byte past the limit to find out.
        """
        limit = min(self.bytes_left, self.max_file_size)
        with gzip.open(path, "rb") as gzip_file:
            data = gzip_file.read(limit + 1)

        if len(data) > limit:
            raise ArchiveTooLargeError(f"{path.name} unpacks to more than the {limit} byte limit")

        self.bytes_left -= len(data)
        return data
