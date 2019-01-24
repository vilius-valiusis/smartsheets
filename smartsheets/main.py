import json
from pprint import pprint

from data.jira import Jira
from data.smartsheets import Smartsheets
from data.testrails import Testrails



pre_r1_sprint_ids = {
    ('1128', 'ALT AES - Sprint 1 8/15 - 8/29'),
    ('1129', 'ALT AES - Sprint 2 8/29 - 9/13'),
    ('1130', 'ALT AES - Sprint 3 9/13 - 9/26'),
    ('1131', 'ALT AES - Sprint 4 9/26 -10/11'),
    ('1132', 'ALT AES - Sprint 5 10/11-10/24'),
    ('1133', 'ALT AES - Sprint 6 10/24- 11/9'),
    ('1149', 'Alterra AES Archive'),
    ('1171', 'ALT AES Sprint 8 - 11/9- 11/26'),
    ('1172', 'ALT AES Sprint 9 - 11/26-12/7'),
    ('1197', 'ALT AES Sprint10- 12/7 - 1/4'),
    # ('1252', 'RELEASE 1 Bugs / Enhancements'),
    # ('1270', 'ALT AES Sprint 12')
}

pre_r1_mobile_sprint_ids = {
    ('1134', 'ALTFueled-Sprint1 8/15 - 8/29'),
    ('1135', 'ALTFueled-Sprint2 8/29 - 9/12'),
    ('1136', 'ALTFueled-Sprint3 9/12 - 9/26'),
    ('1137', 'ALTFueled-Sprint4 9/26 -10/10'),
    ('1138', 'ALTFueled-Sprint5 10/10-10/24'),
    ('1139', 'ALTFueled-Sprint6 10/24- 11/9'),
    ('1141', 'ALTDroid-Sprint1 8/15 - 8/29'),
    ('1142', 'ALTDroid-Sprint2 8/29 - 9/12'),
    ('1143', 'ALTDroid-Sprint4 9/26 -10/10'),
    ('1144', 'ALTDroid-Sprint5 10/10-10/24'),
    ('1150', 'ALTDroid-Sprint8 11/9-11/26'),
    ('1166', 'ALTDroid-Sprint3 9/12- 9/26'),
    ('1172', 'ALT AES Sprint 9 - 11/26-12/7'),
    ('1176', 'ALTFueled-Sprint 9 11/26-12/7'),
    ('1197', 'ALT AES Sprint10- 12/7 - 1/4'),
    ('1219', 'ALTFueled-Sprint9 11/26-12/7'),
    ('1220', 'ALTDroid-Sprint10 12/7-12/21'),
    ('1232', 'ALTDroid-Sprint 9 11/26-12/7'),
    ('1236', 'ALTFueled-Sprint10 12/7-12/21'),
    # ('1252', 'RELEASE 1 Bugs / Enhancements'),
    # ('1259', 'ALT iOS Sprint 12'),
    # ('1260', 'ALT Android Sprint 12')
}

ios = 'FueledAlterra'
android = 'FueledAndroidAlterra'
aes = 'AESAlterra'

testrails_mobile_suit_filters = ['Functional Verification - Release', 'Mobile']
testrails_backend_suit_filters = ['Backend Verification', 'Backend']

backend_ignore_sprints = ['Alterra AES Archive']


def read_json(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)


def main():
    con = read_json('connection_vars.json')
    sprint_mobile_coverage = read_json('ALT in Sprint Mobile Coverage - Daily.json')
    sprint_backend_coverage = read_json('ALT in Sprint Back-end Coverage - Daily.json')
    mobile_coverage = read_json('Mobile Test Coverage.json')
    backend_coverage = read_json('Back-End Test Coverage.json')

    con['AUTH_TESTRAIL'] = (testRailEmail, testRailPassword)
    con['HEADER_SMARTSHEETS']['Authorization'] = 'Bearer ' + smartSheetPassword
    con['HEADER_JIRA']['Authorization'] = 'Basic ' + jiraBasicAuth

    # Mobile Sprint Coverage
    # testrails = Testrails(con, testrails_mobile_suit_filters)
    # references = testrails.get_references()
    # labels = [ios, android]
    # jira = Jira(con, references, labels)
    # ticket_data = jira.get_ticket_data()
    # ALT in Sprint Mobile Coverage - Daily
    # Smartsheets(con, sprint_mobile_coverage, ticket_data)
    # Mobile Test Coverage
    Smartsheets(con, mobile_coverage, {}).create_sheet()

    # Backend Sprint Coverage
    # testrails = Testrails(con, testrails_backend_suit_filters)
    # references = testrails.get_references()
    # labels = [aes]
    # ignore_labels = [ios, android]
    # jira = Jira(con, references, labels, ignore_labels=ignore_labels, ignore_sprints=backend_ignore_sprints)
    # ticket_data = jira.get_ticket_data()
    # Smartsheets(con, sprint_backend_coverage, ticket_data)


if __name__ == main():
    main()
