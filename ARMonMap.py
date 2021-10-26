#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 15:33:39 2021

@author: jiahuiwu
"""
import folium
from folium import plugins
from map import generateBasemap 
import pandas as pd
from datetime import time as t
from seaborn import palplot 
import seaborn as sns


ARMrule = pd.read_csv('/Users/jiahuiwu/Desktop/501/portfolio/ARM_rule.csv')

ARMrule['LHS'] = [str(pd.to_datetime(s[1:9])) for s in ARMrule['LHS']]
ARMrule['RHS'] = [s[1:len(s)-1] for s in ARMrule['RHS']]


# divide rules according to time
rule_dict = {}
for time, loc in zip(ARMrule['LHS'], ARMrule['RHS']):
    if time in rule_dict:
        rule_dict[time].append(loc)
    else:
        rule_dict[time] = [loc]
    
# record the confidence according to each pair of time and location    
conf_dict = {}
for time, loc, conf, lift in zip(ARMrule['LHS'], ARMrule['RHS'], ARMrule['confidence'], ARMrule['lift']):
    time_loc = (time, loc)
    conf_dict[time_loc] = (conf,lift)



from map import getZoneCen_fhv
import matplotlib as plt

colorlist = sns.color_palette("rocket_r", as_cmap=True)

features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": getZoneCen_fhv(s[1]) ,
            },
            "properties": {
                "time": s[0],
                'style': {'color' : ''},
                    'icon': 'circle',
                    'iconstyle':{
                        'fillColor': plt.colors.to_hex(colorlist(int(conf_dict[s][1]*50))),
                        'fillOpacity': 2,
                        'stroke': 'true',
                        'radius': conf_dict[s][0]*10
                    }
            },
        }  for s in conf_dict.keys()
       
    ]


map1 = generateBasemap()  
plugins.TimestampedGeoJson(features,
                        period = 'PT1H',
                        duration = 'PT59M',
                        transition_time = 200,
                        auto_play = True).add_to(map1)
   
   
map1.save( "ARMmap.html")    

