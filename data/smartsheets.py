import requests


class Smartsheets:

    def __init__(self, con, smartsheet_id):
        self._columns: dict
        self._smartsheet_id = str(smartsheet_id)
        self._set_columns(con)
        pass

    def _set_columns(self, con):
        url = con['URL_SMARTSHEETS'] + self._smartsheet_id
        r = requests.get(url, headers=con['HEADER_SMARTSHEETS'])
        print("Getting smartsheets with the ID of {id}".format(id=self._smartsheet_id))
        self._is_request_working(r.status_code)
        for column in r.json()['columns']:
            self._columns[column['title']] = column['id']

    def _set_row(self):
        pass

    def get_columns(self) -> dict:
        return self._columns

    @staticmethod
    def _is_request_working(status):
        if status != 200:
            print('[{status}] Failed to perform get request'.format(status=status))
            print('Exiting ...')
            exit(0)
        else:
            print('[200] Request to Smartsheets was successful')
            return True

