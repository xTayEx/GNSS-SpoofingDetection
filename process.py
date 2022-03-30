import io
import json
import math
import os
import time
from datetime import datetime, timedelta, timezone
from multiprocessing import Pipe, Process

import pynmea2
import serial

from detect import detect, detect_init

ser = serial.Serial('/dev/ttyS1', 4800, timeout=5.0)
#sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
referredtime = datetime.datetime.utcnow()
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
def main():
    detect_init()
    parent_conn, child_conn = Pipe()
    detect_process = Process(target=detect, args=(child_conn,))
    detect_process.start()
    # 考虑到需要经计算距离，那么就需要两条数据才能计算，所以偶数的时候计算距离获取时间差，奇数的时候提取经纬度
    count = 0
    countdown = CLOCKCYCLE
    while ser.inWaiting() != 0:
        # 以0.05s为一个时间间隔（参照表格中的10hz）依据IMU,CAN_SPEED频率可能还要修改
        time.sleep(0.025)
        # 1000条记录为一个json文件
        if countdown == 0:
            cyclecount += 1
            countdown = CLOCKCYCLE
        try:
            count += 1
            line = str(str(ser.readline())[2:])
            # print(line)
            if line.startswith('$GPRMC'):
                line = line.replace('\\r\\n\'', '')
                msg = pynmea2.parse(line)
                if msg.status == "A":
                    # 单位从“度分”转化为“度”
                    if count % 2 == 1:
                        latitude1 = int(float(msg.lat)/100)+((float(msg.lat)/100)-int(float(msg.lat)/100))*100/60
                        longtitude1 = int(float(msg.lon)/100)+(float(msg.lon)/100-int(float(msg.lon)/100))*100/60
                        latitude1 = round(latitude1, 6)
                        longtitude1 = round(longtitude1, 6)
                    else:
                        # 单位从“度分”转化为“度”
                        latitude2 = int(float(msg.lat)/100)+((float(msg.lat)/100)-int(float(msg.lat)/100))*100/60
                        longtitude2 = int(float(msg.lon)/100)+(float(msg.lon)/100-int(float(msg.lon)/100))*100/60
                        latitude2 = round(latitude2, 6)
                        longtitude2 = round(longtitude2, 6)
                        time = msg.timestamp
                        date = msg.datestamp
                        utctime = date+" "+time
                        LOCAL_format = "%Y-%m-%d %H:%M:%S"
                        # 转化成datetime对象
                        a = datetime.strptime(utctime, LOCAL_format)
                        # 转化成北京时间,这些转换可能用不到叭，但是先写下来
                        # a=a.replace(tzinfo=timezone.utc)
                        # tzutc_8=timezone(timedelta(hours=8))
                        # localtime=a.astimezone(tzutc_8)
                        # 计算从程序开始运行的时间与接收到GPS信号传回的时间差,精确到小数点后一位，以此作为传递的参数
                        time_delta = round((a-referredtime).days*3600 + (a-referredtime).seconds +
                                           (a-referredtime).microseconds*0.000001, 1)
                        # 计算距离
                        dis = getDistance(latitude1, longtitude1, latitude2, longtitude2)
                        tuple_dict = {
                            'distance': dis,
                            'time': time_delta
                        }
                        json_str = json.dumps(tuple_dict)
                        parent_conn.send(json_str)
                        # file_name = str(cyclecount)+'.json'
                        # if(os.path.exists(file_name)):
                        #     with open('test_data.json', 'a') as json_file:
                        #         json_file.write(json_str)
                        # else:
                        #     os.makedirs(file_name)
                        #     with open('test_data.json', 'w') as json_file:
                        #         json_file.write(json_str)
                        countdown -= 1
        except serial.SerialException as e:
            print('Device error: {}'.format(e))
            break
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            continue

        detect_process.join()

if __name__ == '__main__':
    main()
