from pprint import pprint

import requests


class Smartsheets:

    def __init__(self, conn, smartsheet, ticket_data: dict, build_type='normal'):
        self._columns: dict = {}
        self._smartsheet = smartsheet
        self._conn = conn
        self._ticket_data = ticket_data
        self._build_type = build_type

        self._build()

    def _build(self):
        self._set_columns()

        if self._build_type == 'normal':
            self._delete_rows()

        self._set_rows()

    def _set_columns(self):
        url = self._conn['URL_SMARTSHEETS'] + self._smartsheet['smarthsheet_id']
        r = requests.get(url, headers=self._conn['HEADER_SMARTSHEETS'])
        message = "Fetching smartsheet with the ID: {id}".format(id=self._smartsheet['smarthsheet_id'])
        self._is_request_working(r, message)
        for column in r.json()['columns']:
            self._columns[column['title']] = column['id']
        pass

    def _delete_rows(self):
        row_ids = []
        url = self._conn['URL_SMARTSHEETS'] + self._smartsheet['smarthsheet_id']
        r = requests.get(url, headers=self._conn['HEADER_SMARTSHEETS'])
        message = "Fetching column IDs for smartsheet ID: {id}".format(id=self._smartsheet['smarthsheet_id'])
        self._is_request_working(r, message)

        [row_ids.append(str(row['id'])) for row in r.json()['rows']]

        for row in range(0, len(row_ids), 450):
            id_string = ",".join(row_ids[row:450 + row])
            url = self._conn['URL_SMARTSHEETS'] + self._smartsheet['smarthsheet_id'] + '/rows?ids=' + id_string
            r = requests.delete(url, headers=self._conn['HEADER_SMARTSHEETS'])
            message = "Deleting the next 450 rows with starting index of: {row}".format(row=len(row_ids[row:450 + row]))
            self._is_request_working(r, message)

    @staticmethod
    def _set_row_data(json, col_id, data, summary_format):
        json.setdefault("cells", []).append({"columnId": col_id, "value": data, "format": summary_format})

    def _set_rows(self):
        url = self._conn['URL_SMARTSHEETS'] + self._smartsheet['smarthsheet_id'] + '/rows'
        data = {}
        if self._ticket_data['tickets']:
            data = self._ticket_data['tickets']
        elif self._ticket_data['runscope']:
            data = self._ticket_data['runscope']['endpoints']
        elif self._ticket_data['openRuns']:
            data = self._ticket_data['openRuns']

        for i, v in enumerate(data):
            json = {"toBottom": 'true', "cells": []}

            total_rows = -1
            if 'totalRows' in self._smartsheet:
                total_rows = self._smartsheet['totalRows']
            if i == total_rows and total_rows != -1:
                break

            for col in self._smartsheet['mappings']:
                sub_value = ''
                col_id = self._columns[col['title']]
                var = self._ticket_data

                if col['action'] != 'valueAsIs':
                    for location in col['value']:
                        var = var[location]
                if 'sub_value' in col:
                    sub_value = col['sub_value']

                formatting = self._smartsheet['formatting'][col['format']]
                row_no = -1
                action = col['action']
                if 'row' in col:
                    row_no = col['row']

                if (i == 0 and row_no == -1) or (row_no != -1 and row_no == i):
                    if action == 'len' and sub_value == '':
                        self._set_row_data(json, col_id, len(var), formatting)
                        continue
                    if action == 'int' or action == 'str':
                        if sub_value == '':
                            self._set_row_data(json, col_id, var, formatting)
                            continue
                        else:
                            self._set_row_data(json, col_id, var[i][sub_value], formatting)
                            continue

                    if action == 'valueAsIs' and sub_value == '':
                        self._set_row_data(json, col_id, col['value'], formatting)
                        continue

                if action == 'valueAsIs' and row_no != -1 and row_no == i:
                    self._set_row_data(json, col_id, col['value'], formatting)
                    continue

                if action == 'get' and i < len(var):
                    if sub_value == '':
                        self._set_row_data(json, col_id, var[i], formatting)
                        continue
                    else:
                        self._set_row_data(json, col_id, var[i][sub_value], formatting)
                        continue

            r = requests.post(url, headers=self._conn['HEADER_SMARTSHEETS'], json=json)
            message = 'Create row: {row}'.format(row=i)
            self._is_request_working(r, message)

    def get_columns(self) -> dict:
        return self._columns

    @staticmethod
    def _is_request_working(r, message):
        if r.status_code != 200:
            print('[{status}] Failed to perform get request. {m}'.format(status=r.status_code, m=message))
            pprint('[ERROR_CONTENT] \n{content}'.format(content=r.content))
            print('Exiting ...')
            exit(0)
        else:
            print('[200] Request to Smartsheets was successful. {m}'.format(m=message))
            return True

