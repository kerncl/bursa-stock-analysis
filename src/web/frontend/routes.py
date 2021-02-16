# Std Library
import pathlib

# 3rd Party Lib
from flask import Flask
from flask import render_template, request

# Internal Script
from src.web.backend.forms import StockForm
from src.build_data.Conversion import Session
from src.database.table import Company, News


template_folder = pathlib.Path(__file__).parent.parent.joinpath('templates').__str__()
app = Flask(__name__, template_folder=template_folder)
app.secret_key = 'bursa'


@app.route('/')
@app.route('/index')
def index():
    # app.logger.debug(app.config.get("ENV"))
    return render_template('index.html')


@app.route('/home', methods=['POST', 'GET'])
def search():
    stockform = StockForm(request.form)
    if request.method == 'POST':    # when submit has been clicked
        print('* Accessing POST Method')
        print(f'User enter:\nCompany: {stockform.company.data}\n '
              f'Company full name: {stockform.company_fullname.data}\n'
              f'Category: {stockform.category.data}\n'
              f'Market: {stockform.market.data}') # return data
        company = '%' + stockform.company.data + '%'    # todo: can be improve by using request.form generate with setattr()
        company_full_name = '%' + stockform.company_fullname.data + '%'
        category = stockform.category.data
        market = stockform.market.data
        # SQL select query
        session = Session()
        # SELECT * FROM company WHERE company LIKE '%%' AND company_name LIKE '%airasia%' AND category LIKE '%%' AND market LIKE '%Main%';
        stock_list = session.query(Company).filter(Company.company.like(company),
                                                   Company.company_name.like(company_full_name),
                                                   Company.category.like(category),
                                                   Company.market.like(market)).all()
        return render_template('home.html', form=stockform)
    elif request.method == 'GET':   # when loaded page
        print('* Accessing GET Method')
        return render_template('home.html', form=stockform)


@app.teardown_appcontext
def close_session(exception=None):  # todo: close session
    Session.remove()
    pass


if __name__ == '__main__':
    app.run(debug=True)


