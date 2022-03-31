from pathlib import Path


def check_image(path):
    return Path(path).exists()
