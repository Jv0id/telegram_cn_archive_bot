#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dbm
import warnings

from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

import webpage2telegraph
from html_telegraph_poster import TelegraphPoster
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters
from telegram_util import matchKey, log_on_fail, getDisplayUserHtml

import config

application = Application.builder().token(config.api_token).build()

# 修改这里，使用异步调用获取 log_chat
log_chat = None


async def init_log_chat():
    global log_chat
    log_chat = await application.bot.get_chat(config.log_chat)


source_flags = dbm.open('source_flags.db', 'c')
simplify_flags = dbm.open('simplify_flags.db', 'c')
telegraph_tokens = dbm.open('telegraph_tokens.db', 'c')


def get_from(msg):
    if msg.from_user:
        return msg.from_user.id, msg.from_user.first_name, msg.from_user.username
    return msg.chat_id, msg.chat.title, msg.chat.username  # from channel


def send_auth_url(msg, p):
    r = p.get_account_info(fields=['auth_url'])
    msg.chat.send_message('请在五分钟内点此链接登录: ' + r['auth_url'])


def get_telegraph_token(msg):
    from_id, name, username = get_from(msg)
    fid = str(from_id)
    if fid in telegraph_tokens:
        p = TelegraphPoster(access_token=telegraph_tokens[fid])
    else:
        p = TelegraphPoster()
        r = p.create_api_token(name, username)
        telegraph_tokens[fid] = r['access_token']
    send_auth_url(msg, p)


def get_telegraph(msg, url):
    from_id, _, _ = get_from(msg)
    fid = str(from_id)
    if fid not in telegraph_tokens:
        get_telegraph_token(msg)
    webpage2telegraph.token = telegraph_tokens[fid]
    simplify = fid in source_flags
    source = fid in source_flags
    return webpage2telegraph.transfer(url, source=source, simplify=simplify)


def transfer(msg):
    for item in msg.entities:
        url = ''
        if item.type == 'url':
            url = msg.text[item.offset:][:item.length]
        elif item.type == 'text_link':
            t = msg.text[item.offset:][:item.length]
            if not matchKey(t, ['source', '原文']):
                url = item.url
        else:
            continue
        if '://' not in url:
            url = 'http://' + url
        elif not url.startswith('http'):
            continue
        result = get_telegraph(msg, url)
        yield result
        if str(msg.chat_id) in source_flags:
            msg.chat.send_message('%s\n<a href="%s">原文</a>' % (result, url), parse_mode=ParseMode.HTML)
        else:
            msg.chat.send_message(result)


@log_on_fail(log_chat)
async def archive(update, context):
    if update.edited_message or update.edited_channel_post:
        return
    msg = update.effective_message
    if msg.forward_origin and hasattr(msg.forward_origin,
                                      'sender_user') and msg.forward_origin.sender_user.username == 'CNArchiveBot':
        return
    try:
        process_msg = await msg.chat.send_message('正在存档…')
    except:
        return
    error = ''
    result = []
    try:
        result = list(transfer(msg))
    except Exception as e:
        error = str(e)
        try:
            await msg.chat.send_message(error)
        except:  # 洪水攻击时会发生异常
            pass
        raise e
    finally:
        log = ['']
        if error:
            log.append('\nError:')
            log.append(error)
        if result:
            log.append('\n\n'.join(result))
        # 确保 log_chat 已经初始化
        if log_chat is None:
            await init_log_chat()
        await log_chat.send_message('\n'.join(log),
                                    parse_mode=ParseMode.HTML,
                                    disable_web_page_preview=False)
        await process_msg.delete()
        await msg.delete()


def switch_source_flag(msg):
    from_id, _, _ = get_from(msg)
    fid = str(from_id)
    if fid in source_flags:
        del source_flags[fid]
        msg.reply_text('将隐藏原文链接')
    else:
        source_flags[fid] = b'1'
        msg.reply_text('将展示原文链接')


def switch_simplify_flag(msg):
    from_id, _, _ = get_from(msg)
    fid = str(from_id)
    if fid in simplify_flags:
        del simplify_flags[fid]
        msg.reply_text('将不再繁简转换')
    else:
        simplify_flags[fid] = b'1'
        msg.reply_text('将进行繁简转换')


with open('help.md') as f:
    help_message = f.read()


@log_on_fail(log_chat)
async def command(update, context):
    msg = update.message
    if matchKey(msg.text, ['auth', 'token']):
        return get_telegraph_token(msg)
    if matchKey(msg.text, ['source']):
        return switch_source_flag(msg)
    if matchKey(msg.text, ['simplify']):
        return switch_simplify_flag(msg)
    if msg.chat_id > 0:  # from private
        await msg.reply_text(help_message)


# 添加处理器
application.add_handler(MessageHandler(
    filters.TEXT &
    (filters.Entity("url") | filters.Entity("text_link")),
    archive)
)
application.add_handler(MessageHandler(filters.COMMAND, command))

# 启动机器人
application.run_polling()
