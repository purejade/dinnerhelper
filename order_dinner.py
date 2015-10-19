# -*- coding: utf-8 -*-
import requests
import re
import codecs
import datetime
import random
import os
import time
# import signal
import ConfigParser
from  daemon import Daemon

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#WARNING： 注意编码，统一utf-8.注意文件所在的文件，用cur_file_dir来获取。注意中英文字符
#TODO  先启动一个线程，得到菜谱，然后再启动另外一个线程，让用户选择配置菜谱。
#TODO 生成守护进程，然后再次运行



headers = {
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    "host" : "gourmet.lain.bdp.cc",
    "Referer":"http://gourmet.lain.bdp.cc/",
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate",
    "Accept-Language":"en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
}

def cur_file_dir():
     #获取脚本路径
     path = sys.path[0]
     #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)

errfile = codecs.open(cur_file_dir() + os.sep + "errMsg.txt", "a+", "utf-8")

def load_config(configFile):
    cf = ConfigParser.ConfigParser()
    cf.read(configFile)
    try:
        userName = cf.get("username", "username")
        orderTime = cf.get("ordertime", "ordertime")
        config={}
        config["username"] = userName
        config["ordertime"] = orderTime
        return config
    except Exception :
        errfile.write("err in load_config" + "\n")
        print "err in load_config"
        return


def order_dinner():
    ROOTDIR = cur_file_dir() + os.sep #cur_file_dir
    config = load_config(ROOTDIR + "config.txt")
    session = requests.Session()
    session.headers = headers
    url = "http://gourmet.lain.bdp.cc/"
    res =  session.get(url)
    content = res.content
    if len(content) == 0:
        errfile.write("网络不通，请人工访问http://gourmet.lain.bdp.cc/" + "\n")
        print "网络不通，请人工访问http://gourmet.lain.bdp.cc/"
        return
    patternAction = r'data-action="(.*?)"'
    patternName = r'data-meal-name="(.*?)"'
    patternState = r'data-state="(.*?)"'
    orders = re.findall(patternAction, content)
    names = re.findall(patternName, content)
    states = re.findall(patternState, content)
    postUrl = "http://gourmet.lain.bdp.cc/login"
    username = config["username"]
    if len(username) == 0:
        errfile.write("请在config.txt中配置用户名" + "\n")
        print "请在config.txt中配置用户名"
        exit(-1)
    data = {
        "name" : username
    }
    res = session.post(postUrl, data=data)
    if username in res.content:
        print "登陆成功"
    else:
        errfile.write("登陆失败，请检查用户名，或者人工登陆http://gourmet.lain.bdp.cc/" + "\n")
        print "登陆失败，请检查用户名，或者人工登陆http://gourmet.lain.bdp.cc/"
        return
    availableMap = {}
    for index, state in enumerate(states):
        if state == '1':
            availableMap[names[index]] = index
    availableFoods = codecs.open(ROOTDIR+'菜单.txt', "wb", "utf-8")
    for name in names:
        availableFoods.write(name)
        availableFoods.write('\n')
    availableFoods.close()

    favFoods = codecs.open(ROOTDIR+'本周菜单.txt', 'rb', "utf-8")
    favFoodMap = {}
    for index, food in enumerate(favFoods):
        if index == 0:
            continue
        food = food.split(':')[1].strip()
        favFoodMap[index - 1] = food

    dayOfWeek = datetime.date.today().weekday()

    availableFoodLen = len(availableMap.keys())
    chooseIndex = random.randint(0, availableFoodLen) #默认随机，如果指定了当日菜谱，则可以选择
    if  availableMap.has_key(favFoodMap[dayOfWeek]):
        chooseIndex = availableMap[favFoodMap[dayOfWeek]]

    # print orders[chooseIndex], names[chooseIndex]
    log = open(ROOTDIR + 'logfile', "a+")
    log.write(orders[chooseIndex]+'\t' + names[chooseIndex] + '\n')
     #GOURMET_SESS=jiayuwang2
    
    orderUrl = "http://gourmet.lain.bdp.cc" + orders[chooseIndex]
    session.headers["X-Requested-With"] = "XMLHttpRequest"
    res = session.post(orderUrl)
    if "orderSuccess" in res.content:
        print "order ok"
        print "亲，今天翻了" + names[chooseIndex]
    elif "orderExist" in res.content:
        errfile.write("已经订购成功了，请登录http://gourmet.lain.bdp.cc/确认" + "\n")
        print "已经订购成功了，请登录http://gourmet.lain.bdp.cc/确认"
    else:
        errfile.write("order has some problems" + "\n")
        print "order has some problems"
        print "connnect the jiayuwang2@creditease.cn"

# def reload(a,b):
#   log=open(logfile,'a')
#   log.write('Daemon reload at %s\n'%(time.strftime('%Y:%m:%d',time.localtime(time.time()))))
#   log.close()

class OrderDinnerDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(2)
            order_dinner()

if __name__ == '__main__':
    order_dinner()

    # daemon = OrderDinnerDaemon('/tmp/daemon-order-dinner.pid')
    # if len(sys.argv) == 2:
    #     if 'start' == sys.argv[1]:
    #         daemon.start()
    #     elif 'stop' == sys.argv[1]:
    #         daemon.stop()
    #     elif 'restart' == sys.argv[1]:
    #         daemon.restart()
    #     else:
    #         print "Unknown command"
    #         sys.exit(2)
    #     sys.exit(0)
    # else:
    #     print "usage: %s staropent|stop|restart" % sys.argv[0]
    #     sys.exit(2)

    # logfile="/tmp/order_dinner_daemon.log"
    # pid = os.fork()
    # #exit parent process
    # if pid: exit()
    #
    # #get the pid of subprocess
    # daeid = os.getpid()
    #
    # os.setsid()
    # os.umask(0)
    # os.chdir("/")
    #
    # #redirection file descriptor
    # fd = open("/dev/null", "a+")
    # os.dup2(fd.fileno(), 0)
    # os.dup2(fd.fileno(), 1)
    # os.dup2(fd.fileno(), 2)
    #
    # fd.close()
    #
    # log = open(logfile, 'a')
    # log.write('Daemon start up at %s\n' % time.strftime('%Y:%m:%d', time.localtime(time.time())))
    #
    # log.close()
    #
    # while True:
    #     signal.signal(signal.SIGHUP, reload)
    #     time.sleep(2)



