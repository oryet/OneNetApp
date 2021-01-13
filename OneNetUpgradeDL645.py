#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import time
from PublicLib.Upgrade.UpgradeMakeFrame_DL645 import upgradeMakeFrame
import PublicLib.Upgrade.UpgradeDealFrame_DL645 as df
# import OneNetApp.OneNetToDev as odev
from PublicLib.CloudAPI.OneNet.OneNetFrame import *
from PublicLib.CloudAPI.OneNet.OneNetApi import *


class onenetupgrade():
    def __init__(self, filename):
        self.mf = upgradeMakeFrame(filename)
        bitmap = [0] * 2048
        self.uplist = {"ip": "", "port": "", "bmap": bitmap}
        # self.ADDRESS = ('192.168.127.16', 8888)  # 绑定地址
        self.upgradeCnt = 0
        # 定义设备信息
        self.deviceinfo = {}
        self.state = {"send": "", "recv":1, "mode":"auto", "retry":1}


    def upgradeStartRecvThread(self):
        tser = threading.Thread(target=self.upgradeRecv, args=())
        tser.start()

    def upgradeInputThread(self):
        tser = threading.Thread(target=self.upgradeInput, args=())
        tser.start()

    def upgradeSendThread(self):
        tser = threading.Thread(target=self.upgradehandle, args=())
        tser.start()


    def upgradeRecv(self):
        while(1):
            # 接收处理
            t = self.state["recv"]
            if t > 0:
                self.state["recv"] = 0
                time.sleep(t)
                parm = {"limit": 1}
                data = {}
                count, recvdata = onenet_recvdata(self.con, self.deviceinfo, parm, data)
                print('upgradeRecv count:', count)
                for d in recvdata:
                    if 'Len' in d:
                        pass
                    elif 'HexStr' in d:
                        df.upgradeDataProc_DL645(d['HexStr'], self.uplist)
                    else:
                        pass
            else:
                time.sleep(1)


    def upgradeInput(self):
        while(1):
            print("[0、暂停 1、启动升级 2、检查漏包 3、检查版本 N、继续升级]")
            n = input("请输入需要执行的流程：")
            if len(n) > 0:
                if n == '0':
                    self.state["send"] = 'pause'
                    self.state["mode"] = 'manual'
                elif n == '1':
                    self.state["send"] = 'upgrade_start'
                    self.upgradeCnt = 0
                    self.state["mode"] = 'auto'
                elif n == '2':
                    self.state["send"] = 'checkPage'
                    self.state["retry"] = 1
                    self.state["mode"] = 'manual'
                elif n == '3':
                    self.state["send"] = 'checkVersions'
                    self.state["retry"] = 1
                    self.state["mode"] = 'manual'
                else:
                    self.state["send"] = 'upgrade_ing'
                    self.state["mode"] = 'auto'

    def upgradehandle(self):
        state = {}
        while(1):
            senddata = ""
            if state != self.state:
                print('upgradehandle state:', self.state)
                state = self.state

            if self.state["send"] == 'upgrade_start':
                senddata = self.mf.upgradeStart()
                self.state["send"] = 'upgrade_ing'
            elif self.state["send"] == 'checkPage':
                if self.state["retry"] > 0:
                    senddata = self.mf.upgradeCheckPack()
                    self.state["recv"] = 1
                    self.state["retry"] -= 1
                    i = df.upgradeGetCurPackNum(self.uplist)
                    if self.state["mode"] == 'auto' and i < self.mf.packnum:
                        self.state["send"] = 'upgrade_ing'
                elif self.state["mode"] == 'auto':
                    self.state["send"] = 'checkVersions'
                    self.state["retry"] = 3
            elif self.state["send"] == 'checkVersions':
                if self.state["retry"] > 0:
                    self.state["recv"] = 1
                    senddata = self.mf.upgradeCheckVision()
                    self.state["retry"] -= 1
                    i = df.upgradeGetCurPackNum(self.uplist)
                    if self.state["mode"] == 'auto' and i < self.mf.packnum:
                        self.state["send"] = 'upgrade_ing'
                elif self.state["mode"] == 'auto':
                    self.state["send"] = 'pause'
                    self.state["retry"] = 0
            elif self.state["send"] == 'upgrade_ing':
                i = df.upgradeGetCurPackNum(self.uplist)
                if i < self.mf.packnum:
                    senddata = self.mf.upgradeSendFile(i)  # 读文件从0开始, 包序号从1开始
                    self.uplist["bmap"][i] = 1
                    # print("当前包序号：", i, " [", i*100/self.mf.packnum, '%]')
                    print("当前包序号：{}, 进度: {:.2%}".format(i, i/self.mf.packnum))
                else:
                    self.state["send"] = 'checkPage'
                    self.state["retry"] = 3
            else:
                time.sleep(1)

            if senddata:
                onenet_sendcmd(self.con, self.deviceinfo, senddata)

    def upgradeProc(self, device_contents, device_id):
        # 定义设备云端信息
        # device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表
        # device_id = 641859315 # 三相移动测试 20190321 7#

        self.con = OneNetApi(device_contents)  # 文件目录

        if len(self.deviceinfo) == 0:
            # 获取设备信息
            res3 = self.con.device_info(device_id=device_id)
            ret, self.deviceinfo = onenet_paresdata(res3.content)

        # 启动数据处理线程
        self.upgradeStartRecvThread()
        self.upgradeInputThread()
        self.upgradeSendThread()


if __name__ == '__main__':
    filename = u'F:\\Work\\软件提交\\TLY2821\\TLY2821-03-UP0000-201211-00\\TLY2821-03-UP0000-201211-00.bin'
    device_contents = "mBnDJfsR8paDmq3g7mh=iWi9lb4="  # NB电表
    device_id = 657412177 # 三相移动测试 20190321 7#
    su = onenetupgrade(filename)
    su.upgradeProc(device_contents, device_id)

