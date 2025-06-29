# pa_autohome_selenium_all.py

import time
import csv
from datetime import date
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from parsel import Selector


def fetch_month_data(year, month, chromedriver_path):
    """
    抓取指定年月的销量榜单，返回列表 [(rank, name, sales), ...]
    """
    url = f"https://www.autohome.com.cn/rank/1-1-21%2C22%2C23%2C24-0_9000-x-x-x/{year}-{month:02d}.html"
    print(f"[DEBUG] 请求 URL：{url}")

    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        time.sleep(2)
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        html = driver.page_source
    finally:
        driver.quit()

    sel = Selector(html)
    items = sel.css('div.tw-relative.tw-grid.tw-items-center')
    results = []
    for idx, item in enumerate(items, start=1):
        name = item.css('div.tw-text-nowrap.tw-text-lg.tw-font-medium::text') \
            .get(default='').strip()
        sales = item.css('span.tw-text-\\[22px\\]::text') \
            .get(default='').strip()
        results.append((idx, name, sales))
    return results


if __name__ == "__main__":
    # ChromeDriver 可执行文件路径
    CHROMEDRIVER_PATH = r"C:\Users\LENOVO\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

    # 计算从上个月起，向前 6 个月的年月列表
    first_of_this_month = date.today().replace(day=1)
    first_of_last_month = first_of_this_month - relativedelta(months=1)
    months = [first_of_last_month - relativedelta(months=i) for i in range(6)]

    # 逐月抓取并写入独立的 CSV 文件
    for dt in months:
        ym = f"{dt.year}-{dt.month:02d}"
        print(f"=== 开始抓取 {ym} 销量榜单 ===")
        data = fetch_month_data(dt.year, dt.month, CHROMEDRIVER_PATH)

        csv_filename = f"MPV_RANGE_{ym}.csv"
        print(f"写入文件：{csv_filename}")
        with open(csv_filename, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["排名", "车系", "销量"])
            for rank, name, sales in data:
                writer.writerow([rank, name, sales])

    print("所有 6 个 CSV 文件已生成完毕！")
