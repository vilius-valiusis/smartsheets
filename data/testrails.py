import requests


class Testrails:

    def __init__(self, connection_details):
        self._suites = []
        self._references = []

        self._set_suites(connection_details)
        self._set_references(connection_details)
        pass

    def _set_suites(self, con):
        list_of_suites = []
        r = requests.get(con['URL_TESTRAIL_SUITES'], headers=con['HEADER_TESTRAIL'], auth=con['AUTH_TESTRAIL'])
        self._is_request_working(r.status_code, '')
        for suite in r.json():
            if 'Mobile' in suite['name'] or 'Functional Verification - Release' in suite['name']:
                suite_id = suite['id']
                list_of_suites.append(suite_id)
        self._suites = list_of_suites

    def _set_references(self, con):
        for suite_id in self._suites:
            url = con['URL_TESTRAIL_CASES'] + str(suite_id)
            r = requests.get(url, headers=con['HEADER_TESTRAIL'], auth=con['AUTH_TESTRAIL'])
            m = "Getting references from TestRails SUIT ID: {suite_id}".format(suite_id=suite_id)
            self._is_request_working(r.status_code, m)
            for test_case in r.json():
                if not test_case['refs']:
                    continue
                reference = test_case['refs'].replace(" ", "").replace(")", "").replace("(", "").replace("  ", "")\
                    .split(',')
                [self._references.append(r) for r in reference]

    def get_suites(self):
        return self._suites

    def get_references(self):
        return self._references

    @staticmethod
    def _is_request_working(status, message):
        if status != 200:
            print('[{status}] Failed to perform get request'.format(status=status))
            print('Exiting ...')
            exit(0)
        else:
            print('[200] Request to Testrails was successful. {m}'.format(m=message))
            return True


