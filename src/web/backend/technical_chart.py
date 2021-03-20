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
from src.tools.globalvar import *


def html_chart(code):
    """
    Obtain technical chart (HTML) from klsescreener website
    Args:
        code (4 digit string): Company code number

    Returns:
        HTML
    """
    url = KLSE_CHART_URL + code

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    print('Opening chrome')
    driver = webdriver.Chrome(executable_path=CHROME_EXECUTED_PATH, chrome_options=options)
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