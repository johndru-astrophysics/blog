from dscheck import DirStructure, FileStructure

"""Example directory structure for a Python repository.
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
"""

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
