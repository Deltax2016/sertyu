import requests # Загрузка новостей с сайта.
from bs4 import BeautifulSoup # Превращалка html в текст.
import re # Регулярные выражения.



def getOneLentaArticle(url):
    """ getLentaArticle gets the body of an article from Lenta.ru"""
    # Получает текст страницы.
    resp=requests.get(url)
    # Загружаем текст в объект типа BeautifulSoup.
    bs=BeautifulSoup(resp.text, "html5lib") 
    # Получаем заголовок статьи.
    aTitle=bs.h2.text.replace("\xa0", " ")
    # Получаем текст статьи.
    anArticle=BeautifulSoup(" ".join([p.text for p in bs.find_all("p")]), "html5lib").get_text().replace("\xa0", " ")
    return aTitle, anArticle

print(getOneLentaArticle("http://pillsman.org/1034-klomifencitrat.html")[0])
print(getOneLentaArticle("http://pillsman.org/1034-klomifencitrat.html")[1])


from flask import Flask, request, json, g
#from pars import parse

app = Flask(__name__)

# r=requests.post('http://melkor.pythonanywhere.com/get', json={'list':[id1, id2, id$
@app.route('/get', methods=['GET', 'POST'])
def get():
    if request.method == 'POST':
        f = open('bd.txt', 'w')
        f.write(str(request.json['list'])) # замени id на что надо, каждый post запр$
        return 'ok'
    else:
        return "Постом запрос делай"



@app.route('/')
def index():
	def index():
    f = open('bd.txt', 'r')
    t=f.read()
    return t

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=6000, threaded=True)


