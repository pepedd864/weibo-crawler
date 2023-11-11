from weibo import schedule_tasks

if __name__ == "__main__":
    search_keywords = ["麒麟9000s", "俄乌冲突", "巴以冲突"]
    schedule_tasks(search_keywords, interval=1200)
    input("按任意键退出")
