#!/usr/bin/python
# -*- coding: UTF-8
import sys
import logging
import PublicLib.public as pub
from PublicLib.CloudAPI.OneNet.OneNetApi import *
from PublicLib.CloudAPI.OneNet.OneNetFrame import *




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
    nl = list(range(len(devlist)))
    connectonenet(con, rlist, devlist, nl)

    # 获取最近信息
    getcurinfo(con, rlist, devlist, predata, parm)
    time.sleep(3)

