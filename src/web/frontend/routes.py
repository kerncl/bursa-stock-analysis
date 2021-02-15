# Std Library
import pathlib

# 3rd Party Lib
from flask import Flask
from flask import render_template

template_folder = pathlib.Path.cwd().parent.joinpath('templates').__str__()
app = Flask(__name__, template_folder=template_folder)


@app.route('/')
@app.route('/index')
def index():
    # app.logger.debug(app.config.get("ENV"))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)


