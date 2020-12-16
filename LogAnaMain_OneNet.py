import sys
from JsonLog import DealLog
import os
import xlwt
import xlrd

unexcpetlist = ['.log', '.log.1', '.log.2', '.log.3', '.log.4', '.log.5', '.log.6', '.log.7', '.log.8', '.log.9', '.log.10']


def savejson2excel(n, dt, jsonstr, wsnew):
    try:
        wsnew.write(n, 0, dt['name'])
        wsnew.write(n, 1, dt['imei'])
        wsnew.write(n, 2, dt['addr'])
        wsnew.write(n, 3, jsonstr['Len'])
        wsnew.write(n, 4, jsonstr['Cmd'])
        wsnew.write(n, 5, jsonstr['SN'])
        wsnew.write(n, 6, jsonstr['DataTime'])
        wsnew.write(n, 7, jsonstr['CRC'])

        i = 0
        for key, values in jsonstr['DataValue'].items():
            wsnew.write(n, 8 + i * 2, key)
            wsnew.write(n, 9 + i * 2, values)
            i += 1
    except:
        pass

# 读取文件，搜索关键信息
def readfile(f, imeiList, wsnew, exceldate=None):
    try:
        lines = f.readlines()
        n = -1

        # 1 查找 IP 和 端口号
        for line in lines:
            # 查找IMEI
            d = line.split(', ', 2)
            if len(d) < 2:
                continue
            dImei = d[1].replace(' ', '')

            try:
                n = imeiList.index(dImei)
            except:
                continue

            # 查找json
            ip, port, jsonstr = DealLog.findjsonframe(line)
            if jsonstr != None and n >= 0:
                dt = {'name': '', 'imei': '', 'addr': ''}
                dt['imei'] = dImei
                dt['addr'] = jsonstr['Addr']
                if exceldate is not None:
                    if exceldate not in jsonstr['DataTime']:
                        continue
                savejson2excel(n, dt, jsonstr, wsnew)


    finally:
        f.close()
        print('读取记录条数:', n)


def openImeiExcel(path, sheetNum, colNum):
    wb = xlrd.open_workbook(path)

    # 获得工作表的方法1
    sh = wb.sheet_by_index(sheetNum)

    imei = sh.col_values(colNum)

    return imei

def newexcel(exceldate):
    # 新建excel表格
    wbnew = xlwt.Workbook()
    wsnew = wbnew.add_sheet(exceldate)

    wsnew.write(0, 0, 'name')
    wsnew.write(0, 1, 'imei')
    wsnew.write(0, 2, 'Addr')
    wsnew.write(0, 3, 'Len')
    wsnew.write(0, 4, 'Cmd')
    wsnew.write(0, 5, 'SN')
    wsnew.write(0, 6, 'DataTime')
    wsnew.write(0, 7, 'CRC')
    wsnew.write(0, 8, 'DataValue')
    return wbnew, wsnew

def excpetfile(file_name):
    for e in unexcpetlist:
        if e == file_name[-len(e):]:  # 筛选.log
            return 1
    return 0


if __name__ == '__main__':
    dirpath = r'F:\\Source\\Python\\OneNetApp'
    # path = r'D:\\Program Files\\大傻串口助手\\Log\\data-2020-610.txt'
    # path = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州 2020-11-8.txt'
    # path = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州 2020-11-9.txt'
    imeipath = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州移动OneNet设备注册ID(750台).xls'
    exceldate = '201215'

    p = os.walk(dirpath)

    imeiList = openImeiExcel(imeipath, 0, 2)

    wbnew, wsnew = newexcel(exceldate)

    for path, dir_list, file_list in p:
        for file_name in file_list:
            # 特殊文件不用处理
            if(excpetfile(file_name) == 1):
                fpath = path + '\\' +  file_name
                print(fpath)
                f = open(fpath, encoding='gbk') # utf-8 , gbk
                readfile(f, imeiList, wsnew, exceldate)


    # 保存关系表
    wbnew.save(dirpath + '\\' + exceldate + '.xls')
