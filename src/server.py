import requests

API_URL = 'http://dev.camera-trap.tw/api/client/v1/'

class Server(object):
    projects = []
    def __init__(self):
        self.projects = self.get_projects()

    def get_projects(self, source_id=0):
        if source_id:
            r = requests.get(f'{API_URL}projects/{source_id}')
            return r.json()
        else:
            r = requests.get(f'{API_URL}projects/')
            return r.json()['results']
