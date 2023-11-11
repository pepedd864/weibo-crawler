from collections import Counter

import jieba
from snownlp import SnowNLP
from harvesttext import HarvestText


def snow_analysis(text):
    s = SnowNLP(text)
    return s.sentiments


def split_sentence(df):
    """
    分割评论生成表
    :param df: 表
    :return: 表
    """
    comments = df["评论内容"]
    for comment in comments:
        if type(comment) != str:
            continue
        # 数据清洗，去除无意义单独的符号
        ht = HarvestText()
        original_comment = comment
        comment = ht.clean_text(comment)
        if comment is None or comment == "":
            continue
        s = SnowNLP(comment)
        df.loc[df["评论内容"] == original_comment, "情感倾向"] = s.sentiments
    df["正向情感"] = df["情感倾向"].apply(lambda x: 1 if x >= 0.5 else 0)
    df["负向情感"] = df["情感倾向"].apply(lambda x: 1 if x < 0.5 else 0)
    return df


def get_sentiments(df):
    """
    计算整体的情感倾向
    :param df: 表
    :return:
    """
    return df["情感倾向"].mean()


def region_sentiments(df):
    """
    计算地区的情感倾向
    :param df: 表
    :return:
    """
    return df.groupby("IP归属地")["情感倾向"].mean().reset_index().rename(columns={"情感倾向": "平均情感倾向"})


def support_sentiments(df):
    """
    计算正向情感和负向情感的点赞
    :param df: 表
    :return:
    """
    positive = df[df["正向情感"] == 1]["点赞数"].sum()
    negative = df[df["负向情感"] == 1]["点赞数"].sum()
    return positive, negative


def split_word(df, word_len=3):
    """
    分割评论生成词表
    :param df: 表
    :param word_len: 词长度
    :return: 词表
    """
    segmented_words = []
    comments = df["评论内容"]
    for comment in comments:
        if type(comment) != str:
            continue
        segmented = [i for i in jieba.cut(comment) if len(i) >= word_len]
        segmented_words.extend(segmented)
    fq = Counter(segmented_words).most_common()
    return dict(fq)


if __name__ == '__main__':
    pass
