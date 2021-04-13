# default library
import os
import pandas as pd
import base64
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
from matplotlib.figure import Figure
from urllib.request import Request, urlopen

# 3rd Party Library
import mpld3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Internal Script
from src.tools.error import *
from src.tools.globalvar import *
from src.build_data.finance import Stock
from src.web.frontend import routes


def technical_chart(code):
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


def finance_chart(df, stock_name, web=True):
    """
    Finance chart by using matplotlib and display on web
    Args:
        web (Boolean): Default True
        df (dataframe): Finance Result in dataframe format
        stock_name (str): stock name eg: KLSE: MAYBANK (1155)

    Returns:
        (str) Image of 64bit encoder text
    """
    million = 1000000   #todo: interactive matplotlib chart
    if web:
        fig = Figure(figsize=(16, 12))
        ax = fig.add_subplot(1, 1, 1)
    else:
        plt.figure(figsize=(16, 12))
        ax = plt.subplot(1, 1, 1)
    twin = ax.twinx()
    xaxis = df['quarter date']
    y_revenue = df['revenue'].div(million)
    y_NP = df['NP'].div(million)
    y_PBT = df['PBT'].div(million)
    y_NPM = df['NP Margin(%)'].mul(100)
    ax.plot(xaxis, y_revenue, color='red', linewidth=2, label='Quarter Revenue')
    ax.plot(xaxis, y_PBT, color='blue', linewidth=2, label='PBT')
    ax.plot(xaxis, y_NP, color='black', linewidth=2, label='NP')
    twin.plot(xaxis, y_NPM, color='green', linewidth=1, label='NP margin', linestyle='--')
    ax.legend(loc="upper left", fontsize=12)
    ax.set(xlabel='Date',
           ylabel='Price RM(million/x1000000) ',
           title=f'{stock_name} Finance Chart',
           xlim=[df['quarter date'].iloc[-1], df['quarter date'].iloc[0]]
           )
    twin.set_ylabel('Percentage (%)')
    twin.legend(loc='upper right', fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))  # set x-axis date formatter
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # set interval for x-axis
    ax.tick_params(left=False, bottom=False)
    ax.grid(b=True, linestyle='--', alpha=0.5)  # background grid
    ax.set_facecolor((.94, .95, .98))   # background colour

    if web:
        # save it to a temporary buffer
        buf = BytesIO()
        # html_str = mpld3.fig_to_html(fig)  # todo: save to html
        fig.savefig(buf, format='svg', bbox_inches='tight')
        temp_chart_html = os.path.join(routes.app.static_folder, 'temp_chart.html')
        with open(temp_chart_html, 'w') as f:   #todo: revisit
            mpld3.save_html(fig, f)
        # embed the result in the html output
        chart = base64.b64encode(buf.getbuffer()).decode('ascii')
        return chart
    plt.show()


if __name__ == '__main__':
    code = '1155'
    # technical chart
    # html = technical_chart(code)

    # finance chart
    stock = Stock(code)
    finance_data = stock.finance_result()
    df = finance_data.to_df()
    finance_chart(df=df, stock_name=stock.name), # web=False)