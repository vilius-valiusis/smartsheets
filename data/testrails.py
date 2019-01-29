import requests


class Testrails:

    def __init__(self, connection_details, filters=[]):
        self._suites = []
        self._references = []
        self._filters = filters
        self._run_type = ['get_runs', 'get_plans']

        self._conn = connection_details
        self._open_runs = []

    def build(self):
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

    def get_open_runs(self):
        for run_type in self._run_type:
            url = self._conn['URL_TESTRAILS'] + run_type + '/' + self._conn['TESTRAILS_PROJECT_ID'] + '&is_completed=0'
            r = requests.get(url, headers=self._conn['HEADER_TESTRAIL'], auth=self._conn['AUTH_TESTRAIL'])
            self._is_request_working(r.status_code, 'Fetching open runs of type {run_type}'.format(run_type=run_type))

            for run in r.json():
                self._open_runs.append({
                    "name":     run['name'],
                    'passed':   run['passed_count'],
                    'blocked':  run['blocked_count'],
                    'untested': run['untested_count'],
                    're-test':  run['retest_count'],
                    'failed':   run['failed_count']
                })
        return self._open_runs

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


