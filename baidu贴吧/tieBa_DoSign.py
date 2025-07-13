import requests, re, json, os, sys, urllib.parse, time, threading, random
from datetime import datetime
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到 sys.path
sys.path.append(project_root)
from utils import email_sender


def get_count():
    all_name_list = []
    page = 1
    
    while True:
        timestamp_with_microseconds = int(datetime.now().timestamp() * 1000)
        params = {'v': str(timestamp_with_microseconds), 'pn': str(page)}
        response = requests.get('https://tieba.baidu.com/f/like/mylike', params=params, cookies=cookies, headers=headers)
        
        if len(response.text) <= 4932:
            if page == 1:
                email_sender.send_QQ_email_plain('获取贴吧列表失败，请更新cookie')
                exit()
            else:
                break
        
        tree = etree.HTML(response.text)
        time.sleep(1)
        tree_list = tree.xpath('//div[@class="forum_table"]/table/tr')
        
        if not tree_list or len(tree_list) <= 1:
            break
        
        count = len(tree_list) - 1
        
        page_name_list = []
        for i in range(1, count + 1):
            name_elements = tree_list[i].xpath('./td[1]/a/text()')
            if name_elements:
                page_name_list.append(name_elements[0])
        
        if not page_name_list:
            break
            
        all_name_list.extend(page_name_list)
        print(f'第{page}页获取到{len(page_name_list)}个贴吧')
        page += 1
        time.sleep(2)
    
    print(f'总共获取到{len(all_name_list)}个贴吧')
    
    # 简单的Cookie有效性检查
    if len(all_name_list) == 0:
        print('警告：未获取到任何贴吧，可能Cookie已失效')
        email_sender.send_QQ_email_plain('Cookie可能已失效，未获取到任何贴吧')
        exit()
    
    return all_name_list


def sign_thread(name, results, lock, success_count, retry_count=3):
    message = ''
    failure_reason = ''
    
    # 添加随机初始延迟
    time.sleep(random.uniform(0.5, 2.0))
    
    for attempt in range(retry_count):
        try:
            url_name = urllib.parse.quote(name)
            url = f'https://tieba.baidu.com/f?ie=utf-8&kw={url_name}&fr=search'
            
            # 添加超时设置
            response = requests.get(url, cookies=cookies, headers=headers, timeout=10)
            tree = etree.HTML(response.text)
            
            # 随机延迟
            time.sleep(random.uniform(1, 2))
            
            tbs_value = None
            
            # 方法1：从script标签获取PageData
            script_elements = tree.xpath('/html/head/script')
            for script in script_elements:
                if script.text:
                    tbs_data = re.search(r'var PageData = ({.*?});', script.text, re.DOTALL)
                    if tbs_data:
                        try:
                            cleaned_json = tbs_data.group(1).replace("'", '"')
                            page_data_dict = json.loads(cleaned_json)
                            tbs_value = page_data_dict.get('tbs')
                            break
                        except:
                            continue
            
            # 方法2：从所有script标签中搜索tbs
            if not tbs_value:
                all_scripts = tree.xpath('//script')
                for script in all_scripts:
                    if script.text:
                        tbs_match = re.search(r'"tbs":"([^"]+)"', script.text)
                        if not tbs_match:
                            tbs_match = re.search(r"'tbs':'([^']+)'", script.text)
                        if tbs_match:
                            tbs_value = tbs_match.group(1)
                            break
            
            # 方法3：从页面内容直接搜索
            if not tbs_value:
                tbs_match = re.search(r'tbs["\']?\s*[:=]\s*["\']([^"\']+)["\']', response.text)
                if tbs_match:
                    tbs_value = tbs_match.group(1)
            
            if not tbs_value:
                failure_reason = '无法获取tbs值'
                message = f'{name}吧签到失败, 尝试次数: {attempt + 1}, 错误: {failure_reason}'
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(3, 5))  # 增加重试间隔
                continue

            # 添加签到请求的随机延迟
            time.sleep(random.uniform(0.5, 1.5))
            
            data = {'ie': 'utf-8', 'kw': name, 'tbs': tbs_value}
            response = requests.post('https://tieba.baidu.com/sign/add', cookies=cookies, headers=headers, data=data, timeout=10)
            json_data = json.loads(response.text)
            
            if json_data["no"] == 0:
                message = f'{name}吧签到成功'
                break
            elif json_data["no"] == 1101:
                message = f'{name}吧今天已经签到过了'
                break
            else:
                failure_reason = f'错误码{json_data.get("no", "未知")}'
                message = f'{name}吧签到失败, 尝试次数: {attempt + 1}, 错误: {failure_reason}'
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(3, 5))
                
        except requests.exceptions.Timeout:
            failure_reason = '请求超时'
            message = f'{name}吧签到失败, 尝试次数: {attempt + 1}, 错误: {failure_reason}'
            if attempt < retry_count - 1:
                time.sleep(random.uniform(4, 6))
                continue
        except Exception as e:
            failure_reason = str(e)
            message = f'{name}吧签到失败, 尝试次数: {attempt + 1}, 错误: {failure_reason}'
            if attempt < retry_count - 1:
                time.sleep(random.uniform(3, 5))
                continue
    else:
        if not message.endswith('签到成功') and not message.endswith('已经签到过了'):
            message = f'{name}吧签到失败, 已重试{retry_count}次 (最后错误: {failure_reason})'

    with lock:
        success_count[0] += 1
        results.append(message)


def main():
    success_count = [0]
    start_time = time.time()
    results = []
    lock = threading.Lock()
    name_list = get_count()
    max_workers = 5  # 进一步减少线程数量，避免请求过于频繁

    print(f"开始第一轮签到，共{len(name_list)}个贴吧...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(sign_thread, name, results, lock, success_count) for name in name_list]
        for future in as_completed(futures):
            future.result()

    # 收集失败的贴吧进行二次重试
    failed_tiebas = []
    for msg in results:
        if '签到失败' in msg and '已重试3次' in msg:
            # 提取贴吧名称
            tieba_name = msg.split('吧签到失败')[0]
            failed_tiebas.append(tieba_name)
    
    if failed_tiebas:
        print(f"第一轮完成，开始对{len(failed_tiebas)}个失败贴吧进行二次重试...")
        time.sleep(5)  # 等待一段时间再开始二次重试
        
        retry_results = []
        retry_count = [0]
        with ThreadPoolExecutor(max_workers=3) as executor:  # 二次重试使用更少线程
            futures = [executor.submit(sign_thread, name, retry_results, lock, retry_count, 2) for name in failed_tiebas]
            for future in as_completed(futures):
                future.result()
        
        # 更新原结果
        for i, msg in enumerate(results):
            if '签到失败' in msg and '已重试3次' in msg:
                tieba_name = msg.split('吧签到失败')[0]
                for retry_msg in retry_results:
                    if retry_msg.startswith(tieba_name + '吧'):
                        results[i] = retry_msg + " (二次重试)"
                        break

    end_time = time.time()
    total_time = end_time - start_time
    
    # 统计签到成功的数量
    success_messages = [msg for msg in results if '签到成功' in msg or '已经签到过了' in msg]
    success_rate = len(success_messages) / len(name_list) * 100 if name_list else 0
    
    summary = f"总共{len(name_list)}个贴吧，成功{len(success_messages)}个，成功率{success_rate:.1f}%，总耗时：{total_time:.2f}秒"
    if failed_tiebas:
        summary += f"（其中{len(failed_tiebas)}个进行了二次重试）"
    results.append(summary)
    email_sender.send_QQ_email_plain('\n'.join(results))


if __name__ == '__main__':
    if os.getenv('EMAIL_ADDRESS') == '' or os.getenv('BDUSS_BFESS') == '' or os.getenv('STOKEN') == '':
        print('请确保环境变量设置正确（邮箱地址、BDUSS_BFESS、STOKEN）')
        exit()

    cookies = {
        'BDUSS_BFESS': os.getenv('BDUSS_BFESS'),
        'STOKEN': os.getenv('STOKEN'),
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    }
    main()
