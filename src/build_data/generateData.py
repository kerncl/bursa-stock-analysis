# default library
import logging
import os
import re
import csv
from time import sleep
from datetime import datetime
from urllib.request import Request, urlopen

# 3rd party library
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Internal Script
from src.tools.error import *
from src.tools.globalvar import *


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
    """
    Web access on KLSE main page and extract Malaysia Listed Company table
    Returns:
        data(html): return html form
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    logs.info('Opening chrome')
    driver = webdriver.Chrome(executable_path=CHROME_EXECUTED_PATH, chrome_options=options)
    driver.get(KLSE_URL)
    logs.info('Loading KLSE web page')
    sleep(2)
    try:
        xpath_submit = "//input[@id='submit']"
        submit_button = driver.find_element_by_xpath(xpath=xpath_submit)
    except Exception as e:
        logs.warning(f"xpath_submit: '{xpath_submit}' not working")
        logs.warning(f'Trying new xpath')
        try:
            xpath_submit = "//*[@id='submit']"
            submit_button = driver.find_element_by_xpath(xpath=xpath_submit)
        except:
            logs.error(f"xpath_submit: '{xpath_submit}' not working too ")
            raise InvalidXpathException(f'Invalid Xpath: {e}') from e
    submit_button.click()
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table-responsive")))
    except Exception as e:
        raise WebLoadException(f'Web loading too slow .... out of time ... exiting code: {e}')
    data = driver.page_source
    logs.info('Done extracting source ... closing chrome')
    driver.close()
    return data


def web_scrapping_stock(data):
    """
    extract Malaysia Listed Company into CSV (stock_list.csv)
    Args:
        data (html): html webpage from KLSE

    Returns:
        None
    """
    html = BeautifulSoup(data, 'lxml')
    stock_tb_list = html.find(name='tbody').findAll(name='tr')
    csv_file_name = datetime.today().date().__str__() + '_stock_list.csv'

    def _extract_data(row_data):
        stock_data = []
        code = str(row_data.find(attrs={'title': 'Code'}).text)
        company_name = row_data.find(name='td').attrs.get('title')
        if re.search(r'[A-Z]', code) or len(code) > 4 or not company_name:
            return stock_data
        match = re.match(r'(?P<company>[\w\d\-]+)', row_data.find(name='td').getText())
        company = match.group('company')
        category, market = row_data.find(attrs={'title': 'Category'}).text.split(',')
        stock_data.extend([code, company, company_name, category, market.strip()])
        for header in csv_header[csv_header.index('EPS'):]:
            stock_data.append(row_data.find(attrs={'title': header}).text)
        return stock_data
        pass

    with open(CSV_PATH, mode='w', newline='') as f:
        writer = csv.writer(f)
        csv_header = ('Code', 'Company', 'Company name', 'Category', 'Market', 'EPS', 'NTA', 'PE', 'DY', 'ROE',
                         'Market Capital')
        writer.writerow(csv_header)
        for index, stock_info in enumerate(map(_extract_data, stock_tb_list), 1):   # todo: can be improve with threading or multiprocessing ?
            if stock_info:
                logs.info(f'{index}: {stock_info}')
                writer.writerow(stock_info)


def web_scrapping_news(code):
    """
    Extract news information based on CODE given
    Args:
        code (int): Company Code (4 digit)

    Returns:
        dict list
    """
    #   todo: migrate to another script using class
    news_dic_list = {}
    for platform in ('KLSE', 'I3INVESTOR'):
        platform_url = globals().get(platform + '_URL') # get global var KLSE_URL / I3INVESTOR_URL
        if platform == 'KLSE':
            platform_news_url = f'{platform_url}/v2/news/stock/{code}'
        elif platform == 'I3INVESTOR':
            platform_news_url = f'{platform_url}servlets/stk/{code}.jsp'

        try:
            req = Request(url=platform_news_url, headers={'user-agent':'my-app'})
            data = urlopen(req)
        except Exception:
            raise WebAccessException(f'unable to access {platform_news_url} webpage')

        html = BeautifulSoup(data, 'lxml')
        news_list = []

        if platform == 'KLSE' and html.text:
            for article_lxml in html.findAll(name='div', attrs={'class': 'article flex-1'}):
                news_dic = {}
                news_lxml = article_lxml.find(name='div', attrs={'class': 'item-title'})
                date_lxml = article_lxml.find(name='div', attrs={'class': 'item-title-secondary subtitle'}).findAll(
                    name='span')
                news_title = news_lxml.text
                if re.search("[\u4e00-\u9FFF]", news_title) or re.search(r"\\u", news_title):  # chinese news
                    continue
                news_dic['title'] = news_title
                news_dic['link'] = KLSE_URL + news_lxml.a.attrs['href']
                news_dic['source'] = date_lxml[0].text
                news_dic['date'] = date_lxml[1].attrs['data-date'].split(' ')[0]
                logs.info("title: {title},source: {source}, date: {date}\nlink: {link}, " .format_map(news_dic))    # todo: log handling when import module
                news_list.append(news_dic)
        elif platform == 'I3INVESTOR' and html.text:
            for article_lxml in html.find(id='nbTable').tbody.findAll(name='tr'):
                news_dic = {}
                news_title = article_lxml.findAll(name='td')[1].text
                if re.search("[\u4e00-\u9FFF]", news_title) or re.search(r"\\u", news_title):  # chinese news
                    continue
                news_dic['date'] = article_lxml.findAll(name='td')[0].text
                news_dic['title'] = news_title
                news_dic['link'] = I3INVESTOR_URL + article_lxml.findAll(name='td')[1].a.attrs['href']
                news_dic['source'] = 'i3investor'
                news_list.append(news_dic)
                logs.info("title: {title},source: {source}, date: {date}\nlink: {link}, " .format_map(news_dic))    # todo: log handling when import module
        else:
            logs.warning(f'No source news found: {platform_news_url}')
        news_dic_list[platform] = news_list.copy()

    return news_dic_list


if __name__ == '__main__':
    data = web_access()
    web_scrapping_stock(data)
    # web_scrapping_news('1023')
    # web_scrapping_stockprice('1155')
    # web_scrapping_finance('1155')
    exit(0)
