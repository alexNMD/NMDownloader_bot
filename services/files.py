import logging
import os
import shutil
import tarfile
import zipfile

import rarfile

logger = logging.getLogger("celery")


class FilesHandlerService:
    def __init__(self, path: str):
        self.path = path
        self._register_rar_support()
        self.archive_extensions = {
            ".zip": self._list_zip_contents,
            ".tar": self._list_tar_contents,
            ".tar.gz": self._list_tar_contents,
            ".tgz": self._list_tar_contents,
            ".tar.bz2": self._list_tar_contents,
            ".tbz": self._list_tar_contents,
            ".tar.xz": self._list_tar_contents,
            ".txz": self._list_tar_contents,
            ".rar": self._list_rar_contents,
        }
        self.is_compressed = self._is_compressed()

    def handle_archive(self) -> list | None:
        _extension = os.path.splitext(self.path)[1]
        _parent_directory = os.path.dirname(self.path)

        if not (list_files_method := self.archive_extensions.get(_extension)):
            logger.warning(f"Unable to find extract method for: {_extension}")
            return None

        logger.info(f"Unpacking Archive: {self.path}")
        try:
            shutil.unpack_archive(self.path, _parent_directory)
        except Exception:
            raise
        logger.info(f"Unpacked Archive: {self.path}")

        os.remove(self.path)
        logger.info(f"{self.path} deleted")

        return [os.path.join(_parent_directory, _file) for _file in list_files_method()]

    def _list_zip_contents(self) -> list:
        with zipfile.ZipFile(self.path, "r") as archive:
            return archive.namelist()

    def _list_tar_contents(self) -> list:
        with tarfile.open(self.path, "r:*") as archive:
            return archive.getnames()

    def _list_rar_contents(self) -> list:
        with rarfile.RarFile(self.path) as archive:
            return archive.namelist()

    def _is_compressed(self) -> bool:
        _file_extension = os.path.splitext(self.path)[1]

        return _file_extension in self.archive_extensions.keys()

    @classmethod
    def _register_rar_support(cls):
        if not any(fmt[0] == "rar" for fmt in shutil.get_unpack_formats()):
            shutil.register_unpack_format("rar", [".rar"], cls._unpack_rar)

    @classmethod
    def _unpack_rar(cls, filename, extract_dir):
        try:
            with rarfile.RarFile(filename) as rf:
                rf.extractall(path=extract_dir)
        except rarfile.Error as e:
            logger.error(e)
            raise
