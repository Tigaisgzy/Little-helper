#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 27/4/2024 下午9:55
# @Author : G5116
import re
import execjs
import json
import requests
import smtplib
from email.mime.text import MIMEText
import os
import sys
from datetime import *

email_address = os.getenv('EMAIL_ADDRESS')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
token = os.getenv('TOKEN')
with open('g5116.js', 'r', encoding='utf-8') as f:
    js = f.read()
ctx = execjs.compile(js)


def send_QQ_email_plain(receiver, content):
    sender = user = '1781259604@qq.com'  # 发送方的邮箱账号
    passwd = 'tffenmnkqsveccdj'  # 授权码

    # receiver 接收方的邮箱账号，不一定是QQ邮箱
    # 获取当前时间并格式化为 "年-月-日 时:分:秒" 格式
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 纯文本内容
    msg = MIMEText(f'{current_time}\n结果：{content}', 'plain', 'utf-8')

    # 正确设置 From 字段为发送方的邮箱
    msg['From'] = f'{sender}'
    msg['To'] = receiver
    msg['Subject'] = '自动结果'  # 点开详情后的标题

    try:
        # 建立 SMTP 、SSL 的连接，连接发送方的邮箱服务器
        smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)

        # 登录发送方的邮箱账号
        smtp.login(user, passwd)

        # 发送邮件：发送方，接收方，发送的内容
        smtp.sendmail(sender, receiver, msg.as_string())

        print('邮件发送成功')

        smtp.quit()
    except Exception as e:
        print(e)
        print('发送邮件失败')


def init():
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    return requests.Session()


def getCode(image, token):
    # 自动打码 注册地址 免费300积分
    # https://console.jfbym.com/register/TG66434
    url = "http://api.jfbym.com/api/YmServer/customApi"
    payload = {
        "image": image,
        "token": str(token),
        "type": "10110"
    }
    resp = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
    result = resp.json()["data"]["data"]
    result = result.replace('o', '0').replace('l', '1').replace('O', '0')
    return eval(result[:-1])


def login(session, username, password):
    params = {'uid': ''}
    yzm_url = 'https://ids.gzist.edu.cn/lyuapServer/kaptcha'
    response = session.get(yzm_url, params=params)
    uid = response.json()['uid']
    yzm_base64 = re.search('base64,(.*)', response.json()['content']).group(1)
    yzm = getCode(yzm_base64, token)
    psw = ctx.call('G5116', username, password, '')
    data = {
        'username': username,
        'password': str(psw),
        'service': 'https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do',
        'loginType': '',
        'id': uid,
        'code': str(yzm),
    }
    response = session.post('https://ids.gzist.edu.cn/lyuapServer/v1/tickets', data=data)
    if response.json()['data']['code'] == 'NOUSER':
        result = '账号不存在'
        send_QQ_email_plain(email_address, result)
        sys.exit(1)
    elif response.json()['data']['code'] == 'PASSERROR':
        result = '密码错误'
        send_QQ_email_plain(email_address, result)
        sys.exit(1)
    elif response.json()['data']['code'] == 'CODEFALSE':
        result = '验证码错误'
        send_QQ_email_plain(email_address, result)
        sys.exit(1)
    else:
        return response.json()['ticket']


def UpdateCookie(session, ticket):
    params = {'ticket': ticket}
    response = session.get(
        'https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do',
        params=params)
    session.cookies = response.cookies


def doWork(session):
    data = {
        'data': '{"APPID":"6390414391613368","APPNAME":"swmqdzsapp"}'
    }

    response = session.post(
        'https://xsfw.gzist.edu.cn/xsfw/sys/swpubapp/MobileCommon/getSelRoleConfig.do',
        cookies=session.cookies,
        data=data,
    )
    _WEU = response.cookies.get('_WEU')
    cookies = {
        '_WEU': _WEU
    }
    data = {
        'data': '{"SFFWN":"1","DDDM":"134D3343A40D51AFE0630717000A7549","DDMC":"广州理工学院白云区","QDJD":113.46617498988796,"QDWD":23.263957044502487,"RWBH":"16FC8C91BCDDEC67E0630717000A97E1","QDPL":"2"}',
    }
    response = session.post(
        'https://xsfw.gzist.edu.cn/xsfw/sys/swmqdzsapp/MobileJrqdController/doSignIn.do',
        cookies=cookies,
        data=data,
    )
    global result
    try:
        if response.json()['msg'] == '成功':
            result = response.json()['data']['prompt']
            print(result)
            return result
    except:
        result = '签到失败'
        return result


def main():
    session = init()
    ticket = login(session, username, password)
    UpdateCookie(session, ticket)
    res = doWork(session)
    send_QQ_email_plain(email_address, res)


if __name__ == '__main__':
    main()
