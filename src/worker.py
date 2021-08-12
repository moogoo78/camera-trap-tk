import logging
import time
import threading

class UploadTask(threading.Thread):
    def __init__(self, name, queue, uploading, data, server_image_map, db):
        '''
        queue: control process
        uploading: gui display
        data: execute upload
        db: main thread db handler
        '''
        # set daemon thread
        threading.Thread.__init__(self, name=name, daemon=True)
        self.thread_name = name
        self.queue = queue
        self.uploading = uploading
        self.data = data
        self.server_image_map = server_image_map
        self.db = db

    def run(self):
        #source_id = self.queue.get(0)
        #item = self.queue.get()
        th_id = self.native_id
        logging.info(f'task start: {self.thread_name} ({th_id})')
        #print (self.queue.qsize(), self.queue.full())
        total = self.uploading[self.data['source'][0]]['total']
        count = self.uploading[self.data['source'][0]]['count']
        #for i in data
        for i in range(total-count):
            self.uploading[self.data['source'][0]]['count'] += 1
            #print ('counting', self.thread_name , i, self.uploading[self.data['source'][0]]['count'])
            time.sleep(2)

        #self.queue.task_done()
        self.queue.put(self.thread_name)
        logging.info(f'task done: {self.thread_name} ({th_id})')

