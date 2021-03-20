import os
import pathlib

# PATH
CHROME_EXECUTED_PATH = os.path.abspath('../../external file/chromedriver.exe')
CSV_PATH = str(pathlib.Path.home().parent.parent.joinpath('temp/stock_list.csv'))

# URL
KLSE_URL = 'https://www.klsescreener.com'
I3INVESTOR_URL = 'https://klse.i3investor.com/'
KLSE_CHART_URL = 'https://www.klsescreener.com/v2/charting/chart/'
TRADINGVIEW_CHART_URL = "https://www.tradingview.com/chart/?symbol=MYX%3A"