#coding=utf-8
"""
@File:views.py
@author:zhanfei
@date: 2021/06/20
"""

import os
import json
from flask import request,Flask,jsonify,send_from_directory,make_response,Response,send_file
from werkzeug.utils import secure_filename
import paramiko
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from . import logmanage
import hashlib



from app.utils import notEmpty
#from app.models import TestTools
from app import db
from app.users.auth import auth_token
from sqlalchemy import or_,and_
#logmanage_app=Flask(__name__)




basedir=os.path.abspath(os.path.dirname(__file__))
@logmanage.route('/logmanage/search', methods=['POST'])
#@auth_token.login_required
def search():
    """
    搜索接口
    """
    requestParams = request.form
    project=requestParams.get('project')
    command=requestParams.get('command')
    if project=='' or command=='':
        return jsonify({'code':99991,'msg':"应用或者命令不能为空!"})
    if 'tail' in command:
        return jsonify({'code':99992,'msg':"暂不支持tail命令!"})

    #dalaran机器
    if project=="dalaran":

        #linux服务器信息
        host_ip1='115.29.188.47'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/dalaran/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='121.41.91.125'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/dalaran/logs;'+command)
        #获取指令结果
        result2=stdout2.read()


    #gateway-protal机器
    if project=="gateway-protal":

        #linux服务器信息
        host_ip1='47.97.30.174'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/gateway-protal/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='121.40.76.172'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/gateway-protal/logs;'+command)
        #获取指令结果
        result2=stdout2.read()



    #customer-center机器
    if project=="customer-center":

        #linux服务器信息
        host_ip1='47.97.30.174'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/customer-center/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='121.40.76.172'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/customer-center/logs;'+command)
        #获取指令结果
        result2=stdout2.read()


    #ironforge机器
    if project=="ironforge":

        #linux服务器信息
        host_ip1='47.97.30.174'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/ironforge/tomcat/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='121.40.76.172'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/ironforge/tomcat/logs;'+command)
        #获取指令结果
        result2=stdout2.read()

    #durotar机器
    if project=="durotar":

        #linux服务器信息
        host_ip1='47.97.30.174'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/durotar/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='115.29.188.47'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/durotar/logs;'+command)
        #获取指令结果
        result2=stdout2.read()

    #shattrath机器
    if project=="shattrath":

        #linux服务器信息
        host_ip1='115.29.188.47'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/shattrath/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='121.41.91.125'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/shattrath/logs;'+command)
        #获取指令结果
        result2=stdout2.read()


    #karazhan机器
    if project=="karazhan":

        #linux服务器信息
        host_ip1='115.29.188.47'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/karazhan/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='121.41.91.125'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/karazhan/logs;'+command)
        #获取指令结果
        result2=stdout2.read()



    #mulgore机器
    if project=="mulgore":

        #linux服务器信息
        host_ip1='47.97.30.174'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/mulgore/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='121.40.76.172'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/mulgore/logs;'+command)
        #获取指令结果
        result2=stdout2.read()
        

    #gateway-kunlai机器
    if project=="gateway-kunlai":

        #linux服务器信息
        host_ip1='115.29.188.47'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/gateway-kunlai/tomcat/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='121.41.91.125'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/gateway-kunlai/tomcat/logs;'+command)
        #获取指令结果
        result2=stdout2.read()




    #gateway-fourwinds机器
    if project=="gateway-fourwinds":

        #linux服务器信息
        host_ip1='47.97.158.32'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/gateway-fourwinds/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")



    #moonbrook机器
    if project=="moonbrook":

        #linux服务器信息
        host_ip1='47.96.146.194'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/moonbrook-core/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")


    #felwood机器
    if project=="felwood":

        #linux服务器信息
        host_ip1='114.55.94.42'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/felwood/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")



    #blackstone机器
    if project=="blackstone":

        #linux服务器信息
        host_ip1='114.55.94.42'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/blackstone/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")


    #maelstrom机器
    if project=="maelstrom":

        #linux服务器信息
        host_ip1='114.55.94.42'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/maelstrom/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")

    #m44机器
    if project=="m44":

        #linux服务器信息
        host_ip1='114.55.94.42'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/m44/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")

    #zh-message-center机器
    if project=="zh-message-center":

        #linux服务器信息
        host_ip1='114.55.57.207'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/zh-message-center/logs;'+command)
        #获取指令结果
        result1=stdout1.read()

        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")


    #sms-center机器
    if project=="sms-center":

        #linux服务器信息
        host_ip1='121.41.35.169'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/sms-center/tomcat/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")


    #noahark机器
    if project=="noahark":

        #linux服务器信息
        host_ip1='121.40.100.128'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/noahark/tomcat/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")

    #maievshadowsong机器
    if project=="maievshadowsong":

        #linux服务器信息
        host_ip1='118.178.59.155'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/maievshadowsong/logs;'+command)
        #获取指令结果
        result1=stdout1.read()

        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")


    #storm机器
    if project=="storm":

        #linux服务器信息
        host_ip1='120.26.211.78'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/storm/logs;'+command)
        #获取指令结果
        result1=stdout1.read()

        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")


    #contract机器
    if project=="contract":

        #linux服务器信息
        host_ip1='114.55.57.207'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/contract/logs;'+command)
        #获取指令结果
        result1=stdout1.read()


        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")

    #wetlands机器
    if project=="wetlands":

        #linux服务器信息
        host_ip1='121.40.100.128'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/wetlands/logs;'+command)
        #获取指令结果
        result1=stdout1.read()

        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")



    #calypso机器
    if project=="calypso":

        #linux服务器信息
        host_ip1='47.97.158.32'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/calypso/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='47.96.146.194'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/calypso/logs;'+command)
        #获取指令结果
        result2=stdout2.read()



    #inn机器
    if project=="inn":

        #linux服务器信息
        host_ip1='47.97.158.32'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/inn/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='47.96.146.194'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/inn/logs;'+command)
        #获取指令结果
        result2=stdout2.read()



    #sentryward机器
    if project=="sentryward":

        #linux服务器信息
        host_ip1='121.40.130.246'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/sentryward/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='120.26.92.111'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/sentryward/logs;'+command)
        #获取指令结果
        result2=stdout2.read()


    #data-center机器
    if project=="data-center":

        #linux服务器信息
        host_ip1='120.26.228.101'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/data-center/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='114.55.219.185'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/data-center/logs;'+command)
        #获取指令结果
        result2=stdout2.read()


    #wakanda-home机器
    if project=="wakanda-home":

        #linux服务器信息
        host_ip1='121.40.130.246'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/wakanda-home/logs;'+command)
        #获取指令结果
        result1=stdout1.read()



        #linux服务器信息
        host_ip2='120.26.92.111'
        host_username2='readonly'
        host_password2='readonly'
        #创建SSH对象
        ssh2=paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh2.connect(hostname=host_ip2,port=22,username=host_username2,password=host_password2)
        #执行命令
        stdin2,stdout2,stderr2=ssh2.exec_command('cd /home/wakanda-home/logs;'+command)
        #获取指令结果
        result2=stdout2.read()



    #wakanda-flink-statistic-core机器
    if project=="wakanda-flink-statistic-core":

        #linux服务器信息
        host_ip1='47.111.135.181'
        host_username1='readonly'
        host_password1='readonly'
        #创建SSH对象
        ssh1=paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #连接服务器
        ssh1.connect(hostname=host_ip1,port=22,username=host_username1,password=host_password1)
        #执行命令
        stdin1,stdout1,stderr1=ssh1.exec_command('cd /home/wakanda-flink-statistic-core/logs;'+command)
        #获取指令结果
        result1=stdout1.read()

        #linux服务器信息
        host_ip2='---'
        result2=bytes('---',encoding="utf8")



    #写入文件
    try:
        write_file1=open(basedir+'\log1.txt',mode='w',encoding='utf-8-sig')
        write_file1.write(bytes.decode(result1))
        write_file1.close()

        write_file2=open(basedir+'\log2.txt',mode='w',encoding='utf-8-sig')
        write_file2.write(bytes.decode(result2))
        write_file2.close()
    except IOError as e:
        return jsonify({'code':99999,'msg':"保存日志失败!"})

        
    #读取文件给前端
    data=[]
    try:
        read_file1=open(basedir+'\log1.txt','r',encoding='utf-8-sig').read()
        read_file2=open(basedir+'\log2.txt','r',encoding='utf-8-sig').read()
    except OSError as reason:
        return jsonify({'code':99999,'msg':"读取日志失败!"})
    data.append({"ip":host_ip1,"logcontent":read_file1})
    data.append({"ip":host_ip2,"logcontent":read_file2})
    return jsonify({'code':10000,'msg': 'Success','data':data})

    #else:
        #return jsonify({'code':99999,'msg': '失败','data':{}})
        
        



    


    

