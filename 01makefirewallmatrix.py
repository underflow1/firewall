#!/usr/bin/python3
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os, sys

dirsep = os.path.sep
folder = sys.path[0] + dirsep
token = folder + 'options/token.json'
credentials = folder + 'options/credentials.json'
routers = []

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SAMPLE_SPREADSHEET_ID = '1pmdLn_KFm2_821NiDhn_QHWblvAfAcRUdaA3OCIE58k'
store = file.Storage(token)
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(credentials, SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))
sheet = service.spreadsheets()

def getValues(range):
        SAMPLE_RANGE_NAME = range
        data = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = data.get('values', [])
        if not values:
            return False
        return values

class endpointAddresses():
    addresses = []
    def __init__(self):
        values = getValues('servicematrix!A:F')
        if not values:
            print('No data found.')
        else:
            rowcount = 0
            addressHeader = []
            for row in values:
                addressItem = {}
                rowcount = rowcount + 1
                if rowcount == 1:
                    for item in row:
                        addressHeader.append(item)
                else:
                    itemcount = 0
                    for item in row:
                        addressItem[addressHeader[itemcount]] = item
                        itemcount = itemcount + 1
                    self.addresses.append(addressItem)
        values = getValues('locationlist!A:C')
        if not values:
            print('No data found.')
        else:
            for row in values:
                addressItem = {}
                addressItem[addressHeader[1]] = row[0]
                addressItem[addressHeader[2]] = row[1]
                addressItem[addressHeader[5]] = row[2]
                self.addresses.append(addressItem)

def fillrouters():
    values = getValues('routerlist!A:B')
    if not values:
        print('No data found.')
    else:
        a = open(folder + '/temp/hosts-mkr','w')
        a.write(f'[mkr-firewall-matrix]\n\n')
        for row in values:
            routerItem = {'ip': row[0], 'name': row[1]}
            routers.append(routerItem)
            router_ip = routerItem.get('ip')
            router_name = routerItem.get('name')
            a.write(f'{router_ip} ansible_ssh_port=2222 router_id={router_name}\n')
            #a.write(f'{row[0]} ansible_ssh_port=2222 router_id={row[1]}\n')
        a.close

def readMatrix(spreadsheet):
    values = getValues(spreadsheet)
    srclist = []
    dstlist = []
    dstHeaders = []
    srcHeaders = []
    rowcount = 0 
    for row in values:
        colcount = 0
        for item in row:
            if rowcount == 0 and colcount == 0:
                dstHeaders = row
            if colcount == 0:
                srcHeaders.append(item)
            if colcount > 0 and rowcount > 0:
                if item == 'x':
                    if srcHeaders[rowcount] not in srclist:
                        srclist.append(srcHeaders[rowcount])
                    if dstHeaders[colcount] not in dstlist:
                        dstlist.append(dstHeaders[colcount])
            colcount = colcount + 1
        rowcount = rowcount + 1
    print(values)
    pass

a = endpointAddresses()

fillrouters()

readMatrix('location-location')


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

