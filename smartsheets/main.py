import json
from pprint import pprint

from data.jira import Jira
from data.smartsheets import Smartsheets
from data.testrails import Testrails

testRailPassword = 'Login123!'
testRailEmail = 'engineering@theexperienceengine.com'
jiraBasicAuth = 'dmlsaXVzLnZhbGl1c2lzQGFjY2Vzc28uY29tOmMyZm5jNm1GWlFuWG9zS0NnNUpENzExQQ=='
smartSheetPassword = '50jhmo20cy2gya3mxvoj1f3xhh'

ios = 'FueledAlterra'
android = 'FueledAndroidAlterra'
aes = 'AESAlterra'


def read_json(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)


def main():
    con = read_json('connection_vars.json')
    con['AUTH_TESTRAIL'] = (testRailEmail, testRailPassword)
    con['HEADER_SMARTSHEETS']['Authorization'] = 'Bearer ' + smartSheetPassword
    con['HEADER_JIRA']['Authorization'] = 'Basic ' + jiraBasicAuth

    smartsheet_id = con["SMARTSHEETS"]["ALT in Sprint Mobile Coverage - Daily"]
    ss = Smartsheets(con, smartsheet_id)
    col = ss.get_columns()
    # ss.build_smartsheets_sample_json(file_name='test.json')
    # testrails = Testrails(con)
    # references = testrails.get_references()
    # labels = [ios, android]
    # jira = Jira(con, references, labels)
    # pprint(jira.get_ticket_data())


if __name__ == main():
    main()
