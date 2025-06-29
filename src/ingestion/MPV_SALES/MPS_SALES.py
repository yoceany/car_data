# pa_autohome_selenium_all.py

import time
import csv
from datetime import date
from dateutil.relativedelta import relativedelta
from collections import OrderedDict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from parsel import Selector

def fetch_month_data(year, month, chrome_path, chromedriver_path):
    url = f"https://www.autohome.com.cn/rank/1-1-21%2C22%2C23%2C24-0_9000-x-x-x/{year}-{month:02d}.html"
    print(f"[DEBUG] 请求 URL：{url}")
    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_path
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
    data = []
    for item in items:
        name = item.css('div.tw-text-nowrap.tw-text-lg.tw-font-medium::text')\
                   .get(default='').strip()
        sales = item.css('span.tw-text-\\[22px\\]::text')\
                    .get(default='').strip()
        data.append((name, sales))
    return data

if __name__ == "__main__":
    CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    CHROMEDRIVER_PATH = r"C:\Users\LENOVO\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

    # 从上个月开始往前数 6 个月
    first_of_this_month = date.today().replace(day=1)
    first_of_last_month = first_of_this_month - relativedelta(months=1)

    months = []
    for i in range(6):
        dt = first_of_last_month - relativedelta(months=i)
        months.append(f"{dt.year}-{dt.month:02d}")

    # 按顺序抓取并保存
    all_data = OrderedDict()
    for ym in months:
        y, m = map(int, ym.split('-'))
        print(f"=== 抓取 {ym} ===")
        all_data[ym] = fetch_month_data(y, m, CHROME_PATH, CHROMEDRIVER_PATH)

    # 准备写入 CSV
    csv_filename = "MPV_sales.csv"
    header = ["车系"] + [f"{ym}销量" for ym in months]

    # 汇总所有车系
    all_cars = sorted({name for data in all_data.values() for name, _ in data})

    # 写文件
    with open(csv_filename, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for car in all_cars:
            row = [car]
            for ym in months:
                row.append(dict(all_data[ym]).get(car, ""))
            writer.writerow(row)

    print(f"\n已将数据保存到：{csv_filename}")

