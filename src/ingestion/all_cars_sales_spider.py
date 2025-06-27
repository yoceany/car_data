import csv

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

months = ['01', '02', '03', '04', '05']

for month in months:
    url = 'https://www.autohome.com.cn/rank/1-1-0-0_9000-x-x-x/2025-{month}.html'.format(month=month)

    # url = 'https://www.autohome.com.cn/rank/1-1-0-0_9000-x-x-x/2025-05.html'
    headers = {
        # 'User-Agent': UserAgent().random
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
        'Cookie': '_ac=2m5f32iqF-OXXs-5r5K5goZL7ylWN3qaD8VECiKjuy1m2jmyzf5S; __ah_uuid_ng=; cookieCityId=510100; series_ask_price_popup=2025-06-26; historyseries=7806%2C66%2C5769%2C7793; ahpvno=24; ahrlid=1750948929674jhFU2xyreL-1750948959590',
        'Referer': ''
    }


    class car_sales():

        def __init__(self):
            self.number = ''  # 排名
            self.name = ''  # 车名
            self.sales = ''  # 销量
            self.month = ''

        def __str__(self):
            return 'number:%s;' \
                   'name:%s;' \
                   'sales:%s;' \
                   'month:%s;' \
                % (self.number,
                   self.name,
                   self.sales,
                   self.month)


    def getData(url, headers):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36')

        service = Service(r'D:\download_edge\chromedriver-win64\chromedriver-win64\chromedriver.exe')  # 替换为实际路径
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.get(url)
            # 模拟滚动页面操作，加载更多数据
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待页面加载新数据
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            html = driver.page_source
            # print(html)
            return html
        except Exception as e:
            print(f"请求出错: {e}")
            return ""
        finally:
            driver.quit()


    def analyzeData(html):
        ls = []
        soup = BeautifulSoup(html, 'lxml')
        # 查找第一个 div 元素
        div1 = soup.find('div', class_='tw-grid tw-grid-cols-[auto_343px] tw-gap-4')
        if div1 is None:
            print("未找到 div1 元素")
            return ls
        # 查找第二个 div 元素
        div2 = div1.find('div', class_='tw-min-w-[633px] tw-text-[#111e36]')
        if div2 is None:
            print("未找到 div2 元素")
            return ls
        # 查找第三个 div 元素
        div3 = div2.find('div', class_='infinite-scroll-component__outerdiv')
        if div3 is None:
            print("未找到 div3 元素")
            return ls
        # 查找第四个 div 元素
        div4 = div3.find('div', class_='infinite-scroll-component ')
        # if div4 is None:
        #     print("未找到 div4 元素")
        #     return ls
        # 查找所有目标 div 元素
        init_table = div3.find_all('div',
                                   class_='tw-relative tw-cursor-pointer tw-rounded tw-border-b tw-border-[#F0F3F8] tw-bg-white tw-pr-4 hover:!tw-z-[5] hover:!tw-shadow-[0_4px_20px_rgba(17,30,54,0.08)]')

        for table in init_table:
            car_sale = car_sales()
            car_sale.month = month
            # Get the car ranking
            number_div = table.find('div',
                                    class_='tw-flex tw-h-[116px] tw-w-[50px] tw-flex-col tw-justify-start tw-pt-5 tw-text-center')
            if number_div:
                number_div = number_div.find('div',
                                             class_='tw-absolute tw-left-0 tw-top-0 tw-flex tw-h-full tw-w-[50px] tw-flex-col tw-justify-start tw-pt-5 tw-text-center')
                if number_div:
                    number_div = number_div.find('div',
                                                 class_='tw-min-w-[50px] tw-bg-[length:100%] tw-text-xl tw-font-bold tw-italic tw-leading-[30px]')
                    if number_div and number_div.string:
                        car_sale.number = number_div.string.strip()

            # Get the car name
            name_div = table.find('div', class_='tw-flex tw-flex-col tw-whitespace-nowrap')
            if name_div:
                name_div = name_div.find('div',
                                         class_='tw-text-nowrap tw-text-lg tw-font-medium hover:tw-text-[#ff6600]')
                if name_div and name_div.string:
                    car_sale.name = name_div.string.strip()

            # Get the car sales
            sales_div = table.find('div',
                                   class_='tw-mx-4 tw-flex tw-flex-col tw-items-center tw-whitespace-nowrap xl:tw-mx-[92px]')
            if sales_div is None:
                print("未找到 sales_div 元素")
                continue
            sales_sub_div = sales_div.find('div', class_='tw-mb-0.5 tw-flex tw-items-center')
            if sales_sub_div is None:
                print("未找到 sales_sub_div 元素")
                continue
            sales_span = sales_sub_div.find('span')
            if sales_span is None:
                print("未找到 sales_span 元素")
                continue
            if sales_span.string:
                car_sale.sales = sales_span.string.strip()
            else:
                print("sales_span 元素没有文本内容")

            ls.append(car_sale)
        return ls


    def writeCSV(ls):
        file_name = 'car_sales_2025{month}.csv'.format(month=month)
        with open(file_name, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['排名', '车名', '销量', '月份'])
            for car_sale in ls:
                writer.writerow([car_sale.number, car_sale.name, car_sale.sales, car_sale.month])


    html = getData(url=url, headers=headers)
    # print(html)
    ls = analyzeData(html)
    #print(ls)

    writeCSV(ls)


