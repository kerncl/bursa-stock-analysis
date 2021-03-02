# default library
from collections import OrderedDict
from urllib.request import Request, urlopen
from pprint import pprint

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
        self.quarter_report_list = []
        temp_key = []
        finance_data = OrderedDict()  # todo: wrote a custom container class
        for row in table_content.findAll(name='tr')[1:]:
            for key in row.findAll(name='th'):
                temp_key.append(key.text.rstrip().strip())
            for key, value in zip(temp_key, row.findAll(name='td')):
                if key in ('F.Y.', 'Ann. Date', 'Quarter', 'Revenue',
                               'PBT', 'NP', 'EOQ DY', 'NP Margin',
                               'ROE', 'DPS', 'QoQ', 'YoY', 'EPS'):
                    finance_data[key] = value.text.rstrip().strip()
            if finance_data:
                self.quarter_report_list.append(finance_data.copy())
        return self.quarter_report_list
        pass

    def _to_json(self):
        temp_annual_report = ''
        json_list = []
        json_yearly = OrderedDict()
        for row in self.quarter_report_list:
            if row['F.Y.'] != temp_annual_report:
                json_yearly.clear()
                temp_annual_report = row['F.Y.']
                json_yearly['Annual Report'] = temp_annual_report
                json_yearly['Quarter Report'] = []
            json_yearly['Quarter Report'].append({**row})
            json_list.append(json_yearly.copy())
        pprint(json_list, indent=4)
        pass
# [
#     {
#         'Annual Report':'31-Dec-2020',
#         'Quarter Report': [
#             {
#                 'Quarter': 'first',
#                 'ROE':10,
#                 'DIV':5
#             },
#             {
#                 'Quarter': 'second',
#                 'ROE':10,
#                 'DIV':5
#             },
#         ]
#     },
#     {
#         'Annual Report':'31-Dec-2019',
#         'Quarter Report': [
#             {
#                 'Quarter': 'first',
#                 'ROE':10,
#                 'DIV':5
#             },
#             {
#                 'Quarter': 'second',
#                 'ROE':10,
#                 'DIV':5
#             },
#         ]
#     }
# ]


if __name__ == '__main__':
    stock = Stock('1155')
    # print(stock.stock_price())
    stock.finance_result()
    stock._to_json()
