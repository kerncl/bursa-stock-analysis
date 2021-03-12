# default library
from collections import OrderedDict
from collections.abc import MutableMapping
from urllib.request import Request, urlopen
from pprint import pprint
import json
import re

# 3rd party library
from bs4 import BeautifulSoup

# Internal Script
from src.tools.error import *
from src.tools.DataStructure import *


class FinanceData(MutableMapping):

    def __init__(self, dic=None):
        if not dic:
            dic = {}
        self.__data = OrderedDict(dic)  # json-like dictionary

    # def __repr__(self):
    #     return str(self.__data.keys())

    def __str__(self):
        return json.dumps(self.__data, indent=4)

    def __getitem__(self, item):
        return self.__data[item]

    def __setitem__(self, key, value):
        if not re.search(r'[0-9]{2}-[A-Z][a-z]{2}-[0-9]{4}', key):  # key: DD-MM-YYYY
            raise FinancialDataErrorException("Invalid Key format, correct format should be DD-MMM-YYYY")  # todo: custom exception
        if not isinstance(value, list): # value is a list
            raise FinancialDataErrorException("Invalid Value format")
        if key in self.__data:
            self.__data[key].extend(value)
        else:
            self.__data[key] = value

    def __delitem__(self, key):
        del self.__data[key]

    def __iter__(self):
        yield from self.__data

    def __len__(self):
        return len(self.__data)

    def pop(self, key):
        self.__data.pop(key)

    def clear(self) -> None:
        self.__data.clear()

    def __copy__(self):
        return self.__data.copy()

    def update(self, *args, **kwargs) -> None:
        if len(args) > 1:
            raise TypeError(f'Expected 1 args, but received {len(args)}')
        if args:
            for annual_report, quarter in dict(args[0]):
                self[annual_report] = quarter
        for annual_report, quarter in kwargs.items():
            self[annual_report] = quarter

    def items(self):
        yield from self.__data.items()

    @staticmethod
    def parser(**kwargs):
        finance_data = {}
        report_data = {}
        annual_report = kwargs.pop('F.Y.')
        quarter = kwargs.pop('#')
        report_data.update({f'{quarter}': kwargs})
        finance_data.update({annual_report: [report_data]})
        return finance_data.copy()


# {
#     '31-Dec-2020':[
#                 '1': {
#                         'ROE': 10,
#                             ...
#                     },
#                 '2':{
#                         'ROE': 10,
#                           ...
#                         }],
#     '31-Aug-2020':[
#                 '1':{
#                         'ROE': 10,
#                             ...
#                     },
#                 '2':{
#                         'ROE': 10,
#                           ...
#                         }],
#         ...
# }

class QuarterResult:
    pass


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
        quarter_result = OrderedDict()  # todo: wrote a custom Object class to handle quarter result
        finance_data = FinanceData()
        for row in table_content.findAll(name='tr')[1:]:
            for key in row.findAll(name='th'):
                temp_key.append(key.text.rstrip().strip())  # Obtain key in list
            for key, value in zip(temp_key, row.findAll(name='td')):
                if key in ('F.Y.', 'Ann. Date', 'Quarter', 'Revenue',
                           'PBT', 'NP', 'EOQ DY', 'NP Margin',
                           'ROE', 'DPS', 'QoQ', 'YoY', 'EPS', '#'):
                    quarter_result[key] = value.text.rstrip().strip()
            if quarter_result:
                json_format = FinanceData.parser(**quarter_result)
                finance_data.update(**json_format)
                self.quarter_report_list.append(quarter_result.copy())
        return finance_data
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
# json format
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


# json format
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


# json format
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
    finance = stock.finance_result()
    for annual, quarter_list in finance.items():
        print(f'*** {annual} ***')
        for quarter in quarter_list:
            for num, fin in quarter.items():
                print(num, fin)
    stock._to_json()
