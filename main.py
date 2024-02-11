# Coding: utf8  |  main.py
# Made by: @OFFpolice
# python-telegram-bot==13.0
import re
import os
import server
import random
import wikipedia

from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, MessageHandler
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from text import (
    start_text,
    help_text,
    wait_for_search_text,
    search_error_text,
    show_other_results_text,
    search_results_text,
    no_more_pages_found_text,
    last_search_key
)
from dotenv import load_dotenv
from os.path import join, dirname


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


random_photo_url = [
    "https://t.me/AEh4oo/100",
    "https://t.me/AEh4oo/102",
    "https://t.me/AEh4oo/104",
    "https://t.me/AEh4oo/106",
    "https://t.me/AEh4oo/108",
]


def handle_start(update, _):
    random_photo = random.choice(random_photo_url)
    update.message.reply_photo(photo=random_photo, caption=start_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🔁 Поширити бота', url='https://t.me/share/url?url=https://t.me/Wikipedia_UA_Bot')]
    ])
)


def handle_help(update, _):
    update.message.reply_text(help_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='🔁 Поширити бота', url='https://t.me/share/url?url=https://t.me/Wikipedia_UA_Bot')]
    ])
)


def handle_text(update, context):
    if update.message.text == show_other_results_text:
        show_other_results_keyboard(update, context)
        return
    update.message.reply_text(wait_for_search_text)
    context.user_data[last_search_key] = update.message.text
    success, reply_text = get_wiki(update.message.text)
    if success:
        keyboard = [
            [show_other_results_text]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    else:
        reply_markup = None
    update.message.reply_text(reply_text, reply_markup=reply_markup)


def show_other_results_keyboard(update, context):
    if last_search_key in context.user_data:
        last_search = context.user_data['last_search']
        search_result = wikipedia.search(last_search)
        if len(search_result) > 1:
            reply_text = search_results_text
            keyboard = []
            number_of_buttons = 5 if (len(search_result) > 5) else len(search_result) - 1
            for i in range(1, number_of_buttons):
                keyboard.append(
                    [search_result[i]]
                )
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        else:
            reply_text = no_more_pages_found_text
            reply_markup = None
        update.message.reply_text(reply_text, reply_markup=reply_markup)


def get_wiki(message_text):
    try:
        search_result = wikipedia.search(message_text)
        if len(search_result) == 0:
            return False, search_error_text
        sentences = wikipedia.page(search_result[0]).content[:1000].split('.')[:-1]
        result_text = ''
        for sentence in sentences:
            if not ('==' in sentence):
                if len((sentence.strip())) > 3:
                    result_text = f"{result_text}{sentence}."
            else:
                break
        result_text = re.sub(r'\([^()]*\)', '', result_text)
        result_text = re.sub(r'\([^()]*\)', '', result_text)
        result_text = re.sub(r'\{[^\{\}]*\}', '', result_text)
        page_url = wikipedia.page(search_result[0]).url
        result_text = f"{result_text}\n\n{page_url}"
        return True, result_text
    except wikipedia.exceptions.DisambiguationError:
        return False, search_error_text


def main():
    wikipedia.set_lang('uk')
    TOKEN = os.environ.get("TOKEN")
    updater = Updater(TOKEN, use_context=True)
    db = updater.dispatcher
    db.add_handler(CommandHandler('start', handle_start, run_async=True))
    db.add_handler(CommandHandler('help', handle_help, run_async=True))
    db.add_handler(MessageHandler(Filters.text, handle_text, run_async=True))
    updater.start_polling()
    updater.idle()

server.start()

if __name__ == '__main__':
    main()
