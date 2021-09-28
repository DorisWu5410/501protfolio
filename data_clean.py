#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 22:30:58 2021

@author: jiahuiwu
"""

import pymysql
import numpy as np
from collections import Counter
import pandas as pd

conn = pymysql.connect(host='localhost',
                             user='root',
                             password='Westlife890@',
                             database='501data')
cur = conn.cursor()
cur.execute("show tables")
table_list = [tuple[0] for tuple in cur.fetchall()]


#unify column name
def change_colN():
    cur = conn.cursor()
    cur.execute("select * from INFORMATION_SCHEMA.columns where COLUMN_NAME Like 'locationID'; ")
    change_collist = [tuple[2] for tuple in cur.fetchall()]
    for name in change_collist:
        query = "ALTER TABLE " + name + " CHANGE locationID PULocationID VARCHAR(30)"
        cur.execute(query)
    conn.commit()
    cur.close()



#create record_id
def create_id(tablename):
    cur = conn.cursor()
    query = "alter table " + tablename + " add record_id int NOT NULL primary key AUTO_INCREMENT first;"
    cur.execute(query)
    conn.commit()
    cur.close()

for tname in table_list:
    create_id(tname)



#________________________________________________________________


###for some table that has location expressed in latitude and longtitued, find their zone


from shapely.geometry import Point
import geopandas as gpd

# taxi zone
zone = gpd.read_file("/Users/jiahuiwu/Desktop/501/portfolio/NYC Taxi Zones.geojson")
zone = zone.to_crs(epsg=4326)
all_polygon = zone['geometry']


# fine the zone of a point
def find_zone(lat_long_elem):
    point = Point(lat_long_elem[0],lat_long_elem[1])
    for i in range(0,len(all_polygon)):
        polygon = all_polygon[i]
        if point.within(polygon):
            zone_id = zone['location_id'][i]
            return(zone_id)
    return('')


# find table with locations expressed in latitude and longtitued
cur = conn.cursor()
cur.execute("select * from INFORMATION_SCHEMA.columns where COLUMN_NAME Like 'Pickup_longitude';")
table_list_latlong = [tuple[2] for tuple in cur.fetchall()]

    

#find zone of points in a table
def FindTaxiZone(tablename):
    cur = conn.cursor()
    query = "select Pickup_longitude, Pickup_latitude from " + tablename + ';'
    cur.execute(query)
    lat_long = cur.fetchall()
    lat_long = list(lat_long)
    for i in range(0,len(lat_long)):
        lat_long[i] = [float(j) for j in lat_long[i]]
    zone_list = []       
    for i in range(0, len(lat_long)):  
        zone_id = find_zone(lat_long[i])
        zone_list.append(zone_id)
    return(zone_list)    

def FindTaxiZone_drop(tablename):
    cur = conn.cursor()
    query = "select Dropoff_longitude, Dropoff_latitude from " + tablename + ';'
    cur.execute(query)
    lat_long = cur.fetchall()
    lat_long = list(lat_long)
    for i in range(0,len(lat_long)):
        for j in lat_long[i]:
            if j == '':
                lat_long[i] = ('0','0')
        lat_long[i] = [float(j) for j in lat_long[i]]
    zone_list = []       
    for i in range(0, len(lat_long)):  
        zone_id = find_zone(lat_long[i])
        zone_list.append(zone_id)
    return(zone_list)  


    
# add update zone id into table
def add_zone(tablename):
    cur = conn.cursor()
    
    #create colume
    query = "alter table " + tablename +  " add column PULocationID varchar(30);"
    cur.execute(query)
    
    #add value into column
    zone_list = FindTaxiZone(tablename)
    for i in range(0,len(zone_list)):
        query = "update " + tablename + " set PULocationID = " + '"'+ str(zone_list[i]) + '"'  + " where record_id = " + str(i+1) + ";"
        cur.execute(query)
    conn.commit()
    cur.close()
    
def add_zone_drop(tablename):
    cur = conn.cursor()
    #create colume
    query = "alter table " + tablename +  " add column DOLocationID varchar(30);"
    cur.execute(query)
    
    #add value into column
    zone_list = FindTaxiZone_drop(tablename)
    for i in range(0,len(zone_list)):
        query = "update " + tablename + " set DOLocationID = " + '"'+ str(zone_list[i]) + '"'  + " where record_id = " + str(i+1) + ";"
        cur.execute(query)
    conn.commit()
    cur.close()
    
    
    
    
for tname in table_list_latlong:
    add_zone(tname)
    print(tname)

for tname in table_list_latlong:
    add_zone_drop(tname)
    print(tname)




#________________________________________________________________________

#assign pick-up/dropoff location to null record according to proportianl probability of other record in that table



def assign_PULoc(tablename):
    cur = conn.cursor()
    cur.execute("select record_id, PULocationID from " + tablename)
    select = cur.fetchall()
    ID = [tuple[0] for tuple in select]    #all if
    col = [tuple[1] for tuple in select]   #all PULocation
    freq = dict(Counter(col))              #freq of location
    location = list(freq.keys())
    if '' in location:
        location.remove('')
        prob = []
        for l in location:
            prob.append(freq[l])
        prob = np.array(prob)
        prob = prob/sum(prob) 
        
        null_idx = []                     #record id with null PULocation
        assign_loc = []                   #location generated  
        while True:
            try:
                idx = col.index('')
                null_idx.append(idx)
                loc = str(np.random.choice(location, p = prob))
                col[idx] = 'assign'
                assign_loc.append(loc)           
            except: break
        null_ID = []
        for i in null_idx:
            null_ID.append(ID[i])
     
        for i in range(0,len(null_ID)):
            query = "update " + tablename + " set PULocationID = " + assign_loc[i] + " where record_id = " + str(null_ID[i]) 
            cur.execute(query)
        conn.commit()
    print(tablename)
    cur.close()

    
def assign_DOLoc(tablename):
    cur = conn.cursor()
    cur.execute("select record_id, DOLocationID from " + tablename)
    select = cur.fetchall()
    ID = [tuple[0] for tuple in select]    #all if
    col = [tuple[1] for tuple in select]   #all PULocation
    freq = dict(Counter(col))              #freq of location
    location = list(freq.keys())
    if '' in location:
        location.remove('')
        prob = []
        for l in location:
            prob.append(freq[l])
        prob = np.array(prob)
        prob = prob/sum(prob) 
        
        null_idx = []                     #record id with null PULocation
        assign_loc = []                   #location generated  
        while True:
            try:
                idx = col.index('')
                null_idx.append(idx)
                loc = str(np.random.choice(location, p = prob))
                col[idx] = 'assign'
                assign_loc.append(loc)           
            except: break
        null_ID = []
        for i in null_idx:
            null_ID.append(ID[i])
     
        for i in range(0,len(null_ID)):
            query = "update " + tablename + " set DOLocationID = " + assign_loc[i] + " where record_id = " + str(null_ID[i]) 
            cur.execute(query)
        conn.commit()
    print(tablename)
    cur.close()





# find table with all null location value
all_null_Loc=[]
for tname in table_list:
    query = "select count(*) from " + tname + " where PULocationID =''; "
    cur.execute(query)
    count_null = cur.fetchall()[0][0]
    query = "select count(*) from " + tname + "; "
    cur.execute(query)
    count_all = cur.fetchall()[0][0]
    if count_null == count_all:
        all_null_Loc.append(tname)

# deal with table with not all null Loction value    
for tname in list(set(table_list) - set(all_null_Loc)) :
    assign_PULoc(tname)


#find tabel without Dropoff location 
cur = conn.cursor()
cur.execute("select * from INFORMATION_SCHEMA.columns where COLUMN_NAME Like 'DOLocationID'; ")
withDO_list = [tuple[2] for tuple in cur.fetchall()]

for tname in list(set(withDO_list) - set(all_null_Loc)):
    assign_DOLoc(tname)     





#_______________________________________________________________
    
# time data



# 1. unify colname
# some table have different column name for pick-up/drop-off time. Need to unify them to Pickup_datetime/Dropoff_datetime

#get all type of column name that describe time
PUTimeName = []
DOTimeName = []
cur = conn.cursor()
for tname in table_list:
    query = "SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_NAME`= " + "'" + tname + "';"
    cur.execute(query)
    colname = cur.fetchall()
    colname = [tuple[0] for tuple in colname]
    time_col = [s for s in colname if "date" in s or "Date" in s]
    PUTName = [s for s in time_col if "ick" in s]
    DOTName = [s for s in time_col if "rop" in s]
    PUTimeName.append(PUTName)
    DOTimeName.append(DOTName)
PUTimeName = [s[0] for s in PUTimeName if len(s)>=1]
PUTimeName = list(set(PUTimeName))
DOTimeName = [s[0] for s in DOTimeName if len(s)>=1]
DOTimeName = list(set(DOTimeName))


def change_colN_time():
    cur = conn.cursor()
    for name in PUTimeName:
        cur.execute("select * from INFORMATION_SCHEMA.columns where COLUMN_NAME Like '"+ name + "'; ")
        change_collist = [tuple[2] for tuple in cur.fetchall()]
        for tname in change_collist:
            query = "ALTER TABLE " + tname + " CHANGE " + name + " Pickup_datetime VARCHAR(30);"
            cur.execute(query)
            # print(tname)
            
    for name in DOTimeName:
        cur.execute("select * from INFORMATION_SCHEMA.columns where COLUMN_NAME Like '"+ name + "'; ")
        change_collist = [tuple[2] for tuple in cur.fetchall()]
        for tname in change_collist:
            query = "ALTER TABLE " + tname + " CHANGE " + name + " Dropoff_datetime VARCHAR(30);"
            cur.execute(query)
            # print(tname)
    conn.commit()
    cur.close()
change_colN_time()




# check null value
null_count = []
for tname in table_list:
    cur = conn.cursor()
    query="select count(*) from " + tname + " where Pickup_datetime = '';"
    cur.execute(query)
    null_count.append(cur.fetchall()[0][0])
if dict(Counter(null_count))[0] == len(null_count):
    print('no null Pickup_datetime value')
else: print('has null Pickup_datatime value')


null_count = []
for tname in withDO_list:
    cur = conn.cursor()
    query="select count(*) from " + tname + " where Dropoff_datetime = '';"
    cur.execute(query)
    null_count.append(cur.fetchall()[0][0]) 
if dict(Counter(null_count))[0] == len(null_count):
    print('no null Dropoff_datetime value')
else: print('has null Dropoff_datatime value')


#table with all null dropoff_datetime 
has_null_tablelist = [withDO_list[i] for i in range(0,len(withDO_list)) if null_count[i]!=0]
nullTable_idx = [i for i in range(0,len(withDO_list)) if null_count[i]!=0]
for i in range(0,len(has_null_tablelist)):
    query="select count(*) from " + has_null_tablelist[i] + ";"
    cur.execute(query)
    count_col = cur.fetchall()[0][0]
    if count_col==null_count[i]:
        print(has_null_tablelist[i] + ' all null dropoff_datetime')
    else:
        print(has_null_tablelist[i] + ' not all null dropoff_datetime')






# 2. drop record with inconsistent time data 

def remove_inconsis_time(tablename):
    # get correct date
    y_m = tablename[-7:]
    y_m = y_m.split('_')
    y_m = y_m[0] + '-' +y_m[1]
    
    cur=conn.cursor()
    query = "select Pickup_datetime, record_id from " + tablename + ";"
    cur.execute(query)
    result = cur.fetchall()
    time_col = [s[0] for s in result]
    id_col = [s[1] for s in result]
    
    #get wrong record id
    wrong_id = []
    for i in range(0,len(time_col)):
        if time_col[i][0] == ' ':
            time = str(time_col[i])[:8].replace(' ', '')
        else: 
            time = str(time_col[i])[:7]
        if time != y_m:
            wrong_id.append(id_col[i])

    for ID in wrong_id:
        query = 'DELETE FROM ' +  tablename + ' WHERE `record_id` = ' + str(ID) + ';'
        cur.execute(query)
    conn.commit()
    print(tablename)
    print(len(wrong_id))
    # print(wrong_id)
    
for tname in list(set(table_list) - set(all_null_Loc)):
    remove_inconsis_time(tname)


