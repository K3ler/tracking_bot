import logging
from db import DB

from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def alarm(context):
	job = context.job
	#print("[SyS] Делаем пиздинг {}".format(job))
	context.bot.send_message(job.context, text="Чем ты сейчас занимаешся?")


def start(update, context):
	update.message.reply_text('Давайте начнем')
	update.message.reply_text("Что сейчас делаете?")


def answer(update, context):
	id = update.message.chat.id
	store = DB(id)
	date = int(update.message.date.timestamp())
	data = {
		"message": update.message.text,
		"date": date
	}
	store.saveMessage(data)
	chat_id = update.message.chat_id
	due = 60*30

	new_job = context.job_queue.run_once(alarm, due, context=chat_id)
	context.chat_data['job'] = new_job


def cancel(update, context):
	if 'job' in context.chat_data:
		job = context.chat_data['job']
		job.shedule_removal()

	DB(update.message.chat.id).save()


def report(update, context):

	path = DB(update.message.chat.id).saveToCSV()
	print(path);
	chat_id = update.message.chat.id
	context.bot.send_document(chat_id=chat_id, document=open(path, 'rb'))


def main():
	updater = Updater(
		"TOKEN", use_context=True)

	dp = updater.dispatcher

	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('report', report))
	dp.add_handler(CommandHandler('cancel', cancel))
	dp.add_handler(MessageHandler(Filters.text, answer))

	updater.start_polling()


main()
