import flask
import discord
from discord.ext import commands, tasks
import asyncio
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

with open('config.json', encoding='utf-8') as config_file:
    config = json.load(config_file)

prefix = config['prefix']

with open('watches.json', encoding='utf-8') as watches_file:
    watches = json.load(watches_file)

if platform.system() == 'Windows':
    with open('C:/ims/' + config['tokenFileName'], encoding='utf-8') as token_file:
        token = token_file.readline()
elif platform.system() == 'Linux':
    with open('/home/pi/ims/' + config['tokenFileName'], encoding='utf-8') as token_file:
        token = token_file.readline()


# mkdir
if not os.path.exists('./logs'):
    os.makedirs('./logs')
if not os.path.exists('./logs/general'):
    os.makedirs('./logs/general')

logger = logging.getLogger('ims')
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_streamh = logging.StreamHandler()
log_streamh.setFormatter(log_formatter)
logger.addHandler(log_streamh)
log_fileh = logging.handlers.RotatingFileHandler('./logs/general/ims.log', maxBytes=config['maxlogbytes'], backupCount=10)
log_fileh.setFormatter(log_formatter)
logger.addHandler(log_fileh)

client = discord.Client(status=discord.Status.online, activity=discord.Game('정상 동작중'))

dataset = {}

status = {}
for one in watches.keys():
    status[one] = {'status': None, 'statname': '정보를 불러오는 중...', 'statdesc': '','colorname': 'secondary'}

@client.event
async def on_ready():
    global masterguild, masterchannel
    logger.info('로그인: {}'.format(client.user))
    statuscheck.start()
    masterguild = client.get_guild(config['masterGuild'])
    masterchannel = masterguild.get_channel(config['masterChannel'])

@tasks.loop(seconds=2)
async def statuscheck():
    global status
    for onename in watches.keys():
        bot = masterguild.get_member(watches[onename]['id'])
        if bot.status in [discord.Status.online, discord.Status.invisible]:
            status[onename]['status'] = 'online'
            status[onename]['statname'] = '정상 동작중'
            status[onename]['statdesc'] = '봇이 정상적으로 동작하고 있어요!'
            status[onename]['colorname'] = 'success'
        if bot.status == discord.Status.idle:
            status[onename]['status'] = 'idle'
            status[onename]['statname'] = '점검중'
            status[onename]['statdesc'] = '봇이 동작중이지만 점검중이에요.'
            status[onename]['colorname'] = 'warning'
        if bot.status == discord.Status.dnd:
            status[onename]['status'] = 'dnd'
            status[onename]['statname'] = '이용 불가(관리자 모드)'
            status[onename]['statdesc'] = '현재 관리자만 사용이 가능해요.'
            status[onename]['colorname'] = 'danger'
        if bot.status == discord.Status.offline:
            status[onename]['status'] = 'offline'
            status[onename]['statname'] = '오프라인'
            status[onename]['statdesc'] = '봇이 종료되어 오프라인 상태예요.'
            status[onename]['colorname'] = 'secondary'

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(prefix + 'ds'):
        j = discord.utils.escape_markdown(str(json.dumps(dataset, indent=2)))
        embed = discord.Embed(title='DATASETS', description=f'```json\n{j}\n```', color=0x4e73df)
        await message.channel.send(embed=embed)

app = flask.Flask(__name__)

def get_activedict(what):
    active = {}
    for tp in ['404', 'blank', 'buttons', 'cards', 'charts', 'forgot-password', 'index', 'login', 'register', 'tables', 'utilities-animation', 'utilities-border', 'utilities-color', 'utilities-other']:
        if what == tp:
            active[tp] = 'active'
        else:
            active[tp] = ''
    return active

@app.route('/ims/salmonbot/', methods=['POST'])
def ims_salmonbot():
    global dataset
    if platform.system() == 'Windows':
        with sqlite3.connect('C:/ims/' + config['dbFileName']) as cur:
            user = cur.execute('select token from bots where name=:user', {'user':flask.request.headers['IMS-User']})
    elif platform.system() == 'Linux':
        with sqlite3.connect('/home/pi/ims/' + config['dbFileName']) as cur:
            user = cur.execute('select token from bots where name=:user', {'user':flask.request.headers['IMS-User']})
    
    row = user.fetchone()

    if row and bcrypt.checkpw(flask.request.headers['IMS-Token'].encode('utf-8'), row[0].encode('utf-8')):
        sender = flask.request.headers['IMS-User']
        logger.info(f'데이터셋을 받았습니다: 수신자: {sender}')
        dataset[sender] = flask.request.json
        return ''
    else:
        logger.info(f'인증에 실패했습니다: 수신자: {sender}')
        return '', 401

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
    