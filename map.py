#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 16:11:08 2021

@author: jiahuiwu
"""
import folium
import geopandas as gpd
import matplotlib.pyplot as plt

path = gpd.datasets.get_path('nybb')
NY = gpd.read_file(path)
NY.head()
NY.plot(figsize=(6, 6))
NY = NY.to_crs(epsg=4326)
NY.head()
NY.to_file("my_file.csv", driver="GeoJSON")

map1 = folium.Map(location=[40.7, -73.98], zoom_start=11)

for _,r in NY.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.0001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'yellow','color':'black','weight':2.5})
    geo_j.add_to(map1)
                      

zone = gpd.read_file("/Users/jiahuiwu/Desktop/501/portfolio/NYC Taxi Zones.geojson")
zone = zone.to_crs(epsg=4326)
for _, r in zone.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.0001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'color':'black','weight':1})
    folium.Popup(r['location_id']+'('+r['borough']+')').add_to(geo_j)
    geo_j.add_to(map1)
    
map1.save("NYtaxi.html")
