# @Time : 15/7/2024 下午9:53
# @Author : G5116
import smtplib, os
from datetime import datetime
from email.mime.text import MIMEText

import pytz


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
    # msg['To'] = '3552971348@qq.com'
    msg['Subject'] = f'{formatted_date}'  # 设置邮件主题

    try:
        # 建立 SMTP 、SSL 的连接，连接发送方的邮箱服务器
        smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)

        # 登录发送方的邮箱账号
        smtp.login(user, passwd)

        # 发送邮件：发送方，接收方，发送的内容
        smtp.sendmail(sender, os.getenv('EMAIL_ADDRESS'), msg.as_string())
        # smtp.sendmail(sender, '3552971348@qq.com', msg.as_string())

        print('邮件发送成功')

        smtp.quit()
    except Exception as e:
        print(e)
        print('发送邮件失败')
