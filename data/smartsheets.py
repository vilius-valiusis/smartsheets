import json
import random

import requests


class Smartsheets:

    def __init__(self, conn, smartsheet_id):
        self._columns: dict = {}
        self._smartsheet_id = str(smartsheet_id)
        self._set_columns(conn)
        pass

    def _set_columns(self, conn):
        url = conn['URL_SMARTSHEETS'] + self._smartsheet_id
        r = requests.get(url, headers=conn['HEADER_SMARTSHEETS'])
        print("Getting smartsheets with the ID of {id}".format(id=self._smartsheet_id))
        self._is_request_working(r.status_code)
        for column in r.json()['columns']:
            self._columns[column['title']] = column['id']

    def _set_row(self):
        pass

    def get_columns(self) -> dict:
        return self._columns

    def build_smartsheets_sample_json(self, col=None, file_name=None):
        smartsheet_dict = {self._smartsheet_id: []}

        if col is None:
            col = self._columns

        if file_name is None:
            file_name = 'smartsheet_' + str(random.random() * 10000)

        if col:
            for k in col:
                smartsheet_dict[self._smartsheet_id].append(
                    {
                        'title':    k,
                        'action':   '' if 'List' in k else 'len',  # single or multiline
                        'value':    [""]
                    }
                )
            with open(file_name, 'w') as outfile:
                json.dump(smartsheet_dict, outfile, indent=2)
        else:
            print('[ERROR] JSON was not built because columns is empty.')

    @staticmethod
    def _is_request_working(status):
        if status != 200:
            print('[{status}] Failed to perform get request'.format(status=status))
            print('Exiting ...')
            exit(0)
        else:
            print('[200] Request to Smartsheets was successful')
            return True

