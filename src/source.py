from pathlib import Path
import shutil
import time
from datetime import datetime
import json

import boto3
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
#S3UploadFailedError

from image import ImageManager, make_thumb, get_thumb
from upload import UploadThread


IGNORE_FILES = ['Thumbs.db', '']
IMAGE_EXTENSIONS = ['.JPG', '.JPEG', '.PNG']

class Source(object):

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

        sql_jobs = []
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

    def gen_upload_file(self, image_list, source_id, deployment_id, server_image_map):
        for i in image_list:
            file_path = i[1]
            server_image_id = server_image_map.get(str(i[0]), '')
            object_name = f'{server_image_id}.jpg'

            thumb_path = get_thumb(i[10], i[2], i[1])
            #print (thumb_path))
            res = self.upload_to_s3(str(thumb_path), object_name)
            #print ('upload file:', file_path, object_name, res)
            if res['error']:
                yield None
            else:
                yield i[0], server_image_id, object_name, res

    def do_upload(self, source_data):
        count = 0
        count_uploaded = 0

        upload_thread = UploadThread(self.db, source_data['image_list'])
        upload_thread.start()
        source_id = source_data['source'][0]
        self.upload_monitor(upload_thread, source_id)

        #for i in source_data['image_list']:
        #    count += 1
        #    file_name = i[1]
        #    img = ImageManager(file_name)
        #    object_key = f'foo-bar-{i[0]}.jgp'
        #    print (object_key)
        #    time.sleep(1)

        #    sql = "UPDATE image SET status='100' WHERE image_id IN ({})".format(','.join([str(x[0]) for x in res['image_list']]))
            #time.sleep(1)
            #self.progress_frame.tkraise()
            #self.pb.start(20)
        '''
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_conf['access_key_id'],
                aws_secret_access_key=aws_conf['secret_access_key']
            )

            try:
            response = s3_client.upload_file(
            file_name,
            aws_conf['bucket_name'],
            object_name,
            ExtraArgs={'ACL': 'public-read'}
            )
            except ClientError as e:
            logging.error(e)
            return False
            return True'''
            #is_uploaded = upload_to_s3(config['AWSConfig'], file_name, object_name)

            #    server_image_id = server_image_map.get(str(i[0]), '')
                #object_name = '{}-{}.jpg'.format(server_image_id, i[6])
                #object_name = '{}.jpg'.format(server_image_id)
                #is_uploaded = upload_to_s3(config['AWSConfig'], file_name, object_name)
    def upload_monitor(self, upload_thread, source_id):
        """ Monitor the uload thread """
        if upload_thread.is_alive():
            images = self.db.fetch_sql_all('SELECT * FROM image WHERE source_id={}'.format(source_id))
            #print (self.app)
            print ('mon', len([x for x in images if x[5] == '100']), len(images))
            self.app.after(1000, lambda: self.upload_monitor(upload_thread, source_id))
        else:
            pass
            #pbstop && raise

    def delete_folder(self, source_id):
        #print ('delete', source_id)
        sql = f"DELETE FROM source WHERE source_id = {source_id}"
        self.db.exec_sql(sql, True)
        sql = f"DELETE FROM image WHERE source_id = {source_id}"
        self.db.exec_sql(sql, True)

        shutil.rmtree(Path(f'./thumbnails/{source_id}'), ignore_errors=True)
