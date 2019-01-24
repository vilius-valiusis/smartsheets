import random
from pprint import pprint
from time import sleep

import requests


class Smartsheets:

    def __init__(self, conn, smartsheet, ticket_data: dict):
        self._columns: dict = {}
        self._smartsheet = smartsheet
        self._conn = conn
        self._ticket_data = ticket_data

        # self._build()

    def create_sheet(self):
        url_o = self._conn['URL_SMARTSHEETS'] + str(1135760750471044)
        r = requests.get(url_o, headers=self._conn['HEADER_SMARTSHEETS'])
        columns = r.json()['columns']
        newCols = []
        for col in columns:

            if 'primary' in col:
                newCols.append({
                    'title': col['title'],
                    'type': col['type'],
                    'primary': col['primary']
                })
            else:
                newCols.append({
                    'title': col['title'],
                    'type': col['type']
                })

        TEST = {"name": "Unit Tests: Android", 'columns': newCols}
        url_r = 'https://api.smartsheet.com/2.0/workspaces/4181067549697924/sheets'
        r = requests.post(url_r, headers=self._conn['HEADER_SMARTSHEETS'], json=TEST)
        print(r.status_code, r.content)

    def _build(self):
        self._set_columns()
        self._delete_rows()
        self._set_rows()

    def _set_columns(self):
        url = self._conn['URL_SMARTSHEETS'] + self._smartsheet['smarthsheet_id']
        r = requests.get(url, headers=self._conn['HEADER_SMARTSHEETS'])
        message = "Fetching smartsheet with the ID: {id}".format(id=self._smartsheet['smarthsheet_id'])
        self._is_request_working(r.status_code, message)
        for column in r.json()['columns']:
            self._columns[column['title']] = column['id']
        pass

    def _delete_rows(self):
        row_ids = []
        url = self._conn['URL_SMARTSHEETS'] + self._smartsheet['smarthsheet_id']
        r = requests.get(url, headers=self._conn['HEADER_SMARTSHEETS'])
        message = "Fetching column IDs for smartsheet ID: {id}".format(id=self._smartsheet['smarthsheet_id'])
        self._is_request_working(r.status_code, message)

        [row_ids.append(str(row['id'])) for row in r.json()['rows']]

        for row in range(0, len(row_ids), 450):
            id_string = ",".join(row_ids[row:450 + row])
            url = self._conn['URL_SMARTSHEETS'] + self._smartsheet['smarthsheet_id'] + '/rows?ids=' + id_string
            r = requests.delete(url, headers=self._conn['HEADER_SMARTSHEETS'])
            message = "Deleting the next 450 rows with starting index of: {row}".format(row=len(row_ids[row:450 + row]))
            self._is_request_working(r.status_code, message)

    @staticmethod
    def _set_row_data(json, col_id, data, summary_format):
        json.setdefault("cells", []).append({"columnId": col_id, "value": data, "format": summary_format})

    def _set_rows(self):
        url = self._conn['URL_SMARTSHEETS'] + self._smartsheet['smarthsheet_id'] + '/rows'

        for i, v in enumerate(self._ticket_data['tickets']):
            json = {"toBottom": 'true', "cells": []}

            total_rows = -1
            if 'totalRows' in self._smartsheet:
                total_rows = self._smartsheet['totalRows']
            if i == total_rows and total_rows != -1:
                break

            for col in self._smartsheet['mappings']:
                col_id = self._columns[col['title']]
                var = self._ticket_data
                if col['action'] != 'valueAsIs':
                    for location in col['value']:
                        var = var[location]

                formatting = self._smartsheet['formatting'][col['format']]
                row_no = -1
                if 'row' in col:
                    row_no = col['row']

                if col['action'] == 'len' and row_no != -1 and row_no == i:
                    self._set_row_data(json, col_id, len(var), formatting)
                    continue

                if col['action'] == 'len' and i == 0 and row_no == -1:
                    self._set_row_data(json, col_id, len(var), formatting)
                    continue

                if col['action'] == 'valueAsIs' and row_no != -1 and row_no == i:
                    self._set_row_data(json, col_id, col['value'], formatting)
                    continue

                if col['action'] == 'int' and i == 0 and row_no == -1:
                    self._set_row_data(json, col_id, var, formatting)
                    continue

                if col['action'] == 'int' and row_no != -1 and row_no == i:
                    self._set_row_data(json, col_id, var, formatting)
                    continue

                if col['action'] == 'get' and i < len(var):
                    self._set_row_data(json, col_id, var[i], formatting)
                    continue

            r = requests.post(url, headers=self._conn['HEADER_SMARTSHEETS'], json=json)
            message = 'Create row: {row}'.format(row=i)
            self._is_request_working(r.status_code, message)

    def get_columns(self) -> dict:
        return self._columns

    # def build_smartsheets_sample_json(self, col=None, file_name=None):
    #     smartsheet_dict = {self._smartsheet_id: []}
    #
    #     if col is None:
    #         col = self._columns
    #
    #     if file_name is None:
    #         file_name = 'smartsheet_' + str(random.random() * 10000)
    #
    #     if col:
    #         for k in col:
    #             smartsheet_dict[self._smartsheet_id].append(
    #                 {
    #                     'title':    k,
    #                     'action':   '' if 'List' in k else 'len',  # single or multiline
    #                     'value':    [""]
    #                 }
    #             )
    #         with open(file_name, 'w') as outfile:
    #             json.dump(smartsheet_dict, outfile, indent=2)
    #     else:
    #         print('[ERROR] JSON was not built because columns is empty.')

    @staticmethod
    def _is_request_working(status, message):
        if status != 200:
            print('[{status}] Failed to perform get request. {m}'.format(status=status, m=message))
            print('Exiting ...')
            exit(0)
        else:
            print('[200] Request to Smartsheets was successful. {m}'.format(m=message))
            return True

