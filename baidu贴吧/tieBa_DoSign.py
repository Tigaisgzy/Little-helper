import requests, re, json, os, urllib.parse, sys
from datetime import *
import time
from lxml import etree

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到 sys.path
sys.path.append(project_root)
from utils import email_sender


def get_count():
    # 获取当前时间戳
    timestamp_with_microseconds = int(datetime.now().timestamp() * 1000)
    params = {
        'v': str(timestamp_with_microseconds),
    }

    response = requests.get('https://tieba.baidu.com/f/like/mylike', params=params, cookies=cookies, headers=headers)
    tree = etree.HTML(response.text)
    time.sleep(1)
    name_list = []
    tree_list = tree.xpath('//div[@class="forum_table"]/table/tr')
    count = len(tree_list) - 1
    for i in range(1, count + 1):
        name = tree_list[i].xpath('./td[1]/a/text()')[0]
        name_list.append(name)

    return name_list


def do_sign(name_list):
    result = ''
    try:
        start_time = time.time()
        for name in name_list:
            url_name = urllib.parse.quote(name)
            url = f'https://tieba.baidu.com/f?ie=utf-8&kw={url_name}&fr=search'
            response = requests.get(url)
            tree = etree.HTML(response.text)
            time.sleep(1)
            tbs = tree.xpath('/html/head/script[1]')[0].text
            tbs_data = re.search(r'var PageData = ({.*?});', tbs, re.DOTALL)
            if tbs_data:
                cleaned_json = tbs_data.group(1).replace("'", '"')  # 将单引号替换为双引号以符合JSON格式
                page_data_dict = json.loads(cleaned_json)
                # 获取tbs的值
                tbs_value = page_data_dict['tbs']
            data = {
                'ie': 'utf-8',
                'kw': name,
                'tbs': tbs_value,
            }
            response = requests.post('https://tieba.baidu.com/sign/add', cookies=cookies, headers=headers, data=data)
            json_data = json.loads(response.text)
            if json_data["no"] == 0:
                result += f'{name}吧签到成功\n'
            elif json_data["no"] == 1101:
                result += f'{name}吧今天已经签到过了\n'
    except Exception as e:
        result += f'{name}吧签到失败\n'
        email_sender.send_QQ_email_plain(result)
        sys.exit()
    end_time = time.time()
    print(f"所有任务完成耗时：{end_time - start_time:.2f}秒")
    return result


if os.getenv('EMAIL_ADDRESS') == '':
    print('请填写邮箱地址')
    exit()
if os.getenv('BDUSS_BFESS') == '' or os.getenv('STOKEN') == '':
    print('请填写BDUSS_BFESS和STOKEN')
    exit()

if __name__ == '__main__':
    cookies = {
        'BDUSS_BFESS': str(os.getenv('BDUSS_BFESS')),
        'STOKEN': str(os.getenv('STOKEN')),
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    }
    name_list = get_count()
    res = do_sign(name_list)
    email_sender.send_QQ_email_plain(res)
