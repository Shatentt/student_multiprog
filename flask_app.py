import os

from flask import Flask, render_template, url_for, redirect

import requests
from bs4 import BeautifulSoup
from time import sleep
from fake_useragent import UserAgent

app = Flask(__name__)

HEADERS = {"User-Agent": UserAgent().random}
imgs_formulas_physics = []
imgs_formulas_math = {}


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
    themes_math = data_math.find('ul').text.split('\n')[1:-4]
    a = data_math.find_all('img')
    b = []
    for elem in a:
        b.append('https://educon.by' + elem.get('src'))
    imgs_formulas_math['Формулы сокращенного умножения'] = b[:9]
    imgs_formulas_math['Квадратное уравнение и формула разложения квадратного трехчлена на множители'] = b[9:17]
    imgs_formulas_math['Свойства степеней и корней'] = b[20:36]
    imgs_formulas_math['Формулы с логарифмами'] = b[36:49]
    imgs_formulas_math['Арифметическая прогрессия'] = b[49:54]
    imgs_formulas_math['Геометрическая прогрессия'] = b[54:60]
    imgs_formulas_math['Тригонометрия'] = b[60:100]
    imgs_formulas_math['Тригонометрические уравнения'] = b[100:113]
    imgs_formulas_math['Геометрия на плоскости (планиметрия)'] = b[113:169]
    imgs_formulas_math['Геометрия в пространстве (стереометрия)'] = b[169:183]
    imgs_formulas_math['Координаты'] = b[183:187]
    ###

    # physics
    url_physics = "https://educon.by/index.php/formuly/formfiz"
    response_physics = requests.get(url_physics, headers=HEADERS)
    sp_physics = BeautifulSoup(response_physics.text, 'lxml')
    data_physics = sp_physics.find('div', itemprop="articleBody")
    themes_physics = data_physics.find('ul').text.split('\n')[1:-2]
    a = data_physics.find_all('img')
    for elem in a:
        imgs_formulas_physics.append('https://educon.by' + elem.get('src'))
    ###
    return render_template('formulas.html', title='Темы', list_math=themes_math, list_physics=themes_physics)


@app.route('/formulas/<theme>')
def themes(theme):
    return render_template('theme.html', title=theme, theme=theme, list_math=imgs_formulas_math)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
