import os

from flask import Flask, render_template

import requests
from bs4 import BeautifulSoup
from time import sleep
from fake_useragent import UserAgent

app = Flask(__name__)

HEADERS = {"User-Agent": UserAgent().random}

url = "https://educon.by/index.php/formuly/formmat"
response = requests.get(url, headers=HEADERS)
sp = BeautifulSoup(response.text, 'lxml')
data = sp.find('div', itemprop="articleBody")
themes = data.find('ul').text.split('\n')[1:-5]


@app.route("/")
def index():
    return render_template("main_page.html")


@app.route('/formulas')
def formulas():
    return render_template('formulas.html', title='Формулы', list=themes)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
