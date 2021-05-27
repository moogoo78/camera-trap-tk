import requests

class Server(object):
    projects = []
    def __init__(self, config):
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
