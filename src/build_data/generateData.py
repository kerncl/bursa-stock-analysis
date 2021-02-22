# default library
import logging
import os
import re
import csv
from datetime import datetime
from urllib.request import Request, urlopen
from collections import OrderedDict

# 3rd party library
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Internal Script
from src.tools.error import *


klse_url = 'https://www.klsescreener.com'
i3investor_url = 'https://klse.i3investor.com/'

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
    executable_path = os.path.abspath(r'../../external file/chromedriver.exe')  #todo: Pathlib to handle it
    driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
    driver.get(klse_url)
    logs.info('Loading KLSE web page')
    try:
        xpath_submit = "//input[@id='submit']"
        submit_button = driver.find_element_by_xpath(xpath=xpath_submit)
    except Exception as e:
        raise InvalidXpathException(f'Invalid Xpath: {e}')
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
    with open('stock_list.csv', mode='w', newline='') as f:     # todo: generate csv at temp folder
        writer = csv.writer(f)  # todo: revisit csv with generator method (ref: cookbook v3)
        writer.writerow(['Code', 'Company', 'Company name', 'Category', 'Market', 'EPS', 'NTA', 'PE', 'DY', 'ROE',
                         'Market capital'])
        for index, row_data in enumerate(stock_tb_list):    # todo: can improve the speed by threading / multiprocessing ?
            code = str(row_data.find(attrs={'title': 'Code'}).text)
            if re.search(r'[A-Z]', code) or len(code) > 4:
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
            logs.info(
                f'{index + 1}\t{code},{company},{company_name},{category},{market.strip()},{EPS},{NTA},{PE},{DY},{ROE},{Market_cap}')
            writer.writerow([code, company, company_name, category, market.strip(), EPS, NTA, PE, DY, ROE, Market_cap])
            # stock news
            # news_list = web_scrapping_news(code)
            # [logs.info(f"tile: {news['news_title']}, date = {news['news_date']} source: {news['news_source']} \n link: {news['news_link']}") for news in news_list]
            # print(f'tile: {news_title}')


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
    for platform in ('klse', 'i3investor'):
        platform_url = globals().get(platform + '_url')
        if platform == 'klse':
            platform_news_url = f'{platform_url}/v2/news/stock/{code}'
        elif platform == 'i3investor':
            platform_news_url = f'{platform_url}servlets/stk/{code}.jsp'

        try:
            req = Request(url=platform_news_url, headers={'user-agent':'my-app'})
            data = urlopen(req)
        except Exception:
            raise WebAccessException(f'unable to access {platform_news_url} webpage')

        html = BeautifulSoup(data, 'lxml')
        news_list = []

        if platform == 'klse' and html.text:
            for article_lxml in html.findAll(name='div', attrs={'class': 'article flex-1'}):
                news_dic = {}
                news_lxml = article_lxml.find(name='div', attrs={'class': 'item-title'})
                date_lxml = article_lxml.find(name='div', attrs={'class': 'item-title-secondary subtitle'}).findAll(
                    name='span')
                news_title = news_lxml.text
                if re.search("[\u4e00-\u9FFF]", news_title) or re.search(r"\\u", news_title):  # chinese news
                    continue
                news_dic['title'] = news_title
                news_dic['link'] = klse_url + news_lxml.a.attrs['href']
                news_dic['source'] = date_lxml[0].text
                news_dic['date'] = date_lxml[1].attrs['data-date'].split(' ')[0]
                logs.info("title: {title},source: {source}, date: {date}\nlink: {link}, " .format_map(news_dic))    # todo: log handling when import module
                news_list.append(news_dic)
        elif platform == 'i3investor' and html.text:
            for article_lxml in html.find(id='nbTable').tbody.findAll(name='tr'):
                news_dic = {}
                news_title = article_lxml.findAll(name='td')[1].text
                if re.search("[\u4e00-\u9FFF]", news_title) or re.search(r"\\u", news_title):  # chinese news
                    continue
                news_dic['date'] = article_lxml.findAll(name='td')[0].text
                news_dic['title'] = news_title
                news_dic['link'] = i3investor_url + article_lxml.findAll(name='td')[1].a.attrs['href']
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
    exit(0)
