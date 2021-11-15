import requests
import telebot
import config
import pytz
import subprocess
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import nltk

nltk.download('punkt')
from nltk import word_tokenize
from nltk.corpus import stopwords
import speech_recognition as sr
from google.oauth2 import service_account

text = []
text1=''



key_path = r"C:\Users\user\Desktop\bot\heroic-charter-331617-ee3ee22d50d3.json"
credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

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
        question = 'что Вы хотите сделать?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
        bot.send_message(message.from_user.id, " функция 'текст в текст' переводит Ваш текст в более сжатый вариант")
        bot.send_message(message.from_user.id,
                         "функция 'аудио в текст' переводит Ваше голосовое сообщение в сжатый текстовый вариант ")
        bot.send_message(message.from_user.id,
                         "функция 'аудио в аудио' переводит Ваше голосовое сообщение в более сжатое аудиосообщение ")
        bot.send_message(message.from_user.id,
                         "функция 'текст' выводит текст из голосового сообщения")
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "text":
        bot.answer_callback_query(call.id, "пришлите голосовое сообщение")

        @bot.message_handler(content_types=['voice'])
        def handle_audio(message):
            global text1
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

            stop = ['ох', 'ой', 'пли', 'ух', 'фу', 'фи', 'ага', 'ах', 'апчхи', 'батюшки', 'браво', 'господи', 'ишь ты',
                    'боже ж ты мой', 'о чёрт', 'ни фига себе', 'ай молодца', 'молодец', 'молодчина', 'да ну', 'господи',
                    'жуть', 'ужас' 'класс', 'а толку что', 'аттолку то', 'а чего ж', 'а что', 'а что ж', 'ааа',
                    'агуленьки', 'агулечки', 'агунюшки', 'агушеньки', 'адью ае', 'ай да', ' ай-ай-ай', 'ай-люли',
                    'ай-я-яй', 'ай-яй-яй', 'айда', 'айда-те', 'айдате', 'алаверды', 'алё', 'алле', 'алле-гоп',
                    'аллилуйя', 'алло', ' ам', 'ам-ам', 'амба', 'аминь', 'анкор', ' ап', 'апорт', 'асеньки', 'асса',
                    'ась', 'атанда', 'атанде', 'атас', 'ату', 'ать', 'ау', 'ах', 'ах вон что', 'aх вот как',
                    'ах вот что', 'ах так', 'ах ты', 'ах-ах', ' ах-ах-ах', 'ахти', 'ахти-хти', 'ахтунг', 'ба',
                    'баиньки', 'баиньки-баю', 'бай-бай', 'банзай', 'баста', 'бац', 'баю', 'баю-баю', 'баю-баю-баю',
                    'баю-баюшки-баю', 'баюшки-баю', 'бе',
                    'бинго', 'бис', 'бла-бла-бла', 'блин', 'бо-бо', 'боже', 'бр', 'брависсимо', 'браво', 'брейк',
                    'брысь', 'бугага', 'буц', 'бяша', 'вау', 'вах', 'виват', 'вира', 'вольно', 'вон', 'вуаля', 'да-а',
                    'да-да', 'да-да-да', 'долой', 'досвидос', 'достаточно', 'дудочки', 'дык', 'ё', 'ё-моё', ' ей-богу',
                    'ей Богу', 'ей ей', 'ёклмн', 'ёксель-моксель', 'ёлки моталки', 'ёлки-палки', 'ёлы-палы', 'ёпрст',
                    'ессно', 'есть', 'ёшкин кот', 'здорово', 'здрасте', 'здрасьте', 'и-го-го', 'извините', 'иншала',
                    'иншалла', 'иншалла', 'исполать', 'р', 'раз-два', 'йоу', 'как бы не так', 'кап', 'карамба', 'кек',
                    'кис-кис', ' ко-ко-ко', 'кругом', 'крутяк', 'кусь', 'кхм', 'кш', ' кыс', 'кыш', 'ловко', 'ля-ля-ля',
                    'м', 'м-да', 'мм', 'майна', 'мама миа', 'маран-афа', 'марш', 'матушки', 'мах', 'ме', 'мерси', 'мм',
                    'мяу', 'нда', 'нате', 'нете', 'ни-ни', 'но', 'но-но', 'ну', 'ну-ка', 'ну-кась', 'ну-кася', 'ну-ко',
                    'ну-кось',
                    'ну-ну', 'ну-тка', 'нуте', 'нуте-ка', 'нуте-с', 'ня', 'о', ' о-го-го', 'о-ля-ля', 'о-о', 'о-хо-хо',
                    'обана', 'ого', 'одначе', 'ой', 'ой йо', 'оп', 'опа', 'опаньки', 'опля', 'оу', 'ох', 'охоньки',
                    'охохоньки', 'охохонюшки', 'охохохоньки', 'охохошеньки', 'охти', 'пак', 'пас', 'пиль', 'пли',
                    'плие', 'поди', 'покеда', 'полундра', 'превед', 'прозит', 'прысь', 'псст', 'пст', 'пух', 'пфу',
                    'пфуй', 'пшш', 'салам', 'салям', 'светыньки', 'слышь', 'сорри', 'сорян', 'ссс', 'стопэ', 'тик-так',
                    'то-то', 'топ', 'точнямба', 'тпру', 'трах', 'тррр', 'тс', 'тсс', 'тубо', 'тьфу', 'тю', 'тюк', 'тяф',
                    'у', 'увы', 'угу', 'ужо', 'ужотко', 'упс', 'ура', 'уря', 'уси-пуси', 'усь', 'уть', 'уф', 'у', 'фап',
                    'фас', 'фи', 'физкульт-привет', 'фить', 'фу', 'фу-ты', 'фу-фу', 'фуй', 'фук', 'фух', 'фырк',
                    'фьють', 'фюйть', 'ц-ц-ц', 'цап', 'цок', 'цып-цып', 'цыц', 'чао', 'чёрт его знает', 'чирик', 'чих',
                    'чу', 'чур', 'чух', 'чш', 'чшш', 'ш-ш', ' ш-ш-ш', 'ша', 'шабаш', 'шит', 'шлик', 'шу', 'шш', 'щёлк',
                    'щуп', 'э', 'э-ге-ге', 'э-хе-хе', 'э-э', ' э-э-э', 'эва', 'ых']
            stop_words = stopwords.words('russian') + stop
            token = word_tokenize(text)
            cleaned_text = []
            for word in token:
                if word not in stop_words and word.lower() not in stop_words:
                    cleaned_text.append(word)
            for word in cleaned_text:
                text1 += " " + word

            bot.send_message(message.from_user.id, text1)
    elif call.data == "texttotext":
        bot.answer_callback_query(call.id, "к сожалению данная кнопка пока в разработке")
    elif call.data == "audiototext":
        bot.answer_callback_query(call.id, "к сожалению данная кнопка пока в разработке")
    elif call.data == "audiotoaudio":
        bot.answer_callback_query(call.id, "к сожалению данная кнопка пока в разработке")


bot.polling(none_stop=True, interval=0)
