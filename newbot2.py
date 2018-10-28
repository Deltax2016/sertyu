import cv2
import numpy as np
import tgflow as tgf
from tgflow import TgFlow as tgf_obj
from tgflow import handles as h
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from enum import Enum
import qrcode
#import main
import apiai, json
import requests
key='732129233:AAG263I7N91OyvR9Z1rLV5QtOjPDa1g6cbU'


class States(Enum):
    START=1
    INFO=2
    LOGIN=3
    PASS=4
    LOGGED=5
    QR=6
    

def stat(i,d):
    return States.LOGGED


def qr(i,d):
    img = qrcode.make(i.text)
    img.save("image.jpg")
    photo = open('image.jpg', 'rb')
    tgf_obj.bot.send_photo(i.message.chat.id,photo)
    l = i.text.split(',')
    s = []
    for u in l:
        w = {}
        w[u.split(' ')[0]] = int(u.split(' ')[1])
        s.append(w)
    requests.post('http://89.223.91.216:6000/get',json={'list':s})
    return States.LOGGED

def send_image(i,d):
	photo = open('wave.png', 'rb')
	tgf_obj.bot.send_photo(i.message.chat.id,photo)
	return States.LOGIN


def login(i,d):
	return States.PASS,{'login':i.text}


def check_user(i,login=None):
    check = 0
    passwd = i.text
    if login==0:
		check = 0
	else:
		if '123456'==i.text:
			check = 1
	if check:
		return States.LOGGED
	else:
		tgf_obj.bot.send_message(i.chat.id,'Неверный логин или пароль')
		return States.LOGIN


UI = {
    States.START:
    {'t':'Добрый день. Вас приветствует система HealthAI',
     'b': [
         {'Войти в систему':tgf.action(States.LOGIN)}],
         'react':h.action(qr, react_to='photo'),

    },
    States.LOGGED:{
        't':'Личный кабинет',
        'b':[ {'Сгенерировать QR':tgf.action(States.START)},
         {'Список пациентов':tgf.action(stat)},
        {'Выйти':tgf.action(States.START)},
        ]
    },
    States.QR:{
        't':'Отправьте список лекарств для пациента',
        'b':[ {'Назад':tgf.action(States.LOGGED)}],
        'react':h.action(qr, react_to='text'),
    },
    States.LOGIN:{
        't':'Введите логин',
        'react':h.action(login,
            react_to = 'text'),
    },
    States.PASS:{
        't':'Введите пароль',
        'react': h.action(check_user, react_to='text',update_msg=False)},
    }

tgf.configure(token=key,state=States.START,data={"foo":'bar'})
tgf.start(UI)