import logging
import os
import re
import shutil
import sys
from typing import LiteralString

logger = logging.getLogger('celery')

SERIE_REGEX = (r'^(?P<series_name>[^ ._-]+(?:[ ._-]+[^ ._-]+)*)[ ._-]*S(?P<season>\d{1,2})[ ._-]*E(?P<episode>\d{1,'
               r'2})[ ._-]+.*\.(?P<extension>mkv|mp4|avi)$')


def organize_series(base_directory: str) -> None:
    # Parcourir tous les fichiers dans le répertoire
    for filename in os.listdir(base_directory):
        if match := __match(filename):
            _dest_directory = os.path.join(base_directory, __get_sub_directory(match))

            os.makedirs(_dest_directory, exist_ok=True)
            __move_file(base_directory, _dest_directory, filename)


def organize_episode(file_path: str) -> LiteralString | str | bytes:
    _filename = os.path.basename(file_path)
    _base_directory = os.path.dirname(file_path)

    if match := __match(_filename):
        _dest_directory = os.path.join(_base_directory, __get_sub_directory(match))

        os.makedirs(_dest_directory, exist_ok=True)
        return __move_file(_base_directory, _dest_directory, _filename)


def dest_file_exists(src_file_path: str) -> bool:
    _filename = os.path.basename(src_file_path)
    _base_directory = os.path.dirname(src_file_path)

    if series := __match(_filename):
        return os.path.isfile(
            os.path.join(_base_directory, __get_sub_directory(series), _filename)
        )
    return os.path.isfile(src_file_path)


def __match(filename: str) -> dict | None:
    _regex = re.compile(SERIE_REGEX, re.IGNORECASE)

    if match := _regex.match(filename):
        return match.groupdict()
    return None


def __move_file(src_directory, dest_directory, filename) -> LiteralString | str | bytes:
    src_path = os.path.join(src_directory, filename)
    dest_path = os.path.join(dest_directory, filename)

    shutil.move(src_path, dest_path)
    logger.info(f'Moved: {src_path} -> {dest_path}')
    return dest_path


def __get_sub_directory(match: dict) -> str:
    _series_name_formatted = match['series_name'].replace(' ', '.')
    _season_formatted = f'Saison.{match["season"]}'

    return os.path.join(
        _series_name_formatted,
        _season_formatted
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python organize_series.py <directory>")
        sys.exit(1)

    source_directory = sys.argv[1]
    if not os.path.isdir(source_directory):
        print(f"Error: {source_directory} is not a valid source_directory")
        sys.exit(1)

    organize_series(source_directory)
