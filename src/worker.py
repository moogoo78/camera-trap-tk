import logging
import time
import threading

from image import get_thumb

class UploadTask(threading.Thread):
    def __init__(self, name, data, image_list, upload_state, func_to_s3):
        '''
        queue: control process
        uploading: gui display
        data: execute upload
        '''
        # set daemon thread
        threading.Thread.__init__(self, name=name, daemon=True)
        self.thread_name = name
        self.data = data
        self.image_list = image_list
        self.upload_state = upload_state
        self.func_to_s3 = func_to_s3

    def run(self):
        th_id = self.native_id
        logging.info(f'task start: {self.thread_name} ({th_id})')
        source_id = self.data['source_id']
        image_list = self.image_list
        #print ('upload task ', source_id, len(image_list))

        for i in image_list:
            self.data['current_text'] = i[2] # name

            # upload to s3
            server_image_id = i[11]
            thumb_paths = get_thumb(i[10], i[2], i[1], 'all')
            for x, path in thumb_paths.items():
                object_name = f'{server_image_id}-{x}.jpg'
                res = self.func_to_s3(str(path), object_name)
                # TODO error

            # simulate upload
            #time.sleep(3)

            self.data['count'] += 1
            self.data['uploaded'].append(i[0])


            # 做完手上的再跳出
            if self.upload_state['is_thread_running'] == False:
                logging.info(f'task terminated: {self.thread_name} ({th_id})')
                return

        # finishing task
        self.upload_state['done_list'].append(source_id)
        logging.info(f'task done: {self.thread_name} ({th_id})')

