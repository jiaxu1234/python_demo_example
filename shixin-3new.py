#coding:utf-8
import requests
from lxml import etree
import os
import re
import json
import pymysql
import time



def make_urls():
    name_list = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
                 '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
                 '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦', '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳',
                 '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤', '滕', '殷', '罗', '毕', '郝', '邬', '安', '常',
                 '乐', '于', '时', '傅', '皮', '卞', '齐', '康', '伍', '余', '元', '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹',
                 '姚', '邵', '堪', '汪', '祁', '毛', '禹', '狄', '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞',
                 '熊', '纪', '舒', '屈', '项', '祝', '董', '梁', '公司', '厂']
    
    url_list = []
    for i in name_list:
        for page_no in range(1,50):
            # url = "https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?resource_id=6899&query=%E8%80%81%E8%B5%96&" + "pn=%s"% page_no + "&rn=10&format=json"
            url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?resource_id=6899&query=%E5%A4%B1%E4%BF%A1%E8%A2%AB%E6%89%A7%E8%A1%8C%E4%BA%BA%E5%90%8D%E5%8D%95' + '&iname=%s'%str(i) + '&areaName=&pn=%s'%page_no + '&rn=10&ie=utf-8&oe=utf-8&format=json&t=1483086921368&_=1483085253724'
            url_list.append(url)
            # print ('******', url)
    return url_list


def get_info():
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'passwd': 'root',
        'port': 3306,
        'db': 'test',
        'charset': 'utf8'
    }
    db = pymysql.connect(host=db_config['host'], user=db_config['user'], passwd=db_config['passwd'],
                         port=db_config['port'], charset=db_config['charset'])
    url_list = make_urls()
    for url in url_list:
        print (url)
        response = requests.get(url,headers = { 'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20' })
        text = response.text
        text = json.loads(text)
        data = text.get("data",[])[0].get("result",[])
        for item in data:
            name = item.get("iname","")
            id = item.get("cardNum","")
            courtName = item.get("courtName", "")
            areaName = item.get("areaName", "")
            caseCode = item.get("caseCode", "")
            duty = item.get("duty", "")
            performance = item.get("performance", "")
            disruptTypeName = item.get("disruptTypeName", "")
            time1 = item.get("publishDate", "")
            ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            post = {

                'name': name,
                'id': id,
                'courtName': courtName,
                'areaName': areaName,
                'caseCode': caseCode,
                'duty': duty,
                'performance': performance,
                'disruptTypeName': disruptTypeName,
                'time': time1,
                'ctime' : ctime
            }
            print (post)


            sql = "insert into shixin(name,id,courtName,areaName,caseCode,duty,performance,disruptTypeName,time,ctime) values ('%s',  '%s',  '%s',  '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (name, id, courtName, areaName, caseCode, duty, performance, disruptTypeName, time1, ctime)
            # print (sql)
            cursor = db.cursor()
            cursor.execute("USE %s" % db_config['db'])
            try:
                # 执行SQL语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except Exception as i:
                print ('to mysql failed', i)
                # 发生错误时回滚
                db.rollback()

            # 关闭数据库连接
            # db.close()

if __name__ == '__main__':
    get_info()
