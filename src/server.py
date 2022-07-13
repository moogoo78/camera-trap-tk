import tkinter as tk
import requests
import logging
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
import json

# ping, via: https://stackoverflow.com/a/32684938/644070
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

# via: https://realpython.com/urllib-request/
def make_request(url, headers=None, data=None):

    request = Request(url, headers=headers or {}, data=data)
    try:
        with urlopen(request, timeout=10) as response:
            method = 'GET' if data == None else 'POST'
            logging.debug(f'{method} {url}:{response.status}')
            return response.read(), response
    except HTTPError as error:
        print(error.status, error.reason)
    except URLError as error:
        print(error.reason)
    except TimeoutError:
        print("Request timed out")


class Server(object):
    projects = []
    def __init__(self, config):
        'config already transform to dict'
        self.config = config
        self.projects = []

        if config.get('no_network', '') == 'yes':
            return None

        #has_network = self.ping()
        #if has_network:
            # ICMP not allowed in default AWS EC2
            #self.has_server = self.ping(config['host'][7:])
            #if self.has_server:
            #    self.projects = self.get_projects()
            #else:
            #    tk.messagebox.showwarning('注意', '伺服器連線失敗')
        #    self.projects = self.get_projects()
        #else:
        #    tk.messagebox.showwarning('注意', '無網路連線')

    def get_projects(self, source_id=0):
        '''get from ini configuration'''
        if source_id:
            return self.get_projects_server(source_id)

        else:
            return self.get_projects_conf()

    def get_projects_conf(self):
        config = self.config
        opts = config.get('project_option_list', '').split(',')
        ret = []
        for x in opts:
            v = x.split('::')
            ret.append({
                'project_id': v[0],
                'name': v[1],
            })
        return ret

    def get_projects_server(self, source_id=0):
        config = self.config
        project_api_prefix = f"{config['host']}{config['project_api']}"
        try:
            if source_id:
                # r = requests.get(f'{project_api_prefix}{source_id}/')
                # return r.json()
                body, response = make_request(f'{project_api_prefix}{source_id}/')
                return json.loads(body)
            else:
                # r = requests.get(project_api_prefix)
                # return r.json()['results']
                body, response = make_request(project_api_prefix)
                data = json.loads(body)
                return data['results']

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

    def post_upload_history(self, deployment_journal_id, status):
        '''
        status: uploading/finished
        deployment_journal_id:
        '''
        url = f"{self.config['host']}{self.config['update_upload_history_api']}"
        payload = {
            'deployment_journal_id': deployment_journal_id,
            'status': status,
        }
        resp = requests.post(url, data=payload)

        ret = {
            'error': ''
        }

        if resp.status_code != 200:
            print ('server.update_upload_history error: ', resp.text)
            ret['error'] = 'server.update_upload_history: post error'

        return ret

    def post_annotation(self, post_dict):
        url = f"{self.config['host']}{self.config['image_annotation_api']}"
        ret = {
            'data': {},
            'error': ''
        }
        #url_encoded_data = urlencode(post_dict)
        #body, response = make_request(url, data=post_data)
        json_string = json.dumps(post_dict)
        post_data = json_string.encode("utf-8")
        body, response = make_request(
            url,
            data=post_data,
            headers={"Content-Type": "application/json"})
        data_str = body.decode('utf-8')
        data = json.loads(data_str)
        ret.update({
            'data': data['saved_image_ids'],
            'deployment_journal_id': data['deployment_journal_id']
        })
        return ret
        ''' TODO
        try:
            resp = requests.post(url, json=payload)
            if resp.status_code != 200:
                #print ('server: post_annotation error: ', resp.text)
                #logging.debug(resp.text)
                ret['error'] = 'server.post_annotation: post error => {}'.format(resp.text)
                return ret
            try:
                d = resp.json()
                ret.update({
                    'data': d['saved_image_ids'],
                    'deployment_journal_id': d['deployment_journal_id']
                })
            except:
                #print ('source: load json error', 'xxxxx', resp.text)
                ret['error'] = 'server.post_annotation: load json error => {}'.format(resp.text)
        except requests.exceptions.RequestException as e:
            ret['error'] = str(e)

        return ret
        '''

    def ping(self, host='google.com'):
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', host]

        result = subprocess.run(command, capture_output=True)
        return result.returncode == 0

