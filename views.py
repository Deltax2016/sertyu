from flask import request, abort, g, current_app
from app.message_new import main
import app.message_new
from app import app
import datetime
from app.models import User, session, Base, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Cities
from sqlalchemy.ext.declarative import declarative_base
import logging
import xlsxwriter
from flask import json
import requests
import csv

# okey to xsl

@app.route('/Armybot', methods=['POST','GET'])
def bot():
    if request.method == 'POST':
        data = request.json
        if data is None:
            return abort(404)
        if data.get('type') == 'confirmation':
            return app.config['VK_CONFIRM_CODE']
        g.data = data['object']
        if data['type'] == 'message_new':
            main()
    return 'ok'

@app.route('/xls', methods=['GET'])
def xls():
    workbook = xlsxwriter.Workbook('partners.xlsx')
    worksheet = workbook.add_worksheet()
    i = 0
    worksheet.write(0, 0, 'ID пользователя')
    worksheet.write(0, 1, 'Временная зона(МСК)')
    worksheet.write(0, 2, 'Партенерская ссылка')
    worksheet.write(0, 3, 'Баллы')
    worksheet.write(0, 4, 'Баллы за утро')
    worksheet.write(0, 5, 'Баллы за вечер')
    worksheet.write(0, 6, 'Баллы за активность')
    worksheet.write(0, 7, 'Дата начала игры')
    worksheet.write(0, 8, 'email')
    for us in session.query(User):
        i+=1
        worksheet.write(i, 0, us.uid)
        worksheet.write(i, 1, us.timezone)
        worksheet.write(i, 2, us.partner_id)
        worksheet.write(i, 3, us.points)
        worksheet.write(i, 4, us.points_mor)
        worksheet.write(i, 5, us.points_eve)
        worksheet.write(i, 6, us.points_act)
        worksheet.write(i, 7, us.start_date)
        worksheet.write(i, 8, us.email)
    workbook.close()
    return 'ok'

@app.route('/parse', methods=['GET'])
def parse():
    l = []
    for name in session.query(User):
        l.append(name.uid)
    r = requests.post('http://127.0.0.1:8765/get', json={'list':l})
    logging.error(r.text)

    return 'ok'


def text(text):
    name = text
    w = nltk.word_tokenize(name)
    if len(w)>=15:
        return 'Твой отчёт принят. Посмотрю, что ты там натворил, как только закончу свои бобриные дела.'
    else:
        return 'Ты что-то делаешь не так. Твой отчёт нечитабилен.'

@app.route('/new_user', methods=['GET'])
def add():
    uid = int(request.args.get('user_id'))
    refer = str(request.args.get('refer'))

    try:
        query = session.query(User).filter(User.uid == uid).first()
        logging.error(query.timezone)
        return 'exists'
    except AttributeError:
        session.add(User(uid,0,15,1,0,refer,0,0,0,0,datetime.datetime.now().date(),'',0,0,0,0))
        session.commit()
    return 'ok'

@app.route('/clear', methods=['GET'])
def clear():
    session.query(User).delete()
    session.commit()
    return 'ok'

@app.route('/mess', methods=['GET'])
def mess():
    api = current_app.vk_api
    filepath = r"txt.csv"
    arr1 = []
    with open(filepath, "r",encoding='utf-8', newline="") as file:
    #читаем файл целиком
        reader = csv.reader(file)
        for row in reader:
            cur_arr = row[5].split(';')
            arr1.extend([cur_arr])
    l = int(request.args.get('arg'))
    timezone = int(request.args.get('timezone'))
    for us in session.query(User).filter(User.timezone==timezone):
        if not us.uid == 0 and us.bot_activated:
            if (datetime.now().hour + 3+us.timezone)>=24:
                date = datetime.datetime.now().date()+datetime.timedelta(1)
            elif (datetime.now().hour + 3+us.timezone)<0:
                date = datetime.datetime.now().date()-datetime.timedelta(1)
            else:
                date = datetime.datetime.now().date()
            k = (us.start_data-date).days
            if k!=0 and (l!=6 or us.resp!=0):
                api.messages.send(user_id=us.uid, message=arr1[((k-1)*6)+(l-1)+3][0])
            if l==6 and k==7:
                us.bot_activated = 0
            if l==2:
                us.resp = 0
    return 'oi'

@app.route('/response', methods=['POST'])
def resp():
    api = current_app.vk_api
    logging.error('okes')
    jsonn = request.json
    for name in session.query(User):
        if jsonn['likes'][name.uid]>=5:
            name.points =name.points + 1
            name.points_act =name.points_act + 1
        if jsonn['comments'][name.uid]>=3:
            name.points =name.points + 1
            name.points_act =name.points_act + 1
        if jsonn['reposts'][0][name.uid]>0:
            name.points =name.points + 1
            name.points_act =name.points_act + 1
        if jsonn['reposts'][1][name.uid]>0:
            name.points =name.points + 1
            name.points_act =name.points_act + 1
    return 'oi'

@app.route('/add_city', methods=['GET'])
def add_city():
    city = request.args.get('city')
    offset = int(request.args.get('offset'))
    session.add(Cities(city,offset))
    session.commit()
    return 'ok'
# 2) in okey.db
def check_city(city):
    try:
        query = session.query(Cities).filter(Cities.city == city).first()
        return str(query.offset)
    except AttributeError:
        return 'nope'
# 1.1) directly to bd - okey.dy
def check_user(uid):
    try:
        query = session.query(User).filter(User.uid == uid).first()
        logging.error('exists '+str(query.uid))
        return 'exists'
    except AttributeError:
        logging.error('ok')
        return 'ok'
# 1.2) add a new user
def insert(uid):
    try:
        query = session.query(User).filter(User.uid == uid).first()
        logging.error('exists '+str(query.uid))
        return 'exists'
    except AttributeError:
        session.add(User(uid,0,0,1,0,'0',0,0,0,0,datetime.datetime.now().date(),'',0,0,0,0))
        session.commit()
        logging.error('ok')
        return 'ok'
# to watch city list
@app.route('/city_list', methods=['GET'])
def city_list():
    s = ''
    for name in session.query(Cities):
        s += str(name.city) +' '+ str(name.offset) + '<br>'
    return s
# list of users
@app.route('/list', methods=['GET'])
def list():
    s = ''
    for name in session.query(User):
        s += str(name.uid) +' '+ str(name.partner_id) + ' '+ str(name.points) +' '+str(name.start_date)+' '+str(name.timezone)+'<br>'
    return s

@app.errorhandler(500)
def internal_error(e):
    return 'ok'

@app.route('/add_points', methods=['GET'])
def add_points():
    uid = int(request.args.get('uid'))
    query = session.query(User).filter(User.uid == uid).first()
    query.points_act=query.points_act+1
    query.points = query.points+1
    logging.error('ne zach '+str(query.uid))

    return 'zachisleno'

'''# creating tables
@app.before_first_request
def init_db(*args, **kwargs):
    session.add(Settings())
    session.commit()'''

@app.route('/init', methods=['GET'])
def init1_db(*args, **kwargs):
    Base.metadata.create_all(engine)
    return 'okes'