from sqlalchemy import create_engine
from sqlalchemy import String, Integer, Column, ForeignKey, FLOAT
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseTable:
    __tablename__ = 'Template'
    company = 'template'

    def __repr__(self):
        return f'<Table: {self.company}>'


class Company(Base, BaseTable):
    __tablename__ = 'company'
    code = Column(String, primary_key=True)
    company = Column(String, unique=True)
    company_name = Column(String, unique=True)
    category = Column(String)
    market = Column(String)
    market_cap = Column(FLOAT)


class News(Base, BaseTable):
    __tablename__ = 'news'
    code = Column(String, unique=True)
    comp = Column(String, ForeignKey('company.company'), primary_key=True)
    news_klse = Column(String)
    news_i3investor = Column(String)
    company = relationship('Company', back_populates='news')


Company.news = relationship('News', back_populates='company')

if __name__ == '__main__':
    engine = create_engine('sqlite:///template.db', echo=True)
    # Session = sessionmaker(bind=engine)
    Session = scoped_session(sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine))
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
        market_cap=17.96,
        news= [News(code='0141'
                    , news_klse='https://www.klsescreener.com/v2/news/stock/0141',
                    news_i3investor='https://klse.i3investor.com/servlets/stk/0141.jsp')]
    )
    session.add(data1)
    session.commit()
    session.close()
