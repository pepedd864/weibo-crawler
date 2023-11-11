import os
import uuid
from datetime import datetime

import requests
import time

from matplotlib import pyplot as plt
from tqdm import tqdm

from requests.adapters import HTTPAdapter
from urllib3 import Retry


def get_terminal_width():
    """
    获取终端宽度
    :return:
    """
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 60
        print("无法获取终端宽度，使用默认宽度60")
    return terminal_width


def log_separator(logger, separator, width, content):
    """
    打印分隔线
    :param logger: 日志对象
    :param separator: 分隔符
    :param width: 宽度
    :param content: 内容
    :return: None
    """
    content_len = len(content)
    separator_line_len = int((width - content_len) / 2)
    separator_line = separator * separator_line_len
    log_message = "{}{}{}".format(separator_line, content, separator_line)
    logger.info(log_message)


def get_cookie():
    """
    从cookie文件中读入cookie
    :return: cookie
    """
    with open("cookie", "r", encoding="utf-8") as f:
        cookie = f.read()
    return cookie


def trans_time(v_str):
    """
    转换GMT时间为标准格式
    :param v_str: GMT时间
    :return: 标准格式时间
    """
    GMT_FORMAT = "%a %b %d %H:%M:%S +0800 %Y"
    timeArray = datetime.strptime(v_str, GMT_FORMAT)
    ret_time = timeArray.strftime("%Y-%m-%d %H:%M:%S")
    return ret_time


def setup_retry_session():
    """
    设置重试session
    :return:
    """
    retry_strategy = Retry(
        total=5,
        status_forcelist=[429, 443, 500, 502, 503, 504],
    )
    adaptor = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adaptor)
    session.mount("http://", adaptor)
    return session


def generate_uuid(length):
    """
    生成uuid
    :param length: uuid长度
    :return: None
    """
    return str(uuid.uuid4()).replace("-", "")[:length]


def show_countdown(total_time):
    """
    显示倒计时
    :param total_time: 总时间
    :return: None
    """
    progress_bar = tqdm(total=total_time, unit='s', unit_divisor=1)
    while total_time > 0:
        progress_bar.update(1)
        progress_bar.set_postfix({'Remaining': f'{total_time} s'})
        time.sleep(1)
        total_time -= 1
    progress_bar.close()


def setup_plt():
    """
    设置matplotlib
    :return:
    """
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    return plt
