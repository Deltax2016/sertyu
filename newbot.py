import cv2
import numpy as np
import tgflow as tgf
from tgflow import TgFlow as tgf_obj
from tgflow import handles as h
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from enum import Enum
#import main
import apiai, json
import requests
key='735824473:AAFkT_eAnCl1eu8L3BaYIxbm7sKYlyDLxr0'


class States(Enum):
    START=1
    INFO=2
    LOGIN=3
    PASS=4
    LOGGED=5
    QR=6
    

def stat(i,d):
    return States.LOGGED

def qwer(i,d):
    raw = i.photo[2].file_id
    name = "pil.png"
    file_info = tgf_obj.bot.get_file(raw)
    downloaded_file = tgf_obj.bot.download_file(file_info.file_path)
    with open(name,'wb') as new_file:
        new_file.write(downloaded_file)
    image = 'pil.png'
    image = cv2.imread(image)
    kernel = np.ones((5,5),np.uint8)
    final_wide = 400
    r = float(final_wide)/image.shape[1]
    dim = (final_wide,int(image.shape[0]*r))
    resized = cv2.resize(image,dim,interpolation = cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.GaussianBlur(gray, (3,3),3)
    gray_tre2 = cv2.threshold(gray2, 20,255,cv2.THRESH_BINARY_INV)[1]
    dilation2 = cv2.dilate(gray_tre2,kernel,iterations = 2)
    im2, contours, hierarchy = cv2.findContours(dilation2, cv2.RETR_TREE ,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(resized, contours, -1, (0,255,0), 3)
    amount = len(contours)
    print(amount)
    return States.LOGGED

def qr(i,d):
    raw = i.photo[2].file_id
    name = "qr.png"
    file_info = tgf_obj.bot.get_file(raw)
    downloaded_file = tgf_obj.bot.download_file(file_info.file_path)
    with open(name,'wb') as new_file:
        new_file.write(downloaded_file)
    tgf_obj.bot.send_message(i.chat.id,'Новые лекарства записаны в вашу базу данных')
    print(r.text)
    return States.LOGGED

def send_image(i,d):
	photo = open('wave.png', 'rb')
	tgf_obj.bot.send_photo(i.message.chat.id,photo)
	return States.LOGIN


def login(i,d):
	return States.PASS,{'login':i.text}


def check_user(i,login=None):
	passwd  =i.text
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
        'b':[ {'Отсканировать QR':tgf.action(States.START)},
         {'Список лекарств':tgf.action(stat)},
        {'Отправить фото':tgf.action(States.START)},
        {'Выйти':tgf.action(States.START)},
        ]
    },
    States.QR:{
        't':'Отправьте фотографию QR кода',
        'b':[ {'Назад':tgf.action(States.LOGGED)}],
        'react':h.action(qr, react_to='photo'),
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