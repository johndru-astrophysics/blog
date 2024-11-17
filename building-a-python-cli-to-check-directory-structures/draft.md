# Overview

In this article we will build a simple CLI (Command Line Interface) to check the validity of a directory structure. 

In many engineering and scientific workflows, we need to pass data from one team to another, and within a team during various stages of data processing.
The software used by each team, either in-house or 3rd party, may have different requirements that we need to meet.

We will cover the following:

* Using Python dataclasses to describe the required directory structure
* Logging using Python's `logging` library: https://docs.python.org/3/library/logging.html
* Creating a CLI using the amazing `click` package: https://click.palletsprojects.com/en/stable

## Specification

We are going to create a tool called `dscheck`, short for Directory Structure Check.

The inputs to our tool will be:

1. An input configuration file, to describe the required directory structure.
1. The name of the directory to check.

The output will be a log containing:

1. A list of missing files and directories, i.e. files that are required.
1. A list of unknown or invalid files and directories, i.e. files that should not be present.

In our configuration file, we need to describe directories and files. A directory contains files and sub-directories. Both files and directories can be required or optional.

We will also use pattern matching (or wildcards) to make creating the configuration much easier.

## CLI

This is how the user will run our tool. Here is the CLI we are going to build:

```
dscheck --config <configuration file> --dir <path to dir> --log <output logfile>
```

# Example directory structure

For this article we are going to use the following directory structure, to describe a Python package repository:

```
.
|
+ .vscode/ (optional) - Directory containing optional VSCode settings
|
+ pyproject.yaml      - A Python project setup file
|
+ README.md           - Documentation for this package
|
+ src/                - Python source code
| |  
| + **/*.py           - Source files should end with *.py
|
+ test/               - Directory containing tests
  |
  + **/test_*.py      - Test files should start with test_ and end with *.py
```

`**` in the pattern means any number of directories.

# Configuration file format

Let's start by defining the dataclasses we need to build the configuration file format.

## FileStructure

A `FileStructure` has the following fields:

* `pattern`: The pattern to check against a directories' files.
* `is_optional`: Determine if this file is optional, or required.

```python
@dataclass
class FileStructure:
    """Represents the structure of a file.

    Attributes:
        pattern (str): The pattern of the file.
        desc (str): Description of the file.
        is_optional (bool): Indicates if the file is optional. Defaults to False.
    """
    pattern: str
    desc: str
    is_optional: bool = False
```

## DirStructure

A `DirStructure` has the following fields:

* `pattern`: The pattern to check against a directories' name.
* `is_optional`: Determine if this directory is optional, or required.
* `sub_dirs`: A list of sub-directories contained in this directory.
* `files`: A list of files contained in this directory.

```python
@dataclass
class DirStructure:
    """Represents the structure of a directory.

    Attributes:
        pattern (str): The pattern of the directory.
        desc (str): Description of the directory.
        is_optional (bool): Indicates if the directory is optional. Defaults to False.
        sub_dirs (List[DirStructure]): List of subdirectories. Defaults to an empty list.
        files (List[FileStructure]): List of files in the directory. Defaults to an empty list.
    """
    pattern: str
    desc: str
    is_optional: bool = False
    sub_dirs: List["DirStructure"] = field(default_factory=list)
    files: List[FileStructure] = field(default_factory=list)
```

## Configuration file for our example

Using the example directory structre, the configuration file would look like this:

```python
from dscheck import DirStructure, FileStructure

ROOT = DirStructure(
    "python_repo_example_structure",
    files=[
        FileStructure("pyproject.yaml"),
        FileStructure("README.md"),
    ],
    sub_dirs=[
        DirStructure("src",
            files=[
                FileStructure("**/*.py")
            ]
        ),
        DirStructure("test",
            files=[
                FileStructure("**/test_*.py")
            ]
        ),
        DirStructure(".vscode", is_optional=True)
    ]
)
```

NOTE: `ROOT` is a global variable we will use later in our code.

# Setting up logging

We are going to use the `logging` library, that comes with Python, to tell the use when an error is found.

The quickest way to setup logging is:

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
```

This will output all messages with a level greater than or equal to INFO. Plus set a custom message format.

Then in our code we can use:

```
logging.error("there was an error") # Outputs "ERROR: there was an error"
logging.warning("something happened") # Outputs "WARNING: something happened"
logging.info("a useful piece of information") # Outputs "WARNING: a useful piece of information"
```

You can also use logging to write to a log file, which we will cover later.

# Create a method to validate our configuration file against a dir

Let's create the following method:

```python
def validate_dir_structure(dir_structure: DirStructure, dir: str) -> None:
    ...
```

This method needs to do two validations:

1. All required (i.e. not optional) files and sub_dirs  in the `DirStructure` exist in the dir.
2. All files and sub_directories in the dir match a pattern in the `DirStructure`.

The first thing we need is a list of files and dirs in the current dir, so let's create a method:

```python
def get_files_and_dirs(dir: str) -> Tuple[List[str], List[str]]:
    """Get a list of files and directories from a directory.

    Args:
        dir (str): The directory to get the files and directories from.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing the list of files and directories.
    """
    paths = os.listdir(dir)
    files = [path for path in paths if path.is_file()]
    dirs = [path for path in paths if path.is_dir()]
    return files, dirs
```

This method returns a tuple of files and directory names in the specified directory.

Now we can check that each required FileStructure is present in the files list:

```python
def validate_required_file_structures(files: List[str], file_structures: List[FileStructure]) -> None:
    """Validate the required file structures.

    Args:
        files (List[str]): The list of files in the directory.
        file_structures (List[FileStructure]): The list of file structures to validate.
    """
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
```

This method loops through the files in the DirStructure to make sure a file matching the pattern exists.

We also need to check that each file matches a pattern:

```python
def validate_files_match_file_structures(files: List[str], file_structures: List[FileStructure]) -> None:
    """Validate the files match the file structures.

    Args:
        files (List[str]): The list of files in the directory.
        file_structures (List[FileStructure]): The list of file structures to validate.
    """
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
```

This method loops through the files and checks there is a valid FileStructure match. In essence, the opposite of `validate_required_file_structures`.

We can do the same for directories:

```python
def validate_required_dir_structures(dirs: List[str], dir_structures: List[DirStructure]) -> None:
    """Validate the required directory structures.

    Args:
        dirs (List[str]): The list of directories in the directory.
        dir_structures (List[DirStructure]): The list of directory structures to validate.
    """
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
```

The only difference between the `validate_required_file_structures` and `validate_required_dir_structures` is that `validate_required_dir_structures` also runs `validate_dir_structure` resursively on valid sub_dirs.

Then the final method to check that each sub-dir matches a pattern:

```python
def validate_dirs_match_dir_structures(dirs: List[str], dir_structures: List[DirStructure]) -> None:
    """Validate the directories match the directory structures.

    Args:
        dirs (List[str]): The list of directories in the directory.
        dir_structures (List[DirStructure]): The list of directory structures to validate.
    """
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
```

```python
def validate_dir_structure(dir_structure: DirStructure, dir: str) -> None:
    """Validate the directory structure.

    Args:
        dir_structure (DirStructure): The directory structure to validate.
        dir (str): The directory to validate.
    """
    logging.info(f"validating directory: {dir}")
    
    # Get a list of files from the current directory
    files, dirs = get_files_and_dirs(dir)

    # Check all required files are present
    validate_required_file_structures(files, dir_structure.files)

    # Check no unknown files exist
    validate_files_match_file_structures(files, dir_structure.files)

    # Check all required directories are present
    validate_required_dir_structures(dirs, dir_structure.sub_dirs)

    # Check no unknown directories exist
    validate_dirs_match_dir_structures(dirs, dir_structure.sub_dirs)
```
