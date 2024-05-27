
from pathlib import Path
import shutil
import time
from datetime import datetime
import json
import re
import logging

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

    def is_uploading(self, status):
        if status in [
                self.STATUS_MEDIA_UPLOAD_PENDING,
                self.STATUS_MEDIA_UPLOADING,
                self.STATUS_MEDIA_UPLOAD_FAILED]:
            return True
        return False

    def is_done_upload(self, status):
        if status in [
                self.STATUS_DONE_UPLOAD,
                self.STATUS_DONE_OVERRIDE_UPLOAD]:
            return True
        return False

    def get_image_list(self, folder_path):
        db = self.db

        image_list = []
        for entry in folder_path.iterdir():
            if not entry.name.startswith('.') and \
               entry.is_file():
                if type_ := self._check_filename(entry):
                    image_list.append((entry, type_))

        return image_list

    def create_import_directory(self, num_image_list, folder_path, parsed_format):
        db = self.db
        ts_now = int(time.time())
        dir_name = folder_path.stem # final path component
        sql = ''
        sql_jobs = []

        if parsed_format:
            descr = {
                'parsed': parsed_format,
            }
            sql = "INSERT INTO source (source_type, path, name, count, created, status, description) VALUES('folder', '{}', '{}', {}, {}, '{}', '{}')".format(folder_path, dir_name, num_image_list, ts_now, self.STATUS_START_IMPORT, json.dumps(descr))
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

        last_timestamp = 0
        for entry, type_ in image_list:
            img = None
            sql = ''
            data = {
                'path': entry.as_posix(),
                'name': entry.name,
            }

            if type_ == 'image':
                img = ImageManager(entry)
                if img.pil_handle:
                    timestamp = ''
                    data['img'] = img
                    timestamp, via = data['img'].get_timestamp()
                    if timestamp == '':
                        # 用上一張照片
                        if last_timestamp:
                            timestamp = last_timestamp
                            via = 'last_timestamp'
                        else:
                            # 只好抓檔案
                            if stat := data['img'].get_stat():
                                timestamp = int(stat.st_mtime)
                                via = 'mtime'
                    data['timestamp'] = timestamp
                    data['via'] = via
                    sql = self.prepare_image_sql_and_thumb(data, ts_now, source_id, thumb_source_path)

            elif type_ == 'video':
                #print(entry, 'video')
                data['mov'] = entry
                stat = data['mov'].stat()
                data['timestamp'] = int(stat.st_mtime)
                data['via'] = 'mtime'
                sql = self.prepare_video_sql(data, ts_now, source_id, thumb_source_path)
                # HACK: if video process too fast, folder_list.folder_importing will has empty value, cause error while update
                # maybe, change folder_list.folder_importing to folder_list.progress_map and add folder_list.import_deque, don't need to sleep(05) here, 230811
                time.sleep(0.5)

            if x := data.get('timestamp'):
                last_timestamp = x
            yield (data, sql)


    def gen_import_file2(self, source_id, image_map, folder_path):
        '''for import from annotation file'''

        # mkdir thumbnails dir
        thumb_conf = 'thumbnails' # TODO config
        thumb_path = Path(thumb_conf)
        if not thumb_path.exists():
            thumb_path.mkdir()

        thumb_source_path = thumb_path.joinpath(f'{source_id}')
        if not thumb_source_path.exists():
            thumb_source_path.mkdir()

        for name, data in image_map.items():
            data['_img'] = None
            data['_file_path_posix'] = data['_file_path'].as_posix()
            if data['_file_type'] == 'image':
                img = ImageManager(data['_file_path'])
                if img.pil_handle:
                    data['_img'] = img
                    data['_exif'] = img.exif
                    data['_img_hash'] = img.make_hash()
                    make_thumb(data['_file_path'], thumb_source_path)

            elif data['_file_type'] == 'video':
                pass


            yield data


    def prepare_video_sql(self, i, ts_now, source_id, thumb_source_path):
        db = self.db

        sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, source_id, sys_note, media_type) VALUES ('{}','{}', {}, '{}', '{}', '{}', '{}', {}, {}, '{}', 'video')".format(
            i['path'],
            i['name'],
            i['timestamp'],
            i['via'],
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
        sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, exif, source_id, sys_note, media_type) VALUES ('{}','{}', {}, '{}', '{}', '{}', '{}', {}, '{}', {}, '{}', 'image')".format(
            i['path'],
            i['name'],
            i['timestamp'],
            i['via'],
            '10',
            img_hash,
            '[]',
            ts_now,
            json.dumps(exif),
            source_id,
            '{}',
        )

        #db.exec_sql(sql, True)

        if is_success := make_thumb(i['path'], thumb_source_path):
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

    def add_media_convert(self, object_name):
        key = self.app.secrets.get('aws_access_key_id')
        secret = self.app.secrets.get('aws_secret_access_key')
        bucket_name = self.app.config.get('AWSConfig', 'bucket_name')
        region = self.app.config.get('AWSConfig', 'mediaconvert_region')
        endpoint = self.app.config.get('AWSConfig', 'mediaconvert_endpoint')
        role = self.app.config.get('AWSConfig', 'mediaconvert_role')
        queue = self.app.config.get('AWSConfig', 'mediaconvert_queue')
        job_template = self.app.config.get('AWSConfig', 'mediaconvert_job_template')
        #input_folder = self.app.config.get('AWSConfig', 'mediaconvert_input_folder')
        output_folder = self.app.config.get('AWSConfig', 'mediaconvert_output_folder')

        client = boto3.client(
            'mediaconvert',
            aws_access_key_id=key,
            aws_secret_access_key=secret,
            region_name=region,
            endpoint_url=endpoint,
            verify=False)

        job_settings = {
            'Inputs': [
                {
                    'AudioSelectors': {
                        "Audio Selector 1": {
                            "Offset": 0,
                            "DefaultSelection": "DEFAULT",
                            "SelectorType": "LANGUAGE_CODE",
                            "ProgramSelection": 1,
                            "LanguageCode": "ENM"
                        },
                    },
                    'VideoSelector': {
                        'ColorSpace': 'FOLLOW',
                    },
                    'FilterEnable': 'AUTO',
                    'PsiControl': 'USE_PSI',
                    'FilterStrength': 0,
                    'DeblockFilter': 'DISABLED',
                    'DenoiseFilter': 'DISABLED',
                    'TimecodeSource': 'EMBEDDED',
                    'FileInput': f's3://{bucket_name}/{object_name}',
                },
            ],
            'OutputGroups': [
                {
                    'Name': 'File Group',
                    'OutputGroupSettings': {
                        'Type': 'FILE_GROUP_SETTINGS',
                        'FileGroupSettings': {
                            'Destination': f's3://{bucket_name}/{output_folder}/',
                            'DestinationSettings': {
                                'S3Settings': {
                                    'AccessControl': {
                                        'CannedAcl': 'PUBLIC_READ'
                                    },
                                },
                            },
                        },
                    },
                    'Outputs': [],
                },
            ],
        }

        client.create_job(
            JobTemplate = job_template,
            Queue = queue,
            Role = role,
            Settings = job_settings,
        )

    def upload_to_s3(self, file_path, object_name):
        key = self.app.secrets.get('aws_access_key_id')
        secret = self.app.secrets.get('aws_secret_access_key')
        bucket_name = self.app.config.get('AWSConfig', 'bucket_name')
        region = self.app.config.get('AWSConfig', 's3_region')
        ret = {
            'data': {},
            'error': ''
        }

        s3_client = boto3.client(
            's3',
            aws_access_key_id=key,
            aws_secret_access_key=secret,
            region_name=region,
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
            #print ('=========s3 upload error', e)
            ret['error'] = 's3 upload client error'
        except S3UploadFailedError as e:
            #print ('---------', e)
            ret['error'] = 's3 upload failed'
        except Exception as e:
            #print('xxxxxxxxxxxxxx', e)
            ret['error'] = e

        return ret


    def delete_folder(self, source_id):
        #print ('delete', source_id)
        sql = f"DELETE FROM source WHERE source_id = {source_id}"
        self.db.exec_sql(sql, True)
        sql = f"DELETE FROM image WHERE source_id = {source_id}"
        self.db.exec_sql(sql, True)

        thumb_dir_path = Path(f'./thumbnails/{source_id}')
        if thumb_dir_path.exists():
            shutil.rmtree(thumb_dir_path, ignore_errors=True)

    def check_import_folder(self, folder_path):
        '''combine check folder rules
        ret: error_message, results
        '''

        results = {
            'error': ''
        }

        # check network
        resp = self.app.server.check_folder('FAKE-FOLDER-NAME-FOR-CHECK-NETWORK')

        if err_msg := resp.get('error', ''):
            results['error'] = err_msg
            return results

        resp = self.app.server.check_folder(folder_path)
        if resp['error'] == '' and resp['json'].get('is_exist') == True:
            results['error'] = '伺服器上已經有同名的資料夾'
            return results

        if exist := self.app.db.fetch_sql(f"SELECT * FROM source WHERE path='{folder_path}'"):
            results['error'] = '已經加過此資料夾'
            return results

        # check folder name syntax
        parsed_format = None
        if check := self.app.config.get('Mode', 'check_folder_format', fallback=False):
            # check falsy
            if check not in ['False', '0', 0]:
                parsed_format = self._check_folder_name_format(folder_path.name)
                logging.info(parsed_format)

                if err := parsed_format.get('error'):
                    results['error'] = f'"{folder_path.name}" 目錄格式不符: {err}\n\n[相機位置標號-YYYYmmdd-YYYYmmdd]\n 範例: HC04-20190304-20190506'
                    return results
                else:
                    #parsed_format = result
                    results['parsed_format'] = parsed_format

        return results

    def _check_folder_name_format(self, folder_name):
        # rules from config, too complicate
        # regex = self.app.config.get('Format', 'folder_name_regex')
        # date_format = self.app.config.get('Format', 'date_format')

        # regex = r'(HC|HL|LD|NT|CY|PT|DS|TD)([0-9]+)([A-Za-z]*)-(19[0-9][0-9]|20[0-9][0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])-(19[0-9][0-9]|20[0-9][0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])'
        # regex = r'(HC|HL|LD|NT|CY|PT|DS|TD)(.*)-(19[0-9][0-9]|20[0-9][0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])-(19[0-9][0-9]|20[0-9][0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])'
        regex = r'(.*)-(19[0-9][0-9]|20[0-9][0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])-(19[0-9][0-9]|20[0-9][0-9])(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])'
        date_format = '%Y-%m-%d'
        result = {'error': ''}
        try:
            m = re.match(regex, folder_name)
            if m:
                sa_key = m.group(1)
                studyarea_name = self.app.config.get('StudyAreaMap', sa_key, fallback='')
                result.update({
                    'studyarea_key': sa_key,
                    'studyarea': studyarea_name,
                    # 'deployment': '{}{}'.format(m.group(1), m.group(2)), #  '{}{}'.format(m.group(2), m.group(3)),
                    'deployment': m.group(1), #  '{}{}'.format(m.group(2), m.group(3)),
                })
                # begin_date = '{}{}{}'.format(m.group(4), m.group(5), m.group(6))
                # end_date = '{}{}{}'.format(m.group(7), m.group(8), m.group(9))
                trip_start = '{}-{}-{}'.format(m.group(2), m.group(3), m.group(4))
                trip_end = '{}-{}-{}'.format(m.group(5), m.group(6), m.group(7))
                if validate_datetime(trip_start, date_format) and \
                   validate_datetime(trip_end, date_format):
                    # 目前用不到，只是判斷格式，也沒有上傳 (上傳有 folder_name可查)
                    result.update({
                        'trip_start': trip_start,
                        'trip_end':  trip_end,
                    })
                else:
                    result.update({'error': '日期錯誤 \n(請檢查年月日是否正確)'})
            else:
                result.update({'error': '格式錯誤'})
        except Exception as err_msg:
            result.update({'error': err_msg})

        return result
