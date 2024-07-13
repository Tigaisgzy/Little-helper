import requests, re, json, smtplib, os, pytz, urllib.parse, sys
from datetime import *
import time
from lxml import etree
from email.mime.text import MIMEText


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
    for i in range(2, count + 1):
        name = tree.xpath(f'//div[@class="forum_table"]/table/tr[{i}]/td[1]//text()')[0]
        print(name)
        name_list.append(name)

    return name_list


def do_sign(name_list):
    result = ''
    try:
        for name in name_list:
            # print(f'正在签到{name}吧')
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
        send_QQ_email_plain(result)
        sys.exit()
    return result


def get_beijing_time():
    # 设置UTC和北京时间的时区
    utc_zone = pytz.utc
    beijing_zone = pytz.timezone('Asia/Shanghai')
    # 获取当前的UTC时间，并添加UTC时区信息
    utc_time = datetime.now(utc_zone)
    # 将UTC时间转换为北京时间
    beijing_time = utc_time.astimezone(beijing_zone)
    # 格式化北京时间为 "年-月-日 星期几 时:分" 格式
    return beijing_time.strftime('%Y-%m-%d %A %H:%M')


def send_QQ_email_plain(content):
    sender = user = '1781259604@qq.com'
    passwd = 'tffenmnkqsveccdj'

    # 格式化北京时间为 "年-月-日 星期几 时:分" 格式
    formatted_date = get_beijing_time()

    # 纯文本内容
    msg = MIMEText(f'签到结果：{content}', 'plain', 'utf-8')

    # 设置邮件主题为今天的日期和星期
    msg['From'] = f'{sender}'
    msg['To'] = os.getenv('EMAIL_ADDRESS')
    msg['Subject'] = f'{formatted_date}'  # 设置邮件主题

    try:
        # 建立 SMTP 、SSL 的连接，连接发送方的邮箱服务器
        smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)

        # 登录发送方的邮箱账号
        smtp.login(user, passwd)

        # 发送邮件：发送方，接收方，发送的内容
        smtp.sendmail(sender, os.getenv('EMAIL_ADDRESS'), msg.as_string())

        print('邮件发送成功')

        smtp.quit()
    except Exception as e:
        print(e)
        print('发送邮件失败')


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
    send_QQ_email_plain(res)
