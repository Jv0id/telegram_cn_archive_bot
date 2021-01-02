#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters
from telegram import MessageEntity

import export_to_telegraph
from html_telegraph_poster import TelegraphPoster
import yaml
from telegram_util import matchKey, log_on_fail, log, tryDelete
import plain_db

with open('token') as f:
    tele = Updater(f.read().strip(), use_context=True)

debug_group = tele.bot.get_chat(420074357)

no_source_link = plain_db.loadKeyOnlyDB('no_source_link')

with open('telegraph_tokens') as f:
	telegraph_tokens = {}
	for k, v in yaml.load(f, Loader=yaml.FullLoader).items():
		telegraph_tokens[int(k)] = v

def saveTelegraphTokens():
	with open('telegraph_tokens', 'w') as f:
		f.write(yaml.dump(telegraph_tokens, sort_keys=True, indent=2))

def getSource(msg):
	if msg.from_user:
		return msg.from_user.id, msg.from_user.first_name, msg.from_user.username
	return msg.chat_id, msg.chat.title, msg.chat.username

def msgAuthUrl(msg, p):
	r = p.get_account_info(fields=['auth_url'])
	msg.reply_text('如果你需要编辑生成的 Telegraph，或者绑定到你的账户以便日后编辑，请在五分钟内点此链接登录：' + r['auth_url'])

def msgTelegraphToken(msg):
	source_id, shortname, longname = getSource(msg)
	if source_id in telegraph_tokens:
		p = TelegraphPoster(access_token = telegraph_tokens[source_id])
	else:
		p = TelegraphPoster()
		r = p.create_api_token(shortname, longname)
		telegraph_tokens[source_id] = r['access_token']
		saveTelegraphTokens()
		msgAuthUrl(msg, p)

def getTelegraph(msg, url):
	source_id, _, _ = getSource(msg)
	if source_id not in telegraph_tokens:
		msgTelegraphToken(msg)
	export_to_telegraph.token = telegraph_tokens[source_id]
	return export_to_telegraph.export(url, throw_exception = True, 
		force = True, toSimplified = (
			'bot_simplify' in msg.text or msg.text.endswith(' s')),
		noSourceLink = str(msg.chat_id) in no_source_link._db.items)

def exportImp(msg):
	for item in msg.entities:
		if (item["type"] == "url"):
			url = msg.text[item["offset"]:][:item["length"]]
			if not '://' in url:
				url = "https://" + url
			result = getTelegraph(msg, url)
			if str(msg.chat_id) in no_source_link._db.items:
				msg.chat.send_message(result)
			else:
				msg.chat.send_message('%s | [source](%s)' % (result, url), 
					parse_mode='Markdown')

@log_on_fail(debug_group)
def export(update, context):
	if update.edited_message or update.edited_channel_post:
		return
	msg = update.effective_message
	if msg.chat_id < 0 and ('source' in msg.text) and ('[source]' in msg.text_markdown):
		return
	try:
		r = msg.chat.send_message('正在存档…')
	except:
		return
	try:
		exportImp(msg)
	except Exception as e:
		msg.chat.send_message(str(e))
		if not matchKey(str(e), ['内容太长！']):
			raise e
	finally:
		r.delete()

with open('help.md') as f:
	help_message = f.read()

def toggleSourceLink(msg):
	result = no_source_link.toggle(msg.chat_id)
	if result:
		msg.reply_text('Source Link Off')
	else:
		msg.reply_text('Source Link On')

@log_on_fail(debug_group)
def command(update, context):
	msg = update.message
	if matchKey(msg.text, ['auth', 'token']):
		return msgTelegraphToken(msg)
	if matchKey(msg.text, ['toggle', 'source']):
		return toggleSourceLink(msg)
	if msg.chat_id > 0:
		msg.reply_text(help_message)

tele.dispatcher.add_handler(MessageHandler(Filters.text & 
	(Filters.entity('url') | Filters.entity(MessageEntity.TEXT_LINK)), export))
tele.dispatcher.add_handler(MessageHandler(Filters.command, command))

tele.start_polling()
tele.idle()