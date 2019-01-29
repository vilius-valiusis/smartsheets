import datetime
import re
from pprint import pprint

import requests


class Jira:

    def __init__(self, conn, references: list, labels, ignore_labels=None, ignore_sprints=[]):
        self._labels: list = labels
        self._ignore_labels = ignore_labels
        self._ignore_sprints = ignore_sprints
        self._conn = conn
        self._total_issues: int = 0
        self._references: list = references
        self._ticket_data: dict = {
            'date': '',
            'total': 0,
            'tickets': {},
            'severity': {},
            'priority': {},
            'status': {},
            'type': {},
            'storyReferences': {},
            'openBugs': [],
            'unlabeled': [],
            'references': references,
            'runscope': {},
            'openRuns': []
        }

    def build(self):
        self._set_date()
        self._set_total_issues()
        self._set_tickets()
        self._set_severity()
        self._set_priority()
        self._set_status()
        self._set_type()
        self._set_story_references()
        self._set_open_bugs()
        self._set_unlabeled()

    def _set_total_issues(self):
        r = requests.get(self._conn['URL_JIRA_TOTAL'], headers=self._conn['HEADER_JIRA'])
        self._is_request_working(r.status_code, 'Getting total number of Jira tickets.')
        self._total_issues = r.json()['total']
        self._ticket_data['total'] = self._total_issues

    def _ignore_ticket(self, sprint):
        for s in self._ignore_sprints:
            if sprint is not None and s in sprint[0]:
                return True
        return False

    def _is_labeled(self, labels):
        has_correct_labels = False
        has_incorrect_labels = False
        for l1 in labels:
            if self._ignore_labels:
                for l2 in self._ignore_labels:
                    if l1 == l2:
                        has_incorrect_labels = True
            for l2 in self._labels:
                if l1 == l2:
                    has_correct_labels = True
        return has_correct_labels, has_incorrect_labels

    def _set_date(self):
        month = datetime.date.today().strftime("%m")
        date = datetime.date.today().strftime("%d")
        year = datetime.date.today().strftime("%y")
        self._ticket_data['date'] = str(month + "/" + date + "/" + year)

    def _set_tickets(self):
        sprints = []
        for i in range(0, self._total_issues, 100):

            url = self._conn['URL_JIRA'] + self._conn['URL_PARAMS_JIRA'] + str(i)
            r = requests.get(url, headers=self._conn['HEADER_JIRA'])
            message = 'Getting the next 100 tickets starting from {no}.'.format(no=(i + 100))
            self._is_request_working(r.status_code, message)
            for ticket in r.json()['issues']:
                labels = ticket['fields']['labels']
                has_correct_labels, has_incorrect_labels = self._is_labeled(labels)
                sprint = ticket['fields']['customfield_10007']
                if has_correct_labels and not has_incorrect_labels and not self._ignore_ticket(sprint):
                    fields = ticket['fields']
                    key = ticket['key']
                    status = fields['status']['name']
                    # if sprint is not None:
                    #     print(sprint)
                    #     m = re.search('id=(.+?),', sprint[0])
                    #     n = re.search('name=(.+?),', sprint[0])
                    #     if m or n:
                    #         found = m.group(1)
                    #         found1 = n.group(1)
                    #         sprints.append((found, found1))
                    # if sprint is not None and sprint not in sprints:
                    #     sprints.append(sprint)
                    self._ticket_data['tickets'][key] = {
                        'Label': labels,
                        'priority': fields['priority']['name'],
                        'severity': fields['customfield_12825']['value'],
                        'status': fields['status']['name'],
                        'type': fields['issuetype']['name'],
                        'isTestable': 'Not-Testable' not in labels,
                        'isOpenBug': fields['issuetype']['name'] == 'Bug' and status != 'Done',
                        'isLabeled': labels != [],
                        'hasTestCase': key in self._references,
                        'hasAssignedSprint': sprint is not None
                    }

    def _set_severity(self):
        severity_dict = {
            'none': {'tickets': []},
            'low': {'tickets': []},
            'medium': {'tickets': []},
            'high': {'tickets': []},
            'critical': {'tickets': []}
        }

        for k, v in self._ticket_data['tickets'].items():
            if v['isOpenBug']:
                if v['severity'] == 'Low':
                    severity_dict['low']['tickets'].append(k)

                elif v['severity'] == 'Medium':
                    severity_dict['medium']['tickets'].append(k)

                elif v['severity'] == 'High':
                    severity_dict['high']['tickets'].append(k)

                elif v['severity'] == 'Critical':
                    severity_dict['critical']['tickets'].append(k)

                else:
                    severity_dict['none']['tickets'].append(k)
        self._ticket_data['severity'] = severity_dict

    def _set_priority(self):
        priority_dict = {
            'P1': {'tickets': []},
            'P2': {'tickets': []},
            'P3': {'tickets': []},
            'P4': {'tickets': []},
            'P5': {'tickets': []}}

        for k, v in self._ticket_data['tickets'].items():
            if v['isOpenBug']:
                if v['priority'] == 'P1 - Blocker':
                    priority_dict['P1']['tickets'].append(k)

                elif v['priority'] == 'P2 - Critical':
                    priority_dict['P2']['tickets'].append(k)

                elif v['priority'] == 'P3 - Major':
                    priority_dict['P3']['tickets'].append(k)

                elif v['priority'] == 'P4 - Minor':
                    priority_dict['P4']['tickets'].append(k)

                elif v['priority'] == 'P5 - Trivial':
                    priority_dict['P5']['tickets'].append(k)
        self._ticket_data['priority'] = priority_dict

    def _set_status(self):
        status_dict = {
            'Draft': {'tickets': []},
            'In Progress': {'tickets': []},
            'Ready for QA': {'tickets': []},
            'QA Complete': {'tickets': []},
            'Done': {'tickets': []},
            'Code Review': {'tickets': []},
            'Blocked': {'tickets': []},
            'Defects Found': {'tickets': []},
            'Ready for DEV': {'tickets': []},
            'QA in Progress': {'tickets': []}}

        for k, v in self._ticket_data['tickets'].items():
            status = v['status']

            if status == 'Draft':
                status_dict['Draft']['tickets'].append(k)

            elif status == 'In Progress':
                status_dict['In Progress']['tickets'].append(k)

            elif status == 'Ready for QA':
                status_dict['Ready for QA']['tickets'].append(k)

            elif status == 'QA Complete':
                status_dict['QA Complete']['tickets'].append(k)

            elif status == 'Done':
                status_dict['Done']['tickets'].append(k)

            elif status == 'Code Review':
                status_dict['Code Review']['tickets'].append(k)

            elif status == 'Blocked':
                status_dict['Blocked']['tickets'].append(k)

            elif status == 'Defects Found':
                status_dict['Defects Found']['tickets'].append(k)

            elif status == 'Ready for DEV':
                status_dict['Ready for DEV']['tickets'].append(k)

            elif status == 'QA in Progress':
                status_dict['QA in Progress']['tickets'].append(k)

        self._ticket_data['status'] = status_dict

    def _set_type(self):
        type_dict = {
            'Bug': {'tickets': []},
            'Story': {'tickets': []},
            'Sub-task': {'tickets': []},
            'Task': {'tickets': []},
            'Epic': {'tickets': []}}

        for k, v in self._ticket_data['tickets'].items():
            ticket_type = v['type']
            if ticket_type == 'Bug':
                type_dict['Bug']['tickets'].append(k)

            elif ticket_type == 'Story':
                type_dict['Story']['tickets'].append(k)

            elif ticket_type == 'Sub-task':
                type_dict['Sub-task']['tickets'].append(k)

            elif ticket_type == 'Task':
                type_dict['Task']['tickets'].append(k)

            elif ticket_type == 'Epic':
                type_dict['Epic']['tickets'].append(k)

        self._ticket_data['type'] = type_dict

    def _set_story_references(self):
        story_reference_dict = {
            'hasReference': [],
            'hasNoReference': [],
            'hasReferenceButDraftOrBlocked': [],
        }

        for k, v in self._ticket_data['tickets'].items():
            if v['type'] == 'Story' and v['isTestable']:
                if v['hasTestCase'] and not (v['status'] == 'Blocked' or v['status'] == 'Draft'):
                    story_reference_dict['hasReference'].append(k)

                elif not v['hasTestCase'] and v['hasAssignedSprint']:
                    story_reference_dict['hasNoReference'].append(k)

                elif (v['status'] == 'Blocked' or v['status'] == 'Draft') and v['hasTestCase']:
                    story_reference_dict['hasReferenceButDraftOrBlocked'].append(k)
        self._ticket_data['storyReferences'] = story_reference_dict

    def _set_open_bugs(self):
        for k, v in self._ticket_data['tickets'].items():
            if v['isOpenBug']:
                self._ticket_data['openBugs'].append(k)

    def _set_unlabeled(self):
        for k, v in self._ticket_data['tickets'].items():
            if not v['isLabeled']:
                self._ticket_data['unlabeled'].append(k)

    def get_ticket_data(self):
        return self._ticket_data

    @staticmethod
    def _is_request_working(status, message):
        if status != 200:
            print('[{status}] Failed to perform get request. {m}'.format(status=status, m=message))
            print('Exiting ...')
            exit(0)
        else:
            print('[200] Request to Jira was successful. {m}'.format(m=message))
            return True
