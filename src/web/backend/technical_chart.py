# default library
import os
from urllib.request import Request, urlopen

# 3rd Party Library
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Internal Script
from src.tools.error import *


def html_chart(code):
    tradingview_url = 'https://www.klsescreener.com/v2/charting/chart/'
    url = tradingview_url + code

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    print('Opening chrome')
    executable_path = os.path.abspath(r'../../external file/chromedriver.exe')  #todo: Pathlib to handle it
    print(executable_path)
    driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
    driver.get(url)
    print('Loading KLSE web page')
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tv_chart_container")))
    except Exception as e:
        raise WebLoadException(f'Web loading too slow .... out of time ... exiting code: {e}')
    data = driver.page_source
    html = BeautifulSoup(data, 'lxml')
    iframe = html.findAll(name='iframe')[0]
    print(iframe)
    driver.close()
    return iframe


if __name__ == '__main__':
    html = html_chart('1155')
    print()