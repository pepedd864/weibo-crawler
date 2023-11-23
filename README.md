# 微博评论爬虫
演示视频 https://www.bilibili.com/video/BV1hG411Q7wK/

**目录结构**

```bash
weibo-keyword-comment
├── PingFang Regular.ttf	# 词云字体
├── README.md				# README
├── analysis_data.py		# 分析数据
├── color_log.py			# 彩色日志工具
├── cookie					# 登录信息
├── main.py					# 主入口
├── nlp.py					# 语言处理
├── process.log				# 日志
├── requirements.txt		# 依赖			
├── utils.py				# 工具
├── visualization.py		# 可视化
└── weibo.py				# 爬虫
```

这就是一个简单的爬虫加可视化演示，算不上高级所以没啥好说的

**可视化截图**

| ![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/992a69ba830abb3393b2c09acae42d5c.png) | ![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/037cd3b5d8f0b628b427e1d418c6c5f6.png) |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| ![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/a47cfc0782346d9614148daeef24f376.png) | ![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/f9c2f3cbcb801afb8668d8569a382aae.png) |
| ![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/8a251f2ad2f494c9fd59f845ddecd7aa.png) | ![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/a47cfc0782346d9614148daeef24f376.png) |

## 1. 原理

使用移动端微博爬取

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/b47246cf56ad5222469a248c1f0a6f8d.png)

使用Wappalyzer查看网页技术栈，看见熟悉的vue，便可知道不是**服务端渲染**，于是可以逆向（其实说不上逆向，就是看参数传值而已）其接口进行爬取

### 1.1 获取微博列表

使用开发者工具查看XHR/fetch请求，可以看到其请求接口

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/2a18a038a068061abe2fb5c4d2bc81dd.png)

观察其响应结果，可以看到主要的属性有`cardListInfo`和`cards`

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/2c5c7adcc923b3311bce4beee6b3c99c.png)



`cardListInfo`对应的是搜索信息，其中有三个地方比较重要，分别是`page`，`page_size`，`total`

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/416a31446c408931da5a92ea38dd2c02.png)

第一页的请求参数没有page参数，从第二页开始，便带上page参数

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/838b4c344cc483c8668f06197d8b544f.png)



`cards`内的`mblog`对应的就是搜索的微博内容

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/46245f408118c0d792c26f7a01dcff92.png)



在代码中，只获取了几个基本的数据，可根据自己需要添加

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/f12fbbeca500c3837c2184150e6889c2.png)



### 1.2 获取微博评论内容

打开任意微博页面，还是查看接口

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/5c435edfd96c0c8c7106c06b75001c0f.png)

参数是`id`，`mid`，`max_id_type`，其中`id`和`mid`都是微博的id固定不变

观察其响应结果

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/a74bef9bbf6d223f54610d3f7e99890a.png)

`data`对应的是评论内容，还有max_id_type在下次请求中需要使用

评论内容

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/3a2ae71004d0080b28325dea681824f2.png)



代码中也只获取了几个数据

![](https://picgo-img-repo.oss-cn-beijing.aliyuncs.com/img/233bef569a54f11f9a5b9649d2bc8dfc.png)



### 1.3 爬取时的注意点

1. 一是使用移动端微博无法获取非常多的数据，搜索时返回的条数完全是随机的，并且无法限制时间，使用桌面端微博（Selenium）可以获取固定时间的微博，较新的内容，但是因为是渲染好的页面，无法通过接口获取，于是需要解析HTML，工作量加大
2. 请求头的UA这里使用了随机UA，在`fake_useragent`这个库中
3. 这里接口是需要携带cookie的，如果没有cookie无法获取数据，cookie也是会过期的，但是时间比较长，所以不用担心，及时更新即可
4. 控制好请求频率，使用`request`时偶尔出现SSL错误，但是只需设置请求重试策略即可



### 1.4 可视化

这里也就是使用jieba分词，harvesttext清洗数据，snownlp分析情感，plt可视化，这对一些有经验的同学来讲应该是太过于入门了，就不展开讲了



## 2. 代码

### 2.1 使用request库发出一次请求

上面讲到可以使用requst库请求接口，这里我做一次简单的实例

在此之前，先设置好请求重试

在utils.py下，写入

```py
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
```

便可在weibo.py中使用

```py
page = 1
v_keyword = "关键字"
headers = {
    "User-Agent": UserAgent().random,
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
}
params = {
    "containerid": "100103type=1&q={}".format(v_keyword),
    "page_type": "searchall",
    "page": page
}
if page == 1:
	params.pop("page")
r = session.get(url, headers=headers, params=params)
cards = r.json()["data"]["cards"]
print(cards)
```

这便完成了一次基本请求

对于数据的处理，主要是去除html标签和判空，由于结果的json的嵌套层数较深，使用jsonpath快速获取json的值

```py
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
```

### 2.2 完成请求微博列表函数

上面提到，请求参数中的page代表的是页码，我们想要获取后续的结果，便将page自增即可，但是如何让他停止呢，这个时候就需要使用到响应结果中的page_size和total了，结合这些数据，将功能封装解耦，便成了下面这样

```py
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
```

其中获取页码的函数

```py
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
```



在get_weibo_list函数中获取到了微博内容，我们可以使用pandas将其保存

```py
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
```



### 2.3 获取微博评论内容

微博的评论一般会一定的限制，不过对于一般正常的1.4w评论程序可以正常获取到1.w左右的评论，如果是评论精选或者关闭评论区的则无法获取，对于这些非正常情况也需要做出一定的判断



同样还是先从简单的获取评论内容开始

```py
max_id = 0
page = 1
v_weibo_id = 4970890514403289
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
r = session.get(url, headers=headers, params=params)
```

这个获取了单页的评论内容，继续向后获取使用循环即可

```py
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
```



### 2.4 设置定时任务

大概就是隔一段时间获取一次，然后与现有的数据对比（id相同的去除即可）这样可以获取尽可能多的数据

```py
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

```



在main.py中即可运行定时任务，注意添加必要的工具函数进项目

```py
from weibo import schedule_tasks

if __name__ == "__main__":
    search_keywords = ["麒麟9000s", "俄乌冲突", "巴以冲突"]
    schedule_tasks(search_keywords, interval=1200)
    input("按任意键退出")
```



### 2.5 工具函数

```py
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
```



### 2.6 彩色日志

```py
import logging
import colorlog


def setup_logger(log_file):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.encoding = 'utf-8'

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    color_formatter = colorlog.ColoredFormatter('%(log_color)s%(levelname)s : %(message)s')

    console_handler.setFormatter(color_formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


if __name__ == '__main__':
    logger = setup_logger('log.txt')

    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')

```

