import requests
import telebot
import config
import pytz
import subprocess
import random
import nltk
import speech_recognition as sr
import torch
from classic_extractive import sentence_summary_trf, build_classic_nlp_pipeline
from nltk.tokenize import sent_tokenize
# from nltk.corpus import stopwords
# from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from nltk import word_tokenize
from transformers import MBartTokenizer, MBartForConditionalGeneration

model_name = "IlyaGusev/mbart_ru_sum_gazeta"
tokenizer = MBartTokenizer.from_pretrained(model_name)
model = MBartForConditionalGeneration.from_pretrained(model_name)

model_punct, example_texts, languages, punct, apply_te = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                                  model='silero_te')
flag = True
nltk.download('punkt')
nlp = build_classic_nlp_pipeline()
print("ready")




def abstractive(article_text, tokenizer=tokenizer, model=model):
    input_ids = tokenizer(
        [article_text],
        max_length=600,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )["input_ids"]

    output_ids = model.generate(
        input_ids=input_ids,
        no_repeat_ngram_size=4
    )[0]

    summary = tokenizer.decode(output_ids, skip_special_tokens=True)
    return summary

def cleaning(text):
    stop = ['ох', 'ой', 'ух', 'фу', 'фи', 'ага', 'ах', 'апчхи', 'господи', 'ишь ты',
            'боже ж ты мой', 'о чёрт', 'ни фига себе', 'ай молодца', 'господи',
            'жуть', 'класс', 'а толку что', 'аттолку то', 'а чего ж', 'а что', 'а что ж', 'ааа',
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
    stop_words = stop
    token = word_tokenize(text)
    cleaned_token = []
    for word in token:
        if word not in stop_words:
            cleaned_token.append(word)
    return cleaned_token


text = []


P_TIMEZONE = pytz.timezone(config.TIMEZONE)
TIMEZONE_COMMON_NAME = config.TIMEZONE_COMMON_NAME
bot = telebot.TeleBot(config.token)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/inf':
        bot.send_message(message.chat.id,
                         "чтобы использовать данного бота напишите одну из команд")
        bot.send_message(message.chat.id,
                         "команда /audio_to_text выводит краткое содержание Вашего текста")

        bot.send_message(message.chat.id,
                         "команда /text выводит текст из голосового сообщения")

        bot.send_message(message.chat.id,
                         "команда /audio_to_highlighted выводит текст из голосового сообщения, в котором выделена "
                         "главная мысль")



    elif message.text == '/text':
        print('/text')
        bot.send_message(message.chat.id, "пришлите голосовое сообщение")

        @bot.message_handler(content_types=['voice'])
        def handle_audio(message):
            file_info = bot.get_file(message.voice.file_id)
            file = requests.get(
                'https://api.telegram.org/file/bot{0}/{1}'.format('1906481644:AAFYdV_gPAqiKcPWQt0SzvSnFfLVLIuBNHs',
                                                                  file_info.file_path))
            src = file_info.file_path[:6] + 'ogg' + file_info.file_path[5:]
            dst = file_info.file_path[:6] + 'wav' + file_info.file_path[5:-3] + 'wav'
            downloaded_file = bot.download_file(file_info.file_path)
            with open('file.ogg', 'wb') as f:
                f.write(downloaded_file)
            b = random.randint(0, 1000)

            src_filename = 'file.ogg'
            dest_filename = f'file{b}.wav'
            process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
            try:
                r = sr.Recognizer()
                with sr.AudioFile(dest_filename) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio, language="ru-RU")

                text = text.lower()
                text = apply_te(text, lan='ru')

                # text=cleaning(text)

                bot.send_message(message.chat.id, text)
            except:
                bot.send_message(message.chat.id, "к сожалению ваше аудио не удалось распознать :(")




    elif message.text == "/audio_to_text":
        print("/audio_to_text")
        bot.send_message(message.chat.id, "пришлите голосовое сообщение")
        @bot.message_handler(content_types=['voice'])
        def handle_audio(message):
            file_info = bot.get_file(message.voice.file_id)
            file = requests.get(
                'https://api.telegram.org/file/bot{0}/{1}'.format('1906481644:AAFYdV_gPAqiKcPWQt0SzvSnFfLVLIuBNHs',
                                                                  file_info.file_path))
            src = file_info.file_path[:6] + 'ogg' + file_info.file_path[5:]
            dst = file_info.file_path[:6] + 'wav' + file_info.file_path[5:-3] + 'wav'
            downloaded_file = bot.download_file(file_info.file_path)

            with open('file.ogg', 'wb') as f:
                f.write(downloaded_file)

            b = random.randint(0, 1000)
            src_filename = 'file.ogg'
            dest_filename = f'file{b}.wav'
            process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
            try:
                r = sr.Recognizer()
                with sr.AudioFile(dest_filename) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio, language="ru-RU")
            except:
                bot.send_message(message.chat.id, "к сожалению, Ваше аудио не удалось распознать :(")
            print(text)
            text = text.lower()
            text = apply_te(text, lan='ru')

            abst_text = abstractive(text)

            bot.send_message(message.chat.id, abst_text, parse_mode='Markdown')


    elif message.text == "/audio_to_highlighted":
        print("/audio_to_text")
        bot.send_message(message.chat.id, "пришлите голосовое сообщение")

        @bot.message_handler(content_types=['voice'])
        def handle_audio(message):
            file_info = bot.get_file(message.voice.file_id)
            file = requests.get(
                'https://api.telegram.org/file/bot{0}/{1}'.format('1906481644:AAFYdV_gPAqiKcPWQt0SzvSnFfLVLIuBNHs',
                                                                  file_info.file_path))
            src = file_info.file_path[:6] + 'ogg' + file_info.file_path[5:]
            dst = file_info.file_path[:6] + 'wav' + file_info.file_path[5:-3] + 'wav'
            downloaded_file = bot.download_file(file_info.file_path)

            with open('file.ogg', 'wb') as f:
                f.write(downloaded_file)

            b = random.randint(0, 1000)
            src_filename = 'file.ogg'
            dest_filename = f'file{b}.wav'
            process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
            try:
                r = sr.Recognizer()
                with sr.AudioFile(dest_filename) as source:
                    audio = r.record(source)
                    text = r.recognize_google(audio, language="ru-RU")
            except:
                bot.send_message(message.chat.id, "к сожалению, Ваше аудио не удалось распознать :(")
            text = text.lower()
            text = apply_te(text, lan='ru')

            ext_text = sentence_summary_trf(text=text, nlp=nlp)

            ext_text = sent_tokenize(ext_text)

            text = sent_tokenize(text)
            text1 = ""
            i = 0
            for sent in range(len(text)):
                if text[sent] == ext_text[i]:
                    text[sent] = '*' + text[sent] + '*'
                    text1 += text[sent]
                    i += 1
                else:
                    text1 += text[sent]

            bot.send_message(message.chat.id, text1, parse_mode='Markdown')

    else:
        bot.send_message(message.chat.id, 'Такой команды я не знаю, напишите /inf, чтобы узнать, как я работаю')


bot.polling(none_stop=True, interval=0)
