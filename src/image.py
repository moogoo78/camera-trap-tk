import hashlib
from pathlib import Path

from PIL import Image as PILImage
from PIL import ExifTags
from PIL import TiffImagePlugin

THUMB_MAP = (
    #('s', (320, 320)),
    ('m', (500, 500)),
    ('l', (1280, 1280)),
    ('x', (2048, 2048)),
)

def make_thumb(src_path, thumb_source_path):
    for i in THUMB_MAP:
        stem = Path(src_path).stem
        target_filename = f'{stem}-{i[0]}.jpg'
        target_path = thumb_source_path.joinpath(Path(target_filename))
        #print (source_path, target_path)
        thumb = PILImage.open(src_path)
        thumb.thumbnail(i[1] , PILImage.ANTIALIAS)
        if thumb.mode != 'RGB': # RGBA, P?
            thumb = thumb.convert('RGB')
        thumb.save(target_path, "JPEG")

def check_thumb(thumb_path, image_path):
    thumb_path = Path(thumb_path)
    # create thumb if not exist
    if not thumb_path.exists():
        thumb_source_path = Path('/'.join(thumb_path.parts[0:2]))
        make_thumb(image_path, thumb_source_path)

    return thumb_path

def get_thumb(source_id, filename, image_path, size='l'):
    stem = Path(filename).stem
    thumb_source_path = Path(f'./thumbnails/{source_id}')
    thumb_path = thumb_source_path.joinpath(f'{stem}-{size}.jpg')
    if not thumb_path.exists():
        make_thumb(image_path, thumb_source_path)
    return thumb_path


class ImageManager(object):
    exif = None
    entity = None
    pil_handle = None

    def __init__(self, path):
        self.entity = path
        im = PILImage.open(path)
        self.pil_handle = im
        self.exif = self.get_exif()

    def get_exif(self):
        exif = {}
        tags = ExifTags.TAGS
        if not self.pil_handle._getexif():
            return exif
        for k, v in self.pil_handle._getexif().items():
            if k in tags:
                t = tags[k]
                if (t in ['MakerNote', 'PrintImageMatching']):
                    # massy binary
                    pass
                elif isinstance(v,int) or isinstance(v, str):
                    exif[t] = v
                elif isinstance(v, TiffImagePlugin.IFDRational):
                    #print ('---------', v.denominator, v.numerator)
                    exif[tags[k]] = str(v)
                elif isinstance(v, bytes):
                    exif[tags[k]] = v.decode('ascii')
        return exif

    def get_stat(self):
        return self.entity.stat()

    def make_hash(self):
        with open(self.entity, 'rb') as file:
            h = hashlib.new('md5')

            while True:
                # Reading is buffered, so we can read smaller chunks.
                chunk = file.read(h.block_size)
                if not chunk:
                    break
                h.update(chunk)

        return h.hexdigest()

