#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 23:44:55 2021

@author: jiahuiwu
"""

import http.client, urllib.request, urllib.parse, urllib.error
import json

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': 'b1fcd9e6ed2e470aa75e2fe9ee101758',
    'Content-type' : 'application/json'
}

conn = http.client.HTTPSConnection('api.nyc.gov')
conn.request('GET', "/dot/trafficSpeed?%s" , "{body}", headers)
response = conn.getresponse()
data = response.read()
data = str(data).split("\\n")

#split data into list whose elements are records 
cut = [item for item in ' '.join(data).split('   "undefined\\\\"id\\\\"":')]
for i in range(1,len(cut)):
    cut[i] = cut[i].strip(',   {  ') 
    cut[i] = '{ "id":' + cut[i]
    
#convert json to dict
cut[len(cut)-1] = cut[len(cut)-1].strip(" ]\'")
for i in range(1,len(cut)):
    cut[i] = json.loads(cut[i])


import pandas as pd
#write data into dataframe
col = list( cut[1].keys())
df = pd.DataFrame(columns=col)
for i in range(1,len(cut)):
    print(i)
    row = list(cut[i].values())
    df.loc[i-1] = row











    
#             df = pd.read_csv(StringIO(content), sep=",")


