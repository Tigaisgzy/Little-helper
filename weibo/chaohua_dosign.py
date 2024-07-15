#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 15/7/2024 下午8:40
# @Author : G5116

import requests, time, threading, os, sys

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到 sys.path
sys.path.append(project_root)
from utils import email_sender


# 获取已关注超话列表信息
def get_super_info_list():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }
    response = requests.get('https://weibo.com/ajax/profile/topicContent?tabid=231093_-_chaohua', cookies=cookies,
                            headers=headers)
    super_list = response.json()['data']['list']
    super_info_list = []
    for super in super_list:
        super_id = str(super['link'].split('/')[-1])
        super_title = str(super['title'])
        super_info = {
            'name': super_title,
            'id': super_id
        }
        super_info_list.append(super_info)
    return super_info_list


# 读取固定参数文件
def load_params():
    params = {}
    with open('./fixed_params', 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split('=')
            params[key] = value
    return params


# 构建请求参数
def build_params(super_info):
    params = load_params()
    timestamp = int(time.time() * 1000)
    params['__rnd'] = str(timestamp)
    params['id'] = str(super_info['id'])
    return params


# 开始签到
def start_sign(super_info, lock, results):
    data = build_params(super_info)
    headers = {
        'user-agent': data['ua'],
    }
    response = requests.get(
        'https://weibo.com/p/aj/general/button',
        cookies=cookies,
        headers=headers,
        params=data
    )
    result = ''
    if response.json()['code'] == 100000:
        result += super_info['name'] + '超话' + '签到成功\n'
    elif response.json()['code'] == 382004:
        result += super_info['name'] + '超话' + '今天已经签到过了\n'
    else:
        result += super_info['name'] + '超话' + '签到失败\n'
    with lock:
        results.append(result)
    return result


def main():
    super_info_list = get_super_info_list()
    threads = []
    results = []
    lock = threading.Lock()
    for super_info in super_info_list:
        thread = threading.Thread(target=start_sign, args=(super_info, lock, results))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 汇总结果并发送邮件
    final_result = ''.join(results)
    email_sender.send_QQ_email_plain(final_result)


if __name__ == '__main__':
    cookies = {
        'SUB': os.getenv('SUB_TOKEN'),
    }
    main()
