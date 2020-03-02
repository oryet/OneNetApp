#!/usr/bin/python
# -*- coding: UTF-8
import sys
sys.path.append("..")
from OneNetApp.OneNetApi import *
import json
from PublicLib.Protocol.ly_Json import subStrToJson
import time




def onenet_paresdata(res):
    # bytes to str
    data = bytes.decode(res)

    # 将json对象转换成python对象
    data_python = json.loads(data)
    if data_python["errno"] == 0 and data_python["error"] == "succ":
        if 'data' in data_python:
            return True, data_python["data"]
        else:
            return True, None
    else:
        return False, None

def onenet_contjson(content):
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


def onenet_makeframe(con, deviceinfo, val):
    # nbiot_url = {"imei": device_imei, "obj_id": obj_id, "obj_inst_id": obj_inst_id, "mode": mode}  # params
    # '3308_0_5750'
    # nbiot_url = {"imei": deviceinfo["rg_id"], "obj_id": deviceinfo["datastreams"][0]["id"][:4],
    #              "obj_inst_id": deviceinfo["datastreams"][0]["id"][5:6], "mode": 2}  # params
    nbiot_url = {"imei": deviceinfo["rg_id"], "obj_id": '3308',
                 "obj_inst_id": '0', "mode": 2}  # params
    nbiot_data = {"data":[{"res_id": '5750', "val": val}]}  # data

    res4 = con.nbiot_write(nbiot_data, nbiot_url)
    return (res4.content)

def onenet_senddata(con, deviceinfo, val):
    if deviceinfo["online"]:
        # 发送数据
        # 其中datastream_id等于obj_id, obj_inst_id, res_id，如obj_id:3200，obj_inst_id:0，res_id:5501，那么这个datastream_id就为3200_0_5501。 ['3308_0_5750']
        # val = "{'Len':'312','Cmd':'Read','SN':'1','DataTime':'180706121314','CRC':'FFFF','DataValue':{'0201FF00':''}}"  # object
        res = onenet_makeframe(con, deviceinfo, val)
        ret, data = onenet_paresdata(res)
        return ret
    return None

# 查询最近10条数据
def onenet_recvdata(con, deviceinfo):
    if deviceinfo["online"]:
        # res3 = con.datapoint_multi_get(device_id = deviceinfo["id"], limit = 1, datastream_ids = deviceinfo["datastreams"][0]["id"])
        res3 = con.datapoint_multi_get(device_id=deviceinfo["id"], limit=1,
                                       datastream_ids='3308_0_5750')
        count, recvtime, jsonstr = onenet_contjson(res3.content)
        return count, jsonstr


if __name__ == '__main__':
    # 定义设备信息
    deviceinfo = {}

    # 定义设备云端信息
    # device_contents = "4Hkjc25uOQ6qDd4AsfMyvMOJLSg="
    # device_id = 522658053
    # device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表
    # device_id = 525383929
    device_contents = "sP5Mezphc5YUN9Q=mdISOM6UKVM=" # NB生产
    con = OneNetApi(device_contents)  # 文件目录

    #设备ID
    # device_id = 586340334 # IMEI: 868334034332431
    device_id = 586366366 # IMEI: 868334031308111
    # device_id = 586366691 # IMEI: 868334031308913
    # device_id = 586329362 # IMEI: 868334034317762

    if len(deviceinfo) == 0:
        # 获取设备信息
        res3 = con.device_info(device_id=device_id)
        ret, deviceinfo = onenet_paresdata(res3.content)
        print('当前测试设备信息', device_id, deviceinfo['auth_info'])

    # 发送数据
    val = "{'Len':'312','Cmd':'Read','SN':'1','DataTime':'190706121314','CRC':'FFFF','DataValue':{'0001FF00':''}}"  # object

    if ret is not None:
        # 接收数据
        for i in range(1):  # 循环抄读次数
            ret = onenet_senddata(con, deviceinfo, val)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'send: ', val)

            time.sleep(5)  # 等待间隔
            n, data = onenet_recvdata(con, deviceinfo)
            if n > 0:
                for i in range(n):
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'recv: ', data[i])
    else:
        print('设备不在线！！！')
