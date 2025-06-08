import logging
import os
import re
import shutil
import sys
import json
from typing import LiteralString
import zipfile
import tarfile

logger = logging.getLogger("celery")

SERIE_REGEX = (
    r"^(?P<series_name>[^ ._-]+(?:[ ._-]+[^ ._-]+)*)[ ._-]*S(?P<season>\d{1,2})[ ._-]*E(?P<episode>\d{1,"
    r"2})[ ._-]+.*\.(?P<extension>mkv|mp4|avi)$"
)


def organize_series(base_directory: str) -> None:
    # Parcourir tous les fichiers dans le répertoire
    for filename in os.listdir(base_directory):
        if match := _match(filename):
            _dest_directory = os.path.join(base_directory, _get_sub_directory(match))

            os.makedirs(_dest_directory, exist_ok=True)
            _move_file(base_directory, _dest_directory, filename)


def organize_episode(file_path: str) -> LiteralString | str | bytes:
    _filename = os.path.basename(file_path)
    _base_directory = os.path.dirname(file_path)

    if match := _match(_filename):
        _dest_directory = os.path.join(_base_directory, _get_sub_directory(match))

        os.makedirs(_dest_directory, exist_ok=True)
        return _move_file(_base_directory, _dest_directory, _filename)


def dest_file_exists(src_file_path: str) -> bool:
    _filename = os.path.basename(src_file_path)
    _base_directory = os.path.dirname(src_file_path)
    _series = _match(_filename)
    case_match = [os.path.isfile(src_file_path)]

    if _series:
        case_match.append(
            os.path.isfile(os.path.join(_base_directory, _get_sub_directory(_series), _filename))
        )
    
    return any(case_match)


def _match(filename: str) -> dict | None:
    _regex = re.compile(SERIE_REGEX, re.IGNORECASE)

    if match := _regex.match(filename):
        return match.groupdict()
    return None


def _move_file(src_directory, dest_directory, filename) -> LiteralString | str | bytes:
    src_path = os.path.join(src_directory, filename)
    dest_path = os.path.join(dest_directory, filename)

    shutil.move(src_path, dest_path)
    logger.info(f"Moved: {src_path} -> {dest_path}")
    return dest_path


def _get_sub_directory(match: dict) -> str:
    _series_name_formatted = match["series_name"].replace(" ", ".")
    _season_formatted = f'Saison.{match["season"]}'

    return os.path.join(_series_name_formatted, _season_formatted)


def is_json_serializable(value) -> bool:
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False


def list_zip_contents(path):
    with zipfile.ZipFile(path, "r") as archive:
        return archive.namelist()


def list_tar_contents(path):
    with tarfile.open(path, "r:*") as archive:
        return archive.getnames()


def is_compressed(path) -> bool:
    _archive_extensions = [
        ".zip",
        ".tar",
        ".tar.gz",
        ".tgz",
        ".tar.bz2",
        ".tbz",
        ".tar.xz",
        ".txz",
    ]
    _file_extension = os.path.splitext(path)[1]

    return _file_extension in _archive_extensions


def handle_archive(directory_path) -> None:
    _list_archive_files_methods = {
        ".zip": list_zip_contents,
        ".tar": list_tar_contents,
        ".tar.gz": list_tar_contents,
        ".tgz": list_tar_contents,
        ".tar.bz2": list_tar_contents,
        ".tbz": list_tar_contents,
        ".tar.xz": list_tar_contents,
        ".txz": list_tar_contents,
    }
    _extension = os.path.splitext(directory_path)[1]
    _parent_directory = os.path.dirname(directory_path)

    if _list_files_method := _list_archive_files_methods.get(_extension):
        logger.info("Unpacking Archive")
        _files = _list_files_method(directory_path)
        shutil.unpack_archive(directory_path, _parent_directory)
        logger.info("Archive Unpacked")
        for file in _files:
            organize_episode(os.path.join(_parent_directory, file))
        os.remove(directory_path)
        logger.info(f"{directory_path} deleted")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python organize_series.py <directory>")
        sys.exit(1)

    source_directory = sys.argv[1]
    if not os.path.isdir(source_directory):
        print(f"Error: {source_directory} is not a valid source_directory")
        sys.exit(1)

    organize_series(source_directory)
