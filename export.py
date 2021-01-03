#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dbm

import export_to_telegraph
import requests
import socket
import socks
from html_telegraph_poster import TelegraphPoster
from telegram import MessageEntity
from telegram.ext import Updater, MessageHandler, Filters
from telegram_util import matchKey, log_on_fail

socks_sys = socket.socket
try:
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket
    response = requests.get('https://api.telegram.org')
except:
    socket.socket = socks_sys

with open('token') as f:
    tele = Updater(f.read().strip(), use_context=True)

debug_chat = tele.bot.get_chat(656869271)

source_flags = dbm.open('source_flags.db', 'c')

telegraph_tokens = dbm.open('telegraph_tokens.db', 'c')


# def saveTelegraphTokens():
# 	telegraph_tokens.sync()

def get_source(msg):
    if msg.from_user:
        return msg.from_user.id, msg.from_user.first_name, msg.from_user.username
    return msg.chat_id, msg.chat.title, msg.chat.username


def msg_auth_url(msg, p):
    r = p.get_account_info(fields=['auth_url'])
    msg.reply_text('如果你需要编辑生成的 Telegraph，或者绑定到你的账户以便日后编辑，请在五分钟内点此链接登录：' + r['auth_url'])


def msg_telegraph_token(msg):
    source_id, shortname, longname = get_source(msg)
    if source_id in telegraph_tokens:
        p = TelegraphPoster(access_token=telegraph_tokens[source_id])
    else:
        p = TelegraphPoster()
        r = p.create_api_token(shortname, longname)
        telegraph_tokens[source_id] = r['access_token']
        # saveTelegraphTokens()
        msg_auth_url(msg, p)


def get_telegraph(msg, url):
    source_id, _, _ = get_source(msg)
    if source_id not in telegraph_tokens:
        msg_telegraph_token(msg)

    export_to_telegraph.token = telegraph_tokens[source_id]
    return export_to_telegraph.export(url, throw_exception=True, force=True,
                                      toSimplified=('bot_simplify' in msg.text or msg.text.endswith(' s')),
                                      noSourceLink=str(msg.chat_id) not in source_flags)


def export_imp(msg):
    for item in msg.entities:
        if item["type"] == "url":
            url = msg.text[item["offset"]:][:item["length"]]
            if '://' not in url:
                url = "https://" + url
            result = get_telegraph(msg, url)
            if str(msg.chat_id) not in source_flags:
                msg.chat.send_message(result)
            else:
                msg.chat.send_message('%s | [来源](%s)' % (result, url), parse_mode='Markdown')


@log_on_fail(debug_chat)
def export(update, context):
    if update.edited_message or update.edited_channel_post:
        return
    msg = update.effective_message
    if msg.chat_id < 0 and ('来源' in msg.text) and ('[来源]' in msg.text_markdown):
        return
    try:
        r = msg.chat.send_message('正在存档…')
    except:
        return
    try:
        export_imp(msg)
    except Exception as e:
        msg.chat.send_message(str(e))
        if not matchKey(str(e), ['内容太长！']):
            raise e
    finally:
        r.delete()


with open('help.md') as f:
    help_message = f.read()


def toggle_source_flag(msg):
    chat_id = str(msg.chat_id)
    if chat_id in source_flags:
        msg.reply_text('将隐藏来源链接')
        del source_flags[chat_id]
    else:
        msg.reply_text('将展示来源链接')
        source_flags[chat_id] = b'1'
    # source_flags.sync()


@log_on_fail(debug_chat)
def command(update, context):
    msg = update.message
    if matchKey(msg.text, ['auth', 'token']):
        return msg_telegraph_token(msg)
    if matchKey(msg.text, ['toggle', 'source']):
        return toggle_source_flag(msg)
    if msg.chat_id > 0:
        msg.reply_text(help_message)


tele.dispatcher.add_handler(
    MessageHandler(Filters.text & (Filters.entity('url') | Filters.entity(MessageEntity.TEXT_LINK)), export))
tele.dispatcher.add_handler(MessageHandler(Filters.command, command))

tele.start_polling()
tele.idle()
