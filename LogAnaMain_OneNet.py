wsnew = wbnew.add_sheet('sheet');
wsnew.write(0, 0, 'name');
wsnew.write(0, 1, 'imei');
wsnew.write(0, 2, 'Addr');
wsnew.write(0, 3, 'Len');
wsnew.write(0, 4, 'Cmd');
wsnew.write(0, 5, 'SN');
wsnew.write(0, 6, 'DataTime');
wsnew.write(0, 7, 'CRC');
wsnew.write(0, 8, 'DataValue');
# con = ConnManage()
# path = 'F:\\Work\\NLY1502\\Log\\ds - cmcc -2020-4-13.log'
# path = r'F:\Source\Python\log\ds.log'
# path = r'D:\\Program Files\\大傻串口助手\\Log\\data-2020-610.txt'
# path = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州 2020-11-8.txt'
path = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州 2020-11-9.txt'
imeipath = r'F:\\Work\\TLY2821\\NB现场项目\\兰州移动\\兰州现场运行情况2020-11-3.xls'
imeiList = openImeiExcel(imeipath, 0, 1)
f = open(path, encoding='utf-8')
readfile(f, imeiList, wsnew)
# 保存关系表
wbnew.save(path + '.xls');