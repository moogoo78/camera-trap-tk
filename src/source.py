from pathlib import Path
import time
from datetime import datetime
import json

from image import ImageManager


IGNORE_FILES = ['Thumbs.db', '']
IMAGE_EXTENSIONS = ['.JPG', '.JPEG', '.PNG']

class Source(object):

    def __init__(self, db):
        self.db = db

    def get_folder_path(self, folder):
        db = self.db
        folder_path = Path(folder)
        exist = self.db.fetch_sql("SELECT * FROM source WHERE path='{}'".format(folder_path))
        if exist:
            return ''
        return folder_path

    def get_image_list(self, folder_path):
        db = self.db

        image_list = []
        for entry in folder_path.iterdir():
            if not entry.name.startswith('.') and \
               entry.is_file() and \
               self._check_image_filename(entry):
                image_list.append(entry)

        return image_list

    def gen_import_image(self, image_list, folder_path):
        db = self.db
        ts_now = int(time.time())
        dir_name = folder_path.stem # final path component
        sql = "INSERT INTO source (source_type, path, name, count, created, status) VALUES('folder', '{}', '{}', {}, {}, '10')".format(folder_path, dir_name, len(image_list), ts_now)
        source_id = db.exec_sql(sql, True)

        for i in image_list:
            data = {
                'path': i.as_posix(),
                'name': i.name,
                'img': ImageManager(i),
            }
            self._insert_image_db(data, ts_now, source_id)
            yield data

    def _insert_image_db(self, i, ts_now, source_id):
        db = self.db
        timestamp = None

        img_hash = i['img'].make_hash()
        exif  = i['img'].exif
        dtime = exif.get('DateTimeOriginal', '')
        via = 'exif'
        if dtime:
            dt = datetime.strptime(exif.get('DateTime', ''), '%Y:%m:%d %H:%M:%S')
            timestamp = dt.timestamp()
        else:
            stat = i['img'].get_stat()
            timestamp = int(stat.st_mtime)
            via = 'mtime'

        sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, exif, source_id) VALUES ('{}','{}', {}, '{}', '{}', '{}','{}', {}, '{}', {})".format(
            i['path'],
            i['name'],
            timestamp,
            via,
            '10',
            img_hash,
            '[]',
            ts_now,
            json.dumps(exif),
            source_id)

        db.exec_sql(sql, True)

    @staticmethod
    def _check_image_filename(dirent):
        p = Path(dirent)
        if p.suffix.upper() in IMAGE_EXTENSIONS:
            return True
        return False

    def get_source(self, source_id):
        db = self.db
        source = db.fetch_sql('SELECT * FROM source WHERE source_id={}'.format(source_id))
        images = db.fetch_sql_all('SELECT * FROM image WHERE source_id={}'.format(source_id))

        return {
            'image_list': images,
            'source': source,
        }
