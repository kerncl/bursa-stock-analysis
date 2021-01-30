# default library
import logging
import os
import sys
import re
import csv
from datetime import datetime

# 3rd party library
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


klse_url = 'https://www.klsescreener.com/v2/'


format = logging.Formatter(fmt='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y%m%d-%H:%M:%S')

logs = logging.getLogger('stock_list')
logs.setLevel(logging.INFO)
handler = logging.FileHandler(filename='stock_list.log', mode='w')
handler.setFormatter(format)

logs_stream = logging.StreamHandler()
logs_stream.setLevel(logging.INFO)
logs_stream.setFormatter(format)

logs.addHandler(logs_stream)
logs.addHandler(handler)


def web_access():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    logs.info('Opening chrome')
    driver = webdriver.Chrome(executable_path=r'../../external file/chromedriver.exe', chrome_options=options)
    driver.get(klse_url)
    logs.info('Loading KLSE web page')
    xpath_submit = "//*[@id='submit']"
    submit_button = driver.find_element_by_xpath(xpath=xpath_submit)
    submit_button.click()
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table-responsive")))
    except Exception as e:
        logs.error(f'Error: {e}')
        logs.error('Web loading too slow .... out of time ... exiting code')
        sys.exit(1)
    data = driver.page_source
    logs.info('Done extracting source ... closing chrome')
    driver.close()
    return data


def web_scrapping_stock(data):
    html = BeautifulSoup(data, 'lxml')
    stock_tb_list = html.find(name='tbody').findAll(name='tr')
    csv_file_name = datetime.today().date().__str__() + '_stock_list.csv'
    with open('stock_list.csv', mode='w') as f:
        writer = csv.writer(f)
        writer.writerow(['Code', 'Company', 'Company name', 'Category', 'Market', 'EPS', 'NTA', 'PE', 'DY', 'ROE', 'Market capital'])
        for index, row_data in enumerate(stock_tb_list):
            code = row_data.find(attrs={'title': 'Code'}).text
            if re.search(r'[A-Z]', code):
                continue
            company_name = row_data.find(name='td').attrs.get('title')
            match = re.match(r'(?P<company>[\w\d\-]+)', row_data.find(name='td').getText())
            company = match.group('company')
            category, market = row_data.find(attrs={'title': 'Category'}).text.split(',')
            EPS = row_data.find(attrs={'title': 'EPS'}).text
            NTA = row_data.find(attrs={'title': 'NTA'}).text
            PE = row_data.find(attrs={'title': 'PE'}).text
            DY = row_data.find(attrs={'title': 'DY'}).text
            ROE = row_data.find(attrs={'title': 'ROE'}).text
            Market_cap = row_data.find(attrs={'title': 'Market Capital'}).text
            logs.info(f'{index+1}\t{code},{company},{company_name},{category},{market.strip()},{EPS},{NTA},{PE},{DY},{ROE},{Market_cap}')
            writer.writerow([code,company,company_name,category,market,EPS,NTA,PE,DY,ROE,Market_cap])
    return 0


if __name__ == '__main__':
    data = web_access()
    web_scrapping_stock(data)
