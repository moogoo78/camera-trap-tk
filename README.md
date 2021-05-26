# Camera Trap Desktop

tkinter GUI

## Development

### Requirements

- Python 3.6+

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
```

2. run

```sh
$ poetry shell
$ python ./src/app.py
```

## Build

```sh
$ pyinstaller.ex.e --onefile -F .\src\app.py --clean
```
