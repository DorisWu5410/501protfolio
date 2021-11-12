#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  9 21:44:01 2021

@author: jiahuiwu
"""

import DT_prepare
# from map import generateBasemap
# from seaborn import palplot 
# import seaborn as sns
# import matplotlib as plt
# import pandas as pd
# import datetime
from folium import plugins



test_dict = DT_prepare.test_dict
predict_dict = DT_prepare.predict_dict
predict_dict_rf = DT_prepare.predict_dict_rf

# test_dict = {'loc':[], 
#              'time':[], 
#              'dayofweek':[], 
#              'count':[]}

# for _, row in test.iterrows(): 
#     test_dict['loc'].append([row['PU_lat'],row['PU_long']])
#     test_dict['time'].append(row['timepoint'])
#     test_dict['dayofweek'].append(row['timepoint'])
#     test_dict['count'].append(row['count'])
    

# colorlist = sns.color_palette("rocket_r", as_cmap=True)

# test_features = [
#         {
#             "type": "Feature",
#             "geometry": {
#                 "type": "Point",
#                 "coordinates": [s[0][1],s[0][0]] ,
#             },
#             "properties": {
#                 "time": str(datetime.datetime.strptime(str(s[1]), '%H')),
#                 'style': {'color' : ''},
#                     'icon': 'circle',
#                     'iconstyle':{
#                         'fillColor': plt.colors.to_hex(colorlist(int(round(test_dict[s],0)*50))),
#                         'fillOpacity': 2,
#                         'stroke': 'true',
#                         'radius': 10
#                     }
#             },
#         }  for s in test_dict if s[2] =='1'
       
#     ]
# plugins.TimestampedGeoJson(test_features,
#                         period = 'PT1H',
#                         duration = 'PT59M',
#                         transition_time = 200,
#                         auto_play = True).add_to(map1)

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

def generateDualmap():
    map1 = folium.plugins.DualMap(location=[40.7, -73.98], zoom_start=11)
    
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




dow_map = {'0':'Monday', '1':'Tuesday', '2':'Wednesday', '3':'Thursday', '4':'Friday', '5':'Saturday', '6':'Sunday'}



def draw_dualmap(type_of_model_predict_dict):
    map1 = generateDualmap()
    time_index_all = []
    
    loc_count_total_true = []
    loc_count_total_predict = []
    
    #iterate by day of week
    for dow in [str(i) for i in range(7)]:
        time_index = []
        
        #true   
        loc_count_all = []
        #iterate by time
        for time in range(24):
            loc_at_time = []
            for s in test_dict: 
                if s[2] == dow and s[1] == time:
                    loc = [[s[0][0],s[0][1],test_dict[s]/15]]*int(round(test_dict[s],0))
                    for i in loc:
                        loc_at_time.append(i)
            loc_count_all.append(loc_at_time)
        
        #record all time in this day of week 
        time_index = [dow_map[dow]+' '+i + ':00:00' for i in ["%.2d" % i for i in range(24)]]
        list(range(24))
        loc_count_total_true = loc_count_total_true + loc_count_all
        time_index_all = time_index_all + time_index
        
        
        #predict
        loc_count_all_predict = []
        for time in range(24):
            loc_at_time = []
            for s in type_of_model_predict_dict: 
                if s[2] == dow and s[1] == time:
                    loc = [[s[0][0],s[0][1],type_of_model_predict_dict[s]/15]]*int(round(type_of_model_predict_dict[s],0))
                    for i in loc:
                        loc_at_time.append(i)
            loc_count_all_predict.append(loc_at_time)
            
        loc_count_total_predict = loc_count_total_predict + loc_count_all_predict
        
    plugins.HeatMapWithTime(loc_count_total_true,time_index_all,
                            auto_play = True,
                            radius=30
                            ).add_to(map1.m2)
    
    plugins.HeatMapWithTime(loc_count_total_predict,time_index_all,
                            auto_play = True,
                            radius=30
                            ).add_to(map1.m1)
    return(map1)
       
map_df = draw_dualmap(predict_dict)   
map_rf = draw_dualmap(predict_dict_rf)
 
map_df.save( "DTmap_.html")  
map_rf.save('RFmap_.html')  
