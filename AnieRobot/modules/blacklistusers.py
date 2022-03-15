﻿#Copyright (C) 2021 Free Software @noobanon @FakeMasked , Inc.[ https://t.me/noobanon https://t.me/FakeMasked ]
#Everyone is permitted to copy and distribute verbatim copies
#of this license document, but changing it is not allowed.
#The GNGeneral Public License is a free, copyleft license for
#software and other kinds of works.
#PTB13 Updated by @noobanon

from telegram import Message, User, Bot, Update, ParseMode
from telegram.ext import CommandHandler, run_async, Filters

from AnieRobot import dispatcher, OWNER_ID

import AnieRobot.modules.sql.blacklistusers_sql as sql


def bl_user(update, context):
    if update.effective_message.reply_to_message:
        bot = context.bot
        args = context.args
        user_id = str(update.effective_message.reply_to_message.from_user.id)
        reason = " ".join(args)
    else:
        user_id = args[0]
        reason = " ".join(args[1:])
    sql.blacklist_user(user_id, reason)
    update.effective_message.reply_text("User has been blacklisted from using me!")
    
 
def bl_users(update, context):
    rep = "<b>Blacklisted Users</b>\n"
    for x in sql.BLACKLIST_USERS:
        name = bot.get_chat(x)
        name = name.first_name.replace("<", "&lt;")
        name = name.replace(">", "&gt;")
        reason = sql.get_reason(x)
        if reason:
            rep += f"• <a href='tg://user?id={x}'>{name}</a> :- {reason}\n"
        else:
            rep += f"• <a href='tg://user?id={x}'>{name}</a>\n"
    update.effective_message.reply_text(rep, parse_mode=ParseMode.HTML)
    
    
def unbl_user(update, context):
    rep = update.effective_message
    msg = update.effective_message.reply_to_message
    bot = context.bot
    args = context.args
    if msg:
        user_id = str(msg.from_user.id)
    else:
        user_id = args[0]
    if sql.is_user_blacklisted(int(user_id)):
        sql.unblacklist_user(user_id)
        rep.reply_text("User removed from blacklist!")
    else:
        rep.reply_text("User isn't even blacklisted!")
        
        
def __user_info__(user_id):
    is_blacklisted = sql.is_user_blacklisted(user_id)
    
    text = "Blacklisted: <b>{}</b>"
    if is_blacklisted:
        text = text.format("Yes")
        reason = sql.get_reason(user_id)
        if reason:
            text += f"\nReason: <code>{reason}</code>"
    else:
        text = text.format("No")
    return text
           
    
BL_HANDLER = CommandHandler("ignore", bl_user, pass_args=True, filters=Filters.user(OWNER_ID), run_async=True)
UNBL_HANDLER = CommandHandler("notice", unbl_user, pass_args=True, filters=Filters.user(OWNER_ID), run_async=True)
BLUSERS_HANDLER = CommandHandler("ignored", bl_users, filters=Filters.user(OWNER_ID), run_async=True)

dispatcher.add_handler(BL_HANDLER)
dispatcher.add_handler(UNBL_HANDLER)
dispatcher.add_handler(BLUSERS_HANDLER)
