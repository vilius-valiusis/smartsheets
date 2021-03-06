from datetime import datetime

import requests


class Runscope:

    def __init__(self, con):
        self._con = con
        self._test_ids = []

        self._runscope = {
            "endpoints": [],
            "total_passed": 0,
            "total_failed": 0,
            "last_test": ''
        }
        self._build()

    def _build(self):
        self._set_test_ids()
        self._set_data()

    def _set_test_ids(self):
        r = requests.get(self._con['URL_RUNSCOPE'], headers=self._con['HEADER_RUNSCOPE'])
        self._is_request_working(r.status_code, 'Fetching Runscope tests IDs')
        for test_id in r.json()['data']:
            self._test_ids.append(test_id['id'])

    def _set_data(self):
        for test_id in self._test_ids:
            url = self._con['URL_RUNSCOPE'] + '/' + str(test_id) + "/results/latest"
            r = requests.get(url, headers=self._con['HEADER_RUNSCOPE'])
            message = 'Fetching latest results Runscope results for ID {id}'.format(id=str(test_id))
            data = r.json()['data']

            self._is_request_working(r.status_code, message)
            self._runscope['total_passed'] += int(data['assertions_passed'])
            self._runscope['total_failed'] += int(data['assertions_failed'])
            if data['finished_at'] is not None:

                finished_at_stamp = float(data['finished_at'])
                finished_at = datetime.utcfromtimestamp(finished_at_stamp).strftime('%H:%M:%S %m/%d/%y UTC')
            else:
                finished_at = 'Tests are yet to be run'

            self._runscope["last_test"] = finished_at

            for request in data['requests']:
                if request['result'] is not None:
                    if request['result'] == 'Pass':
                        self._runscope["total_passed"] += 1
                    if request['result'] == 'Fail':
                        self._runscope["total_failed"] += 1

                if request['url'] is not None:
                    self._runscope["endpoints"].append(
                        {
                            "url": request['url'].replace("https://", ""),
                            "result": request['result']
                        }
                    )

    def get_data(self):
        return self._runscope

    @staticmethod
    def _is_request_working(status, message):
        if status != 200:
            print('[{status}] Failed to perform get request. {m}'.format(status=status, m=message))
            print('Exiting ...')
            exit(0)
        else:
            print('[200] Request to Runscope was successful. {m}'.format(m=message))
            return True
