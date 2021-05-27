import requests

class Server(object):
    projects = []
    def __init__(self, config):
        'config already transform to dict'
        self.config = config

        self.projects = self.get_projects()

    def get_projects(self, source_id=0):
        config = self.config
        project_api_prefix = f"{config['host']}{config['project_api']}"
        try:
            if source_id:
                r = requests.get(f'{project_api_prefix}{source_id}')
                return r.json()
            else:
                r = requests.get(project_api_prefix)
                return r.json()['results']

        except BaseException as error:
            print('server error: ', error)
            return []

    def post_image_status(self, payload):
        url = f"{self.config['host']}{self.config['image_update_api']}"
        resp = requests.post(url, json=payload)

        ret = {
            'error': ''
        }

        if resp.status_code != 200:
            print ('server.post_image_status error: ', resp.text)
            ret['error'] = 'server.post_image_status: post error'

        return ret

    def post_annotation(self, payload):
        url = f"{self.config['host']}{self.config['image_annotation_api']}"
        resp = requests.post(url, json=payload)

        ret = {
            'data': {},
            'error': ''
        }

        if resp.status_code != 200:
            print ('server: post_annotation error: ', resp.text)
            ret['error'] = 'server.post_annotation: post error'
        else:
            try:
                d = resp.json()
                ret['data'] = d['saved_image_ids']
            except:
                print ('source: load json error')
                ret['error'] = 'server.post_annotation: load json error'

        return ret
