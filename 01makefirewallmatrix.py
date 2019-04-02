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
parsedMatrixDst = {}
filter = ['comenergo', 'kkk']

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
    def __init__(self,filter):
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
                        if item != '':
                            addressItem[addressHeader[itemcount]] = item
                            itemcount = itemcount + 1
                        else:
                            pass
                    aff = addressItem.get('affilation')
                    if aff in filter:
                        self.addresses.append(addressItem)
        values = getValues('locationlist!A:C')
        if not values:
            print('No data found.')
        else:
            for row in values:
                addressItem = {}
                addressItem[addressHeader[3]] = row[0]
                addressItem[addressHeader[2]] = row[1]
                addressItem[addressHeader[5]] = row[2]
                self.addresses.append(addressItem)

    def getAddressesDst(self, entity, router):
        output = []
        for addressRecord in self.addresses:
            if addressRecord.get('entity') == entity and addressRecord.get('router') == router:
                output.append(addressRecord)
        return output

    def getAddressesSrc(self, entity):
        output = []
        for item in self.addresses:
            if item.get('entity') == entity:
                output.append(item)
        return output

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
    dstHeaders = []
    rowcount = 0 
    for row in values:
        colcount = 0
        for cell in row:
            if rowcount == 0 and colcount == 0:
                for cell in row:
                    if cell != '' and cell not in parsedMatrixDst:
                        parsedMatrixDst[cell] = []
                dstHeaders = row
            if colcount == 0:
                src = cell
            if colcount > 0 and rowcount > 0:
                if cell == 'x':
                    ddd = dstHeaders[colcount]
                    vvv = parsedMatrixDst[dstHeaders[colcount]]
                    if ddd not in vvv:
                        parsedMatrixDst[dstHeaders[colcount]].append(src)
            colcount = colcount + 1
        rowcount = rowcount + 1
    print(values)
    pass

addresses = endpointAddresses(filter)
fillrouters()
readMatrix('location-location')
readMatrix('location-service')
readMatrix('service-service')

for routerRecord in routers:
    router = routerRecord.get('name')
    if os.path.exists(folder + '/temp/matrix_' + router + '.rsc'):
        os.remove(folder + '/temp/matrix_' + router + '.rsc')
    a = open(folder + '/temp/matrix_' + router + '.rsc','a')
    a.write(f'/ip firewall address-list\n')
    print('write rsc', router)
    for dstEntity in parsedMatrixDst:
        dstList = addresses.getAddressesDst(dstEntity, router)
        if dstList:
            for dstRecord in dstList:
                dstaddress = dstRecord.get('ip')
                a.write(f'add address={dstaddress} comment=\"_ansible_{dstEntity}\" list=_ans_dst_{dstEntity}\n')
            srcEntityList = parsedMatrixDst[dstEntity]
            for srcEntity in srcEntityList:
                srcList = addresses.getAddressesSrc(srcEntity)
                if srcList:
                    for srcRecord in srcList:
                        srcAddress = srcRecord.get('ip')
                        srcItem = srcRecord.get('item', srcEntity)
                        a.write(f'add address={srcAddress} comment=\"_ansible_{srcItem}->{dstEntity}\" list=_ans_src_{dstEntity}\n')
                        pass

#    a.write(f'/ip firewall filter\n')
#    for record in routers[router]:
#        a.write(f'add chain=forward src-address-list=_ans_src_{record} dst-address-list=_ans_dst_{record} action=accept comment=\"ANSIBLE MATRIX RULE {record}\"\n')
#    a.write(f'add action=drop chain=forward comment=\"ANSIBLE DROP ALL FORWARD\" connection-nat-state=!dstnat connection-state=new\n')
#    a.write(f'add action=drop chain=input in-interface-list=WAN comment=\"ANSIBLE DROP ALL INPUT\"\n')            
#    a.close