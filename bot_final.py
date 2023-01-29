import requests
import telebot
import pytz
import subprocess
import random
import nltk
import speech_recognition as sr
import torch
from classic_extractive import sentence_summary_trf, build_classic_nlp_pipeline
from nltk.tokenize import sent_tokenize
from transformers import MBartForConditionalGeneration, MBartTokenizer
from nltk import word_tokenize


path1=r"C:\Users\user\Desktop\mbart_sum\tokenizer"
path=r"C:\Users\user\Desktop\mbart_sum"
text = ""

#обработка весов модели для суммаризации
tokenizer = MBartTokenizer.from_pretrained(path1)
model = MBartForConditionalGeneration.from_pretrained(path)


bot = telebot.TeleBot('1906481644:AAFYdV_gPAqiKcPWQt0SzvSnFfLVLIuBNHs')# Создаем экземпляр бота

#подгрузка модели для расставления пунктуации
model_punct, example_texts, languages, punct, apply_te = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                                        model='silero_te')
nltk.download('punkt')
nlp = build_classic_nlp_pipeline()


#функция для абстрактивной суммаризации
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


print("ready")

#описание послуедующих команд
@bot.message_handler(commands=['inf'])
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


@bot.message_handler(commands=['text']) #функция бота /text
def send_auth(message):
    bot.send_message(message.chat.id, "пришлите голосовое сообщение")
    bot.register_next_step_handler(message, voice2text)


def voice2text(message):
    file_info = bot.get_file(message.voice.file_id)
    # перевод формата .OGG в .WAV
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
    # распознавание речи из голосового сообщения
    try:
        r = sr.Recognizer()
        with sr.AudioFile(dest_filename) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language="ru-RU")

        text = text.lower()
        text = apply_te(text, lan='ru')

        bot.send_message(message.chat.id, text)
    except:
        bot.send_message(message.chat.id, "к сожалению ваше аудио не удалось распознать :(")


@bot.message_handler(commands=['audio_to_highlighted'])#функция бота /audio_to_highlighted
def send_aud(message):
    bot.send_message(message.chat.id, "пришлите голосовое сообщение")
    bot.register_next_step_handler(message, voice2highlight)


def voice2highlight(message):
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
    except:
        bot.send_message(message.chat.id, "к сожалению, Ваше аудио не удалось распознать :(")


@bot.message_handler(commands=['audio_to_text'])#функция бота /audio_to_text
def send_audio(message):
    bot.send_message(message.chat.id, "пришлите голосовое сообщение")
    bot.register_next_step_handler(message, audio2text)


def audio2text(message):
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
            abst_text = abstractive(text)

            bot.send_message(message.chat.id, abst_text, parse_mode='Markdown')

    except:
        bot.send_message(message.chat.id, "к сожалению, Ваше аудио не удалось распознать :(")


bot.polling(none_stop=True, interval=0)
