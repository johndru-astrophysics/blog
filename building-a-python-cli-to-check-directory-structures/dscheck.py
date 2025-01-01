from dataclasses import dataclass, field
from fnmatch import fnmatch
import logging
import os
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@dataclass
class FilePattern:
    """Represents the structure of a file or directory.

    Attributes:
        pattern (str): The pattern of the file or directory.
        is_optional (bool): Indicates if the item is optional. Defaults to False.
        is_dir (bool): Indicates if the item is a directory. Defaults to False.
        sub_items (List[FilePattern]): List of sub-items (for directories). Defaults to an empty list.
    """

    expression: str
    is_optional: bool = False
    is_dir: bool = False
    sub_items: List["FilePattern"] = field(default_factory=list)


def get_files_and_dirs(dir: str) -> Tuple[List[str], List[str]]:
    """Get a list of files and directories from a directory."""
    paths = os.listdir(dir)
    files = [path for path in paths if Path(os.path.join(dir, path)).is_file()]
    dirs = [path for path in paths if Path(os.path.join(dir, path)).is_dir()]
    return files, dirs


def validate_patterns(
    items: List[str], patterns: List[FilePattern], item_type: str
) -> bool:
    """Validate the required patterns and match existing items."""
    result = True

    # Check required patterns
    for pattern in patterns:
        if not pattern.is_optional and not any(
            fnmatch(item, pattern.expression) for item in items
        ):
            logging.error(f"missing {item_type}: {pattern.expression}")
            result = False

    # Check for unexpected items
    for item in items:
        if not any(fnmatch(item, pattern.expression) for pattern in patterns):
            logging.error(f"unexpected {item_type}: {item}")
            result = False

    return result


def validate_dir_structure(dir_pattern: FilePattern, dir: str) -> bool:
    """Validate the directory structure."""
    logging.info(f"validating directory: {dir}")

    files, dirs = get_files_and_dirs(dir)

    result = True
    result &= validate_patterns(
        files, [item for item in dir_pattern.sub_items if not item.is_dir], "file"
    )
    result &= validate_patterns(
        dirs, [item for item in dir_pattern.sub_items if item.is_dir], "directory"
    )

    # Recursively validate subdirectories
    for subdir in dirs:
        for subdir_pattern in [item for item in dir_pattern.sub_items if item.is_dir]:
            if fnmatch(subdir, subdir_pattern.expression):
                result &= validate_dir_structure(
                    subdir_pattern, os.path.join(dir, subdir)
                )
                break

    return result
