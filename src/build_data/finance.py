# default library
from collections import OrderedDict
from collections.abc import MutableMapping
from urllib.request import Request, urlopen
from pprint import pprint
from datetime import datetime
import json
import re
import pandas as pd

# 3rd party library
from bs4 import BeautifulSoup

# Internal Script
from src.tools.error import *
from src.tools.DataStructure import *


class FinanceData(MutableMapping, dict):

    def __init__(self, dic=None):
        if not dic:
            dic = {}
        self.__data = OrderedDict(dic)  # json-like dictionary

    def __repr__(self):
        return f"<{self.__class__} Number of Annual Report: {len(self)},object at {int(id(self))}>"

    def __str__(self):
        return json.dumps(self.__data, indent=4)

    def __getitem__(self, item):
        return self.__data[item]

    def __setitem__(self, key, value):
        if not re.search(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', key):  # key: YYYY-MM-DD
            raise FinancialDataErrorException("Invalid Key format, correct format should be DD-MMM-YYYY")
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

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    def to_df(self):    # todo: save as csv
        """
        Convert dict-like into dataframe structure
        Returns:
            df
        """
        overall_quarter = []
        header = ('annual', 'quarter no', 'announ date', 'quarter date', 'revenue',
                  'PBT', 'NP', 'NP Margin(%)', 'ROE(%)', 'EPS', 'DPS', 'QoQ(%)', 'YoY(%)',
                  'DY(%)')
        for annual, quarter_list in self.items():
            yyyy, mm, dd = annual.split('-')
            for quarter in quarter_list:
                for quarter_no, quarter_data in quarter.items():
                    quarter_ = []
                    quarter_.extend([datetime(int(yyyy), int(mm), int(dd)), int(quarter_no)])
                    for data in quarter_data.values():
                        quarter_.append(data)
                    overall_quarter.append(quarter_.copy())
        df = pd.DataFrame(overall_quarter, columns=header)
        return df

    def to_csv(self):
        """
        Convert to CSV
        Returns:
            CSV file
        """
        df = self.to_df()
        df.to_csv(index=False)
        pass

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

    def __setattr__(self, key, value):
        if key in ('F.Y.', 'Ann. Date', 'Quarter', 'Revenue',
                           'PBT', 'NP', 'EOQ DY', 'NP Margin',
                           'ROE', 'DPS', 'QoQ', 'YoY', 'EPS', '#'):

            if key in ('Revenue', 'PBT', 'NP', '#'):
                try:
                    value = int(value.replace(',', ''))
                except Exception as e:
                    raise FinancialDataErrorException(f'Key: {key}, Unable to convert to int: {e}')
            elif key in ('DPS', 'EPS'):
                try:
                    value = float(value)
                except Exception as e:
                    raise FinancialDataErrorException(f'Key: {key}, Unable to convert to float: {e}')
            elif key in ('Ann. Date', 'Quarter', 'F.Y.'):
                month_convertion = {
                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
                    'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                }
                dd, mm, yyyy = value.split('-')
                mm = month_convertion.get(mm.lower(), None)
                if key in ('Quarter', 'Ann. Date'):
                    try:
                        value = datetime(int(yyyy), int(mm), int(dd))
                    except Exception as e:
                        raise FinancialDataErrorException(f'Key: {key}, Unable to convert to datetime: {e}')
                else:
                    value = f'{yyyy}-{mm}-{dd}'
            elif key in ('NP Margin', 'ROE', 'QoQ', 'YoY', 'EOQ DY'):
                try:
                    value = value.replace(',', '')
                    value = round(float(value.strip('%'))/100,4)
                except Exception as e:
                    raise FinancialDataErrorException(f'Key: {key}, Unable to convert to float: {e}')

            super().__setattr__(key, value)

    def __repr__(self):
        return f"<{self.__class__}, Annual Report: {getattr(self,'F.Y.')}, Quarter: {getattr(self, '#')}: object at {int(id(self))}>"

    def __str__(self):
        txt = ''
        for key, value in self.__dict__.items():
            txt += f"{key}\t: {value}" + '\n'
        return txt

    def __len__(self):
        return len(self.__dict__)
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
        self._html = BeautifulSoup(data, 'lxml')
        self._stock_information()

    def _stock_information(self):
        table_list = self._html.find(name='table', id='stockhdr').findAll(name='td')
        for key, value in zip(table_list[:len(table_list) // 2], table_list[len(table_list) // 2:]):
            setattr(self, key.text.rstrip().strip().split(' ')[-1].lower(), value.text.rstrip().strip())    # turn into instance attribute
        setattr(self, 'name', self._html.find(name='span', attrs={'class': 'stname'}).text)

    def finance_result(self):
        table_content = self._html.find(name='table', id='financialResultTable')
        temp_key = []
        finance_data = FinanceData()
        for row in table_content.findAll(name='tr')[1:]:
            quarter_class = QuarterResult()
            for key in row.findAll(name='th'):
                temp_key.append(key.text.rstrip().strip())  # Obtain key in list
            for key, value in zip(temp_key, row.findAll(name='td')):
                value = value.text.rstrip().strip()
                setattr(quarter_class, key, value)
            if quarter_class:
                json_format = FinanceData.parser(**quarter_class.__dict__)
                finance_data.update(**json_format)
        return finance_data
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


if __name__ == '__main__':
    stock = Stock('1155')
    finance = stock.finance_result()
    for annual, quarter_list in finance.items():
        print(f'*** {annual} ***')
        for quarter in quarter_list:
            for num, fin in quarter.items():
                print(num, fin)
    df = finance.to_df()

