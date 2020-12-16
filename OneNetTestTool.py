#!/usr/bin/python
# -*- coding: UTF-8
import sys
sys.path.append("..")
from OneNetApp.OneNetApi import *
from PublicLib.CloudAPI.OneNet.OneNetFrame import *
import logging
from PublicLib import public as pub


if __name__ == '__main__':
    pub.loggingConfig('logging.conf')
    logger = logging.getLogger('ToolMain')

    # 定义设备信息
    deviceinfo = {}

    # 定义设备云端信息
    device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表

    s = input("设备目录选择\n1:NB电表\n2:NB生产\n3:linyang sim7020C\n")
    if s == '1':
        device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表
    elif s == '2':
        device_contents = "sP5Mezphc5YUN9Q=mdISOM6UKVM="  # NB生产
    elif s == '3':
        device_contents = "4Hkjc25uOQ6qDd4AsfMyvMOJLSg="  # linyang sim7020C
    con = OneNetApi(device_contents)  # 文件目录


    while(1):
        state = ''
        nl = []
        s = input("查询设备数据输入:query\n    [ 所有设备-all  某个设备-index ]\n实时抄读设备:read\n    [ 所有设备-all  某个设备-index ]\n输入 exit 结束\n")

        config = pub.loadDefaultSettings("devIDcfg.json")
        devlist = config['deviceID']

        if 'exit' in s:
            break
        elif 'query' in s:
            state = 'query'
            if 'all' in s:
                nl = list(range(len(devlist)))
            else:
                s = s.replace(' ', '')
                s = s.replace('query-', '')
                nl = indexList2List(s, len(devlist))
        elif 'read' in s:
            state = 'read'
            if 'all' in s:
                nl = list(range(len(devlist)))
            else:
                s = s.replace(' ', '')
                s = s.replace('read-', '')
                nl = indexList2List(s, len(devlist))

        print(state, nl)

        if state == 'read':
            sendstr = input('请输入需要发送的报文:\n')
            print('发送中...\n')
            rlist = []
            if len(nl) > 0:
                connectonenet(con, rlist, devlist, nl)
                devListSend(con, rlist, devlist, sendstr)
            else:
                print('输入的设备index错误')


        if state == 'query' or state == 'read':
            kw = input('请输入查询关键词：[分隔符 ,]\n')
            print('查询中...\n')
            kwl = []
            if kw != '':
                kwl = kw.split(',')
            rlist = []
            if len(nl) > 0:
                connectonenet(con, rlist, devlist, nl)
                getcurinfo(con, rlist, devlist, keyword=kwl)
            else:
                print('输入的设备index错误')





