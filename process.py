import csv
import io
import json
import math
import os
import time
from datetime import datetime, timedelta, timezone

import pynmea2


EARTH_REDIUS = 6378.137
CLOCKCYCLE = 2000

latitude1 = 0
latitude2 = 0
longtitude1 = 0
longtitude2 = 0
cyclecount = 0


def rad(d):
    return d * math.pi / 180.0


def getDistance(lat1, lng1, lat2, lng2):
    # 对数组取元素做运算
    radLat1 = rad(lat1)
    radLat2 = rad(lat2)
    a = rad(lat1) - rad(lat2)
    b = rad(lng1) - rad(lng2)
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(
        math.sin(b / 2), 2)))
    s = s * EARTH_REDIUS * 1000
    return s


# 串口数据转换成标准格式
# 提取数据
# 打包成字典
# 写入Json
def process():

    count = 0
    f = open(r"test/NMEA1083.txt")
    line = f.readline()
    file_name = r"test/test.csv"
    des_csvfile = open(file_name, 'w', encoding='utf-8', newline="")
    spoofing_csvfile = open("/root/autodl-nas/Chunk_01/b0c9d2329ad1606b|2018-08-06--10-04-53.csv")
    writer = csv.writer(des_csvfile, delimiter=',')
    reader = csv.reader(spoofing_csvfile, delimiter=',')
    next(reader)
    writer.writerow(["CAN_speeds(t-1)", "steering_angles(t-1)", "acceleration_forward(t-1)", "distance", "times"])
    while line != "":
        try:
            count += 1
            if line.startswith('$GPRMC'):
                #line = line.replace('\\r\\n\'', '')
                msg = pynmea2.parse(line)
                if msg.status == "A":
                    # 单位从“度分”转化为“度”
                    if count % 2 == 1:
                        latitude1 = int(float(msg.lat) / 100) + ((float(msg.lat) / 100) - int(float(msg.lat) / 100)) * 100 / 60
                        longtitude1 = int(float(msg.lon) / 100) + (float(msg.lon) / 100 - int(float(msg.lon) / 100)) * 100 / 60
                    else:
                        # 单位从“度分”转化为“度”
                        latitude2 = int(float(msg.lat) / 100) + ((float(msg.lat) / 100) - int(float(msg.lat) / 100)) * 100 / 60
                        longtitude2 = int(float(msg.lon) / 100) + (float(msg.lon) / 100 - int(float(msg.lon) / 100)) * 100 / 60
                        time = msg.timestamp
                        # 转化成datetime对象
                        # 转化成北京时间
                        # 计算从程序开始运行的时间与接收到GPS信号传回的时间差,精确到小数点后一位，以此作为传递的参数
                        # 计算距离
                        dis = getDistance(latitude1, longtitude1, latitude2, longtitude2)
                        fields = next(reader)
                        can, angle, accelerate = fields[0], fields[1], fields[2]

                        writer.writerow([can, angle, accelerate, dis, time])
            line = f.readline()
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            break

    
    f.close()
    des_csvfile.close()
    spoofing_csvfile.close()

if __name__ == '__main__':
    process()