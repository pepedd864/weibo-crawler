import re
import random

from color_log import setup_logger
from time import sleep

from jsonpath import jsonpath
import pandas as pd
from fake_useragent import UserAgent
from utils import *

logger = setup_logger("process.log")
terminal_width = get_terminal_width() - len("[INFO] : ") - 6

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
        v_max_page = page_size
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
        if os.path.exists(v_weibo_comment_file):
            header = None
        df.to_csv(v_weibo_comment_file, mode="a+", index=False, header=header, encoding="utf-8-sig")
        logger.info("评论表格保存成功:{}".format(v_weibo_comment_file))
        page += 1


def get_weibo_list(v_keyword, v_max_page):
    """
    爬取微博内容列表
    :param v_keyword: 关键字
    :param v_max_page: 爬前几页
    :return: None
    """
    headers = {
        "User-Agent": UserAgent().random,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }
    for page in range(1, v_max_page + 1):
        log_separator(logger, "=", terminal_width, "正在爬取{}关键字的第{}页微博".format(v_keyword, page))
        url = "https://m.weibo.cn/api/container/getIndex"
        params = {
            "containerid": "100103type=1&q={}".format(v_keyword),
            "page_type": "searchall",
            "page": page
        }
        # 如果是第一页，不需要page参数
        if page == 1:
            params.pop("page")
        r = None
        try:
            r = session.get(url, headers=headers, params=params)
        except Exception as e:
            logger.error("爬取第{}页微博失败".format(page))
            logger.error(e)
            continue
        logger.info("返回状态码: {}".format(r.status_code))
        try:
            cards = r.json()["data"]["cards"]
        except:
            logger.error("解析微博内容json失败")
            continue
        # 微博内容
        text_list = jsonpath(cards, "$..mblog.text")
        dr = re.compile(r"<[^>]+>", re.S)
        text2_list = []
        if not text_list:
            logger.error("text_list is empty")
            continue
        if type(text_list) == list and len(text_list) > 0:
            for text in text_list:
                text2 = dr.sub("", text)
                text2_list.append(text2)
        # 微博发布时间
        time_list = jsonpath(cards, "$..mblog.created_at")
        time_list = [trans_time(v_str=i) for i in time_list]
        # 微博作者
        author_list = jsonpath(cards, "$..mblog.user.screen_name")
        # 微博id
        id_list = jsonpath(cards, "$..mblog.id")
        # 微博bid
        bid_list = jsonpath(cards, "$..mblog.bid")
        # 转发数
        reposts_count_list = jsonpath(cards, "$..mblog.reposts_count")
        # 评论数
        comments_count_list = jsonpath(cards, "$..mblog.comments_count")
        # 点赞数
        attitudes_count_list = jsonpath(cards, "$..mblog.attitudes_count")
        # dataframe
        df = pd.DataFrame(
            {
                "微博id": id_list,
                "微博bid": bid_list,
                "微博作者": author_list,
                "发布时间": time_list,
                "微博内容": text2_list,
                "转发数": reposts_count_list,
                "评论数": comments_count_list,
                "点赞数": attitudes_count_list
            }
        )
        # 表头
        header = False if page != 1 else True
        if os.path.exists(v_weibo_file):
            header = None
        df.to_csv(v_weibo_file, mode="a+", index=False, header=header, encoding="utf-8-sig")
        logger.info("表格保存成功:{}".format(v_weibo_file))

        # 爬取评论
        for id in id_list:
            comment_count = comments_count_list[id_list.index(id)]
            if comment_count == 0:
                logger.warning("{}没有评论".format(id))
                continue
            page_size = 20
            get_weibo_comment_list(id, comment_count // page_size + 1)


def get_keyword_pagesize(v_keyword):
    """
    获取关键字搜索结果页数
    :param v_keyword: 关键字
    :return: 页数
    """
    headers = {
        "User-Agent": UserAgent().random,
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                  "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
    }
    url = "https://m.weibo.cn/api/container/getIndex"
    params = {
        "containerid": "100103type=1&q={}&t=".format(v_keyword),  # t时间 传空为实时
        "page_type": "searchall",
        "page": 1
    }
    r = session.get(url, headers=headers, params=params)
    logger.info("返回状态码: {}".format(r.status_code))
    total = r.json()["data"]["cardlistInfo"]["total"]
    per_page = r.json()["data"]["cardlistInfo"]["page_size"]
    # 总页数
    pagesize = int(total) // int(per_page) + 1
    return pagesize


def task(search_keyword, max_page=50):
    max_search_page = min(get_keyword_pagesize(search_keyword), max_page)
    logger.info("开始爬取，共{}页".format(max_search_page))
    global v_weibo_file
    v_weibo_file = "微博_{}.csv".format(search_keyword)
    global v_weibo_comment_file
    v_weibo_comment_file = "微博评论_{}.csv".format(search_keyword)
    get_weibo_list(search_keyword, max_search_page)

    # 数据清洗
    df = pd.read_csv(v_weibo_file)
    df.drop_duplicates(subset=["微博bid"], inplace=True, keep="first")
    df.to_csv(v_weibo_file, index=False, encoding="utf-8-sig")

    df = pd.read_csv(v_weibo_comment_file)
    df.drop_duplicates(subset=["评论id"], inplace=True, keep="first")
    df.to_csv(v_weibo_comment_file, index=False, encoding="utf-8-sig")


def schedule_tasks(keywords, interval=3600):
    """
    隔一段执行一次，并去除重复微博id
    :param keywords: 关键字列表
    :param interval: 间隔时间
    :return:
    """
    round = 1
    while True:
        log_separator(logger, "~", terminal_width, "第{}轮开始, 间隔{}秒".format(round, interval))
        for search_keyword in keywords:
            log_separator(logger, "+", terminal_width, "开始爬取关键字：{}".format(search_keyword))
            task(search_keyword, 30)
        logger.info("第{}轮结束".format(round))
        logger.info("等待{}秒，请及时更新cookie，防止无法获取评论".format(interval))
        show_countdown(interval)
        round += 1

