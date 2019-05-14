from PublicLib.Protocol.protocol import prtl2Make
from PublicLib.Protocol.protocol import judgePrtl
from UpgradeReadfile import UpgradeReadfile
import PublicLib.public as pfun

'''
FILE_MANUIDEN = "594C"
FILE_DEV_TYPE = "03"
FILE_LEN = 0x000173ed
if FILE_LEN%128 == 0:
    FILE_PACK_NUM = hex((int)(FILE_LEN / 128))
else:
    FILE_PACK_NUM = hex((int)(FILE_LEN / 128) + 1)
FILE_PACK_NUM = str(FILE_PACK_NUM).replace("0x", "0000")[-4:]
FILE_LEN = hex(FILE_LEN).replace("0x", "00000000")[-8:]
FILE_CRC = "1a4c"
'''


class upgradeMakeFrame():
    def __init__(self):
        rf = UpgradeReadfile()
        self.FILE_MANUIDEN = "594C"
        self.FILE_DEV_TYPE = "03"
        self.flen = rf.flen
        self.packnum = rf.packnum
        self.FILE_LEN = hex(rf.flen).replace("0x", "00000000")[-8:]
        self.FILE_CRC = rf.fcrc
        self.FILE_PACK_NUM = hex(rf.packnum).replace("0x", "00000000")[-4:]
        self.flist = rf.flist


    def upgradeCheckVision(self):
        prtl = judgePrtl("LY_JSON")
        data = "04A00101"
        value = ""
        List = dict(zip([data], [value]))
        VList = []
        VList += ["Read"]
        VList += [List]
        senddata = prtl2Make(prtl, VList)
        return senddata


    def upgradeCheckPack(self, sindex):
        prtl = judgePrtl("LY_JSON")
        data = "04A00503"
        # value = "594C#03#03F4#000" + sindex  # 索引号从1开始      厂家标识 + 设备类型 + 总包数 + 当前包序号 + 单包数据单元
        value =self. FILE_MANUIDEN + "#" + self.FILE_DEV_TYPE + "#" + self.FILE_PACK_NUM + "#000" + sindex  # 索引号从1开始      厂家标识 + 设备类型 + 总包数 + 当前包序号 + 单包数据单元

        List = dict(zip([data], [value]))
        VList = []
        VList += ["Read"]
        VList += [List]
        senddata = prtl2Make(prtl, VList)
        return senddata


    def upgradeStart(self):
        prtl = judgePrtl("LY_JSON")
        data = "04A00502"
        # 产品类型 + 版本日期 + 软件版本 + 硬件版本 + 文件总长 + 总包数 + 包长度 + 文件CRC校验 + 升级模式字
        # value = "28210000#18121716#01010002#01000000#0001f9c1#03f4#80#75d3#0000"
        value = "28210000#19042515#01000099#01010000#" + self.FILE_LEN + "#" +  self.FILE_PACK_NUM + "#" + "80" + "#" +  self.FILE_CRC + "#" + "0000"
        List = dict(zip([data], [value]))
        VList = []
        VList += ["UpDate"]
        VList += [List]
        senddata = prtl2Make(prtl, VList)
        return senddata


    def upgradeSendFile(self, i):
        sindex = hex(i+1).replace("0x", "0000")[-4:]
        prtl = judgePrtl("LY_JSON")
        data = "04A00501"
        # print(value)
        value = pfun._strReverse(self.flist[i])
        # print(value)
        value = self.FILE_MANUIDEN + "#" + self.FILE_DEV_TYPE + "#" + self.FILE_PACK_NUM + "#" + sindex + "#" + value  # 字节倒序
        List = dict(zip([data], [value]))
        VList = []
        VList += ["UpDate"]
        VList += [List]
        senddata = prtl2Make(prtl, VList)
        return senddata
