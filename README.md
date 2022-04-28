# Camera Trap Desktop

tkinter GUI

## Development

### Requirements

- Python 3.6+ 

Note: Python 3.9.6 cannot be used on Windows 7 or earlier - [Python Releases for Windows](https://www.python.org/downloads/windows/)

**Dependency**
- Pillow
- tksheet
- requests
- boto3
- pyinstaller (for build win exe)

### Usage

1. Install packages

use poetry to manage python environment

```sh
$ poetry install
$ poetry shell
```

2. run

```sh
$ python ./src/app.py
```

or

```
$ poetry run python src/app.py
```

use custom ini file

```sh
$ python ./src/app.py -i my-dev.ini
```

## Build

```sh
$ pyinstaller.exe --onefile -F .\src\app.py --clean
```
**⚠WARNING**: 要進去 virtualenv (poetry shell)，才不會找不到 tkdatagrid 的 module

提供 config.ini file, 注意: `account_id`,

## Changes

[CHANGELOG.md](CHANGELOG.md)
