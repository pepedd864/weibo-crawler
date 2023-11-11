import pandas as pd

from nlp import *
from visualization import *

if __name__ == "__main__":
    # 读取数据
    gdf = pd.read_csv("微博评论_麒麟9000s.csv")
    df = split_sentence(gdf)
    print(df)
    print(get_sentiments(df))
    show_ip_location(df)
    show_senti_distribution(df)
    show_region_senti(region_sentiments(df))
    show_senti_support(*support_sentiments(df))
    show_wordcloud(split_word(gdf))
