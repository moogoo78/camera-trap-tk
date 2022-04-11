from pathlib import Path
import shutil
import time
from datetime import datetime
import json
import re

import boto3
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
#S3UploadFailedError

from image import ImageManager, make_thumb, get_thumb
from utils import validate_datetime
#from upload import UploadThread

IGNORE_FILES = ['Thumbs.db', '']
IMAGE_EXTENSIONS = ['.JPG', '.JPEG', '.PNG']

class Source(object):
    '''much like a helper'''

    def __init__(self, app):
        self.db = app.db
        self.app = app

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

    def create_import_directory(self, image_list, folder_path):
        db = self.db
        ts_now = int(time.time())
        dir_name = folder_path.stem # final path component
        sql = ''
        sql_jobs = []
        # validate date format
        if m := re.search(r'([0-9]{8})-([0-9]{8})',dir_name):
            start = m.group(1)
            end = m.group(2)
            if validate_datetime(start, '%Y%m%d') and \
               validate_datetime(end, '%Y%m%d'):
                sql = "INSERT INTO source (source_type, path, name, count, created, status, trip_start, trip_end) VALUES('folder', '{}', '{}', {}, {}, '10', '{}', '{}')".format(folder_path, dir_name, len(image_list), ts_now, start, end)
        else:
            sql = "INSERT INTO source (source_type, path, name, count, created, status) VALUES('folder', '{}', '{}', {}, {}, '10')".format(folder_path, dir_name, len(image_list), ts_now)

        source_id = db.exec_sql(sql, True)

        return source_id

    def gen_import_image(self, source_id, image_list, folder_path):
        ts_now = int(time.time())
        # mkdir thumbnails dir
        thumb_conf = 'thumbnails' # TODO config
        thumb_path = Path(thumb_conf)
        if not thumb_path.exists():
            thumb_path.mkdir()

        thumb_source_path = thumb_path.joinpath(f'{source_id}')
        if not thumb_source_path.exists():
            thumb_source_path.mkdir()

        for i in image_list:
            data = {
                'path': i.as_posix(),
                'name': i.name,
                'img': ImageManager(i),
            }
            sql = self._insert_image_db(data, ts_now, source_id, thumb_source_path)

            yield data, sql

    def _insert_image_db(self, i, ts_now, source_id, thumb_source_path):
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

        sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, exif, source_id, sys_note) VALUES ('{}','{}', {}, '{}', '{}', '{}', '{}', {}, '{}', {}, '{}')".format(
            i['path'],
            i['name'],
            timestamp,
            via,
            '10',
            img_hash,
            '[]',
            ts_now,
            json.dumps(exif),
            source_id,
            '{}',
        )

        #db.exec_sql(sql, True)

        make_thumb(i['path'], thumb_source_path)
        return sql

    @staticmethod
    def _check_image_filename(dirent):
        p = Path(dirent)
        if p.suffix.upper() in IMAGE_EXTENSIONS:
            return True
        return False

    def get_source(self, source_id):
        db = self.db
        source = db.fetch_sql('SELECT * FROM source WHERE source_id={}'.format(source_id))
        images = db.fetch_sql_all('SELECT * FROM image WHERE source_id={} order by timestamp'.format(source_id))

        return {
            'image_list': images,
            'source': source,
        }

    # depricated
    def upload_annotation(self, image_list, source_id, deployment_id):
        '''set upload_status in local database and post data to server'''
        sql = "UPDATE image SET upload_status='100' WHERE image_id IN ({})".format(','.join([str(x[0]) for x in image_list]))
        self.db.exec_sql(sql, True)
        #print ('- update all image status -')
        account_id = self.app.config.get('Installation', 'account_id')
        # post to server
        payload = {
            'image_list': image_list,
            'key': f'{account_id}-{source_id}',
            'deployment_id': deployment_id,
        }
        return self.app.server.post_annotation(payload)

    def upload_to_s3(self, file_path, object_name):
        key = self.app.config.get('AWSConfig', 'access_key_id')
        secret = self.app.config.get('AWSConfig', 'secret_access_key')
        bucket_name = self.app.config.get('AWSConfig', 'bucket_name')
        ret = {
            'data': {},
            'error': ''
        }

        s3_client = boto3.client(
            's3',
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )

        try:
            response = s3_client.upload_file(
                file_path,
                bucket_name,
                object_name,
                ExtraArgs={'ACL': 'public-read'}
            )
            ret['data'] = response
        except ClientError as e:
            #logging.error(e)
            print ('s3 upload error', e)
            ret['error'] = 's3 upload client error'
        except S3UploadFailedError as e:
            print (e)
            ret['error'] = 's3 upload failed'

        return ret



    def delete_folder(self, source_id):
        #print ('delete', source_id)
        sql = f"DELETE FROM source WHERE source_id = {source_id}"
        self.db.exec_sql(sql, True)
        sql = f"DELETE FROM image WHERE source_id = {source_id}"
        self.db.exec_sql(sql, True)

        shutil.rmtree(Path(f'./thumbnails/{source_id}'), ignore_errors=True)

############
    def finish_upload_task(self, source_id):
        #source_id = source_data['source'][0]
        sql = f"UPDATE source SET status='30' WHERE source_id={source_id}"
        self.db.exec_sql(sql, True)
