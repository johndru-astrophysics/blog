import unittest
import os
from pathlib import Path
import tempfile
from dscheck import (
    DirStructure,
    FileStructure,
    get_files_and_dirs,
    validate_files_match_file_structures,
    validate_required_dir_structures,
    validate_required_file_structures,
)


class TestGetFilesAndDirs(unittest.TestCase):
    def test_simple(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(f"{temp_dir}/test").mkdir()
            Path(f"{temp_dir}/test2").mkdir()
            Path(f"{temp_dir}/test3.txt").touch()
            Path(f"{temp_dir}/test4.txt").touch()
            self.assertEqual(
                get_files_and_dirs(temp_dir),
                (["test3.txt", "test4.txt"], ["test", "test2"]),
            )


class TestValidateRequiredFileStructures(unittest.TestCase):
    def test_all_valid(self):
        self.assertTrue(
            validate_required_file_structures(
                ["test.txt", "test2.txt"], [FileStructure("*.txt")]
            )
        )

    def test_optional_missing(self):
        self.assertTrue(
            validate_required_file_structures(
                ["README.txt"],
                [FileStructure("README.txt"), FileStructure("*.txt", is_optional=True)],
            )
        )

    def test_optional_exists(self):
        self.assertTrue(
            validate_required_file_structures(
                ["README.txt", "optional.txt"],
                [FileStructure("README.txt"), FileStructure("*.txt", is_optional=True)],
            )
        )

    def test_missing(self):
        self.assertFalse(
            validate_required_file_structures(
                ["test.txt"], [FileStructure("required.txt")]
            )
        )


class TestValidateFilesMatchFileStructures(unittest.TestCase):
    def test_all_valid(self):
        self.assertTrue(
            validate_files_match_file_structures(
                ["test.txt", "test2.txt"], [FileStructure("*.txt")]
            )
        )

    def test_missing(self):
        self.assertFalse(
            validate_files_match_file_structures(
                ["test.txt", "test2.txt"], [FileStructure("required.txt")]
            )
        )


class TestValidateRequiredDirStructures(unittest.TestCase):
    def test_all_valid(self):
        self.assertTrue(
            validate_required_dir_structures(["test", "test2"], [DirStructure("*")])
        )

    def test_optional_missing(self):
        self.assertTrue(
            validate_required_dir_structures(
                ["test"],
                [DirStructure("test"), DirStructure("*", is_optional=True)],
            )
        )

    def test_optional_exists(self):
        self.assertTrue(
            validate_required_dir_structures(
                ["test", "optional"],
                [DirStructure("test"), DirStructure("*", is_optional=True)],
            )
        )

    def test_missing(self):
        self.assertFalse(
            validate_required_dir_structures(["test"], [DirStructure("required")])
        )


if __name__ == "__main__":
    unittest.main()
