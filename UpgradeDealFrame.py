import PublicLib.Protocol.ly_Json as jsonframe
import time
import PublicLib.public as pfun

def upgradeRecvDataToMap(index, bmapstr, self):
    bmapstr = pfun._strReverse(bmapstr)
    for i in range(0, len(bmapstr), 2):
        b = bmapstr[i:i + 2]
        n = int(b, 16)
        for j in range(8):
            if n & (1 << j):
                self.uplist["bmap"][index*512 + i * 4 + j] = 1
            else:
                self.uplist["bmap"][index*512 + i * 4 + j] = 0


def upgradeSendData(self):
    for i in range(len(self.uplist["bmap"])):
        if self.uplist["bmap"][i] != 1:
            # print(i, uplist["bmap"][i])
            self.uplist["bmap"][i] = 1
            return i
    return -1


def upgradeDataProc(recv, self):
    if isinstance(recv, dict):
        data = recv
    elif isinstance(recv, str):
        data = jsonframe.subStrToJson(recv)
        if "ip" and "port" in data:
            self.uplist["ip"] = data["ip"]
            self.uplist["port"] = data["port"]
            if "DataTime" not in data["recvData"]:
                return
        data = data["recvData"]
    else:
        return


    if "04A00503" in data["DataValue"]:
        if data["DataValue"]["04A00503"][13:17] == "0001":
            bstr = data["DataValue"]["04A00503"][18:]
            upgradeRecvDataToMap(0, bstr, self)
        elif data["DataValue"]["04A00503"][13:17] == "0002":
            bstr = data["DataValue"]["04A00503"][18:]
            upgradeRecvDataToMap(1, bstr, self)

def upgradeRecvProc(self):
    while 1:
        time.sleep(1)
        while not self.qRecv.empty():
            recv = self.qRecv.get()
            print(recv)
            if 'linkNum' not in recv:
                upgradeDataProc(recv, self)

def upgradeGetCurPackNum(self):
    for i in range(len(self.uplist["bmap"])):
        if self.uplist["bmap"][i] == 0:
            return i