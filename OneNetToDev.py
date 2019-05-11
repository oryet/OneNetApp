#!/usr/bin/python
# -*- coding: UTF-8

from OneNetApi import *
import json
from ly_Json import subStrToJson
import xlwt
import datetime
import time

device_contents = "4Hkjc25uOQ6qDd4AsfMyvMOJLSg="
datastream_ids = ['3308_0_5750']

device_id = 522658053
limit = 100
device_imei = "868334032456596"

if __name__ == '__main__':
    test = OneNetApi(device_contents)  # 文件目录

    '''
    # 获取数据
    # stream_id使用list
    # datastream_ids = ['temperature', 'humidity']
    datastream_ids = ['3308_0_5750']
    print (type(datastream_ids))
    start_time = "2019-05-07 00:00:01"
    end_time = "2019-05-07 23:59:59"
    limit = 100
    res3 = test.datapoint_multi_get(device_id = device_id, start_time = start_time, end_time = end_time, limit = limit, datastream_ids = datastream_ids)
    print (res3.content)
    '''

    # 增加触发器
    # device_id = *******
    # trigger = {"ds_id": "test1", "url": "http://xx.bb.com", "type":">=", "threshold":100}
    # res1 = test.trigger_add(trigger = trigger)
    # print res1.content

    # 其中datastream_id等于obj_id, obj_inst_id, res_id，如obj_id:3200，obj_inst_id:0，res_id:5501，那么这个datastream_id就为3200_0_5501。 ['3308_0_5750']
    # 及时命令 写设备资源

    obj_id = 3308  # int
    obj_inst_id = 0  # int
    mode = 2
    res_id = 5750  # int
    val = "{'Len':'312','Cmd':'Read','SN':'1','DataTime':'180706121314','CRC':'FFFF','DataValue':{'0201FF00':''}}"  # object

    nbiot_url = {"imei": device_imei, "obj_id": obj_id, "obj_inst_id": obj_inst_id, "mode": mode, "timeout":25}  # params
    nbiot_data = {"data":[{"res_id": res_id, "val": val}]}  # data

    res4 = test.nbiot_write(nbiot_data, nbiot_url)
    print(res4.content)
