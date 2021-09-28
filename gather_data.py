#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 23:46:24 2021

@author: jiahuiwu
"""
import urllib.request

baseurl = "https://s3.amazonaws.com/nyc-tlc/trip+data/"
headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",}


monthlist = ['01','02','03','04','05','06','07','08','09','10','11','12']


import pymysql
import random

#read data into Mysql
def DfToSql(cartype,year,m,content):
    try:
        conn = pymysql.connect(host='localhost',
                             user='root',
                             password='mypassword',
                             database='501data')
        cur = conn.cursor()
        
        # create table
        tablename = cartype + year +'_'+ m
        cur.execute("drop table if exists " + tablename + ';')
        colname = str(content[0]).split(",")
        colname[0] = colname[0].strip("b'")
        colname[len(colname)-1]=colname[len(colname)-1].strip("\\r\\n'")
        for i in range(0,len(colname)):
            colname[i] = colname[i].strip('"')
        query_create = "CREATE TABLE " + tablename +'('+ " VARCHAR(30),".join(colname) + " VARCHAR(30));"      
        cur.execute(query_create)
        
        #insert
        #pick subset of 1/300 of the original size 
        pick = random.sample(range(1,len(content)),len(content)//300)
        for i in pick:
            line = str(content[i]).split(",")
            if len(line) >= len(colname):
                line = line[0:len(colname)]
                line[0] = line[0].strip("b'")
                line[len(line)-1] = line[len(line)-1].strip("\\r\\n'")
                for j in range(0,len(line)):
                    line[j] = line[j].strip('"')
                query_insert = "INSERT INTO " + tablename + ' VALUES (" ' + '" , "'.join(line) + '");'
                cur.execute(query_insert)
        conn.commit()
        cur.close()  
    except ConnectionError as e:
        print(e)
        
        
            
def getdata(car_type, year):
    for m in monthlist:
        print(m)
        url = baseurl + car_type + "_" + year + "-" + m + ".csv"
        req = urllib.request.Request(url = url , headers = headers)    
        response = urllib.request.urlopen(req)
        try:
            content =response.readlines()
            DfToSql(car_type, year,m,content)

        except OverflowError as e:                         #case with original data >2GB
            print(e,"document size larger than 2GB")
            content = str()
            chunksize = 1024*1024*50
            while True:
                chunk = response.readlines(chunksize)
                if not chunk:
                    break
                content += chunk
            DfToSql(car_type, year,m,content)



getdata("yellow_tripdata", "2020")
getdata("green_tripdata", "2020")
getdata("fhv_tripdata", "2020")

getdata("yellow_tripdata", "2019")
getdata("green_tripdata", "2019")
getdata("fhv_tripdata", "2019")

getdata("yellow_tripdata", "2018")
getdata("green_tripdata", "2018")
getdata("fhv_tripdata", "2018")

getdata("yellow_tripdata", "2017")
getdata("green_tripdata", "2017")
getdata("fhv_tripdata", "2017")

getdata("yellow_tripdata", "2016")
getdata("green_tripdata", "2016")
getdata("fhv_tripdata", "2016")

getdata("yellow_tripdata", "2015")
getdata("green_tripdata", "2015")
getdata("fhv_tripdata", "2015")

getdata("yellow_tripdata", "2014")
getdata("green_tripdata", "2014")
getdata("fhv_tripdata", "2014")











