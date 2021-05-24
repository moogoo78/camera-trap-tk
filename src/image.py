import hashlib

from PIL import Image as PILImage
from PIL import ExifTags
from PIL import TiffImagePlugin

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
