import re
import random
from time import sleep

from requests.adapters import HTTPAdapter
from urllib3 import Retry

from color_log import setup_logger

import requests
import pandas as pd
from utils import *
from fake_useragent import UserAgent

logger = setup_logger("test.log")
terminal_width = get_terminal_width()

session = setup_retry_session()


def get_weibo_comment_list(v_weibo_id, v_max_page):
    """
    爬取微博评论列表
    :param v_weibo_id: 微博id
    :param v_max_page: 最大页数
    :return: None
    """
    max_id = 0
    page = 1
    while page <= v_max_page:
        wait_seconds = random.uniform(0, 1)
        log_separator(logger, "*", terminal_width, "开始爬取{}的第{}页评论".format(v_weibo_id, page))
        logger.info("等待{}秒".format(wait_seconds))
        sleep(wait_seconds)
        params = {
            "id": v_weibo_id,
            "mid": v_weibo_id,
            "max_id_type": "0"
        }
        if page == 1:
            url = "https://m.weibo.cn/comments/hotflow"
        else:
            if max_id == 0:
                logger.warning("评论有限制,无法爬取后续页数")
                break
            url = "https://m.weibo.cn/comments/hotflow"
            params["max_id"] = max_id
            if page >= 16:
                params["max_id_type"] = "1"
        headers = {
            "user-agent": UserAgent().random,
            # 如果cookie失效，不会返回结果
            "cookie": get_cookie(),
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "referer": "https://m.weibo.cn/detail/{}".format(v_weibo_id),
            "x-requested-with": "XMLHttpRequest",
            "mweibo-pwa": "1",
        }
        try:
            r = session.get(url, headers=headers, params=params)
        except Exception as e:
            logger.error("爬取第{}页评论失败".format(page))
            logger.error(e)
            break
        logger.info("返回状态码: {}".format(r.status_code))
        try:
            max_id = r.json()["data"]["max_id"]
            datas = r.json()["data"]["data"]
            page_size = r.json()["data"]["max"]
        except:
            msg = None
            try:
                msg = r.json()["msg"]
            except:
                pass
            logger.error(msg or "解析json失败")
            break
        v_max_page = min(page_size, v_max_page)
        logger.info("当前页码: {}, 共: {}页".format(page, v_max_page))
        page_list = []  # 评论页码
        id_list = []  # 评论id
        text_list = []  # 评论内容
        time_list = []  # 评论时间
        like_count_list = []  # 点赞数
        source_list = []  # IP归属地
        user_name_list = []  # 评论用户
        for data in datas:
            page_list.append(page)
            dr = re.compile(r"<[^>]+>", re.S)
            text = dr.sub("", data["text"])
            text_list.append(text)  # 评论内容
            id_list.append(data["id"])  # 评论id
            time_list.append(trans_time(v_str=data["created_at"]))  # 评论时间
            like_count_list.append(data["like_count"])  # 点赞数
            if data["source"].startswith("来自"):
                data["source"] = data["source"][2:]
            source_list.append(data["source"])  # IP归属地
            user_name_list.append(data["user"]["screen_name"])  # 评论用户
        df = pd.DataFrame(
            {
                "微博id": [v_weibo_id] * len(id_list),
                "评论id": id_list,
                "评论用户": user_name_list,
                "评论内容": text_list,
                "点赞数": like_count_list,
                "评论时间": time_list,
                "IP归属地": source_list,
            }
        )
        header = False if page != 1 else True
        df_file_name = "{}.csv".format(v_weibo_id)
        df.to_csv(df_file_name, mode="a+", index=False, header=header, encoding="utf-8-sig")
        logger.info("评论表格保存成功:{}".format(df_file_name))
        page += 1


if __name__ == "__main__":
    search_keywords = ["保障性租赁", "保障房", "公租房", "共有产权房", "廉租房", "经济适用房"]
    get_weibo_comment_list(v_weibo_id="4966078201201698", v_max_page=10000)
