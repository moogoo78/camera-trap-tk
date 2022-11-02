import tkinter as tk
import requests
import logging
import urllib3
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
from http.client import HTTPResponse
import ssl
import json

# ping, via: https://stackoverflow.com/a/32684938/644070
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

def to_json(body):
    data_str = body.decode('utf-8')
    return json.loads(data_str)


# via: https://realpython.com/urllib-request/
# modified return struct
def make_request_urllib(url, headers=None, data=None, is_json=False):

    if is_json is True:
        if not headers:
            headers = {}
        headers.update({"Content-Type": "application/json"})

        json_string = json.dumps(data)
        data = json_string.encode("utf-8")

    ret = {
        'body': None,
        'response': None,
        'error': None
    }

    try:
        request = Request(url, headers=headers or {}, data=data, unverifiable=True) # unverifiable default: False
        method = 'GET' if data == None else 'POST'
        logging.info(f'{method} {url} | {response.status}')
        ret['body'] = response.read() # 如果先 return response, read() 內容會不見
        ret['response'] = response        
        '''urlopen
        # ssl._create_default_https_context = ssl._create_unverified_context
        context = ssl._create_unverified_context() # bad idea for disabled check
        with urlopen(request, context=context, timeout=10) as response:
            method = 'GET' if data == None else 'POST'
            logging.info(f'{method} {url} | {response.status}')
            # if data:
            #   logging.debug(f'POST payload: {data}') # print too many
            ret['body'] = response.read() # 如果先 return response, read() 內容會不見
            ret['response'] = response
        '''
        '''urllib3
        # ref: https://drola.si/post/2019-09-05-python-ssl-verification-error/
        http = urllib3.PoolManager()
        method = 'GET'

        if data is None:
            response = http.request('GET', url)
        else:
            method = 'POST'
            response = http.request(
                'POST',
                url,
                body=data,
                headers=headers)
        logging.info(f'{method} {url} | {response.status}')
        ret['body'] = response.data # 如果先 return response, read() 內容會不見
        ret['response'] = response
        '''
    except HTTPError as error:
        logging.error(f'HTTPError: {error.status} {error.reason}')
        ret['error'] = error
    except URLError as error:
        logging.error(f'URLError: {error.reason}')
        ret['error'] = error
    except TimeoutError:
        logging.error('Request timed out')
        ret['error'] = 'Request timed out'
    except BaseException as err:
        logging.error(f'Unexpected: {err}')
    finally:
        return ret

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
        if source_id:
            # r = requests.get(f'{project_api_prefix}{source_id}/')
            # return r.json()
            url = f'{project_api_prefix}{source_id}/'
            resp = self.make_request(url)
            if not resp['error']:
                #return to_json(resp['body'])
                return resp['json']
            else:
                tk.messagebox.showerror('server error', resp['error'])

            if x:= resp.get('response'):
                x.close()

        # else: # TODO
            # r = requests.get(project_api_prefix)
            # return r.json()['results']
            #body, response = make_request(project_api_prefix)
            #data = json.loads(body)
            #return data['results']

        return []

    def post_image_status(self, payload):
        url = f"{self.config['host']}{self.config['image_update_api']}"
        # resp = requests.post(url, json=payload)
        resp = self.make_request(
            url,
            data=payload,
            is_json=True)

        ret = {
            'error': ''
        }

        # if resp.status_code != 200:
        #    print ('server.post_image_status error: ', resp.text)
        #    ret['error'] = 'server.post_image_status: post error'
        if err := resp['error']:
            ret['error'] = err
            logging.error(f'error: {err}')

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
        # resp = requests.post(url, data=payload)
        resp = self.make_request(
            url,
            data=payload,
            is_json=True)

        ret = {
            'error': ''
        }

        if err := resp['error']:
            ret['error'] = err
            logging.error(f'error: {err}')
        else:
            # server 傳 200, 但是是有錯
            #data = to_json(resp['body'])
            data = resp['json']
            if msg := data.get('messages', ''):
                if msg != 'success':
                    ret['error'] = msg
                    logging.error(f'error: {msg}')

        #if resp.status_code != 200:
        #    print ('server.update_upload_history error: ', resp.text)
        #    ret['error'] = 'server.update_upload_history: post error'

        return ret

    def post_annotation(self, post_dict):
        url = f"{self.config['host']}{self.config['image_annotation_api']}"
        ret = {
            'data': {},
            'error': ''
        }
        #url_encoded_data = urlencode(post_dict)
        #body, response = make_request(url, data=post_data)
        resp = self.make_request(
            url,
            data=post_dict,
            is_json=True)

        if not resp['error']:
            # data = to_json(resp['body'])
            data = resp['json']
            ret.update({
                'data': data['saved_image_ids'],
                'deployment_journal_id': data['deployment_journal_id']
            })
        else:
            # tk.messagebox.showerror('server error', resp['error'])
            ret['error'] = resp['error']
            logging.error(f"error: {resp['error']}")

        if x:= resp.get('response'):
            x.close()

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

    def make_request(self, url, headers=None, data=None, is_json=False):
        ret = {
            'body': None,
            'response': None,
            'error': None,
            'method': 'GET',
        }

        response = None
        ssl_verify = True
        if v := self.config.get('ssl_verify'):
            # check falsy
            if v in ['False', '0', 0]:
                ssl_verify = False
        try:
            if data:
                ret['method'] = 'POST'
                response = requests.post(url, json=data, verify=ssl_verify)
            else:
                response = requests.get(url, verify=ssl_verify)

            logging.info(f"{ret['method']} {url} | {response.status_code}")
            if response.status_code == requests.codes.ok:
                ret['response'] = response
                #ret['body']
                ret['json'] = response.json()
            else:
                ret['error'] = f'request error: {response.status_code}'

            #response.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            ret['error']: f'連線失敗: {err}_msg'
        except requests.exceptions.ConnectionError as err_msg:
            ret['error'] = '連線失敗，請檢查網路連線是否有問題，或是伺服器有無正常運作?'
            logging.error(f'request connection error: {err_msg}')
        return ret
