import unittest
import os
from pathlib import Path
import tempfile
import logging
from dscheck import (
    FilePattern,
    get_files_and_dirs,
    validate_patterns,
    validate_dir_structure,
)


class TestDSCheck(unittest.TestCase):
    def setUp(self):
        # Disable logging for tests
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        # Re-enable logging after tests
        logging.disable(logging.NOTSET)

    def test_get_files_and_dirs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(f"{temp_dir}/test").mkdir()
            Path(f"{temp_dir}/test2").mkdir()
            Path(f"{temp_dir}/test3.txt").touch()
            Path(f"{temp_dir}/test4.txt").touch()
            self.assertEqual(
                get_files_and_dirs(temp_dir),
                (["test3.txt", "test4.txt"], ["test", "test2"]),
            )

    def test_validate_patterns_files(self):
        files = ["test1.txt", "test2.txt", "test3.py"]
        patterns = [
            FilePattern("*.txt"),
            FilePattern("*.py"),
        ]
        self.assertTrue(validate_patterns(files, patterns, "file"))

    def test_validate_patterns_missing_file(self):
        files = ["test1.txt", "test2.txt"]
        patterns = [
            FilePattern("*.txt"),
            FilePattern("*.py"),
        ]
        self.assertFalse(validate_patterns(files, patterns, "file"))

    def test_validate_patterns_unexpected_file(self):
        files = ["test1.txt", "test2.txt", "test3.py", "unexpected.md"]
        patterns = [
            FilePattern("*.txt"),
            FilePattern("*.py"),
        ]
        self.assertFalse(validate_patterns(files, patterns, "file"))

    def test_validate_dir_structure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory structure
            Path(f"{temp_dir}/src").mkdir()
            Path(f"{temp_dir}/src/main.py").touch()
            Path(f"{temp_dir}/tests").mkdir()
            Path(f"{temp_dir}/tests/test_main.py").touch()
            Path(f"{temp_dir}/README.md").touch()

            # Define the expected structure
            dir_pattern = FilePattern(
                "root",
                is_dir=True,
                sub_items=[
                    FilePattern(
                        "src",
                        is_dir=True,
                        sub_items=[
                            FilePattern("*.py"),
                        ],
                    ),
                    FilePattern(
                        "tests",
                        is_dir=True,
                        sub_items=[
                            FilePattern("test_*.py"),
                        ],
                    ),
                    FilePattern("README.md"),
                ],
            )

            self.assertTrue(validate_dir_structure(dir_pattern, temp_dir))

    def test_validate_dir_structure_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory structure with a missing file
            Path(f"{temp_dir}/src").mkdir()
            Path(f"{temp_dir}/src/main.py").touch()
            Path(f"{temp_dir}/tests").mkdir()
            Path(f"{temp_dir}/tests/test_main.py").touch()
            # README.md is missing

            # Define the expected structure
            dir_pattern = FilePattern(
                "root",
                is_dir=True,
                sub_items=[
                    FilePattern(
                        "src",
                        is_dir=True,
                        sub_items=[
                            FilePattern("*.py"),
                        ],
                    ),
                    FilePattern(
                        "tests",
                        is_dir=True,
                        sub_items=[
                            FilePattern("test_*.py"),
                        ],
                    ),
                    FilePattern("README.md"),
                ],
            )

            self.assertFalse(validate_dir_structure(dir_pattern, temp_dir))


if __name__ == "__main__":
    unittest.main()
