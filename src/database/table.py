from sqlalchemy import create_engine
from sqlalchemy import String, Integer, Column, ForeignKey, FLOAT
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Company(Base):
    __tablename__ = 'company'
    code = Column(String, primary_key=True)
    company = Column(String, unique=True)
    company_name = Column(String, unique=True)
    category = Column(String)
    market = Column(String)
    market_cap = Column(FLOAT)


if __name__ == '__main__':
    engine = create_engine('sqlite:///template.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)
    session.query(Company)
    data1 = Company(
        code='0141',
        company='WINTONI',
        company_name='WINTONI GROUP BERHAD',
        category='Technology',
        market='Ace Market',
        market_cap=17.96
    )
    session.add(data1)
    session.commit()
    session.close()
