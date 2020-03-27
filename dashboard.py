import flask
import discord
from discord.ext import commands, tasks
import asyncio
import json
import platform
import threading
import time
import sys

with open('config.json', encoding='utf-8') as config_file:
    config = json.load(config_file)

with open('watches.json', encoding='utf-8') as watches_file:
    watches = json.load(watches_file)

if platform.system() == 'Windows':
    with open('C:/ims/' + config['tokenFileName'], encoding='utf-8') as token_file:
        token = token_file.readline()
elif platform.system() == 'Linux':
    with open('/home/pi/ims/' + config['tokenFileName'], encoding='utf-8') as token_file:
        token = token_file.readline()

client = discord.Client(status=discord.Status.online, activity=discord.Game('정상 동작중'))
status = {}
for one in watches:
    status[one] = {'status': None, 'statname': '정보를 불러오는 중...', 'statdesc': '','colorname': 'secondary'}

@client.event
async def on_ready():
    print('로그인:', client.user)

@client.event
async def on_member_update(before, after):
    global status 
    if after.id == watches['salmonbot']['id']:
        if after.status in [discord.Status.online, discord.Status.invisible]:
            status['salmonbot']['status'] = 'online'
            status['salmonbot']['statname'] = '정상 동작중'
            status['salmonbot']['statdesc'] = '봇이 정상적으로 동작하고 있어요!'
            status['salmonbot']['colorname'] = 'success'
        if after.status == discord.Status.idle:
            status['salmonbot']['status'] = 'idle'
            status['salmonbot']['statname'] = '점검중'
            status['salmonbot']['statdesc'] = '봇이 동작중이지만 점검중이에요.'
            status['salmonbot']['colorname'] = 'warning'
        if after.status == discord.Status.dnd:
            status['salmonbot']['status'] = 'dnd'
            status['salmonbot']['statname'] = '이용 불가(관리자 모드)'
            status['salmonbot']['statdesc'] = '현재 관리자만 사용이 가능해요.'
            status['salmonbot']['colorname'] = 'danger'
        if after.status == discord.Status.offline:
            status['salmonbot']['status'] = 'offline'
            status['salmonbot']['statname'] = '오프라인'
            status['salmonbot']['statdesc'] = '봇이 종료되어 오프라인 상태예요.'
            status['salmonbot']['colorname'] = 'secondary'


app = flask.Flask(__name__)
title = 'IMS'

def get_activedict(what):
    active = {}
    for tp in ['404', 'blank', 'buttons', 'cards', 'charts', 'forgot-password', 'index', 'login', 'register', 'tables', 'utilities-animation', 'utilities-border', 'utilities-color', 'utilities-other']:
        if what == tp:
            active[tp] = 'active'
        else:
            active[tp] = ''
    return active

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

def bot():
    client.run(token)

if __name__ == '__main__':
    task = threading.Thread(target=bot)
    task.start()
    app.run(host='0.0.0.0')
    