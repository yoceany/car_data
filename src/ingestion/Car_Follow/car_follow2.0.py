import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import random
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text

# 配置数据库连接，根据实际情况修改
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/house')

city_range_dict = {
    # '全国': '999999',
    '北京': '110100',
    '上海': '310100',
    '广州': '440100',
    '深圳': '440300',
    '杭州': '330100',
    '西安': '610100',
    '成都': '510100',
    '重庆': '500100'
}

base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
    'Referer': ''
}

class car_sales():
    def __init__(self):
        self.number = ''  # 排名
        self.name = ''  # 车名
        self.sales = ''  # 销量
        self.score = ''  # 口碑评分
        self.price = ''
        self.follow = ''  # 关注
        self.month = ''  # 月份
        self.img_url = ''

    def __str__(self):
        return 'number:%s;' \
               'name:%s;' \
               'sales:%s;' \
               'score:%s;'\
               'price:%s;'\
               'follow:%s;'\
               'month:%s;' \
               'img_url:%s;' \
            % (self.number,
               self.name,
               self.sales,
               self.score,
               self.price,
               self.follow,
               self.month,
               self.img_url)

def getData(url, headers):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    # 替换为实际路径
    service = Service(r'D:\download_edge\chromedriver-win64\chromedriver-win64\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(url)
        # 等待页面加载
        time.sleep(5)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 滚动到页面底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 等待新内容加载
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        html = driver.page_source
        return html
    finally:
        driver.quit()

def analyzeData(html):
    ls = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find('div', class_='tw-grid tw-grid-cols-[auto_343px] tw-gap-4').find('div',class_='tw-min-w-[633px] tw-text-[#111e36]').find('div',class_='infinite-scroll-component__outerdiv').find_all('div',class_='tw-relative tw-cursor-pointer tw-rounded tw-border-b tw-border-[#F0F3F8] tw-bg-white tw-pr-4 hover:!tw-z-[5] hover:!tw-shadow-[0_4px_20px_rgba(17,30,54,0.08)]')
        for table in tables:
            car_sale = car_sales()
            number = table.find('div',class_='tw-min-w-[50px] tw-bg-[length:100%] tw-text-xl tw-font-bold tw-italic tw-leading-[30px]').string.strip()
            print(number)
            car_sale.number = number

            name = table.find('div',class_='tw-text-nowrap tw-text-lg tw-font-medium hover:tw-text-[#ff6600]').string.strip()
            car_sale.name = name
            print(name)

            score = table.find('div',class_='tw-flex tw-items-center').find('span').get_text().strip()
            car_sale.score = score
            print(score)

            price = table.find('div',class_='tw-font-medium tw-text-[#717887]').string.strip()
            car_sale.price = price
            print(price)

            follow = table.find('div',class_='tw-mx-4 tw-flex tw-flex-col tw-items-center tw-whitespace-nowrap xl:tw-mx-[92px]').get_text().strip()
            # 去掉“日均关注度”并转换为整数
            follow = follow.replace('日均关注度', '').strip()
            try:
                car_sale.follow = int(follow)
            except ValueError:
                car_sale.follow = 0  # 若转换失败，设为 0
            print(car_sale.follow)

            ls.append(car_sale)
    except Exception as e:
        print(f"analyzeData 函数出错: {e}")
    return ls

def writeToDatabase(ls, city_range):
    # 获取昨天的日期，格式调整为 YYYY-MM-DD
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        # 连接数据库并删除昨天的数据
        with engine.connect() as conn:
            delete_query = text("DELETE FROM car_follow WHERE date = :yesterday")
            conn.execute(delete_query, {"yesterday": yesterday})
            conn.commit()
            print(f"成功删除 {yesterday} 的数据！")
    except Exception as e:
        print(f"删除 {yesterday} 数据时出错: {e}")

    data = []
    today = datetime.now().strftime("%Y-%m-%d")  # 格式调整为 YYYY-MM-DD
    for car_sale in ls:
        data.append({
            'ranking': car_sale.number,
            'car_name': car_sale.name,
            'score': car_sale.score,
            'price': car_sale.price,
            'follow': car_sale.follow,
            'city_range': city_range,
            'date': today
        })
    df = pd.DataFrame(data)

    try:
        # 写入数据库，修改表名为 car_follow
        df.to_sql(
            name='car_follow',
            con=engine,
            if_exists='append',
            index=False
        )
        print(f"成功将 {len(df)} 条 {city_range} 相关数据写入数据库！")
    except Exception as e:
        print(f"写入 {city_range} 相关数据到数据库时出错: {e}")

def wait_for_time_window():
    while True:
        now = datetime.now()
        if 0 <= now.hour < 2:
            break
        # 计算距离下一个 0 点的秒数
        next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        wait_seconds = (next_midnight - now).total_seconds()
        print(f"等待到 0 点，将在 {wait_seconds // 3600} 小时后开始爬取")
        time.sleep(wait_seconds)

if __name__ == "__main__":
    while True:
        wait_for_time_window()
        # 动态修改 Cookie 中的城市 ID
        for city_range, url_segment in city_range_dict.items():
            headers = base_headers.copy()
            headers['Cookie'] = f'_ac=2m5f32iqF-OXXs-5r5K5goZL7ylWN3qaD8VECiKjuy1m2jmyzf5S; __ah_uuid_ng=; cookieCityId={url_segment}; series_ask_price_popup=2025-06-26; historyseries=7806%2C66%2C5769%2C7793; ahpvno=24; ahrlid=1750948929674jhFU2xyreL-1750948959590'
            url = f'https://www.autohome.com.cn/rank/2-2001-0-{url_segment}-x-x-x-0_9000.html'
            html = getData(url=url, headers=headers)
            # print(html)
            ls = analyzeData(html)
            # print(ls)
            writeToDatabase(ls, city_range)
        # 爬取完成后，等待到 2 点之后再继续循环
        while datetime.now().hour < 2:
            time.sleep(3600)