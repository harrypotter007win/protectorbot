﻿#Copyright (C) 2021 Free Software @noobanon @FakeMasked , Inc.[ https://t.me/noobanon https://t.me/FakeMasked ]
#Everyone is permitted to copy and distribute verbatim copies
#of this license document, but changing it is not allowed.
#The GNGeneral Public License is a free, copyleft license for
#software and other kinds of works.
#PTB13 Updated by @noobanon

import html
import re
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, MessageHandler, Filters, run_async

import AnieRobot.modules.sql.blacklist_sql as sql
from AnieRobot import dispatcher, LOGGER
from AnieRobot.modules.disable import DisableAbleCommandHandler
from AnieRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin, user_can_change
from AnieRobot.modules.helper_funcs.extraction import extract_text
from AnieRobot.modules.helper_funcs.misc import split_message

from AnieRobot.modules.connection import connected

from AnieRobot.modules.translations.strings import tld

BLACKLIST_GROUP = 11



def blacklist(update, context):
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    bot = context.bot
    
    conn = connected(bot, update, chat, user.id, need_admin=False)
    if not conn == False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            exit(1)
        else:
            chat_id = update.effective_chat.id
            chat_name = chat.title
    
    filter_list = tld(chat.id, "<b>Current blacklisted words in {}:</b>\n").format(chat_name)

    all_blacklisted = sql.get_chat_blacklist(chat_id)

    if len(args) > 0 and args[0].lower() == 'copy':
        for trigger in all_blacklisted:
            filter_list += "<code>{}</code>\n".format(html.escape(trigger))
    else:
        for trigger in all_blacklisted:
            filter_list += " • <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(filter_list)
    for text in split_text:
        if filter_list == tld(chat.id, "<b>Current blacklisted words in {}:</b>\n").format(chat_name): #We need to translate
            msg.reply_text(tld(chat.id, "There are no blacklisted messages in <b>{}</b>!").format(chat_name), parse_mode=ParseMode.HTML)
            return
        msg.reply_text(text, parse_mode=ParseMode.HTML)



@user_admin
@user_can_change
def add_blacklist(update, context):
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    bot = context.bot
    words = msg.text.split(None, 1)

    conn = connected(bot, update, chat, user.id)
    if not conn == False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            exit(1)
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_blacklist = list(set(trigger.strip() for trigger in text.split("\n") if trigger.strip()))
        for trigger in to_blacklist:
            sql.add_to_blacklist(chat_id, trigger.lower())

        if len(to_blacklist) == 1:
            msg.reply_text(tld(chat.id, "Added <code>{}</code> to the blacklist in <b>{}</b>!").format(html.escape(to_blacklist[0]), chat_name),
                           parse_mode=ParseMode.HTML)

        else:
            msg.reply_text(tld(chat.id, 
             "Added <code>{}</code> to the blacklist in <b>{}</b>!").format(len(to_blacklist)), chat_name, parse_mode=ParseMode.HTML)

    else:
        msg.reply_text(tld(chat.id, "Tell me what words you would like to add to the blacklist."))



@user_admin
@user_can_change
def unblacklist(update, context):
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    bot = context.bot
    words = msg.text.split(None, 1)

    conn = connected(bot, update, chat, user.id)
    if not conn == False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            exit(1)
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_unblacklist = list(set(trigger.strip() for trigger in text.split("\n") if trigger.strip()))
        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_blacklist(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                msg.reply_text(tld(chat.id, "Removed <code>{}</code> from the blacklist in <b>{}</b>!").format(html.escape(to_unblacklist[0]), chat_name),
                               parse_mode=ParseMode.HTML)
            else:
                msg.reply_text(tld(chat.id, "This isn't a blacklisted trigger...!"))

        elif successful == len(to_unblacklist):
            msg.reply_text(tld(chat.id, 
                "Removed <code>{}</code> triggers from the blacklist in <b>{}</b>!").format(
                    successful, chat_name), parse_mode=ParseMode.HTML)

        elif not successful:
            msg.reply_text(tld(chat.id, 
                "None of these triggers were exist, so they weren't removed.").format(
                    successful, len(to_unblacklist) - successful), parse_mode=ParseMode.HTML)

        else:
            msg.reply_text(tld(chat.id, 
                "Removed <code>{}</code> triggers from the blacklist in <b>{}</b>! {} did not exist, "
                "so were not removed.").format(successful, chat_name, len(to_unblacklist) - successful),
                parse_mode=ParseMode.HTML)
    else:
        msg.reply_text(tld(chat.id, "Tell me what words you would like to remove from the blacklist."))


@user_not_admin
def del_blacklist(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    bot = context.bot
    to_match = extract_text(message)
    if not to_match:
        return

    chat_filters = sql.get_chat_blacklist(chat.id)
    for trigger in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            try:
                message.delete()
            except BadRequest as excp:
                if excp.message == "Message to delete not found":
                    pass
                else:
                    LOGGER.exception("Error while deleting blacklist message.")
            break


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(bot, update, chat, chatP, user):
    blacklisted = sql.num_blacklist_chat_filters(chat.id)
    return "There are {} blacklisted words.".format(blacklisted)


def __stats__():
    return "{} blacklist triggers, across {} chats.".format(sql.num_blacklist_filters(),
                                                            sql.num_blacklist_filter_chats())


__mod_name__ = "Blacklists"

__help__ = """
You can set blacklist filters to take automatic action on people when they say certain things. This is done using:
 - /addblacklist <blacklist trigger> <blacklist reason>: blacklists the trigger. You can set sentences by putting quotes around the reason.
 - /unblacklist <blacklist trigger>: stop blacklisting a certain blacklist trigger.
 - /rmblacklist <blacklist trigger>: same as /unblacklist
 - /blacklist: list all active blacklist filters

/addblacklist "the admins suck" Respect your admins!
This would delete any message containing 'the admins suck'.
If you've enabled an alternative blacklist mode, it will warn, ban, kick, or mute a user with a message specifying the reason.

Top tip:
Blacklists allow you to use some modifiers to match "unknown" characters. For example, you can use the ? character to match a single occurence of any non-whitespace character.
You could also use the * modifier, which matches any number of any character. If you want to blacklist urls, this will allow you to match the full thing. It matches every character except spaces. This is cool if you want to stop, for example, url shorteners.
For example, the following will ban any bit.ly link:
/addblacklist "bit.ly/*" We dont like shorteners!
If you wanted to only match bit.ly/ links followed by three characters, you could use:
/addblacklist "bit.ly/???" We dont like shorteners!
This would match bit.ly/abc, but not bit.ly/abcd.
"""

BLACKLIST_HANDLER = DisableAbleCommandHandler("blacklist", blacklist, pass_args=True, admin_ok=True, run_async=True)
ADD_BLACKLIST_HANDLER = CommandHandler("addblacklist", add_blacklist, run_async=True)
UNBLACKLIST_HANDLER = CommandHandler(["unblacklist", "rmblacklist"], unblacklist, run_async=True)
BLACKLIST_DEL_HANDLER = MessageHandler(
    (Filters.text | Filters.command | Filters.sticker | Filters.photo) & Filters.chat_type.groups, del_blacklist, Filters.update.edited_message, run_async=True)

dispatcher.add_handler(BLACKLIST_HANDLER)
dispatcher.add_handler(ADD_BLACKLIST_HANDLER)
dispatcher.add_handler(UNBLACKLIST_HANDLER)
dispatcher.add_handler(BLACKLIST_DEL_HANDLER, group=BLACKLIST_GROUP)
