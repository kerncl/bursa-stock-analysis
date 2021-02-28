# default library
from collections import OrderedDict
from urllib.request import Request, urlopen

# 3rd party library
from bs4 import BeautifulSoup

# Internal Script
from src.tools.error import *
from src.tools.DataStructure import *


class Stock:
    URL = 'https://klse.i3investor.com/servlets/stk/fin/'
    code = FourDigitstr()

    def __init__(self, code):
        self.code = code
        url = Stock.URL + code + '.jsp'
        try:
            req = Request(url=url, headers={'user-agent': 'my-app'})
            data = urlopen(req)
        except Exception:
            raise WebAccessException(f'unable to access {url} webpage')
        self.html = BeautifulSoup(data, 'lxml')

    def stock_price(self):
        table_list = self.html.find(name='table', id='stockhdr').findAll(name='td')
        stock = {}
        for key, value in zip(table_list[:len(table_list) // 2], table_list[len(table_list) // 2:]):
            stock[key.text.rstrip().strip()] = value.text.rstrip().strip()
        stock['name'] = self.html.find(name='span', attrs={'class': 'stname'}).text
        return stock

    def finance_result(self):
        table_content = self.html.find(name='table', id='financialResultTable')
        quarter_report_list = []
        finance_data = OrderedDict()  # todo: wrote a custom container class
        for row in table_content.findAll(name='tr')[1:]:
            for key in row.findAll(name='th'):
                finance_data.update({key.text.rstrip().strip(): None})
            for key, value in zip(finance_data.keys(), row.findAll(name='td')):
                finance_data[key] = value.text.rstrip().strip()
            quarter_report_list.append(finance_data.copy())
        return quarter_report_list
        pass

    def _to_json(self):
        pass


if __name__ == '__main__':
    stock = Stock('1155')
    print(stock.stock_price())
    print(stock.finance_result())
