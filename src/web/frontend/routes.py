# Std Library
import pathlib

# 3rd Party Lib
from flask import Flask
from flask import render_template, request, jsonify

# Internal Script
from src.web.backend.forms import StockForm
from src.build_data.Conversion import GenerateDB
from src.database.table import Company, News
from src.build_data.generateData import web_scrapping_news
from src.build_data.finance import Stock


template_folder = pathlib.Path(__file__).parent.parent.joinpath('templates').__str__()
static_folder = pathlib.Path(__file__).parent.parent.joinpath('static').__str__()
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = 'bursa'
app.config['JSON_SORT_KEYS'] = False    # ignore key order during jsonify


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
        company = '%' + stockform.company.data + '%'    # todo: can be improve by using request.form generate with setattr()
        company_full_name = '%' + stockform.company_fullname.data + '%'     # todo: will be move to backend script
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
    # for platform, news_list in news.items():
    #     print(platform)
    #     print(news_list)
    # pass
    stock = Stock(code)
    return render_template('stock.html',
                           result=news,
                           finance=stock.finance_result(),
                           stock=stock)


@app.route('/stock/api', methods=['GET'])
def api():
    query_param = request.args
    code = query_param.get('code', None)
    if code:
        api_stock = Stock(code)
        return jsonify(stock=api_stock.name,
                       code=code,
                       price=api_stock.price,
                       finance=api_stock.finance_result())

    return f"<p>Unable related information," \
           f" we only support finance data by providing us stock code</p>"


@app.teardown_appcontext
def loaded(exception=None):
    # Session.remove()
    print('Loaded Completed')
    pass


@app.errorhandler(404)
def page_not_found(e):
    # handling 404 ERROR
    return "<h1>404</h1>" \
           "<p>The resource could not be found</p>", 404


if __name__ == '__main__':
    app.run(debug=True)
