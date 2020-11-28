import sys
from JsonLog import DealLog
from JsonLog.ConnManage import ConnManage
import xlwt
import xlrd


def savejson2excel(n, dt, jsonstr, wsnew):
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

# 读取文件，搜索关键信息
def readfile(f, imeiList, wsnew):
    try:
        lines = f.readlines()
        n = -1

        # 1 查找 IP 和 端口号
        for line in lines:
            # 查找IMEI
            d = line.split(',', 2)
            dImei = d[1].replace(' ', '')

            n = imeiList.index(dImei)

            # 查找json
            ip, port, jsonstr = DealLog.findjsonframe(line)
            if jsonstr != None and n >= 0:
                dt = {'name': '', 'imei': '', 'addr': ''}
                dt['imei'] = dImei
                dt['addr'] = jsonstr['Addr']
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

if __name__ == '__main__':
    # 新建excel表格
    wbnew = xlwt.Workbook();
    wsnew = wbnew.add_sheet('sheet');

    wsnew.write(0, 0, 'DeviceID');
    wsnew.write(0, 1, 'IMEI');
    wsnew.write(0, 2, 'Date');


    # con = ConnManage()
    # path = 'F:\\Work\\NLY1502\\Log\\ds - cmcc -2020-4-13.log'
    # path = r'F:\Source\Python\log\ds.log'
    # path = r'D:\\Program Files\\大傻串口助手\\Log\\data-2020-610.txt'
    # path = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州 2020-11-8.txt'
    path = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州移动九洲城 第四批次 2020-11-27.xls'
    imeipath = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州现场运行情况2020-11-3.xls'


    imeiList = openImeiExcel(imeipath, 0, 1)

    deviceListNew = openImeiExcel(path, 0, 0)
    imeiListNew = openImeiExcel(path, 0, 1)

    i = 1
    for n in imeiListNew[1:]:
        wsnew.write(i, 0, deviceListNew[i])
        wsnew.write(i, 1, imeiListNew[i])
        if n in imeiList:
            wsnew.write(i, 2, '2020-11-4')
        else:
            wsnew.write(i, 2, '2020-11-26')  # 868334034720064
        i+=1

    # 保存关系表
    wbnew.save(path + '.xls')
    print('ok!')
