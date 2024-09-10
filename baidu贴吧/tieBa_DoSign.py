import requests, re, json, os, sys, urllib.parse, time, threading
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
    timestamp_with_microseconds = int(datetime.now().timestamp() * 1000)
    params = {'v': str(timestamp_with_microseconds)}
    response = requests.get('https://tieba.baidu.com/f/like/mylike', params=params, cookies=cookies, headers=headers)
    if len(response.text) <= 4932:
        email_sender.send_QQ_email_plain('获取贴吧列表失败，请更新cookie')
        exit()
    tree = etree.HTML(response.text)
    time.sleep(1)
    tree_list = tree.xpath('//div[@class="forum_table"]/table/tr')
    count = len(tree_list) - 1
    # print(f'共有{count}个贴吧')
    name_list = [tree_list[i].xpath('./td[1]/a/text()')[0] for i in range(1, count + 1)]
    # for name in name_list:
    #     print(name)
    return name_list


def sign_thread(name, results, lock, success_count, retry_count=3):
    message = ''
    for attempt in range(retry_count):
        try:
            url_name = urllib.parse.quote(name)
            url = f'https://tieba.baidu.com/f?ie=utf-8&kw={url_name}&fr=search'
            response = requests.get(url)
            tree = etree.HTML(response.text)
            time.sleep(1)
            tbs = tree.xpath('/html/head/script[1]')[0].text
            tbs_data = re.search(r'var PageData = ({.*?});', tbs, re.DOTALL)
            if tbs_data:
                cleaned_json = tbs_data.group(1).replace("'", '"')
                page_data_dict = json.loads(cleaned_json)
                tbs_value = page_data_dict['tbs']

            data = {'ie': 'utf-8', 'kw': name, 'tbs': tbs_value}
            response = requests.post('https://tieba.baidu.com/sign/add', cookies=cookies, headers=headers, data=data)
            json_data = json.loads(response.text)
            if json_data["no"] == 0:
                message = f'{name}吧签到成功'
                break
            elif json_data["no"] == 1101:
                message = f'{name}吧今天已经签到过了'
                break
        except Exception as e:
            message = f'{name}吧签到失败, 尝试次数: {attempt + 1}, 错误: {str(e)}'
            break
        time.sleep(2)  # 等待一段时间后重试
    else:
        message = f'{name}吧签到失败, 已重试{retry_count}次'

    with lock:
        success_count[0] += 1  # 使用列表的第一个元素作为可变的计数器
        results.append(message)


def main():
    success_count = [0]  # 使用列表来存储成功计数
    start_time = time.time()
    results = []
    lock = threading.Lock()
    name_list = get_count()
    max_workers = 10  # 控制最大线程数量

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(sign_thread, name, results, lock, success_count) for name in name_list]
        for future in as_completed(futures):
            future.result()  # 获取线程执行结果

    end_time = time.time()
    total_time = end_time - start_time
    results.append(f"{success_count[0]}个贴吧签到完成总耗时：{total_time:.2f}秒")
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    }
    main()
