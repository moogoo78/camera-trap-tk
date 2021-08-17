import logging
import time
import threading

# class UploadTask(threading.Thread):
#     def __init__(self, name):

#         threading.Thread.__init__(self, name=name, daemon=True)
#         self.thread_name = name

#     def run(self):
#         sec = random.randint(1, 8)
#         await asyncio.sleep(sec)
#         return 'url: {}\tsec: {}'.format(url, sec)

class UploadTask(threading.Thread):
    def __init__(self, name, data, image_list, upload_state):
        '''
        queue: control process
        uploading: gui display
        data: execute upload
        db: main thread db handler
        '''
        # set daemon thread
        threading.Thread.__init__(self, name=name, daemon=True)
        self.thread_name = name
        self.upload_state = upload_state
        self.data = data
        self.image_list = image_list
        #self.server_image_map = server_image_map

    def run(self):
        th_id = self.native_id
        logging.info(f'task start: {self.thread_name} ({th_id})')
        #for i in data
        #for i in range(total-count):
        #    self.uploading[self.data['source'][0]]['count'] += 1
        #    print ('counting', self.thread_name , i, self.uploading[self.data['source'][0]]['count'])
        source_id = self.data['source_id']
        image_list = self.image_list
        #print ('upload task ', source_id, len(image_list))

        for i in image_list:
            self.data['current_text'] = i[2]
            time.sleep(3)
            self.data['count'] += 1
            self.data['uploaded'].append(i[0])

        # finishing task
        self.upload_state['done_list'].append(source_id)
        logging.info(f'task done: {self.thread_name} ({th_id})')

