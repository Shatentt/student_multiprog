import os

from flask import Flask, render_template

import requests
from bs4 import BeautifulSoup
from time import sleep
from fake_useragent import UserAgent

app = Flask(__name__)

HEADERS = {"User-Agent": UserAgent().random}


@app.route("/")
def index():
    return render_template("main_page.html")


@app.route('/formulas')
def formulas():
    # math
    url_math = "https://educon.by/index.php/formuly/formmat"
    response_math = requests.get(url_math, headers=HEADERS)
    sp_math = BeautifulSoup(response_math.text, 'lxml')
    data_math = sp_math.find('div', itemprop="articleBody")
    themes_math = data_math.find('ul').text.split('\n')[1:-5]
    a = data_math.find_all('img')
    imgs_formulas_math = []
    for elem in a:
        imgs_formulas_math.append('https://educon.by' + elem.get('src'))
    ###

    # physics
    url_physics = "https://educon.by/index.php/formuly/formfiz"
    response_physics = requests.get(url_physics, headers=HEADERS)
    sp_physics = BeautifulSoup(response_physics.text, 'lxml')
    data_physics = sp_physics.find('div', itemprop="articleBody")
    themes_physics = data_physics.find('ul').text.split('\n')[1:-2]
    a = data_physics.find_all('img')
    imgs_formulas_physics = []
    for elem in a:
        imgs_formulas_physics.append('https://educon.by' + elem.get('src'))
    ###
    return render_template('formulas.html', title='Темы', list_math=themes_math, list_physics=themes_physics)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
