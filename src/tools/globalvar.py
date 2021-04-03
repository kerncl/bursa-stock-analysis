import os
import pathlib


# URL
KLSE_URL = 'https://www.klsescreener.com'
I3INVESTOR_URL = 'https://klse.i3investor.com/'
KLSE_CHART_URL = 'https://www.klsescreener.com/v2/charting/chart/'
TRADINGVIEW_CHART_URL = "https://www.tradingview.com/chart/?symbol=MYX%3A"

# PATH  # todo: script to verify path, subprocess to handle if no file found ?
CHROME_EXECUTED_PATH = os.path.abspath('../../external file/chromedriver.exe')
CSV_PATH = str(pathlib.Path.home().parent.parent.joinpath('temp/stock_list.csv'))
DB_PATH = os.path.abspath('../database/stock.db')

if not os.path.exists(CSV_PATH):
    from src.build_data import Conversion
    Conversion.GenerateDB.update_csv()
    Conversion.GenerateDB.renew_table(CSV_PATH)
    print(f'Done generate CSV & DB')