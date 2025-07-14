import logging
import os
import shutil
import tarfile
import zipfile

logger = logging.getLogger("celery")


class FilesHandlerService:
    def __init__(self, path: str):
        self.path = path
        self.archive_extensions = {
            ".zip": self.list_zip_contents,
            ".tar": self.list_tar_contents,
            ".tar.gz": self.list_tar_contents,
            ".tgz": self.list_tar_contents,
            ".tar.bz2": self.list_tar_contents,
            ".tbz": self.list_tar_contents,
            ".tar.xz": self.list_tar_contents,
            ".txz": self.list_tar_contents,
        }
        self.is_compressed = self._is_compressed()

    def list_zip_contents(self):
        with zipfile.ZipFile(self.path, "r") as archive:
            return archive.namelist()

    def list_tar_contents(self):
        with tarfile.open(self.path, "r:*") as archive:
            return archive.getnames()

    def handle_archive(self) -> list | None:
        _extension = os.path.splitext(self.path)[1]
        _parent_directory = os.path.dirname(self.path)

        if not (_list_files_method := self.archive_extensions.get(_extension)):
            return None

        logger.info("Unpacking Archive")
        extracted_files = _list_files_method()
        shutil.unpack_archive(self.path, _parent_directory)
        logger.info("Archive Unpacked")
        os.remove(self.path)
        logger.info(f"{self.path} deleted")
        return extracted_files

    def _is_compressed(self) -> bool:
        _file_extension = os.path.splitext(self.path)[1]

        return _file_extension in self.archive_extensions.keys()
