# import telebot
# from telebot import types
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '6623692052:AAEr6l5YByR5mr0LPdLryNCG1JuwhtakcfY'
BOT_USERNAME: Final = '@polyglot_buddy_bot'

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hi there! I am Polyglot Travel Buddy. How may I assist you today?')


# Responses

# bot = telebot.TeleBot('6702133422:AAHWL7IDtrh9N6RNS1iUp4N-FogK7Ye9YhM')

# @bot.message_handler(commands=['start'])
# def greet(message):
#     welcome_message = 'Hello ' + message.from_user.username + ' I am Polyglot Buddy'
#     # bot.reply_to(message, welcome_message)
#     bot.send_message(message.chat.id, welcome_message)
#     bot.send_message(message.chat.id,"I support Spanish, Mandarin, French, German and Italian")

#     markup = types.InlineKeyboardMarkup(row_width=5)
    
#     spanish = types.InlineKeyboardButton('Spanish', callback_data='answer')
#     mandarin = types.InlineKeyboardButton('Mandarin', callback_data='answer')
#     french = types.InlineKeyboardButton('French', callback_data='answer')
#     german = types.InlineKeyboardButton('German', callback_data='answer')
#     italian = types.InlineKeyboardButton('Italian', callback_data='answer')
    
#     markup.add(spanish, mandarin, french, german, italian)
#     bot.send_message(message.chat.id, "What Language do you want to learn?", reply_markup = markup)



# # @bot.message_handler(commands=['quiz'])
# # def quiz(message):
# #     markup = types.InlineKeyboardMarkup(row_width=2)
    
# #     option_1 = types.InlineKeyboardButton('option 1', callback_data='answer')
# #     option_2 = types.InlineKeyboardButton('option 2', callback_data='answer')

# #     markup.add(option_1, option_2)

# #     bot.send_message(message.chat.id, 'What do you like to choose', reply_markup = markup)


# @bot.callback_query_handler(func=lambda call:True)
# def answer(callback):
#     pass


# bot.polling()