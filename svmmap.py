#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 01:20:41 2021

@author: jiahuiwu
"""

from map import generateBasemap
from seaborn import palplot 
import seaborn as sns
import matplotlib as plt
import pandas as pd
import datetime
import folium
import geopandas as gpd
from folium import plugins
from DT_map import test_dict


dow_map = {'0':'Monday', '1':'Tuesday', '2':'Wednesday', '3':'Thursday', '4':'Friday', '5':'Saturday', '6':'Sunday'}
def draw_map():
    map1 = generateBasemap()
    time_index_all = []
    
    loc_count_total_true = []
    
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
        
        
    plugins.HeatMapWithTime(loc_count_total_true,time_index_all,
                            auto_play = True,
                            radius=30
                            ).add_to(map1)
    return(map1)

map1 = draw_map()
map1.save('map.html')
