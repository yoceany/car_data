import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# 年份和月份列表
year = '2025'
months = [f'{i:02d}' for i in range(1, 6)]  # 示例：1 到 5 月

# 类别及其对应链接部分
category_dict = {
    '轿车': '1-1-1%2C2%2C3%2C4%2C5%2C6',
    'SUV': '1-1-16%2C17%2C18%2C19%2C20',
    '新能源': '1-1-201908',
    'MPV': '1-1-21%2C22%2C23%2C24',
}

# 输出目录路径（可以修改）
output_dir = 'D:/大三下/25暑期实训/CarBigData/data_collection1/'

# 定义数据类，新增score和price字段
class CarSales:
    def __init__(self):
        self.category = ''
        self.month = ''
        self.number = ''
        self.name = ''
        self.sales = ''
        self.score = ''      # 口碑评分
        self.price = ''      # 价格区间

def get_html(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    service = Service(r'D:\Tools\ChromeDriver\chromedriver-win64\chromedriver.exe')  # 请替换为你的路径
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(3)  # 等待加载
        return driver.page_source
    finally:
        driver.quit()

def parse_html(html, category, year, month):
    soup = BeautifulSoup(html, 'lxml')
    result = []
    blocks = soup.select('div.tw-relative.tw-cursor-pointer.tw-rounded.tw-border-b.tw-bg-white.tw-pr-4')

    for block in blocks:
        car = CarSales()
        car.category = category
        car.month = f"{year}-{month}"

        num = block.select_one('div.tw-text-xl')
        name = block.select_one('div.tw-text-nowrap.tw-text-lg')
        sales_div = block.find('div', class_='tw-mb-0.5')
        sales = sales_div.find('span').get_text(strip=True) if sales_div and sales_div.find('span') else ''

        # 新增：口碑评分 - 查找对应class或标签（假设用tw-text-green之类标记，需根据真实页面调整）
        score_tag = block.select_one('strong.tw-font-bold')
        score = score_tag.get_text(strip=True) if score_tag else ''

        # 新增：价格区间 - 假设价格信息在某个class为priceinfo的标签里（需按实际页面改）
        price = ''
        for tag in block.select('div.tw-font-medium[class*="tw-text-"]'):
            text = tag.get_text(strip=True)
            if '-' in text and '万' in text:
                price = text
                break

        car.number = num.get_text(strip=True) if num else ''
        car.name = name.get_text(strip=True) if name else ''
        car.sales = sales
        car.score = score
        car.price = price

        result.append(car)

    return result

def save_to_csv(car_list, category, year, month):
    output_path = f"{output_dir}{category}_{year}-{month}.csv"
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # 新增口碑评分和价格区间
        writer.writerow(['类别', '月份', '排名', '车型', '销量', '口碑评分', '价格区间'])
        for car in car_list:
            writer.writerow([car.category, car.month, car.number, car.name, car.sales, car.score, car.price])
    print(f'✔ 数据已保存到: {output_path}')

# 主程序入口
for category, path_segment in category_dict.items():
    for month in months:
        url = f'https://www.autohome.com.cn/rank/{path_segment}-0_9000-x-x-x/{year}-{month}.html'
        print(f'正在爬取：{url}')
        html = get_html(url)
        car_list = parse_html(html, category, year, month)
        save_to_csv(car_list, category, year, month)
