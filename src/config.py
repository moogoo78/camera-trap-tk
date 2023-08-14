import configparser
import os
import json

class Config(configparser.ConfigParser):
    ini_file = None

    def __init__(self, ini_file='config.ini'):
        super().__init__()

        self.ini_file = ini_file
        self.secrets = {
            'aws_access_key_id': '',
            'aws_secret_access_key': '',
        }
        # copy sample if init_file not exists
        if not os.path.exists(self.ini_file):
            self.cp_sample()

        self.read(self.ini_file, encoding='utf-8')

        # credentials
        #if is_publish := self.get('Mode', 'publish', fallback=''):
        #    if is_publish and str(is_publish) not in ['f', '0', 'false']:
        with open('credentials.json') as f:
            cred = json.loads(f.read())
            if key := cred.get('aws-s3-upload'):
                self.secrets['aws_access_key_id'] = key['access_key_id']
                self.secrets['aws_secret_access_key'] = key['secret_access_key']


    def cp_sample(self):
        init_sample_path = '{}.sample'.format(self.ini_file)
        with open(init_sample_path, encoding='utf-8') as f:
            sample_data = f.read()
            f.close()
            with open(self.ini_file, 'w', encoding='utf-8') as f_init:
                f_init.write(sample_data)
                f_init.close()

    def overwrite(self):
        if not self.ini_file:
            return

        with open(self.ini_file, 'w', encoding='utf-8') as orig_file:
            self.write(orig_file)

        # self.read(self.ini_file, encoding='utf-8')
