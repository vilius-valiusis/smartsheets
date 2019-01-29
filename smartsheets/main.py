import json
import sys
from pprint import pprint

import requests

from data.jira import Jira
from data.runscope import Runscope
from data.smartsheets import Smartsheets
from data.testrails import Testrails


testRailPassword = sys.argv[1]
testRailEmail = sys.argv[2]
jiraBasicAuth = sys.argv[3]
smartSheetPassword = sys.argv[4]
runScopePassword = sys.argv[5]

pre_r1_sprint_ids = [
    'ALT AES - Sprint 1 8/15 - 8/29', 'ALT AES - Sprint 2 8/29 - 9/13', 'ALT AES - Sprint 3 9/13 - 9/26',
    'ALT AES - Sprint 4 9/26 -10/11', 'ALT AES - Sprint 5 10/11-10/24', 'ALT AES - Sprint 6 10/24- 11/9',
    'Alterra AES Archive', 'ALT AES Sprint 8 - 11/9- 11/26', 'ALT AES Sprint 9 - 11/26-12/7',
    'ALT AES Sprint10- 12/7 - 1/4']


pre_r1_mobile_sprint_ids = [
    'ALTFueled-Sprint1 8/15 - 8/29', 'ALTFueled-Sprint2 8/29 - 9/12', 'ALTFueled-Sprint3 9/12 - 9/26',
    'ALTFueled-Sprint4 9/26 -10/10', 'ALTFueled-Sprint5 10/10-10/24', 'ALTFueled-Sprint6 10/24- 11/9',
    'ALTDroid-Sprint1 8/15 - 8/29', 'ALTDroid-Sprint2 8/29 - 9/12', 'ALTDroid-Sprint4 9/26 -10/10',
    'ALTDroid-Sprint5 10/10-10/24', 'ALTDroid-Sprint8 11/9-11/26', 'ALTDroid-Sprint3 9/12- 9/26',
    'ALT AES Sprint 9 - 11/26-12/7', 'ALTFueled-Sprint 9 11/26-12/7', 'ALT AES Sprint10- 12/7 - 1/4',
    'ALTFueled-Sprint9 11/26-12/7', 'ALTDroid-Sprint10 12/7-12/21', 'ALTDroid-Sprint 9 11/26-12/7',
    'ALTFueled-Sprint10 12/7-12/21']


testrails_mobile_suit_filters = ['Functional Verification - Release', 'Mobile']
testrails_backend_suit_filters = ['Backend Verification', 'Backend']
jira_mobile_labels = ['FueledAlterra', 'FueledAndroidAlterra']
jira_backend_labels = ['AESAlterra']
jira_backend_labels_ignore = ['FueledAlterra', 'FueledAndroidAlterra']

backend_ignore_sprints = ['Alterra AES Archive']


def read_json(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)


# def create_sheet(con):
#     url_o = con['URL_SMARTSHEETS'] + str(6110252539111300)
#     r = requests.get(url_o, headers=con['HEADER_SMARTSHEETS'])
#     columns = r.json()['columns']
#     newCols = []
#     for col in columns:
#
#         if 'primary' in col:
#             newCols.append({
#                 'title': col['title'],
#                 'type': col['type'],
#                 'primary': col['primary']
#             })
#         else:
#             newCols.append({
#                 'title': col['title'],
#                 'type': col['type']
#             })
#
#     TEST = {"name": "Testrail: Open Runs", 'columns': newCols}
#     url_r = 'https://api.smartsheet.com/2.0/workspaces/4181067549697924/sheets'
#     r = requests.post(url_r, headers=con['HEADER_SMARTSHEETS'], json=TEST)
#     print(r.status_code, r.content)


def run_mobile(con):
    sprint_mobile_coverage = read_json('templates/ALT in Sprint Mobile Coverage - Daily.json')
    sprint_mobile_coverage_historical = read_json('templates/ALT in Sprint Mobile Coverage - Historical.json')
    mobile_coverage = read_json('templates/Mobile Test Coverage.json')

    testrails = Testrails(con, testrails_mobile_suit_filters)
    testrails.build()
    references = testrails.get_references()
    jira = Jira(con, references, jira_mobile_labels, ignore_sprints=pre_r1_mobile_sprint_ids)
    jira.build()
    ticket_data = jira.get_ticket_data()

    # ALT in Sprint Mobile Coverage - Daily
    Smartsheets(con, sprint_mobile_coverage, ticket_data)
    # Mobile Test Coverage
    Smartsheets(con, mobile_coverage, ticket_data)
    # ALT in Sprint Mobile Coverage - historical
    Smartsheets(con, sprint_mobile_coverage_historical, ticket_data, build_type='historical')


def run_backend(con):
    sprint_backend_coverage = read_json('templates/ALT in Sprint Back-end Coverage - Daily.json')
    sprint_mobile_coverage_historical = read_json('templates/ALT in Sprint Back-end Coverage - Historical.json')
    backend_coverage = read_json('templates/Back-End Test Coverage.json')

    testrails = Testrails(con, testrails_backend_suit_filters)
    testrails.build()
    references = testrails.get_references()
    jira = Jira(con, references, jira_backend_labels,
                ignore_labels=jira_backend_labels_ignore, ignore_sprints=pre_r1_sprint_ids)
    jira.build()
    ticket_data = jira.get_ticket_data()

    # ALT in Sprint Back-end Coverage - Daily
    Smartsheets(con, sprint_backend_coverage, ticket_data)
    # Back-end Test Coverage
    Smartsheets(con, backend_coverage, ticket_data)
    # ALT in Sprint Mobile Coverage - historical
    Smartsheets(con, sprint_mobile_coverage_historical, ticket_data, build_type='historical')


def run_runscope(con):
    runscope_daily = read_json('templates/Runscope - Daily.json')
    runscope_historical = read_json('templates/Runscope - Historical.json')
    runscope_current_status = read_json('templates/Runscope - Current Status.json')

    runscope = Runscope(con)
    runscope_data = runscope.get_data()
    ticket_data = Jira(con, [], []).get_ticket_data()
    ticket_data['runscope'] = runscope_data

    Smartsheets(con, runscope_daily, ticket_data)
    Smartsheets(con, runscope_historical, ticket_data, build_type='historical')
    Smartsheets(con, runscope_current_status, ticket_data)


def run_testrails(con):
    testrail_open_runs = read_json('templates/testrail open runs.json')
    testrails = Testrails(con)
    open_runs = testrails.get_open_runs()
    ticket_data = Jira(con, [], []).get_ticket_data()
    ticket_data['openRuns'] = open_runs

    Smartsheets(con, testrail_open_runs, ticket_data)


def main():
    con = read_json('connection_vars.json')

    con['AUTH_TESTRAIL'] = (testRailEmail, testRailPassword)
    con['HEADER_SMARTSHEETS']['Authorization'] = 'Bearer ' + smartSheetPassword
    con['HEADER_JIRA']['Authorization'] = 'Basic ' + jiraBasicAuth
    con['HEADER_RUNSCOPE']['Authorization'] = 'Bearer ' + runScopePassword

    run_mobile(con)
    run_backend(con)
    run_runscope(con)
    run_testrails(con)

    # create_sheet(con)


if __name__ == main():
    main()
