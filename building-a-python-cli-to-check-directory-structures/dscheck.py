from dataclasses import dataclass, field
from fnmatch import fnmatch
import logging
import os
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@dataclass
class FileStructure:
    """Represents the structure of a file.

    Attributes:
        pattern (str): The pattern of the file.
        is_optional (bool): Indicates if the file is optional. Defaults to False.
    """

    pattern: str
    is_optional: bool = False


@dataclass
class DirStructure:
    """Represents the structure of a directory.

    Attributes:
        pattern (str): The pattern of the directory.
        is_optional (bool): Indicates if the directory is optional. Defaults to False.
        sub_dirs (List[DirStructure]): List of subdirectories. Defaults to an empty list.
        files (List[FileStructure]): List of files in the directory. Defaults to an empty list.
    """

    pattern: str
    is_optional: bool = False
    sub_dirs: List["DirStructure"] = field(default_factory=list)
    files: List[FileStructure] = field(default_factory=list)


def get_files_and_dirs(dir: str) -> Tuple[List[str], List[str]]:
    """Get a list of files and directories from a directory.

    Args:
        dir (str): The directory to get the files and directories from.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing the list of files and directories.
    """
    paths = os.listdir(dir)
    files = [path for path in paths if Path(os.path.sep.join([dir, path])).is_file()]
    dirs = [path for path in paths if Path(os.path.sep.join([dir, path])).is_dir()]
    return files, dirs


def validate_required_file_structures(
    files: List[str], file_structures: List[FileStructure]
) -> bool:
    """Validate the required file structures.

    Args:
        files (List[str]): The list of files in the directory.
        file_structures (List[FileStructure]): The list of file structures to validate.
    """
    result = True
    for file_structure in file_structures:

        # Skip optional files
        if file_structure.is_optional:
            continue

        # Search for the file pattern
        found = False
        for file in files:
            if fnmatch(file, file_structure.pattern):
                found = True
                break

        # If not found, log an error
        if not found:
            logging.error(f"missing file: {file_structure.pattern}")
            result = False

    return result


def validate_files_match_file_structures(
    files: List[str], file_structures: List[FileStructure]
) -> bool:
    """Validate the files match the file structures.

    Args:
        files (List[str]): The list of files in the directory.
        file_structures (List[FileStructure]): The list of file structures to validate.
    """
    result = True
    for file in files:

        # Search for the file pattern
        found = False
        for file_structure in file_structures:
            if fnmatch(file, file_structure.pattern):
                found = True
                break

        # If not found, log an error
        if not found:
            logging.error(f"unexpected file: {file}")
            result = False

    return result


def validate_required_dir_structures(
    dirs: List[str], dir_structures: List[DirStructure]
) -> bool:
    """Validate the required directory structures.

    Args:
        dirs (List[str]): The list of directories in the directory.
        dir_structures (List[DirStructure]): The list of directory structures to validate.
    """
    result = True
    for dir_structure in dir_structures:

        # Skip optional directories
        if dir_structure.is_optional:
            continue

        # Search for the directory pattern
        found = False
        for dir in dirs:
            if fnmatch(dir, dir_structure.pattern):
                # Recursively validate the directory structure
                validate_dir_structure(dir_structure, dir)
                found = True
                break

        # If not found, log an error
        if not found:
            logging.error(f"missing directory: {dir_structure.pattern}")
            result = False

    return result


def validate_dirs_match_dir_structures(
    dirs: List[str], dir_structures: List[DirStructure]
) -> bool:
    """Validate the directories match the directory structures.

    Args:
        dirs (List[str]): The list of directories in the directory.
        dir_structures (List[DirStructure]): The list of directory structures to validate.
    """
    result = True
    for dir in dirs:

        # Search for the directory pattern
        found = False
        for dir_structure in dir_structures:
            if fnmatch(dir, dir_structure.pattern):
                found = True
                break

        # If not found, log an error
        if not found:
            logging.error(f"unexpected directory: {dir}")
            result = False
    return result


def validate_dir_structure(dir_structure: DirStructure, dir: str) -> bool:
    """Validate the directory structure.

    Args:
        dir_structure (DirStructure): The directory structure to validate.
        dir (str): The directory to validate.
    """
    logging.info(f"validating directory: {dir}")

    # Get a list of files from the current directory
    files, dirs = get_files_and_dirs(dir)

    result = True

    # Check all required files are present
    result &= validate_required_file_structures(files, dir_structure.files)

    # Check no unknown files exist
    result &= validate_files_match_file_structures(files, dir_structure.files)

    # Check all required directories are present
    result &= validate_required_dir_structures(dirs, dir_structure.sub_dirs)

    # Check no unknown directories exist
    result &= validate_dirs_match_dir_structures(dirs, dir_structure.sub_dirs)

    return result
