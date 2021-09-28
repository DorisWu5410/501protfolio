#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 16:11:08 2021

@author: jiahuiwu
"""
import folium
import geopandas as gpd
from folium import plugins

path = gpd.datasets.get_path('nybb')
NY = gpd.read_file(path)
NY.head()
NY.plot(figsize=(6, 6))
NY = NY.to_crs(epsg=4326)
NY.head()
NY.to_file("my_file.csv", driver="GeoJSON")
zone = gpd.read_file("/Users/jiahuiwu/Desktop/501/portfolio/NYC Taxi Zones.geojson")
zone = zone.to_crs(epsg=4326)
all_polygon = zone['geometry']
zone_ID_col = list(zone['location_id'])

def generateBasemap():
    map1 = folium.Map(location=[40.7, -73.98], zoom_start=11)
    
    for _,r in NY.iterrows():
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.0001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                               style_function=lambda x: {'fillColor': 'yellow','color':'black','weight':2.5})
        geo_j.add_to(map1)
                          
    
    
    
    for _, r in zone.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.0001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                               style_function=lambda x: {'color':'black','weight':1})
        folium.Popup(r['location_id']+r['zone']+' ('+r['borough']+')').add_to(geo_j)
        geo_j.add_to(map1)
    
    return(map1)





#____________________________________________________________


#deal with time data


import pymysql
conn = pymysql.connect(host='localhost',
                             user='root',
                             password='Westlife890@',
                             database='501data')
cur = conn.cursor()

import datetime
from datetime import datetime as dt
from datetime import date as d
from datetime import time as t

#create endpoints of time intervals (1 hour for 1 interval) 
start_time = dt(year=2014, month=1, day=1, hour=0)
end_time = dt(year=2020, month=12, day=31, hour=23, minute=59,second = 59)

time_add = datetime.timedelta(hours=1)
time_point = [start_time]
time = start_time
while time < end_time:
    time = time + time_add
    time_point.append(time)   


#put datetime into interval
def getTinterval(time_pt):
    if int(time_pt[11:13])%2 ==0:
        time_interval=time_pt[:14] + '00:00'       #eg. 2020-06-30 11:55:00 belongs to interval 2020-06-30 10:00:00
    else: 
        time_interval = time_pt[:11] + str(int(time_pt[11:13]) - 1).zfill(2) + ':00:00'
    
    # dt.fromisoformat(time_pt)
    
    # absolute_difference_function = lambda list_value : abs(list_value - time_pt)
    # time_interval = min(time_point, key=absolute_difference_function)
    # #if the closest is larger, denate the interval by the previous.
    # if time_interval > time_pt: 
    #     time_interval = time_point[time_point.index(time_interval) - 1]
    return(time_interval)


        
cur=conn.cursor()
query = "select Pickup_datetime from green_tripdata2018_03;"
cur.execute(query)
time_col = cur.fetchall()
time_col = [s[0] for s in time_col]
#transfer into datetime object
time_col = [dt.fromisoformat(time_col[i]) for i in range(0,len(time_col))]


#get inddex of centroid of each zone
def getZoneCen_green(zoneID):
    idx = zone_ID_col.index(zoneID)
    location = all_polygon[idx].centroid.wkt
    location = location.strip('POINT (')
    location = location.strip(')')
    location = location.split(' ')
    location = [float("%.4f" % float(s))-0.001 for s in location]
    return(location)

def getZoneCen_yellow(zoneID):
    idx = zone_ID_col.index(zoneID)
    location = all_polygon[idx].centroid.wkt
    location = location.strip('POINT (')
    location = location.strip(')')
    location = location.split(' ')
    location = [float("%.4f" % float(s))+0.001 for s in location]
    return(location)

def getZoneCen_fhv(zoneID):
    idx = zone_ID_col.index(zoneID)
    location = all_polygon[idx].centroid.wkt
    location = location.strip('POINT (')
    location = location.strip(')')
    location = location.split(' ')
    location = [float("%.4f" % float(s)) for s in location]
    return(location)



def merge(list1, list2):    
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    return merged_list



from collections import Counter
from datetime import datetime as dt

def countCar_Z_T_pick(tablename):
    cur=conn.cursor()
    query = "select Pickup_datetime, PULocationID from " + tablename + ";"
    cur.execute(query)
    result = cur.fetchall()
    
    PU_Tinterval = [s[0] for s in result]
    PU_Tinterval = [getTinterval(s) for s in PU_Tinterval]
    
    zone_col = [s[1] for s in result]
    
    count_record_list = []
    
    Z_T = merge(zone_col, PU_Tinterval)
    count_dict_all = dict(Counter(Z_T))    #dict that count all record correspoding to zone and time
    key = list(count_dict_all.keys())
    value = list(count_dict_all.values())
    
    for i in range(0,len(count_dict_all)):
        count_record = dict()              #dict that give count of service in one zone and one datetime
        
        if key[i][0] in zone_ID_col:                       # a few of record has zone id not recoreded in the taxi zone document, drop them       
            
            if 'yellow' in tablename:
                coordn = getZoneCen_yellow(key[i][0])
                count_record['Coordinate'] = coordn
            if 'green' in tablename:
                coordn = getZoneCen_green(key[i][0])
                count_record['Coordinate'] = coordn
            if 'fhv' in tablename:
                coordn = getZoneCen_fhv(key[i][0])
                count_record['Coordinate'] = coordn
                
            dateT = key[i][1]
            count_record['Datetime']= dateT
         
            count = value[i]
            count_record['count'] = count
            
            count_record_list.append(count_record)
    
    return(count_record_list)

def countCar_Z_T_drop(tablename):
    cur=conn.cursor()
    query = "select Pickup_datetime, DOLocationID from " + tablename + ";"
    cur.execute(query)
    result = cur.fetchall()
    
    DO_Tinterval = [s[0] for s in result]
    DO_Tinterval = [getTinterval(s) for s in DO_Tinterval]
    
    zone_col = [s[1] for s in result]
    
    count_record_list = []
    
    Z_T = merge(zone_col, DO_Tinterval)
    count_dict_all = dict(Counter(Z_T))    #dict that count all record correspoding to zone and time
    key = list(count_dict_all.keys())
    value = list(count_dict_all.values())
    
    for i in range(0,len(count_dict_all)):
        count_record = dict()              #dict that give count of service in one zone and one datetime
        
        if key[i][0] in zone_ID_col:                       # a few of record has zone id not recoreded in the taxi zone document, drop them       
            
            if 'yellow' in tablename:
                coordn = getZoneCen_yellow(key[i][0])
                count_record['Coordinate'] = coordn
            if 'green' in tablename:
                coordn = getZoneCen_green(key[i][0])
                count_record['Coordinate'] = coordn
            if 'fhv' in tablename:
                coordn = getZoneCen_fhv(key[i][0])
                count_record['Coordinate'] = coordn
                
            dateT = key[i][1]
            count_record['Datetime']= dateT
         
            count = value[i]
            count_record['count'] = count
            
            count_record_list.append(count_record)
    
    return(count_record_list)


test =  countCar_Z_T_drop('green_tripdata2020_06')


#apply to tables
conn = pymysql.connect(host='localhost',
                             user='root',
                             password='Westlife890@',
                             database='501data')
cur = conn.cursor()
cur.execute("show tables")
table_list = [tuple[0] for tuple in cur.fetchall()]

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

table_withloc = list(set(table_list) - set(all_null_Loc))
yellow_tablename = [s for s in table_withloc if 'yellow' in s]
green_tablename = [s for s in table_withloc if 'green' in s]
fhv_tablename = [s for s in table_withloc if 'fhv' in s]



#convert data to geojson and add to map
def generate_Feature(tablename,cartype_color):  #yellow taxi for yellow, green taxi for green, fhv for blue
    result = countCar_Z_T_pick(tablename)
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": point["Coordinate"] ,
            },
            "properties": {
                "time": point["Datetime"],
                'style': {'color' : ''},
                    'icon': 'circle',
                    'iconstyle':{
                        'fillColor': cartype_color,
                        'fillOpacity': 0.8,
                        'stroke': 'true',
                        'radius': point['count'] + 4 
                    }
            },
        }  for point in result
       
    ]
    print(tablename)
    return(features)
    


#create map
   
def savemap_part1(year):
    map1 = generateBasemap()   
    total_feature = []
    for tname in green_tablename:
        if year in tname and int(tname[-2:])<=6:
            features = generate_Feature(tname, 'lime')
            total_feature = total_feature + features
            
    for tname in yellow_tablename:
        if year in tname and int(tname[-2:])<=6:
            features = generate_Feature(tname, 'yellow')
            total_feature = total_feature + features
            
    for tname in fhv_tablename:
        if year in tname and int(tname[-2:])<=6:
            features = generate_Feature(tname, 'blue')
            total_feature = total_feature + features   
            
            
    plugins.TimestampedGeoJson(total_feature,
                         period = 'PT1H',
                         duration = 'PT1H',
                         transition_time = 200,
                         auto_play = True).add_to(map1)
    
    
    map1.save("NYtaxi"+year+'P1' + ".html")

def savemap_part2(year):
    map1 = generateBasemap()   
    total_feature = []
    for tname in green_tablename:
        if year in tname and int(tname[-2:])>6:
            features = generate_Feature(tname, 'lime')
            total_feature = total_feature + features
            
    for tname in yellow_tablename:
        if year in tname and int(tname[-2:])>6:
            features = generate_Feature(tname, 'yellow')
            total_feature = total_feature + features
            
    for tname in fhv_tablename:
        if year in tname and int(tname[-2:])>6:
            features = generate_Feature(tname, 'blue')
            total_feature = total_feature + features   
            
            
    plugins.TimestampedGeoJson(total_feature,
                         period = 'PT1H',
                         duration = 'PT1H',
                         transition_time = 200,
                         auto_play = True).add_to(map1)
    
    
    map1.save("NYtaxi"+year+'P2' + ".html")



yearlist = ['2014','2015','2016','2017','2018','2019','2020']
for year in yearlist:
    savemap_part1(year)
    savemap_part2(year)



