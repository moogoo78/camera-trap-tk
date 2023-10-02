from datetime import datetime
import re
from zipfile import ZipFile, ZIP_DEFLATED
#from bson.objectid import ObjectId
from pathlib import Path

IGNORE_FILES = ['Thumbs.db', '']
IMAGE_EXTENSIONS = ['.JPG', '.JPEG', '.PNG']
VIDEO_EXTENSIONS = ['.MOV', '.AVI', '.M4V', '.MP4', '.WMV', '.MKV', '.WEBM']

def check_file_type(dirent):
    """
    return "image"|"video"|""
    """
    p = Path(dirent)
    if p.name not in IGNORE_FILES:
        if p.suffix.upper() in IMAGE_EXTENSIONS:
            return 'image'
        elif p.suffix.upper() in VIDEO_EXTENSIONS:
            return 'video'
    return ''

# not use
# def find_image_files(folder_path):
#     image_list = []
#     for entry in folder_path.iterdir():
#         if not entry.name.startswith('.') and \
#            entry.is_file():
#             if type_ := _check_filename(entry):
#                 image_list.append((entry, type_))

#     return image_list

def validate_datetime(datetime_text, datetime_format=''):
    try:
        if datetime_text != datetime.strptime(datetime_text, datetime_format).strftime(datetime_format):
            raise ValueError
        return True
    except ValueError:
        return False


# via: https://stackoverflow.com/a/61162928/644070
def create_round_polygon(canvas, x, y, sharpness, **kwargs):

    # The sharpness here is just how close the sub-points
    # are going to be to the vertex. The more the sharpness,
    # the more the sub-points will be closer to the vertex.
    # (This is not normalized)
    if sharpness < 2:
        sharpness = 2

    ratioMultiplier = sharpness - 1
    ratioDividend = sharpness

    # Array to store the points
    points = []

    # Iterate over the x points
    for i in range(len(x)):
        # Set vertex
        points.append(x[i])
        points.append(y[i])

        # If it's not the last point
        if i != (len(x) - 1):
            # Insert submultiples points. The more the sharpness, the more these points will be
            # closer to the vertex. 
            points.append((ratioMultiplier*x[i] + x[i + 1])/ratioDividend)
            points.append((ratioMultiplier*y[i] + y[i + 1])/ratioDividend)
            points.append((ratioMultiplier*x[i + 1] + x[i])/ratioDividend)
            points.append((ratioMultiplier*y[i + 1] + y[i])/ratioDividend)
        else:
            # Insert submultiples points.
            points.append((ratioMultiplier*x[i] + x[0])/ratioDividend)
            points.append((ratioMultiplier*y[i] + y[0])/ratioDividend)
            points.append((ratioMultiplier*x[0] + x[i])/ratioDividend)
            points.append((ratioMultiplier*y[0] + y[i])/ratioDividend)
            # Close the polygon
            points.append(x[0])
            points.append(y[0])

    return canvas.create_polygon(points, **kwargs, smooth=True)

def human_sorting(alist):
    # via: https://stackoverflow.com/a/5967539/644070
    def atoi(text):
        return int(text) if text.isdigit() else text

    def sort_keys(text):
        return [ atoi(c) for c in re.split(r'(\d+)', text) ]

    alist.sort(key=sort_keys)

    return alist
