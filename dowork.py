#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 27/4/2024 下午9:55
# @Author : G5116
import re
import execjs
import json
import requests

with open('g5116.js', 'r', encoding='utf-8') as f:
    js = f.read()
ctx = execjs.compile(js)


def init():
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    return requests.Session()


def getCode(image):
    # 自动打码 注册地址 免费300积分
    # https://console.jfbym.com/register/TG66434
    url = "http://api.jfbym.com/api/YmServer/customApi"
    payload = {
        "image": image,
        "token": "VglEBCVb7uEmFh5EczocSCaGLCedNwpVlmF2sgmjCQk",
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
    yzm = getCode(yzm_base64)
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
    if response.json()['msg'] == '成功':
        print('签到成功')


if __name__ == '__main__':
    session = init()
    ticket = login(session, '20220407430746', '511677gzy')
    UpdateCookie(session, ticket)
    doWork(session)
