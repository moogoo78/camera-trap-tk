# Camera Trap Desktop
[CameraTrap](https://camera-trap.tw) Destop App for data upload

GUI: tkinter (Pythen)

## Documentation

- [Usage](./docs/usage.rst) (使用說明)
- [System](./docs/system-design.rst)
- [FAQ](./docs/test-case.rst)
- [Workflow](./docs/workflow.md) (import folder, upload status)
- [Test Case](./docs/test-case.rst)


## Development

### Requirements

- Python 3.6+ (Recommanded: Python3.8)

Note: Python 3.9.6 cannot be used on Windows 7 or earlier - [Python Releases for Windows](https://www.python.org/downloads/windows/)

**Dependency**
- Pillow: after 9.5.0 (10.0.0) not suppert 32-bit wheels
- requests
- boto3
- pyinstaller (for build win exe)
- nuitka (after version 1.1.3)

### Usage (Microsoft Windows shell)

1. Install packages

First create python virtual envirmont and activate it

```powerscript
$ python3.8 -m venv venv
$ python3.8 .\venv\Scripts\Activate.ps1
```

2. run

```powerscript
$(venv) python3.8 .\src\app.py
```

use custom ini file

```powerscript
$(venv) python3.8 .\src\app.py -i my-dev.ini
```

## Build
Can build with [PyInstaller](https://pyinstaller.org/en/stable/) or [Nuitka](https://nuitka.net/), currently `build.ps1` script use Nuitka.

```sh
$ build.ps1
```

## Changes

[CHANGELOG.md](CHANGELOG.md)
