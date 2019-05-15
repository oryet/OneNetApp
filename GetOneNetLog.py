#!/usr/bin/python
# -*- coding: UTF-8
import sys
sys.path.append("..")
from OneNetApi import *
import json
from PublicLib.Protocol.ly_Json import subStrToJson
import xlwt
import datetime
import time


device_contents = "4Hkjc25uOQ6qDd4AsfMyvMOJLSg="
datastream_ids = ['3308_0_5750']

device_id = 522658053
limit = 100

path = r'F:\Source\Python\\'

def contjson(content):
    jsondata = bytes.decode(content)

    # 将json对象转换成python对象
    data = json.loads(jsondata)

    count = data["data"]["count"]
    recvtimelist = []
    valuelist = []
    for i in range(count):
        dic = data["data"]["datastreams"][0]["datapoints"][i]

        recvtime = dic["at"]
        value = dic["value"]
        value = subStrToJson(value)
        recvtimelist +=[recvtime]
        valuelist += [value]
    return count,recvtimelist,valuelist

def createxls():
    # 新建excel表格
    wbnew = xlwt.Workbook();
    wsnew = wbnew.add_sheet('sheet');

    # wsnew.write(0, 0, 'IP');
    wsnew.write(0, 1, 'date');
    wsnew.write(0, 2, 'time');
    wsnew.write(0, 3, 'Len');
    wsnew.write(0, 4, 'Cmd');
    wsnew.write(0, 5, 'SN');
    wsnew.write(0, 6, 'DataTime');
    wsnew.write(0, 7, 'CRC');
    wsnew.write(0, 8, 'DataValue');
    return  wbnew, wsnew

def savedata(start_n, start_time, end_time, wsnew):
    res3 = test.datapoint_multi_get(device_id = device_id, start_time = start_time, end_time = end_time, limit = limit, datastream_ids = datastream_ids)

    count, recvtime, jsonstr = contjson(res3.content)
    if count == 0:
        return count, None

    for n in range(count):
        print(recvtime[n], jsonstr[n])
        row = n+1+start_n
        # wsnew.write(n, 0, ip);
        wsnew.write(row, 1, recvtime[n][:10]);
        wsnew.write(row, 2, recvtime[n][11:]);
        wsnew.write(row, 3, jsonstr[n]['Len']);
        wsnew.write(row, 4, jsonstr[n]['Cmd']);
        wsnew.write(row, 5, jsonstr[n]['SN']);
        wsnew.write(row, 6, jsonstr[n]['DataTime']);
        wsnew.write(row, 7, jsonstr[n]['CRC']);

        i = 0
        for key, values in jsonstr[n]['DataValue'].items():
            wsnew.write(row, 8 + i * 2, key);
            wsnew.write(row, 9 + i * 2, values);
            i += 1
    return count, recvtime[count-1]

def str2timestamp(date_str):
    # string --> datetime obj
    dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    # print("dt_obj:", dt_obj)

    # dt obj --> time obj
    time_tuple = dt_obj.timetuple()
    # print("time_tuple:", time_tuple)

    # time obj --> timestamp
    timestamp = time.mktime(time_tuple)
    # print("timestamp:", timestamp)
    return timestamp

def timestamp2str(timestamp):
    # timestamp 转 datetime obj
    dt_obj = datetime.datetime.fromtimestamp(timestamp)
    # print("dt_obj:", dt_obj)

    # dt obj --> string
    date_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
    # print("date_str:", date_str)
    return date_str

if __name__ == '__main__':
    wbnew, wsnew = createxls()

    test = OneNetApi(device_contents)  # 文件目录

    start_time = "2019-05-01 00:00:00"
    end_time = "2019-05-08 23:59:59"

    start_n = 0
    n, cur_time = savedata(0, start_time, end_time, wsnew)
    while n > 0:
        # print("s", n, cur_time[:19])
        timestamp = str2timestamp(cur_time[:19])
        timestamp += 1
        cur_time = timestamp2str(timestamp)

        start_n += n
        n, cur_time = savedata(start_n, cur_time, end_time, wsnew)
        # print("e", n, cur_time[:19])



    # 保存关系表
    start_time = start_time.replace("-","")
    end_time = end_time.replace("-", "")
    start_time = start_time.replace(":", "")
    end_time = end_time.replace(":", "")
    wbnew.save(path + str(device_id) + "-" + start_time + end_time + '.xls');

