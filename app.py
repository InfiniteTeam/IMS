# -*- coding: utf-8 -*-

import flask
import json
import platform
import threading
import time
import sys
import os
import logging
import logging.handlers
import bcrypt
import sqlite3
import traceback

with open('config.json', encoding='utf-8') as config_file:
    config = json.load(config_file)

with open('watches.json', encoding='utf-8') as watches_file:
    watches = json.load(watches_file)

status = {}
for one in watches.keys():
    status[one] = {'status': None, 'statname': '정보를 불러오는 중...', 'statdesc': '','colorname': 'secondary'}
dataset = {}

app = flask.Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def get_activedict(what):
    active = {}
    for tp in ['404', 'blank', 'buttons', 'cards', 'charts', 'forgot-password', 'index', 'login', 'register', 'tables', 'utilities-animation', 'utilities-border', 'utilities-color', 'utilities-other']:
        if what == tp:
            active[tp] = 'active'
        else:
            active[tp] = ''
    return active

@app.route('/ims/dataset', methods=['POST'])
def ims_dataset():
    global dataset, status

    sender = flask.request.headers['IMS-User']

    if platform.system() == 'Windows':
        with sqlite3.connect('C:/ims/' + config['dbFileName']) as cur:
            user = cur.execute('select token from bots where name=:user', {'user':sender})
    elif platform.system() == 'Linux':
        with sqlite3.connect('/home/pi/ims/' + config['dbFileName']) as cur:
            user = cur.execute('select token from bots where name=:user', {'user':sender})
    
    row = user.fetchone()
    
    if row and bcrypt.checkpw(flask.request.headers['IMS-Token'].encode('utf-8'), row[0].encode('utf-8')):
        print(f'데이터셋을 받았습니다: 수신자: {sender}')
        dataset[sender] = flask.request.json
        if sender == 'ims':
            status = flask.request.json['bot-status']
        return ''
    else:
        print(f'인증에 실패했습니다: 수신자: {sender}')
        return '', 401

@app.route('/ims/dataset.json')
def ims_dataset_json():
    return dataset

@app.route('/')
def index():
    return flask.render_template(
        'index.html',
        title='IMS - 대시보드',
        active=get_activedict('index'),
        status=status
        )

@app.errorhandler(404)
def notfound(error):
    return flask.render_template('404.html', title='IMS - 존재하지 않는 페이지', active=get_activedict('404'))

@app.route('/404')
def rsp404():
    return flask.render_template('404.html', title='IMS - 존재하지 않는 페이지', active=get_activedict('404'))

@app.route('/blank')
def blank():
    return flask.render_template('blank.html', title='IMS - 빈 페이지', active=get_activedict('blank'))

@app.route('/buttons')
def buttons():
    return flask.render_template('buttons.html', title='IMS - 버튼', active=get_activedict('buttons'))

@app.route('/cards')
def cards():
    return flask.render_template('cards.html', title='IMS - 카드', active=get_activedict('cards'))

@app.route('/charts')
def charts():
    return flask.render_template('charts.html', title='IMS - 차트', active=get_activedict('charts'))

@app.route('/forgot-password')
def forgot_password():
    return flask.render_template('forgot-password.html', title='IMS - 비밀번호 변경', active=get_activedict('forgot-password'))

@app.route('/login')
def login():
    return flask.render_template('login.html', title='IMS - 로그인', active=get_activedict('login'))

@app.route('/register')
def register():
    return flask.render_template('register.html', title='IMS - 회원가입', active=get_activedict('register'))

@app.route('/tables')
def tables():
    return flask.render_template('tables.html', title='IMS - 테이블', active=get_activedict('tables'))

@app.route('/utilities-animation')
def utilities_animation():
    return flask.render_template('utilities-animation.html', title='IMS - 애니메이션', active=get_activedict('utilities-animation'))

@app.route('/utilities-border')
def utilities_border():
    return flask.render_template('utilities-border.html', title='IMS - 보더', active=get_activedict('utilities-border'))

@app.route('/utilities-color')
def utilities_color():
    return flask.render_template('utilities-color.html', title='IMS - 컬러', active=get_activedict('utilities-color'))

@app.route('/utilities-other')
def utilities_other():
    return flask.render_template('utilities-other.html', title='IMS - 기타', active=get_activedict('utilities-other'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')