
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
VIDEO_EXTENSIONS = ['.MOV', '.AVI', '.M4V', '.MP4', '.WMV', '.MKV', '.WEBM']

class Source(object):
    '''much like a helper'''

    STATUS_START_IMPORT = 'a1'
    STATUS_DONE_IMPORT = 'a2'
    STATUS_START_ANNOTATE = 'a3'
    STATUS_START_UPLOAD = 'b1'
    STATUS_ANNOTATION_UPLOAD_FAILED = 'b1a'
    STATUS_MEDIA_UPLOAD_PENDING = 'b2'
    STATUS_MEDIA_UPLOADING = 'b2a'
    STATUS_MEDIA_UPLOAD_FAILED = 'b2b'
    STATUS_DONE_UPLOAD = 'b2c'
    STATUS_START_OVERRIDE_UPLOAD = 'b3'
    STATUS_OVERRIDE_ANNOTATION_UPLOAD_FAILED = 'b3a'
    STATUS_DONE_OVERRIDE_UPLOAD = 'b3b'
    STATUS_ARCHIVE = 'c'

    STATUS_LABELS = {
        'STATUS_START_IMPORT': '',
        'STATUS_DONE_IMPORT': '未編輯',
        'STATUS_START_ANNOTATE': '編輯中',
        'STATUS_START_UPLOAD': '',
        'STATUS_ANNOTATION_UPLOAD_FAILED': '上傳失敗',
        'STATUS_MEDIA_UPLOAD_PENDING': '上傳中',
        'STATUS_MEDIA_UPLOADING': '上傳中',
        'STATUS_MEDIA_UPLOAD_FAILED': '上傳不完全',
        'STATUS_DONE_UPLOAD': '完成',
        'STATUS_START_OVERRIDE_UPLOAD': '上傳覆寫',
        'STATUS_OVERRIDE_ANNOTATION_UPLOAD_FAILED': '上傳失敗',
        'STATUS_DONE_OVERRIDE_UPLOAD': '覆寫完成',
        'STATUS_ARCHIVE': '歸檔',
    }

    def __init__(self, app):
        self.db = app.db
        self.app = app

    def update_status(self, source_id, key, **kwargs):
        if value := getattr(self, f'STATUS_{key}', ''):
            sql = f"UPDATE source SET status='{value}' WHERE source_id={source_id}"
            # 特別處理 "首次上傳時間/上次上傳時間"
            if key == 'START_UPLOAD':
                if now := kwargs.get('now', ''):
                    sql = f"UPDATE source SET status='{value}', upload_created={now}, upload_changed={now} WHERE source_id={source_id}"
            if key == 'START_OVERRIDE_UPLOAD':
                if now := kwargs.get('now', ''):
                    sql = f"UPDATE source SET status='{value}', upload_changed={now} WHERE source_id={source_id}"

            self.app.db.exec_sql(sql, True)
            return True
        return False

    def get_status_label(self, code):
        for k, v in self.STATUS_LABELS.items():
            if status := getattr(self, k, ''):
                if status == code:
                    return v
        return ''

    def is_done_upload(self, status):
        if status in [
                self.STATUS_DONE_UPLOAD,
                self.STATUS_DONE_OVERRIDE_UPLOAD]:
            return True
        return False

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
               entry.is_file():
                if type_ := self._check_filename(entry):
                    image_list.append((entry, type_))

        return image_list

    def create_import_directory(self, num_image_list, folder_path):
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
                sql = "INSERT INTO source (source_type, path, name, count, created, status, trip_start, trip_end) VALUES('folder', '{}', '{}', {}, {}, '{}', '{}', '{}')".format(folder_path, dir_name, num_image_list, ts_now, self.STATUS_START_IMPORT, start, end)
        else:
            sql = "INSERT INTO source (source_type, path, name, count, created, status) VALUES('folder', '{}', '{}', {}, {}, '{}')".format(folder_path, dir_name, num_image_list, ts_now, self.STATUS_START_IMPORT)

        source_id = db.exec_sql(sql, True)

        return source_id

    def gen_import_file(self, source_id, image_list, folder_path):
        ts_now = int(time.time())
        # mkdir thumbnails dir
        thumb_conf = 'thumbnails' # TODO config
        thumb_path = Path(thumb_conf)
        if not thumb_path.exists():
            thumb_path.mkdir()

        thumb_source_path = thumb_path.joinpath(f'{source_id}')
        if not thumb_source_path.exists():
            thumb_source_path.mkdir()

        for entry, type_ in image_list:
            img = None
            data = {
                'path': entry.as_posix(),
                'name': entry.name,
            }
            if type_ == 'image':
                data['img'] = ImageManager(entry)
                sql = self.prepare_image_sql_and_thumb(data, ts_now, source_id, thumb_source_path)
            elif type_ == 'video':
                data['mov'] = entry
                sql = self.prepare_video_sql(data, ts_now, source_id, thumb_source_path)
                # HACK: if video process too fast, folder_list.folder_importing will has empty value, cause error while update
                time.sleep(0.5)
            yield (data, sql)


    def prepare_video_sql(self, i, ts_now, source_id, thumb_source_path):
        db = self.db
        stat = i['mov'].stat()
        timestamp = int(stat.st_mtime)
        via = 'mtime'

        sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, source_id, sys_note, media_type) VALUES ('{}','{}', {}, '{}', '{}', '{}', '{}', {}, {}, '{}', 'video')".format(
            i['path'],
            i['name'],
            timestamp,
            via,
            '10',
            '',
            '[]',
            ts_now,
            source_id,
            '{}',
        )
        return sql

    def prepare_image_sql_and_thumb(self, i, ts_now, source_id, thumb_source_path):
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

        sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, exif, source_id, sys_note, media_type) VALUES ('{}','{}', {}, '{}', '{}', '{}', '{}', {}, '{}', {}, '{}', 'image')".format(
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
    def _check_filename(dirent):
        """
        return "image"|"video"|""
        """
        p = Path(dirent)
        if p.suffix.upper() in IMAGE_EXTENSIONS:
            return 'image'
        elif p.suffix.upper() in VIDEO_EXTENSIONS:
            return 'video'
        return ''

    def get_source(self, source_id):
        db = self.db
        source = db.fetch_sql('SELECT * FROM source WHERE source_id={}'.format(source_id))
        images = db.fetch_sql_all('SELECT * FROM image WHERE source_id={} order by timestamp'.format(source_id))

        return {
            'image_list': images,
            'source': source,
        }

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
