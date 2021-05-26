import time
#from threading import Thread
import threading


class UploadThread(threading.Thread):
    def __init__(self, db, upload_list):
        super().__init__()

        self.db = db
        self.upload_list = upload_list

        data = threading.local()
        data.upload_list = upload_list
        data.current_index = 0

    def run(self):
        # init state
        sql = "UPDATE image SET status='100' WHERE image_id IN ({})".format(','.join([str(x[0]) for x in self.upload_list]))
        self.db.exec_sql(sql, True)
        print ('- update all image status -')
        for i in self.upload_list:
            time.sleep(1)
            print (i[0], i[1])
            sql = 'UPDATE image SET status="200", server_image_id={} WHERE image_id={}'.format(99, i[0])
            self.db.exec_sql(sql, True)
