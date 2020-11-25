import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters


import logging
import sqlite3
from random import randint
import re


# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',\
	level=logging.INFO)


logger = logging.getLogger(__name__)


# extract random facts from the database
def random_fact(lev):
	connection = sqlite3.connect("mydatabase.db")
	cursor = connection.cursor()

	cursor.execute("SELECT * FROM russian WHERE level='%s'"%(lev))

	result = cursor.fetchall() 
	rand_fact_numb = randint(1,len(result)-1)
	rand_fact = result[rand_fact_numb]

	connection.close()

	return rand_fact


# function for starting conversation
def start(update, context):
	custom_keyboard = [['базовый', 'усложненный', 'дополнительный'], ['о боте']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=False)
	context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Отправь мне команду /basic , /advanced или /extra, чтобы узнать интересные факты о русском языке. Подробнее о боте /help",
							 reply_markup=reply_markup)


# help command that returns description of the bot
def help_(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id,  parse_mode = 'Markdown', text="Бот, который случайным образом выдаёт пользователю интересные факты русского языка.\n\
Основной источник фактов — [корпус ошибок](http://web-corpora.net/RLC/search/), которые делают изучающие русский язык \n\
*Доступные команды:*\n\
/start запустить бота\n\
/help описание бота и инструкции\n\
/basic присылает интересный факт базового уровня сложности\n\
/advanced присылает интересный факт усложненного уровня сложности\n\
/extra присылает интересный факт дополнительного уровня сложности")


def fact(update, context, lev):
	rand_fact = random_fact(lev)
	name = rand_fact[0]
	description = rand_fact[1]
	example = rand_fact[2]
	level_db = rand_fact[3]
	levels = ['базовый', 'усложненный', 'дополнительный']
	level = ''
	if level_db == 'Б':
		level = levels[0]
	elif level_db == 'У':
		level = levels[1]
	else:
		level = levels[2]
	example = re.sub('✔️', '\n✔️', example)
	example = re.sub('❌', '\n❌', example)
	context.bot.send_message(chat_id=update.effective_chat.id, parse_mode = 'Markdown',\
		text = '*' + name.strip().capitalize() + '*\n\n'\
		+ 'Уровень факта: ' + level + '\n\n' + description.strip().capitalize()+'\n'\
		+ example)


def fact_1(update, context):
	lev = 'Б'
	fact(update, context, lev)


def fact_2(update, context):
	lev = 'У'
	fact(update, context, lev)


def fact_3(update, context):
	lev = 'Д'
	fact(update, context, lev)


# function that replies to messages that bot doesn't understand
def unknown(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="Прости, я не понимаю, что ты говоришь")


# logging errors
def error(update, context):
	logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
	""" Run bot """

	updater = Updater(token='', use_context=True)
	dispatcher = updater.dispatcher


	# add handlers
	dispatcher.add_handler(CommandHandler('start', start)) # run start function 
	dispatcher.add_handler(CommandHandler('help', help_)) # help function
	dispatcher.add_handler(CommandHandler('basic', fact_1))
	dispatcher.add_handler(CommandHandler('advanced', fact_2))
	dispatcher.add_handler(CommandHandler('extra', fact_3))
	dispatcher.add_handler(MessageHandler(Filters.regex('базовый'), fact_1))
	dispatcher.add_handler(MessageHandler(Filters.regex('усложненный'), fact_2))
	dispatcher.add_handler(MessageHandler(Filters.regex('дополнительный'), fact_3))
	dispatcher.add_handler(MessageHandler(Filters.regex('о боте'), help_))
	dispatcher.add_handler(MessageHandler(Filters.text, unknown))


	# log all errors
	dispatcher.add_error_handler(error)

	updater.start_polling()

	updater.idle()




if __name__ == '__main__':
	main()