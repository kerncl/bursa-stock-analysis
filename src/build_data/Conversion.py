# std library
import os
import sys
import csv
import subprocess
import threading

# 3rd party library
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Internal Script
from src.database.table import Base, Company, News
from src.tools.globalvar import *


class GenerateDB:
    """
    Handling on SQL DB
    """
    def __init__(self, csv_file=None):
        """
        Initialize and connect to DB
        Args:
            csv_file (path): csv full path
            echo (bool): Echo on SQL engine
        """
        # read csv
        if csv_file:
            self._f = open(csv_file, 'r')
            self.csv_data = csv.DictReader(self._f)

    def __enter__(self):
        # Initialize db
        self.engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
        Session = scoped_session(sessionmaker(autocommit=False,
                                              autoflush=False,
                                              bind=self.engine))
        # Session =  sessionmaker(bind=engine)
        self.session = Session()
        return self.session
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        if getattr(self, 'csv_data', None):
            self._f.close()
        pass

    def update_table(self):
        """
        Update DB table based on below 3 case:
        1. Table doesnt exist
        2. Company doesnt exist in the table
        3. Company Market value increased
        Returns:
            None
        """
        if not self.engine.dialect.has_table(self.engine, 'company'):
            # company table doesnt not exist
            Base.metadata.create_all(self.engine)  # Create all table
            insert_data_list = []
            for csv_row in self.csv_data:
                insert_data = Company(
                    code=csv_row['Code'],
                    company=csv_row['Company'],
                    company_name=csv_row['Company name'],
                    category=csv_row['Category'],
                    market=csv_row['Market'],
                    market_cap=float(csv_row['Market Capital']),
                    news=[News(code=csv_row['Code'],
                               news_klse='https://www.klsescreener.com/v2/news/stock/{Code}'.format_map(csv_row),
                               news_i3investor='https://klse.i3investor.com/servlets/stk/{Code}.jsp'.format_map(csv_row))]
                )
                insert_data_list.append(insert_data)
            self.session.add_all(insert_data_list)
            self.session.commit()
        else:
            # company table exist
            print('Table already exists')
            for csv_row in self.csv_data:
                data = self.session.query(Company).filter(Company.code == csv_row['Code']).one_or_none()
                if not data:
                    # Company doesnt exist
                    insert_data = Company(
                        code=csv_row['Code'],
                        company=csv_row['Company'],
                        company_name=csv_row['Company name'],
                        category=csv_row['Category'],
                        market=csv_row['Market'],
                        market_cap=float(csv_row['Market Capital']),
                        news=[News(code=csv_row['Code'],
                                   news_klse='https://www.klsescreener.com/v2/news/stock/{Code}'.format_map(csv_row),
                                   news_i3investor='https://klse.i3investor.com/servlets/stk/{Code}.jsp'.format_map(csv_row))]
                    )
                    self.session.add(insert_data)
                    self.session.commit()
                    continue
                if data.market_cap != float(csv_row['Market Capital']):
                    # Market value changes
                    self.session.query(Company)\
                        .filter(Company.code == csv_row['Code'])\
                        .filter(Company.company == csv_row['Company'])\
                        .filter(Company.company_name == csv_row['Company name'])\
                        .update({'market_cap': float(csv_row['Market Capital'])})
                    self.session.commit()
                    continue

    @staticmethod
    def update_csv():
        """
        Staticmethod to update csv file
        Returns:
            None
        """
        def real_time_output(process):
            for line in iter(process.stdout.readline, b''):
                line = line.decode().rstrip()
                print(line)

        p = subprocess.Popen([sys.executable, 'generateData.py'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        t = threading.Thread(target=real_time_output, args=(p,), name='log_info')
        t.start()
        p.wait()    # Waiting thread to executed finish
        err = p.communicate()[1]  # wait until return code
        if err:
            err = err.decode()
            print(f'Generate CSV processing error: {err}')
        print(f'Executed finish with exitcode: {p.returncode}')
        t.join()
        pass

    @classmethod
    def renew_table(cls, csv_file):
        """
        Clear existing table and update the table
        Returns:
            None
        """
        # cls.update_csv()  # update csv from staticmethod
        self = cls(csv_file)    # execute __init__
        with self:  # call __enter__ and __exit__
            if self.engine.dialect.has_table(self.engine, 'company'):
                Base.metadata.drop_all(bind=self.engine, tables=[Company.__table__, News.__table__])
            self.update_table()
        return self


if __name__ == '__main__':
    # csv_file = os.path.abspath('stock_list.csv')
    GenerateDB.update_csv()
    db = GenerateDB.renew_table(CSV_PATH)
    # db = GenerateDB(csv_file)
    # db.stock_main_table()
