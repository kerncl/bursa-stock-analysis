# Std Library
import pathlib

# 3rd Party Lib
from flask import Flask
from flask import render_template, request

# Internal Script
from src.web.backend.forms import StockForm


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
        print(f'User enter:\nCompany: {stockform.company.data}\n Company full name: {stockform.company_fullname.data}') # return data
        # SQL select query
        # select * from company where company like '%%' and company_name like '%airasia%' and category like '%%' and market like '%Main%';
        return render_template('home.html', form=stockform)
    elif request.method == 'GET':   # when loaded page
        print('* Accessing GET Method')
        return render_template('home.html', form=stockform)


if __name__ == '__main__':
    app.run(debug=True)


