#!/usr/bin/python3

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os
#dir = os.path.dirname(__file__)
dir = os.getcwd()
token = os.path.join(dir, 'options/token.json') 
credentials = os.path.join(dir, 'options/credentials.json')

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SAMPLE_SPREADSHEET_ID = '1pmdLn_KFm2_821NiDhn_QHWblvAfAcRUdaA3OCIE58k'
store = file.Storage(token)
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(credentials, SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))
sheet = service.spreadsheets()
simplelistdict = {}
sourcelistsarray = {}
sourcelistsdict = {}
routers = {}

def filldict():
    SAMPLE_RANGE_NAME = 'routerlist!A:B'
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        a = open(dir+'/temp/hosts-mkr','w')
        a.write(f'[mkr-firewall-matrix]\n\n')
        for row in values:
            a.write(f'{row[0]} ansible_ssh_port=2222 router_id={row[1]}\n')
            routers[row[1]] = []
        a.close


def buildservicelists():
    SAMPLE_RANGE_NAME = 'servicematrix!B2:H'
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            if (row[3] == "comenergo" or row[3] == "shared") and row[1] != '':
                if row[2] not in simplelistdict:
                    simplelistdict[row[2]] = []
                simplelistdict[row[2]].append([row[1],row[0],row[4]])
    
def buildlocationlists():
    SAMPLE_RANGE_NAME = 'locationlist!A2:C'
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        for row in values:
            if not row[0] in simplelistdict:
                simplelistdict[row[0]] = []
            simplelistdict[row[0]].append([row[1],row[0],row[2]])

def buildsourcelistsarray(range_name, sourcelistsarray):
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=range_name).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        destinationlist = values[0]
        row = 0
        for line in values: 
            col = 0
            currentlocation = ''
            for cell in line:
                if col == 0 and cell in simplelistdict:
                    currentlocation = cell
                if col != 0 and row == 0 and cell not in sourcelistsarray:
                    sourcelistsarray[destinationlist[col]] = []
                if col != 0 and row != 0 and cell != '':
                    sourcelistsarray[destinationlist[col]].append(currentlocation)
                col += 1
            row += 1

def buildsourcelists(sourcelistsarray):
    for sourcelist in sourcelistsarray:
        if sourcelist not in sourcelistsdict:
            sourcelistsdict[sourcelist] = []
        for simplelist in sourcelistsarray[sourcelist]:
            sourcelistsdict[sourcelist].extend(simplelistdict[simplelist])

if __name__ == '__main__':
    print("build services simple lists")
    buildservicelists()
    print("build locations simple lists")
    buildlocationlists()
    print("create location-location lists")
    buildsourcelistsarray('location-location!A:z', sourcelistsarray)
    buildsourcelistsarray('location-service!A:Z', sourcelistsarray)
    buildsourcelistsarray('service-service!A:Z', sourcelistsarray)
    buildsourcelists(sourcelistsarray)

    filldict()
    for simplelist in simplelistdict:
        for record in simplelistdict[simplelist]:
            if record[2] not in routers and record[2] != '':
                routers[record[2]] = []
            if record[2] != '' and simplelist not in routers[record[2]]:
                routers[record[2]].append(simplelist)

    for router in routers:
        if os.path.exists(dir+'/temp/matrix_'+router+'.rsc'):
            os.remove(dir+'/temp/matrix_'+router+'.rsc')
        a = open(dir+'/temp/matrix_'+router+'.rsc','a')
        a.write(f'/ip firewall address-list\n')
        print('write rsc', router)
        for record in routers[router]:
            for sourcelist in sourcelistsdict:
                for simplelist in sourcelistsdict[sourcelist]:
                    if record == sourcelist:
                        a.write(f'add address={simplelist[0]} comment=\"_ansible_{simplelist[1]}->{sourcelist}\" list=_ans_src_{sourcelist}\n')
            for simplelist in simplelistdict:
                if simplelist == record :
                    for address in simplelistdict[simplelist]:
                        a.write(f'add address={address[0]} comment=\"_ansible_{address[1]}\" list=_ans_dst_{simplelist}\n')
        a.write(f'/ip firewall filter\n')
        for record in routers[router]:
            a.write(f'add chain=forward src-address-list=_ans_src_{record} dst-address-list=_ans_dst_{record} action=accept comment=\"ANSIBLE MATRIX RULE {record}\"\n')
        a.write(f'add action=drop chain=forward comment=\"ANSIBLE DROP ALL FORWARD\" connection-nat-state=!dstnat connection-state=new\n')
        a.write(f'add action=drop chain=input in-interface-list=WAN comment=\"ANSIBLE DROP ALL INPUT\"\n')            
        a.close

