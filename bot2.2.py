import requests
import telebot
import config
import pytz
import speech_recognition as sr
import subprocess
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME
bot = telebot.TeleBot(config.token)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        keyboard = InlineKeyboardMarkup()
        keyboard.row_width = 2
        keyboard.add(InlineKeyboardButton('текст в текст', callback_data='texttotext'),
                     InlineKeyboardButton('аудио в текст', callback_data='audiototext'),
                     InlineKeyboardButton('аудио в аудио', callback_data='audiotoaudio'),
                     InlineKeyboardButton('текст', callback_data='text'))
        question = 'что ты хочешь сделать?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "text":
        bot.answer_callback_query(call.id, "пришлите код")
        @bot.message_handler(content_types=['voice'])
        def handle_audio(message):
            global text
            file_info = bot.get_file(message.voice.file_id)
            file = requests.get(
                'https://api.telegram.org/file/bot{0}/{1}'.format('1906481644:AAFYdV_gPAqiKcPWQt0SzvSnFfLVLIuBNHs',
                                                                file_info.file_path))
            src = file_info.file_path[:6] + 'ogg' + file_info.file_path[5:]
            dst = file_info.file_path[:6] + 'wav' + file_info.file_path[5:-3] + 'wav'
            downloaded_file = bot.download_file(file_info.file_path)
            with open('file.ogg', 'wb') as f:
                f.write(downloaded_file)
            b=random.randint(0, 1000)

            src_filename = 'file.ogg'
            dest_filename = f'file{b}.wav'

            process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])

            r = sr.Recognizer()
            with sr.AudioFile(dest_filename) as source:
                audio = r.record(source)
                text = r.recognize_google(audio, language="ru-RU")
            bot.send_message(message.from_user.id, text)
    elif call.data == "texttotext":
        bot.answer_callback_query(call.id, "к сожалению данная кнопка пока в разработке")
    elif call.data == "audiototext":
        bot.answer_callback_query(call.id, "к сожалению данная кнопка пока в разработке")
    elif call.data == "audiotoaudio":
        bot.answer_callback_query(call.id, "к сожалению данная кнопка пока в разработке")




bot.polling(none_stop=True, interval=0)