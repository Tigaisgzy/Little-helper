#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 15/7/2024 下午8:40
# @Author : G5116

import requests, time, threading, os, sys, random
from concurrent.futures import ThreadPoolExecutor, as_completed

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到 sys.path
sys.path.append(project_root)
from utils import email_sender


# 获取已关注超话列表信息（基于真实API机制）
def get_super_info_list():
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    
    all_super_info_list = []
    seen_ids = set()  # 用于去重（防止意外重复）
    page = 1
    max_page = None
    total_number = None
    
    while True:
        # 使用标准的page参数
        url = f'https://weibo.com/ajax/profile/topicContent?tabid=231093_-_chaohua&page={page}'
        
        try:
            response = requests.get(url, cookies=cookies, headers=headers, timeout=10)
            
            # 检查HTTP状态
            if response.status_code != 200:
                if page == 1:
                    print(f'HTTP错误: {response.status_code}')
                    email_sender.send_QQ_email_plain('微博超话签到失败！HTTP请求失败')
                    exit(0)
                else:
                    print(f'第{page}页HTTP错误，停止获取')
                    break
            
            # 检查cookie是否失效
            if 'url' in response.text:
                print('cookie失效，请重新获取')
                email_sender.send_QQ_email_plain('微博超话签到失败！cookie失效，请更新')
                exit(0)
            
            data = response.json()
            
            # 检查API响应状态
            if data.get('ok') != 1:
                print(f'API响应错误: {data}')
                if page == 1:
                    exit(0)
                else:
                    break
            
            # 检查数据结构
            if 'data' not in data:
                print('响应数据结构异常')
                break
                
            data_content = data['data']
            super_list = data_content.get('list', [])
            
            # 获取分页信息（第一页时）
            if page == 1:
                max_page = data_content.get('max_page', 1)
                total_number = data_content.get('total_number', 0)
                print(f'总共{total_number}个超话，共{max_page}页')
            
            # 检查是否超出最大页数
            if max_page and page > max_page:
                print(f'已达到最大页数{max_page}，停止获取')
                break
            
            # 检查当前页是否有数据
            if not super_list:
                print(f'第{page}页无数据，已获取完毕')
                break
            
            # 处理当前页的超话数据
            page_super_info_list = []
            new_items_count = 0
            
            for super in super_list:
                try:
                    super_id = str(super['link'].split('/')[-1])
                    super_title = str(super['title'])
                    
                    # 去重检查（虽然API应该不会重复，但保险起见）
                    if super_id not in seen_ids:
                        seen_ids.add(super_id)
                        super_info = {
                            'name': super_title,
                            'id': super_id
                        }
                        page_super_info_list.append(super_info)
                        new_items_count += 1
                except (KeyError, AttributeError, IndexError) as e:
                    print(f"解析超话数据出错: {e}")
                    continue
            
            all_super_info_list.extend(page_super_info_list)
            print(f'第{page}页获取到{len(page_super_info_list)}个超话')
            
            # 如果这是最后一页，停止
            if max_page and page >= max_page:
                print(f'已完成所有{max_page}页的获取')
                break
            
            page += 1
            time.sleep(random.uniform(0.5, 1.5))  # 添加延迟避免请求过快
            
        except requests.exceptions.Timeout:
            print(f'第{page}页请求超时')
            if page == 1:
                print('首页请求超时，请检查网络')
                exit(0)
            break
        except requests.exceptions.RequestException as e:
            print(f'第{page}页网络请求失败: {e}')
            if page == 1:
                exit(0)
            break
        except Exception as e:
            print(f'第{page}页数据处理失败: {e}')
            if page == 1:
                exit(0)
            break
    
    # 验证获取结果
    actual_count = len(all_super_info_list)
    print(f'实际获取到{actual_count}个超话')
    
    if total_number and actual_count != total_number:
        print(f'警告：获取数量({actual_count})与API返回的总数({total_number})不匹配')
    
    # 数据验证
    if actual_count == 0:
        print('警告：未获取到任何超话，可能Cookie已失效')
        email_sender.send_QQ_email_plain('微博超话获取失败，未获取到任何超话')
        exit(0)
    
    return all_super_info_list


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


# 开始签到（增强版，支持重试）
def start_sign(super_info, lock, results, retry_count=3):
    result = ''
    failure_reason = ''
    
    # 添加随机初始延迟
    time.sleep(random.uniform(0.3, 1.2))
    
    for attempt in range(retry_count):
        try:
            data = build_params(super_info)
            headers = {
                'user-agent': data['ua'],
            }
            
            response = requests.get(
                'https://weibo.com/p/aj/general/button',
                cookies=cookies,
                headers=headers,
                params=data,
                timeout=10
            )
            
            # 检查响应状态
            if response.status_code != 200:
                failure_reason = f'HTTP状态码{response.status_code}'
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(2, 4))
                    continue
                else:
                    result = super_info['name'] + f'超话签到失败 (最后错误: {failure_reason})\n'
                    break
            
            response_data = response.json()
            print(response_data)
            
            if response_data['code'] == '100000':
                result = super_info['name'] + '超话签到成功\n'
                break
            elif response_data['code'] == 382004:
                result = super_info['name'] + '超话今天已经签到过了\n'
                break
            else:
                failure_reason = f'错误码{response_data["code"]}'
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(2, 4))
                    continue
                else:
                    result = super_info['name'] + f'超话签到失败 (最后错误: {failure_reason})\n'
                    
        except requests.exceptions.Timeout:
            failure_reason = '请求超时'
            if attempt < retry_count - 1:
                time.sleep(random.uniform(3, 5))
                continue
            else:
                result = super_info['name'] + f'超话签到失败 (最后错误: {failure_reason})\n'
                
        except requests.exceptions.RequestException as e:
            failure_reason = f'网络错误: {str(e)}'
            if attempt < retry_count - 1:
                time.sleep(random.uniform(3, 5))
                continue
            else:
                result = super_info['name'] + f'超话签到失败 (最后错误: {failure_reason})\n'
                
        except Exception as e:
            failure_reason = f'未知错误: {str(e)}'
            if attempt < retry_count - 1:
                time.sleep(random.uniform(2, 4))
                continue
            else:
                result = super_info['name'] + f'超话签到失败 (最后错误: {failure_reason})\n'
    
    with lock:
        results.append(result)
    return result


def main():
    super_info_list = get_super_info_list()
    results = []
    completed_count = [0]
    lock = threading.Lock()
    start_time = time.time()
    max_workers = 6  # 降低并发数量，避免请求过于频繁
    
    def show_progress():
        """显示进度的函数"""
        while completed_count[0] < len(super_info_list):
            time.sleep(3)
            with lock:
                current_completed = completed_count[0]
                current_success = len([msg for msg in results if '签到成功' in msg or '已经签到过了' in msg])
                progress = (current_completed / len(super_info_list)) * 100
                print(f"进度: {current_completed}/{len(super_info_list)} ({progress:.1f}%) - 成功: {current_success}")

    print(f"开始超话签到，共{len(super_info_list)}个超话...")
    
    # 启动进度显示线程
    progress_thread = threading.Thread(target=show_progress, daemon=True)
    progress_thread.start()
    
    def sign_with_progress(super_info):
        result = start_sign(super_info, lock, results)
        with lock:
            completed_count[0] += 1
        return result
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(sign_with_progress, super_info) for super_info in super_info_list]
        for future in as_completed(futures):
            future.result()
    
    print("签到完成！")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 统计签到结果
    success_messages = [msg for msg in results if '签到成功' in msg or '已经签到过了' in msg]
    success_rate = len(success_messages) / len(super_info_list) * 100 if super_info_list else 0
    
    # 生成统计信息
    summary = f"总共{len(super_info_list)}个超话，成功{len(success_messages)}个，成功率{success_rate:.1f}%，总耗时：{total_time:.2f}秒\n"
    
    print(f"\n{summary.strip()}")
    results.append(summary)
    
    # 发送邮件
    final_result = ''.join(results)
    email_sender.send_QQ_email_plain(final_result)


if __name__ == '__main__':
    cookies = {
        'SUB': os.getenv('SUB_TOKEN'),
    }
    main()
