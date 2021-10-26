#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 15:01:13 2021

@author: jiahuiwu
"""

import pymysql
import numpy as np
from collections import Counter
import pandas as pd
import random
from generate_tablelist import clust_table;
from datetime import datetime as dt
import csv

random.seed(10)
ARMtable = ['fhv_tripdata2018_06', 'green_tripdata2018_06', 'yellow_tripdata2018_06']
conn = pymysql.connect(host='localhost',
                             user='root',
                             password='Westlife890@',
                             database='501data')

def getTinterval(time_pt):
    if time_pt[0] == ' ':
        time_pt = time_pt.replace(' ', '',1)
    time_interval=time_pt[:14] + '00:00'       #eg. 2020-06-30 11:55:00 belongs to interval 2020-06-30 11:00:00
    return(time_interval)


def get_time_PU(tablenamelist):
    dict_datetimepoint = {}
    for tablename in tablenamelist:
        cur = conn.cursor()
        query = "select Pickup_datetime, PULocationID from " + tablename + ' where Pickup_datetime is not null;'
        cur.execute(query)
        result = cur.fetchall()
        Pickup_datetime = [getTinterval(s[0]) for s in result]
        PULocationID = [s[1] for s in result]
    
        for i in range(len(Pickup_datetime)):
            if Pickup_datetime[i] in dict_datetimepoint:
            # if PULocationID[i] not in dict_datetimepoint[Pickup_datetime[i]]:
                dict_datetimepoint[Pickup_datetime[i]].append(PULocationID[i])
            else:
                dict_datetimepoint[Pickup_datetime[i]] = [Pickup_datetime[i][11:], PULocationID[i]]
        print(tablename) 
        
    for time in dict_datetimepoint:
        C = Counter(dict_datetimepoint[time])
        dict_datetimepoint[time] = [time[11:]] + [loc for loc in list(C.keys()) if C[loc] > 2]
  
    df = [item for item in dict_datetimepoint.values() if len(item)>1]
    
    with open('ARM.csv', 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(df)
    
get_time_PU(ARMtable)
    

