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


def get_tbs_enhanced(tieba_name):
    """增强版tbs获取函数，使用多种方法获取tbs值"""
    
    # 方法1：从主页获取tbs
    try:
        response = requests.get('https://tieba.baidu.com/', cookies=cookies, headers=headers, timeout=10)
        tbs_match = re.search(r'PageData\.tbs\s*=\s*["\']([^"\']+)["\']', response.text)
        if not tbs_match:
            tbs_match = re.search(r'"tbs":"([^"]+)"', response.text)
        if tbs_match:
            return tbs_match.group(1)
    except:
        pass
    
    # 方法2：从API接口获取tbs
    try:
        api_url = 'https://tieba.baidu.com/dc/common/tbs'
        response = requests.get(api_url, cookies=cookies, headers=headers, timeout=10)
        tbs_data = json.loads(response.text)
        if 'tbs' in tbs_data:
            return tbs_data['tbs']
    except:
        pass
    
    # 方法3：从贴吧页面获取（原方法的改进版）
    try:
        url_name = urllib.parse.quote(tieba_name)
        url = f'https://tieba.baidu.com/f?ie=utf-8&kw={url_name}&fr=search'
        response = requests.get(url, cookies=cookies, headers=headers, timeout=10)
        tree = etree.HTML(response.text)
        
        # 多种xpath尝试
        script_paths = [
            '/html/head/script',
            '//script[contains(text(), "PageData")]',
            '//script[contains(text(), "tbs")]'
        ]
        
        for path in script_paths:
            script_elements = tree.xpath(path)
            for script in script_elements:
                if script.text:
                    # 尝试多种正则模式
                    patterns = [
                        r'var PageData = ({.*?});',
                        r'PageData\s*=\s*({.*?});',
                        r'"tbs":"([^"]+)"',
                        r"'tbs':'([^']+)'",
                        r'tbs["\']?\s*[:=]\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, script.text, re.DOTALL)
                        if match:
                            if pattern.startswith('var PageData') or pattern.startswith('PageData'):
                                try:
                                    cleaned_json = match.group(1).replace("'", '"')
                                    page_data_dict = json.loads(cleaned_json)
                                    if 'tbs' in page_data_dict:
                                        return page_data_dict['tbs']
                                except:
                                    continue
                            else:
                                return match.group(1)
    except:
        pass
    
    # 方法4：尝试不同的贴吧入口
    try:
        url_name = urllib.parse.quote(tieba_name)
        alt_url = f'https://tieba.baidu.com/f?kw={url_name}'
        response = requests.get(alt_url, cookies=cookies, headers=headers, timeout=10)
        tbs_match = re.search(r'"tbs":"([^"]+)"', response.text)
        if tbs_match:
            return tbs_match.group(1)
    except:
        pass
    
    return None


def sign_thread(name, results, lock, success_count, retry_count=3):
    message = ''
    failure_reason = ''
    
    # 添加随机初始延迟
    time.sleep(random.uniform(0.3, 1.5))
    
    for attempt in range(retry_count):
        try:
            # 使用增强版tbs获取函数
            tbs_value = get_tbs_enhanced(name)
            
            if not tbs_value:
                failure_reason = '无法获取tbs值'
                message = f'{name}吧签到失败, 尝试次数: {attempt + 1}, 错误: {failure_reason}'
                
                # 对无法获取tbs值的错误，使用递增延迟
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt + random.uniform(1, 3)  # 指数退避
                    time.sleep(wait_time)
                continue

            # 添加签到请求的随机延迟
            time.sleep(random.uniform(0.3, 1.0))
            
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
                # 对签到错误码的重试使用较短延迟
                if attempt < retry_count - 1:
                    time.sleep(random.uniform(2, 4))
                
        except requests.exceptions.Timeout:
            failure_reason = '请求超时'
            message = f'{name}吧签到失败, 尝试次数: {attempt + 1}, 错误: {failure_reason}'
            if attempt < retry_count - 1:
                time.sleep(random.uniform(3, 5))
                continue
        except Exception as e:
            failure_reason = str(e)
            message = f'{name}吧签到失败, 尝试次数: {attempt + 1}, 错误: {failure_reason}'
            if attempt < retry_count - 1:
                time.sleep(random.uniform(2, 4))
                continue
    else:
        if not message.endswith('签到成功') and not message.endswith('已经签到过了'):
            message = f'{name}吧签到失败, 已重试{retry_count}次 (最后错误: {failure_reason})'

    with lock:
        success_count[0] += 1
        results.append(message)


def main():
    success_count = [0]
    completed_count = [0]
    start_time = time.time()
    results = []
    lock = threading.Lock()
    name_list = get_count()
    max_workers = 5
    
    def show_progress():
        """显示进度的函数"""
        while completed_count[0] < len(name_list):
            time.sleep(3)
            with lock:
                current_completed = completed_count[0]
                current_success = len([msg for msg in results if '签到成功' in msg or '已经签到过了' in msg])
                progress = (current_completed / len(name_list)) * 100
                print(f"进度: {current_completed}/{len(name_list)} ({progress:.1f}%) - 成功: {current_success}")

    print(f"开始第一轮签到，共{len(name_list)}个贴吧...")
    
    # 启动进度显示线程
    import threading
    progress_thread = threading.Thread(target=show_progress, daemon=True)
    progress_thread.start()
    
    def sign_thread_with_progress(name):
        sign_thread(name, results, lock, success_count)
        with lock:
            completed_count[0] += 1
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(sign_thread_with_progress, name) for name in name_list]
        for future in as_completed(futures):
            future.result()

    print(f"第一轮完成！")

    # 收集失败的贴吧进行二次重试
    failed_tiebas = []
    for msg in results:
        if '签到失败' in msg and '已重试3次' in msg:
            tieba_name = msg.split('吧签到失败')[0]
            failed_tiebas.append(tieba_name)
    
    if failed_tiebas:
        print(f"开始对{len(failed_tiebas)}个失败贴吧进行二次重试...")
        time.sleep(3)
        
        retry_results = []
        retry_count = [0]
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(sign_thread, name, retry_results, lock, retry_count, 2) for name in failed_tiebas]
            for i, future in enumerate(as_completed(futures)):
                future.result()
                print(f"二次重试进度: {i+1}/{len(failed_tiebas)}")
        
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
    
    print(f"\n{summary}")
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
