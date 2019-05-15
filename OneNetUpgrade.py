#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import queue
import time
from UpgradeMakeFrame import upgradeMakeFrame
import UpgradeDealFrame as df
import OneNetToDev as odev
from OneNetApi import *


class onenetupgrade():
    def __init__(self):
        self.qRecv = queue.Queue()
        self.mf = upgradeMakeFrame()
        self.state = 0
        bitmap = [0] * 1024
        self.uplist = {"ip": "", "port": "", "bmap": bitmap}
        # self.ADDRESS = ('192.168.127.16', 8888)  # 绑定地址
        self.upgradeCnt = 0
        # 定义设备信息
        self.deviceinfo = {}


    def upgradeStartRecvThread(self):
        tser = threading.Thread(target=df.upgradeRecvProc, args=(self, ))
        tser.start()


    def upgradehandle(self, nSocket):
        print("[1、启动升级 2、检查漏包 3、检查版本 4、继续升级]")
        str = input("请输入需要执行的流程：")
        if str == "":
            return 0
        n = int(str, 10)
        senddata = ""

        if (n == 1):
            senddata = self.mf.upgradeStart()
            self.upgradeCnt = 0
        elif (n == 2):
            strindex = input("请输入需要查询的包序号：")
            senddata = self.mf.upgradeCheckPack(strindex)
        elif (n == 3):
            senddata = self.mf.upgradeCheckVision()
        else:
            pass

        if senddata:
            # socketServer.SocketSend(nSocket, senddata)
            odev.onenet_senddata(self.con, self.deviceinfo, senddata)
            print(senddata)

        # 接收处理
        count, recvdata = odev.onenet_recvdata(self.con, self.deviceinfo)
        if count > 0:
            for i in range(count):
                self.qRecv.put(recvdata[i])
        return n

    def upgradeProc(self):
        # 定义设备云端信息
        device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表
        device_id = 525383929 # 三相移动测试 20190321 7#

        self.con = OneNetApi(device_contents)  # 文件目录

        if len(self.deviceinfo) == 0:
            # 获取设备信息
            res3 = self.con.device_info(device_id=device_id)
            ret, self.deviceinfo = odev.onenet_paresdata(res3.content)

        # 启动数据处理线程
        self.upgradeStartRecvThread()

        # 升级应用线程
        while 1:
            time.sleep(5)

            if self.deviceinfo["online"]:
                nSocket = self.con  # self.uim.socketComboBox.currentIndex()

                # 接收处理
                if self.state != 1:
                    count, recvdata = odev.onenet_recvdata(self.con, self.deviceinfo)
                    if count > 0:
                        for i in range(count):
                            self.qRecv.put(recvdata[i])

                # 根据状态进行 1、启动升级 2、检查漏包 3、升级文件 4、检查版本
                if self.state == 0:
                    n = self.upgradehandle(nSocket)
                    if n == 1 or n > 10:
                        self.state = 1
                elif self.state == 2:  # 自动查漏包1
                    senddata = self.mf.upgradeCheckPack("1")
                    # socketServer.SocketSend(nSocket, senddata)
                    odev.onenet_senddata(self.con, self.deviceinfo, senddata)
                    self.state = 3
                elif self.state == 3:  # 自动查漏包2
                    senddata = self.mf.upgradeCheckPack("2")
                    # socketServer.SocketSend(nSocket, senddata)
                    odev.onenet_senddata(self.con, self.deviceinfo, senddata)
                    self.state = 4
                elif self.state == 4:  # 自动查版本号
                    senddata = self.mf.upgradeCheckVision()
                    # socketServer.SocketSend(nSocket, senddata)
                    odev.onenet_senddata(self.con, self.deviceinfo, senddata)
                    self.state = 1
                    self.upgradeCnt += 1
                    if self.upgradeCnt > 5:
                        self.state = 0  # 大于自动尝试次数，进入手动模式
                else:
                    i = df.upgradeGetCurPackNum(self)
                    if i < self.mf.packnum:
                        senddata = self.mf.upgradeSendFile(i)  # 读文件从0开始, 包序号从1开始
                        self.uplist["bmap"][i] = 1
                        print("升级ing, 当前包序号：", i)
                        # socketServer.SocketSend(nSocket, senddata)
                        odev.onenet_senddata(self.con, self.deviceinfo, senddata)
                        print(senddata)
                    if (i == 10) or (i > 10 and i >= n):
                        self.state = 0 # 手动
                    elif (i >= self.mf.packnum):
                        self.state = 2 # 自动查漏包

if __name__ == '__main__':
    su = onenetupgrade()
    su.upgradeProc()

