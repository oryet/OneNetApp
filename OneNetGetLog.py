#!/usr/bin/python
# -*- coding: UTF-8
import sys

sys.path.append("..")
from OneNetApp.OneNetApi import *
import json
from PublicLib.Protocol.ly_Json import subStrToJson
import time
import logging
from PublicLib import public as pub


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
        recvtimelist += [recvtime]
        valuelist += [value]
    return count, recvtimelist, valuelist


def onenet_makeframe(con, deviceinfo, val):
    # nbiot_url = {"imei": device_imei, "obj_id": obj_id, "obj_inst_id": obj_inst_id, "mode": mode}  # params
    # '3308_0_5750'
    # nbiot_url = {"imei": deviceinfo["rg_id"], "obj_id": deviceinfo["datastreams"][0]["id"][:4],
    #              "obj_inst_id": deviceinfo["datastreams"][0]["id"][5:6], "mode": 2}  # params
    nbiot_url = {"imei": deviceinfo["rg_id"], "obj_id": '3308',
                 "obj_inst_id": '0', "mode": 2}  # params
    nbiot_data = {"data": [{"res_id": '5750', "val": val}]}  # data

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


def getcurtime():
    # 时间戳
    now = time.time()
    int(now)

    # 时间
    tl = time.localtime(now)

    # 格式化时间
    return time.strftime("%Y-%m-%d %H:%M:%S", tl)


def getpreday(n):
    # 时间戳
    now = time.time()
    int(now)

    pre = now - n*24*3600

    # 时间
    tl = time.localtime(pre)

    # 格式化时间
    return time.strftime("%Y-%m-%d %H:%M:%S", tl)


# 查询最近N条数据
def onenet_recvdata(con, deviceinfo, parm):
    if deviceinfo["online"]:
        # res3 = con.datapoint_multi_get(device_id = deviceinfo["id"], limit = 1, datastream_ids = deviceinfo["datastreams"][0]["id"])

        if "start_time" in parm and "end_time" in parm and "limit" in parm:
            res3 = con.datapoint_multi_get(device_id=deviceinfo["id"],
                                           start_time=parm["start_time"],
                                           end_time=parm["end_time"],
                                           limit=parm["limit"],
                                           datastream_ids='3308_0_5750')
        elif "start_time" in parm and  "end_time":
            res3 = con.datapoint_multi_get(device_id=deviceinfo["id"],
                                           start_time=parm["start_time"],
                                           end_time=parm["end_time"],
                                           datastream_ids='3308_0_5750')
        elif "limit" in parm:
            res3 = con.datapoint_multi_get(device_id=deviceinfo["id"],
                                           limit=parm["limit"],
                                           datastream_ids='3308_0_5750')
        else:
            res3 = con.datapoint_multi_get(device_id=deviceinfo["id"],
                                           limit=1,
                                           datastream_ids='3308_0_5750')
        count, recvtime, jsonstr = onenet_contjson(res3.content)
        return count, jsonstr
    else:
        print('设备不在线')


def connectonenet(rlist, devlist):
    for i in range(len(devlist)):
        rlist += [con.device_info(device_id=devlist[i])]
    return rlist


def getdevinfo(res3, device_id):
    # 获取设备信息
    ret, deviceinfo = onenet_paresdata(res3.content)
    # print('当前测试设备信息', device_id, deviceinfo['auth_info'], 'online:',deviceinfo["online"])
    return ret, deviceinfo


def getcurinfo(con, rlist, devlist, prelist, parm):
    # 获取设备信息
    for i in range(len(devlist)):
        nret, deviceinfo = getdevinfo(rlist[i], devlist[i])

        if nret is True and deviceinfo["online"]:
            # val = "{'Len':'312','Cmd':'Set','SN':'2','DataTime':'200428121314','CRC':'FFFF','DataValue':{'04A20105':'01'}}"  # object
            val = "{'Len':'312','Cmd':'Set','SN':'2','DataTime':'180706121314','CRC':'FFFF','DataValue':{'04A10101':'02#FF#8002#0005#180901120100#05#00900200#05060101#04A20201#04A50302#04A50303','04A10102':'02#01'}}"  # object
            ret = onenet_senddata(con, deviceinfo, val)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'send: ', val)
            time.sleep(5)  # 等待间隔

            # val = "{'Len':'312','Cmd':'Read','SN':'1','DataTime':'200428121314','CRC':'FFFF','DataValue':{'04A00101':'','04A00102':'','04A20201':'','04A50302':'','04A50303':''}}"  # object
            val = "{'Len':'0104','Cmd':'Set','SN':'179','DataTime':'200527144935','CRC':'FFFF','DataValue':{'04A20106':'0060'}}"  # object
            ret = onenet_senddata(con, deviceinfo, val)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'send: ', val)
            time.sleep(1)  # 等待间隔


        if nret is True and deviceinfo["online"]:
            n, data = onenet_recvdata(con, deviceinfo, parm)
            if n > 0:
                s = deviceinfo['title'] + ', ' + deviceinfo['rg_id']
                print(s)
                logger.info(s)
                for d in data:
                    print(d)
                    logger.info(d)
        else:
            # print(deviceinfo['title'], '不在线！ 最近在线时间:',deviceinfo["act_time"])
            try:
                s = deviceinfo['title'] + ', ' + deviceinfo['rg_id'] + ', 不在线！ 最近在线时间:' + deviceinfo["last_ct"]
                if prelist[i] != s:
                    prelist[i] = s
                    print(s)
                    logger.info(s)
            except:
                pass



if __name__ == '__main__':
    pub.loggingConfig('logging.conf')
    logger = logging.getLogger('ToolMain')

    # 定义设备信息
    deviceinfo = {}

    # 定义设备云端信息
    # device_contents = "4Hkjc25uOQ6qDd4AsfMyvMOJLSg="
    # device_id = 522658053
    # device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表
    # device_id = 525383929
    device_contents = "sP5Mezphc5YUN9Q=mdISOM6UKVM="  # NB生产
    con = OneNetApi(device_contents)  # 文件目录

    # 设备ID
    # device_id_1 = 593477971 # IMEI: 868334034252753   TLY2821_移动_200424
    # device_id_2 = 593476181  # IMEI: 868334034332290   TLY2823_联通_200424
    # device_id_3 = 593474168  # IMEI: 868334033126362   TLY2823_电信_200424
    # device_id_4 = 586340334  # IMEI: 868334034332431   TLY2821_联通_200424

    config = pub.loadDefaultSettings("devIDcfg.json")
    devlist = config['deviceID']

    # namelist = ['TLY2821_移动_200424', 'TLY2823_联通_200424', 'TLY2823_电信_200424', 'TLY2821_联通_200424']
    # devlist = [device_id_1, device_id_2, device_id_3, device_id_4]
    # devnum = len(devlist)
    predata = [''] * 4

    # start_time = getpreday(3)
    # end_time = getcurtime()
    # parm = {"start_time":start_time, "end_time":end_time, "limit":64}

    parm = {"limit": 64}

    # 连接设备
    rlist = []
    connectonenet(rlist, devlist)

    # 获取最近信息
    getcurinfo(con, rlist, devlist, predata, parm)
    time.sleep(3)

