import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.table import Company, Base


class GenerateDB:
    def __init__(self, csv_file):
        # read csv
        with open(csv_file, 'r') as f:
            row_data = csv.DictReader(f)
            self.csv_data = [row for row in row_data]

        # Initialize db
        db_file_path = os.path.abspath(r"../database/stock.db")
        self.engine = create_engine(f"sqlite:///{db_file_path}", echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

    def stock_main_table(self):
        if not self.engine.dialect.has_table(self.engine, 'company'):
            # table doesnt not exist
            insert_data_list = []
            for csv_row in self.csv_data:
                insert_data = Company(
                    code=csv_row['Code'],
                    company=csv_row['Company'],
                    company_name=csv_row['Company name'],
                    category=csv_row['Category'],
                    market=csv_row['Market'],
                    market_cap=float(csv_row['Market capital'])
                )
                insert_data_list.append(insert_data)
            self.session.add_all(insert_data_list)
            self.session.commit()
        else:
            # table exist
            print('Table already exists')
            for csv_row in self.csv_data:
                data = self.session.query(Company).filter(Company.code == csv_row['Code']).one_or_none()
                if not data:
                    # row doesnt exists
                    insert_data = Company(
                        code=csv_row['Code'],
                        company=csv_row['Company'],
                        company_name=csv_row['Company name'],
                        category=csv_row['Category'],
                        market=csv_row['Market'],
                        market_cap=float(csv_row['Market capital'])
                    )
                    self.session.add(insert_data)
                    self.session.commit()
                    continue
                if data.market_cap != float(csv_row['Market capital']):
                    self.session.query(Company)\
                        .filter(Company.code == csv_row['Code'])\
                        .filter(Company.company == csv_row['Company'])\
                        .filter(Company.company_name == csv_row['Company name'])\
                        .update({'market_cap': float(csv_row['Market capital'])})
                    self.session.commit()
                    continue
        self.session.close()


if __name__ == '__main__':
    csv_file = os.path.abspath('stock_list.csv')
    db = GenerateDB(csv_file)
    db.stock_main_table()
