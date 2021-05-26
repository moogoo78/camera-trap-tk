from pathlib import Path
import time
from datetime import datetime
import json

import boto3
from botocore.exceptions import ClientError

from image import ImageManager
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

    def gen_upload(self, image_list, source_id):
        sql = "UPDATE image SET status='100' WHERE image_id IN ({})".format(','.join([str(x[0]) for x in image_list]))
        self.db.exec_sql(sql, True)
        print ('- update all image status -')

        for i in image_list:
            time.sleep(2)
            sql = 'UPDATE image SET status="200", server_image_id={} WHERE image_id={}'.format(99, i[0])
            self.db.exec_sql(sql, True)
            yield i


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
