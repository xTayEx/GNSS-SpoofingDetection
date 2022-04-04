from email.policy import default
import pynmea2
import io
import serial
from datetime import datetime,timezone,timedelta
import time
import math
import json
import os
import csv
#ser = serial.Serial('/dev/ttyS1', 4800, timeout=5.0)
#sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
#referredtime=datetime.datetime.utcnow()
EARTH_REDIUS = 6378.137
CLOCKCYCLE=2000

latitude1=0
latitude2=0
longtitude1=0
longtitude2=0
cyclecount=0
def rad(d):
    return d * math.pi / 180.0
def getDistance(lat1, lng1, lat2, lng2):
    # 对数组取元素做运算
    radLat1=rad(lat1)
    radLat2=rad(lat2)
    a = rad(lat1) - rad(lat2)
    b = rad(lng1) - rad(lng2)
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(
        math.sin(b / 2), 2)))
    s = s * EARTH_REDIUS * 1000
    return s

#串口数据转换成标准格式
#提取数据
#打包成字典
#写入Json
if __name__ == '__main__': 
    count=0
    f = open(r"D:\test\NMEA1083.txt")
    line = f.readline()
    file_name=r"D:\test\test.csv"
    csvfile=open( file_name,'w',encoding='utf-8',newline="" )
    writer = csv.writer(csvfile)
    writer.writerow(["distance","time"])
    while line!="": 
        try:
            count+=1
            if line.startswith('$GPRMC'):
                #line = line.replace('\\r\\n\'', '')
                msg = pynmea2.parse(line)
                #print(repr(msg))
                if msg.status=="A":
                    #单位从“度分”转化为“度”
                    if count%2==1:
                        latitude1=int(float(msg.lat)/100)+((float(msg.lat)/100)-int(float(msg.lat)/100))*100/60
                        longtitude1=int(float(msg.lon)/100)+(float(msg.lon)/100-int(float(msg.lon)/100))*100/60
                    else:
                        #单位从“度分”转化为“度”
                        latitude2=int(float(msg.lat)/100)+((float(msg.lat)/100)-int(float(msg.lat)/100))*100/60
                        longtitude2=int(float(msg.lon)/100)+(float(msg.lon)/100-int(float(msg.lon)/100))*100/60
                        time=msg.timestamp    
                        #转化成datetime对象    
                        #转化成北京时间,这些转换可能用不到叭，但是先写下来  
                        #a=a.replace(tzinfo=timezone.utc)
                        #tzutc_8=timezone(timedelta(hours=8))  
                        #localtime=a.astimezone(tzutc_8) 
                        #计算从程序开始运行的时间与接收到GPS信号传回的时间差,精确到小数点后一位，以此作为传递的参数   
                        #计算距离
                        dis=getDistance(latitude1, longtitude1, latitude2, longtitude2)
                        with open('test.csv', 'w') as csvfile:
                            writer.writerow([dis,time])
            line = f.readline()
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            break
    f.close()
