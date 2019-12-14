import os
import logging
import csv

from tinydb import TinyDB, Query
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)


# Some logging
logging.basicConfig(filename="trouble.log", level=logging.INFO)


# Function that alarm, every 30 mins
def alarm(context):
	job = context.job
	context.bot.send_message(job.context, text="Чем ты сейчас занимаешся?")
	logging.info("Alarm fired")


# /start command function
def start(update, context):
	update.message.reply_text("Что сейчас делаете?")
	logging.info("Start Firede")

#Function for collect user data and restart job-queue
def answer(update, context):
	logging.info("Answer started")
	id = "id{}".format(update.message.chat.id)

	db = TinyDB('db.json')
	store = db.table(id)
	date = int(update.message.date.timestamp())
	chat_id = update.message.chat_id
	due = 30*60
	data = {
		"message": update.message.text,
		"date": date
	}

	store.insert(data)
	update.message.reply_text("Записано")

	if 'job' in context.chat_data:
		old_job = context.chat_data['job']
		old_job.schedule_removal()

	new_job = context.job_queue.run_once(alarm, due, context=chat_id)
	context.chat_data['job'] = new_job

# /cancel command
def cancel(update, context):
	if 'job' in context.chat_data:
		context.chat_data['job'].shedule_removal()

	update.message.reply_text(
		"Бот остановлен, что бы начать заново, просто напишите ему то что делаете, и процесс запустится снова.")

# Get csv report /report command
def report(update, context):
	chat_id = update.message.chat.id
	path = saveToCSV(chat_id)
	update.message.reply_text("Ваш отчет готов")
	context.bot.send_document(chat_id=chat_id, document=open(path, 'rb'))

# Saving data from db to csv file
def saveToCSV(id):

	idTable = "id{}".format(id)
	csvPath = "{0}/csv/id{1}.csv".format(
            os.path.dirname(os.path.abspath(__file__)), id)

	if not os.path.isdir('csv'):
		os.mkdir('csv')

	db = TinyDB('db.json')
	store = db.table(idTable)

	f = csv.writer(open(csvPath, "w+", encoding="utf-8"))
	f.writerow(['Что делали?', 'Время'])

	for item in store.all():
		f.writerow([item['message'], datetime.fromtimestamp(item["date"])])

	return csvPath

def error_callback(update, context):
    try:
        raise context.error

    except BadRequest:
        logging.debug(BadRequest)

    except NetworkError:
        logging.debug(NetworkError)

    except ChatMigrated as e:
        logging.debug(ChatMigrated)

    except TelegramError:
        logging.debug(TelegramError)

#Collect toggether
def main():
	updater = Updater(
		"TOKEN", use_context=True) #Setup your own Token

	dp = updater.dispatcher

	# Attach function to handlers...  
	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('report', report))
	dp.add_handler(CommandHandler('cancel', cancel))
	dp.add_handler(MessageHandler(Filters.text, answer))
	dp.add_error_handler(error_callback)

	# Start polling
	updater.start_polling()

	#For correct shutdown
	updater.idle()


main()
