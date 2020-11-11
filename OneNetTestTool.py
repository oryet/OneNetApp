#!/usr/bin/python
# -*- coding: UTF-8
import sys
sys.path.append("..")
from OneNetApp.OneNetApi import *
import json
from PublicLib.Protocol.ly_Json import *
import time
import logging
from PublicLib import public as pub
import random


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
        # val = "{'Len':'312','Cmd':'Read','SN':'1','DataTime':'180706121314','CRC':'FFFF','DataValue':{'04A50300':'','04A50301':'','04A20201':'','04A50302':'','04A50303':''}}"  # object
        res = onenet_makeframe(con, deviceinfo, val)
        ret, data = onenet_paresdata(res)
        return ret
    return None

# 查询最近10条数据
def onenet_recvdata(con, deviceinfo):
        # res3 = con.datapoint_multi_get(device_id = deviceinfo["id"], limit = 1, datastream_ids = deviceinfo["datastreams"][0]["id"])
        res3 = con.datapoint_multi_get(device_id=deviceinfo["id"], limit=10,
                                       datastream_ids='3308_0_5750')
        count, recvtime, jsonstr = onenet_contjson(res3.content)
        return count, jsonstr


def connectonenet(rlist, devlist):
    for i in range(len(devlist)):
        rlist += [con.device_info(device_id=devlist[i])]
    return rlist

def getdevinfo(res3, device_id):
    # 获取设备信息
    try:
        ret, deviceinfo = onenet_paresdata(res3.content)
        # print('当前测试设备信息', device_id, deviceinfo['auth_info'], 'online:',deviceinfo["online"])
        return ret, deviceinfo
    except:
        return False, None


def getcurinfo(con, rlist, devlist, prelist=None, keyword=None):
    # 获取设备信息
    for i in range(len(devlist)):
        ret, deviceinfo = getdevinfo(rlist[i], devlist[i])

        if ret is True: # and deviceinfo["online"]:
            n, data = onenet_recvdata(con, deviceinfo)
            if n > 0:
                for d in data:
                    s = deviceinfo['title'] + ', ' + deviceinfo['rg_id'] + ', ' + str(d)
                    # print(deviceinfo['title'], data[0])
                    if prelist != None and prelist[i] != s:
                        prelist[i] = s
                        print(s)
                        logger.info(s)
                    elif len(keyword) > 0:
                        kcnt = 0
                        for k in keyword:
                            if k in s:
                                kcnt+=1
                        if kcnt == len(keyword):
                            print(s)
                            logger.info(s)
                            break
                    else:
                        print(s)
                        logger.info(s)
        else:
            # print(deviceinfo['title'], '不在线！ 最近在线时间:',deviceinfo["act_time"])
            try:
                s = deviceinfo['title'] + ', ' + deviceinfo['rg_id'] + ', 不在线！ 最近在线时间:' + deviceinfo["last_ct"]
                if prelist != None and prelist[i] != s:
                    prelist[i] = s
                    print(s)
                    logger.info(s)
                else:
                    print(s)
                    logger.info(s)
            except:
                pass

def devListSend(con, rlist, devlist, sendstr=None):
    # 获取设备信息
    for i in range(len(devlist)):
        ret, deviceinfo = getdevinfo(rlist[i], devlist[i])

        if ret is True and deviceinfo["online"]:
            val = "{'Len':'312','Cmd':'Read','SN':'1','DataTime':'180706121314','CRC':'FFFF','DataValue':{'04A50300':'','04A50301':'','04A20201':'','04A50302':'','04A50303':''}}"  # object
            # val = "{'Len':'312','Cmd':'Set','SN':'2','DataTime':'200428121314','CRC':'FFFF','DataValue':{'04A10101':'01#FF#0096#0005#180901120000#02#05060101#00900200','04A10102':'01#01','04A10103':'01'}}"  # object
            if sendstr != None and sendstr != '':
                sendjson = subStrToJson(sendstr)
                if sendjson != None and IsJsonFrame(sendjson):
                    val = sendstr

            hour = '00' + str(random.randint(0, 7))
            min = '00' + str(random.randint(0, 59))
            sec = '00' + str(random.randint(0, 59))
            ctime = '201029' + hour[-2:] + min[-2:] + sec[-2:]
            val = val.replace('180901120000',ctime)

            sret = onenet_senddata(con, deviceinfo, val)
            print('Send:', sret, val)
            logger.info(val)
            time.sleep(0.1)

if __name__ == '__main__':
    pub.loggingConfig('logging.conf')
    logger = logging.getLogger('ToolMain')

    # 定义设备信息
    deviceinfo = {}

    # 定义设备云端信息
    # device_contents = "4Hkjc25uOQ6qDd4AsfMyvMOJLSg="  # linyang sim7020C
    # device_id = 522658053
    device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表
    # device_id = 525383929
    # device_contents = "sP5Mezphc5YUN9Q=mdISOM6UKVM=" # NB生产

    s = input("设备目录选择\n1:NB电表\n2:NB生产\n3:linyang sim7020C\n")
    if s == '1':
        device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表
    elif s == '2':
        device_contents = "sP5Mezphc5YUN9Q=mdISOM6UKVM="  # NB生产
    elif s == '3':
        device_contents = "4Hkjc25uOQ6qDd4AsfMyvMOJLSg="  # linyang sim7020C
    con = OneNetApi(device_contents)  # 文件目录

    #设备ID
    # device_id_1 = 593477971 # IMEI: 868334034252753   TLY2821_移动_200424
    # device_id_2 = 593476181  # IMEI: 868334034332290   TLY2823_联通_200424
    # device_id_3 = 593474168  # IMEI: 868334033126362   TLY2823_电信_200424
    # device_id_4 = 586340334  # IMEI: 868334034332431   TLY2821_联通_200424



    # namelist = ['TLY2821_移动_200424', 'TLY2823_联通_200424', 'TLY2823_电信_200424', 'TLY2821_联通_200424']
    # devlist = [device_id_1, device_id_2, device_id_3, device_id_4]
    # devnum = len(devlist)
    # predata = ['']*len(devlist)


    while(1):
        state = ''
        n = -1
        s = input("查询设备数据输入:query\n    [ 所有设备-all  某个设备-index ]\n实时抄读设备:read\n    [ 所有设备-all  某个设备-index ]\n输入 exit 结束\n")
        if 'exit' in s:
            break
        elif 'query' in s:
            state = 'query'
            if 'all' in s:
                pass
            else:
                s = s.replace(' ', '')
                s = s.replace('query-', '')
                try:
                    n = int(s, 10)
                except:
                    pass
        elif 'read' in s:
            state = 'read'
            s = s.replace(' ', '')
            s = s.replace('read-', '')
            if 'all' in s:
                pass
            else:
                try:
                    n = int(s, 10)
                except:
                    pass

        print(state, n)
        config = pub.loadDefaultSettings("devIDcfg.json")
        devlist = config['deviceID']

        if state == 'read':
            sendstr = input('请输入需要发送的报文:\n')
            print('发送中...\n')
            if 0 <= n < len(devlist):
                cdevlist = [devlist[n]]
                rlist = []
                connectonenet(rlist, cdevlist)
                devListSend(con, rlist, cdevlist, sendstr)
            elif n == -1:
                rlist = []
                connectonenet(rlist, devlist)
                devListSend(con, rlist, devlist, sendstr)
            else:
                print('输入的设备index错误')


        if state == 'query' or 'read':
            kw = input('请输入查询关键词：[分隔符 ,]\n')
            print('查询中...\n')
            kwl = []
            if kw != '':
                kwl = kw.split(',')
            if 0 <= n < len(devlist):
                time.sleep(3)
                cdevlist = [devlist[n]]
                rlist = []
                connectonenet(rlist, cdevlist)
                getcurinfo(con, rlist, cdevlist, keyword=kwl)
            elif n == -1:
                rlist = []
                connectonenet(rlist, devlist)
                getcurinfo(con, rlist, devlist, keyword=kwl)
            else:
                print('输入的设备index错误')





