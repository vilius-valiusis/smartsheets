import requests


class Testrails:

    def __init__(self, connection_details, filters, ignore_filters=None):
        self._suites = []
        self._references = []
        self._filters = filters

        self._conn = connection_details

        self._build()

    def _build(self):
        self._set_suites()
        self._set_references()

    def _set_suites(self):
        list_of_suites = []
        r = requests.get(self._conn['URL_TESTRAIL_SUITES'], headers=self._conn['HEADER_TESTRAIL'],
                         auth=self._conn['AUTH_TESTRAIL'])
        self._is_request_working(r.status_code, 'Getting Testrail Suites')
        for suite in r.json():
            if any(s in suite['name'] for s in self._filters):

                suite_id = suite['id']
                list_of_suites.append(suite_id)
        self._suites = list_of_suites

    def _set_references(self):
        for suite_id in self._suites:
            url = self._conn['URL_TESTRAIL_CASES'] + str(suite_id)
            r = requests.get(url, headers=self._conn['HEADER_TESTRAIL'], auth=self._conn['AUTH_TESTRAIL'])
            m = "Getting references from TestRails SUIT ID: {suite_id}".format(suite_id=suite_id)

            self._is_request_working(r.status_code, m)
            for test_case in r.json():
                if not test_case['refs']:
                    continue
                reference = test_case['refs'].replace(" ", "").replace(")", "").replace("(", "").replace("  ", "")\
                    .split(',')
                [self._references.append(x) for x in reference]

    def get_suites(self):
        return self._suites

    def get_references(self):
        return self._references

    @staticmethod
    def _is_request_working(status, message):
        if status != 200:
            print('[{status}] Failed to perform get request. {m}'.format(status=status, m=message))
            print('Exiting ...')
            exit(0)
        else:
            print('[200] Request to Testrails was successful. {m}'.format(m=message))
            return True


