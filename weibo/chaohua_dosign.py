#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 15/7/2024 下午8:40
# @Author : G5116

import requests, time, threading, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到 sys.path
sys.path.append(project_root)
from utils import email_sender


# 获取已关注超话列表信息
def get_super_info_list(page):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }
    response = requests.get(f'https://weibo.com/ajax/profile/topicContent?tabid=231093_-_chaohua&page={page}',
                            cookies=cookies,
                            headers=headers)
    if 'url' in response.text:
        print('cookie失效，请重新获取')
        email_sender.send_QQ_email_plain('微博超话签到失败！cookie失效，请更新')
        exit(0)
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
    file_path = os.path.join(current_dir, 'ch_fixed_params')
    with open(file_path, 'r', encoding='utf-8') as file:
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
    if response.json()['code'] == '100000':
        result += super_info['name'] + '超话' + '签到成功\n'
    elif response.json()['code'] == 382004:
        result += super_info['name'] + '超话' + '今天已经签到过了\n'
    else:
        result += super_info['name'] + '超话' + '签到失败\n'
    with lock:
        results.append(result)
    return result


def main():
    super_info_list = []
    page = 1
    while True:
        res = get_super_info_list(page)
        if len(res) == 0:
            break
        super_info_list += res
        page += 1
    results = []
    lock = threading.Lock()
    start_time = time.time()
    max_workers = 10  # 控制最大线程数量
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(start_sign, super_info, lock, results) for super_info in super_info_list]
        for future in as_completed(futures):
            future.result()
    end_time = time.time()
    # 汇总结果并发送邮件
    total_time = end_time - start_time
    results.append(f"{len(super_info_list)}个超话签到完成总耗时：{total_time:.2f}秒")
    final_result = ''.join(results)
    email_sender.send_QQ_email_plain(final_result)


if __name__ == '__main__':
    cookies = {
        'SUB': os.getenv('SUB_TOKEN'),
    }
    main()
