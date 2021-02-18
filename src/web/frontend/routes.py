# Std Library
import pathlib

# 3rd Party Lib
from flask import Flask
from flask import render_template, request

# Internal Script
from src.web.backend.forms import StockForm
from src.build_data.Conversion import GenerateDB
from src.database.table import Company, News
from src.build_data.generateData import web_scrapping_news


template_folder = pathlib.Path(__file__).parent.parent.joinpath('templates').__str__()
static_folder = pathlib.Path(__file__).parent.parent.joinpath('static').__str__()
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = 'bursa'


@app.route('/')
@app.route('/index')
def index():
    # app.logger.debug(app.config.get("ENV"))
    return render_template('index.html')


@app.route('/home', methods=['POST', 'GET'])
def search():
    stockform = StockForm(request.form)
    if request.method == 'POST':  # when submit has been clicked
        print('* Accessing POST Method')
        print(f'User enter:\nCompany: {stockform.company.data}\n '
              f'Company full name: {stockform.company_fullname.data}\n'
              f'Category: {stockform.category.data}\n'
              f'Market: {stockform.market.data}')  # return data
        company = '%' + stockform.company.data + '%'  # todo: can be improve by using request.form generate with setattr()
        company_full_name = '%' + stockform.company_fullname.data + '%'
        category = stockform.category.data
        market = stockform.market.data
        # SQL select query
        with GenerateDB() as session:
            # SELECT * FROM company WHERE company LIKE '%%' AND company_name LIKE '%airasia%' AND category LIKE '%%' AND market LIKE '%Main%';
            stock_list = session.query(Company).filter(Company.company.like(company),
                                                       Company.company_name.like(company_full_name),
                                                       Company.category.like(category),
                                                       Company.market.like(market)).all()
        return render_template('searchresult.html', form=stockform, result=stock_list)
    elif request.method == 'GET':  # when loaded page
        print('* Accessing GET Method')
        return render_template('home.html', form=stockform)


@app.route('/stock/<code>', methods=['GET'])
def stock(code):  # code obtain from url_for **kwargs
    with GenerateDB() as session:
        news_data = session.query(News).filter(News.code == code).one_or_none()
        print(news_data)
    news = web_scrapping_news(code)
    for platform, news_list in news.items():
        print(platform)
        print(news_list)
    pass
    return render_template('stock.html', result=news)
    # return f'<h>Stock Page: {code}</h>'


@app.teardown_appcontext
def loaded(exception=None):
    # Session.remove()
    print('Loaded Completed')
    pass


if __name__ == '__main__':
    app.run(debug=True)
