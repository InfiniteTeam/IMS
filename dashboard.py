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

with open('watches.txt', encoding='utf-8') as watches_file:
    watches = watches_file.read().splitlines()
for ind in range(len(watches)):
    watches[ind] = int(watches[ind])

if platform.system() == 'Windows':
    with open('C:/ims/' + config['tokenFileName'], encoding='utf-8') as token_file:
        token = token_file.readline()
elif platform.system() == 'Linux':
    with open('/home/pi/ims/' + config['tokenFileName'], encoding='utf-8') as token_file:
        token = token_file.readline()

client = discord.Client(status=discord.Status.online, activity=discord.Game('정상 동작중'))
status = {discord.Status.online: [], discord.Status.idle: [], discord.Status.dnd: [], discord.Status.offline: []}

@client.event
async def on_ready():
    print('로그인:', client.user)

@client.event
async def on_member_update(before, after):
    return
    global status
    if after.id in watches:
        if (not after.id in status[after.status]) and (after.status == discord.Status.online):
            try:
                status[before.status].remove(after.id)
            except ValueError: pass
            status[after.status].append(after.id)
            await client.get_guild(config['noticeGuild']).get_channel(config['noticeChannel']).send(after.name + ' 이(가) 온라인입니다.')
        if (not after.id in status[after.status]) and (after.status == discord.Status.online):
            try:
                status[before.status].remove(after.id)
            except ValueError: pass
            status[after.status].append(after.id)
            await client.get_guild(config['noticeGuild']).get_channel(config['noticeChannel']).send(after.name + ' 이(가) 자리 비움 상태입니다.')
        if (not after.id in status[after.status]) and (after.status == discord.Status.dnd):
            try:
                status[before.status].remove(after.id)
            except ValueError: pass
            status[after.status].append(after.id)
            await client.get_guild(config['noticeGuild']).get_channel(config['noticeChannel']).send(after.name + ' 이(가) 방해 금지 상태입니다.')
        if (not after.id in status[after.status]) and (after.status == discord.Status.offline):
            try:
                status[before.status].remove(after.id)
            except ValueError: pass
            status[after.status].append(after.id)
            await client.get_guild(config['noticeGuild']).get_channel(config['noticeChannel']).send(after.name + ' 이(가) 오프라인입니다.')

app = flask.Flask(__name__)
title = 'IMS'

def get_activedict(what):
    active = {}
    for tp in ['404', 'blank', 'buttons', 'cards', 'charts', 'forgot-password', 'index', 'login', 'register', 'tables', 'utilities-animation', 'utilities-border', 'utilities-color', 'utilities-other']:
        if what == tp:
            active[tp] = 'active'
        else:
            active[tp] = ''
    print(active)
    return active

@app.errorhandler(404)
def notfound(error):
    return flask.render_template('404.html', active=get_activedict('404'))

@app.route('/404')
def rsp404():
    return flask.render_template('404.html', active=get_activedict('404'))

@app.route('/blank')
def blank():
    return flask.render_template('blank.html', active=get_activedict('blank'))

@app.route('/buttons')
def button():
    return flask.render_template('buttons.html', active=get_activedict('buttons'))

@app.route('/cards')
def cards():
    return flask.render_template('cards.html', active=get_activedict('cards'))

@app.route('/charts')
def charts():
    return flask.render_template('charts.html', active=get_activedict('charts'))

@app.route('/forgot-password')
def forgot_password():
    return flask.render_template('forgot-password.html', active=get_activedict('forgot-password'))

@app.route('/')
def index():
    return flask.render_template('index.html', active=get_activedict('index'))

@app.route('/login')
def login():
    return flask.render_template('login.html', active=get_activedict('login'))

@app.route('/register')
def register():
    return flask.render_template('register.html', active=get_activedict('register'))

@app.route('/tables')
def tables():
    return flask.render_template('tables.html', active=get_activedict('tables'))

@app.route('/utilities-animation')
def utilities_animation():
    return flask.render_template('utilities-animation.html', active=get_activedict('utilities-animation'))

@app.route('/utilities-border')
def utilities_border():
    return flask.render_template('utilities-border.html', active=get_activedict('utilities-border'))

@app.route('/utilities-color')
def utilities_color():
    return flask.render_template('utilities-color.html', active=get_activedict('utilities-color'))

@app.route('/utilities-other')
def utilities_other():
    return flask.render_template('utilities-other.html', active=get_activedict('utilities-other'))



def bot():
    client.run(token)

if __name__ == '__main__':
    task = threading.Thread(target=bot)
    task.start()
    app.run()
    