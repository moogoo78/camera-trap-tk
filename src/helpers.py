import re
from pathlib import Path
import json
from datetime import datetime
import random
import colorsys
#    'sn': {
#        'label': '編號',
#        'width': 50,
#        'type': 'text',
#    },
IMG_SEQ_COLOR_LIST = [
    '#FFD99F',
    '#FFD781',
    '#E6B98F',
    '#E9E3AD',
    '#CBC7A1',
    '#CCFFFF',
    '#AAE3E3',
    '#99CCFF',
    '#CCCCFF',
    '#7373F3',
]
USE_COLOR_LIST = True

HEADER = {
    'status_display': {
        'label': '狀態',
        'width': 100,
        'type': 'text',
    },
    'thumb': {
        'label': '照片',
        'width': 55,
        'type': 'image',
    },
    'filename': {
        'label': '檔名',
        'width': 150,
        'type': 'text',
    },
    'datetime_display': {
        'label': '日期時間',
        'width': 130,
        'type': 'text',
    },
    'annotation_species': {
        'label': '物種',
        'width': 80,
        'type': 'autocomplete',
        'choices': [],
        'extra_choices': []
    },
    'annotation_lifestage': {
        'label': '年齡',
        'width': 80,
        'type': 'listbox',
        'choices': []
    },
    'annotation_sex': {
        'label': '性別',
        'width': 80,
        'type': 'listbox',
        'choices': []
    },
    'annotation_antler': {
        'label': '角況',
        'width': 80,
        'type': 'listbox',
        'choices': []
    },
    'annotation_remark': {
        'label': '備註',
        'width': 80
    },
    'annotation_animal_id': {
        'label': '個體ID',
        'width': 80
    }
}
STATUS_MAP = {
    '10': '未看',
    '20': '已看',
    '30': '已標',
}
UPLOAD_STATUS_MAP = {
    '100': '上傳中*',
    '110': '上傳中',
    '200': '已上傳',
}

def make_status_display(status, upload_status):
    return f'{status} ({upload_status})'


class DataHelper(object):
    def __init__(self, db, annotate_status_list):
        #self.annotation_item = [4, 5, 6, 7, 8, 9] # index from sqlite
        self.db = db
        self.annotate_status_list = annotate_status_list

        self.annotation_map = {
            4: 'annotation_species',
            5: 'annotation_lifestage',
            6: 'annotation_sex',
            7: 'annotation_antler',
            8: 'annotation_remark',
            9: 'annotation_animal_id'
        } #[4, 5, 6, 7, 8, 9] # index from sqlite
        self.data = {}
        #self.image_list = []
        self.columns = HEADER
        self.img_seq_rand_salt = random.random()
        # annotation_data = {
        #     '97': [{}],
        #     '98': [{}, {}],
        #     ...
        #}
        self.annotation_data = {}
        self.exif_data = {}
        self.test_foto_time = ''
        self.source_id_status = []

    def get_image_row_keys(self, image_id):
        row_keys = []
        for iid, item in self.data.items():
            if image_id == item['image_id']:
                row_keys.append(iid)
        return row_keys

    def set_status_display(self, row_key='', status_code=''):
        orig = self.data[row_key]['status_display']
        m = re.search(r'(.+)\((.+)\)', orig)
        if m:
            orig_status = m.group(1)
            orig_upload_status = m.group(2)

        if len(status_code) == 2:
            self.data[row_key]['status_display'] = make_status_display(STATUS_MAP.get(status_code, '-'), orig_upload_status)
        elif len(status_code) == 3:
            self.data[row_key]['status_display'] = make_status_display(orig_status, UPLOAD_STATUS_MAP.get(status_code, '-'))

    def update_annotation(self, row_key, col_key, value, seq_info=None):
        print('! update_annotation', row_key, col_key, value)

        # update source status if start annotation
        if self.source_id_status and \
           self.source_id_status[1] == self.annotate_status_list[0]:
            sql = f"UPDATE source SET status='{self.annotate_status_list[1]}' WHERE source_id={self.source_id_status[0]}"
            self.db.exec_sql(sql, True)

        item = self.data[row_key]
        image_id = item['image_id']

        #print (row_key, image_id, self.annotation_data[image_id], row_key.split('-')[1])
        annotation_col = col_key.replace('annotation_', '')
        annotation_index = int(row_key.split('-')[1])
        adata = self.annotation_data[image_id]

        #如果不屬於那個欄位選項不能貼上
        col_data = self.columns[col_key]
        choices = col_data.get('choices', [])
        if annotation_col == 'species':
            choices = choices + col_data['extra_choices']

        if col_data.get('type', '') == 'listbox' and (value != '' and value not in choices):
            return False

        original_species= adata[annotation_index].get('species', '')

        adata[annotation_index].update({
            annotation_col: value
        })
        json_data = json.dumps(adata)

        sql = ''
        if seq_info:
            tag_name = item.get('img_seq_tag_name', '')
            # 複製的不用連拍補齊
            # print(row_key, '---')
            if row_key.endswith('-0') and tag_name:
                # print('*first', self.check_test_foto(item))
                sql2 = ''
                if self.check_test_foto(item) is True:
                    if original_species != '測試':
                        sql2 = f"UPDATE image SET status='30', annotation='{json_data}' WHERE image_id={image_id}"
                else:
                    sql2 = f"UPDATE image SET status='30', annotation='{json_data}' WHERE image_id={image_id}"
                if sql2:
                    self.db.exec_sql(sql2)

                # related rows
                keys = seq_info['map'][tag_name]['row_keys']
                img_list = []
                sql2 = ''
                for k, v in keys.items():
                    if k != row_key and k.endswith('-0'):
                        tag_image_id = v['image_id']
                        tag_adata = self.annotation_data[tag_image_id]
                        original_species2 = tag_adata[annotation_index].get('species', '')
                        tag_adata[0].update({
                            annotation_col: value
                        })
                        tag_json_data = json.dumps(tag_adata)
                        # print('*rel', self.check_test_foto(item))
                        item2 = self.data[k]
                        # print (original_species2, self.check_test_foto(item2))
                        if self.check_test_foto(item2) is True:
                            if original_species2 != '測試':
                                sql2 = f"UPDATE image SET status='30', annotation='{tag_json_data}' WHERE image_id={tag_image_id}"
                                self.db.exec_sql(sql2)
                        else:
                            sql2 = f"UPDATE image SET status='30', annotation='{tag_json_data}' WHERE image_id={tag_image_id}"
                            self.db.exec_sql(sql2)

                if sql2:
                    self.db.commit()

            else:
                # 勾了沒中或是複製列, 直接更新
                # print('*dir', self.check_test_foto(item))
                if self.check_test_foto(item) is True:
                    if original_species != '測試':
                        sql = f"UPDATE image SET status='30', annotation='{json_data}' WHERE image_id={image_id}"
                else:
                    sql = f"UPDATE image SET status='30', annotation='{json_data}' WHERE image_id={image_id}"
        else:
            # 沒勾連拍, 直接更新
            # print('*normal', self.check_test_foto(item), original_species, value)
            # 直接更新，不管是不是測試照
            sql = f"UPDATE image SET status='30', annotation='{json_data}' WHERE image_id={image_id}"

        if sql:
            self.db.exec_sql(sql, True)

        return True

    def check_test_foto(self, item):
        if self.test_foto_time:
            # 有設定測試照, 而且時間一樣
            image_hms = datetime.fromtimestamp(item['time']).strftime('%H:%M:%S')
            if image_hms == self.test_foto_time:
                return True

        return False

    def read_image_list(self, image_list):
        '''
        iid rule: `iid:{image_id}-{annotation_counter}`
        '''
        self.data = {}
        self.annotation_data = {}
        counter = 0
        for i_index, i in enumerate(image_list):
            image_id = i[0]
            status_display = make_status_display(
                STATUS_MAP.get(i[5], '-'),
                UPLOAD_STATUS_MAP.get(i[12]) if i[12] else '未上傳')

            if i[15] == 'image':
                thumb = f'./thumbnails/{i[10]}/{Path(i[2]).stem}-q.jpg'
            elif i[15] == 'video':
                thumb = './assets/movie_small.png'

            alist = json.loads(i[7])
            if len(alist) == 0:
                alist = [{}]
            self.annotation_data[image_id] = alist
            self.exif_data[image_id] = json.loads(i[9]) if i[9] else ''
            row_basic = {
                'status_display': status_display,
                'filename': i[2],
                'datetime_display': str(datetime.fromtimestamp(i[3])),
                'image_id': image_id,
                'path': i[1],
                'status': i[5],
                'upload_status': i[12],
                'time': i[3],
                'seq': 0,
                'sys_note': json.loads(i[13]),
                'thumb': thumb,
                'image_index': i_index,
                'media_type': i[15]
            }

            has_cloned = True if len(alist) > 1 else False
            for a_index, a in enumerate(alist):
                row_annotation = {
                    'counter': counter,
                    'sn': f'{i_index+1}-{a_index+1}' if has_cloned else f'{i_index+1}',
                }
                for _, a_key in self.annotation_map.items():
                    k = a_key.replace('annotation_', '')
                    row_annotation[a_key] = a.get(k, '')
                self.data[f'iid:{image_id}-{a_index}'] = {**row_basic, **row_annotation}
                counter += 1
        return self.data

    def get_item(self, row):
        for counter, (row_key, item) in enumerate(self.data.items()):
            if row == counter:
                return item

    def get_rc_key(self, row, col):
        '''rc to rc_key'''
        get_row_key = ''
        for counter, (row_key, item) in enumerate(self.data.items()):
            if row == counter:
                get_row_key = row_key
                break

        for counter, col_key in enumerate(self.columns.keys()):
            if col == counter:
                get_col_key = col_key

        return get_row_key, get_col_key

    def get_image_index(self, row):
        for counter, (row_key, item) in enumerate(self.data.items()):
            if row == counter:
                return item['image_index']
        return 0

    def group_image_sequence(self, time_interval, seq_tag=''):
        seq_info = {
            'group_prev': False,
            'group_next': False,
            'map': {},
            'idx': 0,
            'salt': self.img_seq_rand_salt,
            'int': int(time_interval) * 60,
        }
        # via: https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
        golden_ratio_conjugate = 0.618033988749895
        data_list = list(self.data.items())
        for counter, (i, v) in enumerate(data_list):
            tag_name = ''
            next_idx = min(counter+1, len(data_list)-1)
            this_time = v['time']
            next_time = data_list[counter+1][1]['time'] if counter < next_idx else 0
            #print (i, this_time, next_time,(next_time - this_time), seq_info['int'])
            seq_info['group_prev'] = seq_info['group_next']
            if next_time and \
               (next_time - this_time) <= seq_info['int']:
                seq_info['group_next'] = True
            else:
                seq_info['group_next'] = False

            if seq_info['group_next'] == True and not seq_info['group_prev']:
                seq_info['idx'] += 1
                seq_info['salt'] += golden_ratio_conjugate
                seq_info['salt'] %= 1

            if seq_info['group_next'] or seq_info['group_prev']:
                tag_name = 'tag{}'.format(seq_info['idx'])
            else:
                tag_name = ''

            rgb_hex = ''
            if tag_name:
                if USE_COLOR_LIST:
                    color_idx = (seq_info['idx']-1) % len(IMG_SEQ_COLOR_LIST)
                    rgb_hex = IMG_SEQ_COLOR_LIST[color_idx]
                else:
                    rgb = colorsys.hls_to_rgb(seq_info['salt']*265, 0.8, 0.5)
                    rgb_hex = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'

                if tag_name not in seq_info['map']:
                    seq_info['map'][tag_name] = {
                        'color': rgb_hex,
                        'rows': [],
                        'row_keys': {},
                    }
                seq_info['map'][tag_name]['rows'].append(counter)
                seq_info['map'][tag_name]['row_keys'][i] = {'image_id': v['image_id']}

            self.data[i]['img_seq_tag_name'] = tag_name
            self.data[i]['img_seq_color'] = rgb_hex
        #print (seq_info)
        return seq_info

    def has_empty_species(self):
        for k,v in self.data.items():
            if v.get('annotation_species', '') == '':
                return True
        return False

