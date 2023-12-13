from openai import OpenAI
import telebot
from telebot import types
import logging
import requests
from gtts import gTTS
import io
from tempfile import TemporaryFile
import speech_recognition as sr
from pydub import AudioSegment
import re

import os 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)
logger = logging.getLogger(__name__)

token = ''
os.environ["OPENAI_API_KEY"] = ""
client = OpenAI(
	api_key=os.environ.get(""),
)


bot = telebot.TeleBot(token)

admin_id = ''

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
	markup = types.ReplyKeyboardMarkup(row_width=2)
	itembtn1 = types.KeyboardButton(text = 'Course for ENT')
	itembtn2 = types.KeyboardButton('Course progr')
	itembtn3 = types.KeyboardButton('Help AI')
	markup.add(itembtn1, itembtn2, itembtn3)
	bot.reply_to(message, "Welcome test msg", reply_markup=markup)

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
	markup = types.ReplyKeyboardMarkup(row_width=2)
	itembtn1 = types.KeyboardButton('Course for ENT')
	itembtn2 = types.KeyboardButton('Course progr')
	itembtn3 = types.KeyboardButton('Help AI')
	markup.add(itembtn1, itembtn2, itembtn3)
	bot.reply_to(message, "Welcome test msg", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def response(message):
	if message.text == "Course for ENT":					# ENT course choise
		markup = types.ReplyKeyboardMarkup(row_width=2)
		itembtn1 = types.KeyboardButton('ENT Themes')
		itembtn2 = types.KeyboardButton('ENT Zadania')
		itembtn3 = types.KeyboardButton('Sprosi u AI')
		markup.add(itembtn1, itembtn2, itembtn3)
		bot.reply_to(message, "Course on ENT", reply_markup=markup)

	elif message.text == "Course progr":
		markup = types.ReplyKeyboardMarkup(row_width=2)
		itembtn1 = types.KeyboardButton('Theme 1')
		itembtn2 = types.KeyboardButton('Theme 2')
		itembtn3 = types.KeyboardButton('Theme 3')
		itembtn4 = types.KeyboardButton('Theme 4')
		markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
		msg_bot = bot.send_message(message.chat.id,"Course prog\n Choose Theme", reply_markup=markup)
		bot.register_next_step_handler(msg_bot,)

	elif message.text == "ENT Themes":
		markup = types.ReplyKeyboardMarkup(row_width=1)
		theme_btn_1 = types.KeyboardButton('1.ENT. Системы исчисления в информатике: перевод чисел')
		theme_btn_2 = types.KeyboardButton('2.ENT. Хранение данных и Память в Информатике')
		theme_btn_3 = types.KeyboardButton('3.ENT. Сети и Их Топологии в Информатике')
		theme_btn_4 = types.KeyboardButton('4.ENT. Основы Баз Данных и Реляционные Системы Управления Базами Данных (СУБД)')

		markup.add( theme_btn_1,
					theme_btn_2,
					theme_btn_3,
					theme_btn_4 )

		msg_bot = bot.send_message(message.chat.id,"Please choose theme", reply_markup=markup)

	elif re.fullmatch(r'\d\.\w+\..+' , message.text):
		spl_txt = message.text.split(".")
		fname = spl_txt[0]+"_theme_"
		match spl_txt[1]:
			case "ENT":
				fname += "ent.txt"
			case "PROG":
				fname += "prog.txt"

		file = open(fname , "r" , encoding="utf8")
		text = ""
		for line in file:
			text += line
		file.close()

		markup = types.ReplyKeyboardMarkup(row_width=2)
		back_btn = types.KeyboardButton('Back')
		ai_btn = types.KeyboardButton('Sprosi u AI')
		quest_btn = types.KeyboardButton('Quest')

		markup.add(	ai_btn,
					quest_btn,
					back_btn )

		msg_bot = bot.send_message(message.chat.id, text , reply_markup = markup)

	elif message.text == "Back":
		markup = types.ReplyKeyboardMarkup(row_width=2)
		itembtn1 = types.KeyboardButton('Course for ENT')
		itembtn2 = types.KeyboardButton('Course progr')
		itembtn3 = types.KeyboardButton('Help AI')
		markup.add(itembtn1, itembtn2, itembtn3)

		msg_bot = bot.send_message(message.chat.id , "Home" , reply_markup = markup)

	elif message.text == "ENT Zadania":
		msg_bot = bot.send_message(message.chat.id,"Please write question")
		bot.register_next_step_handler(msg_bot,help_ai)

	elif message.text == "Help AI":
		msg_bot = bot.send_message(message.chat.id,"Please write question")
		bot.register_next_step_handler(msg_bot,help_ai)

	elif message.text == "Sprosi u AI":
		msg_bot = bot.send_message(message.chat.id,"Please write question")
		bot.register_next_step_handler(msg_bot,help_ai)

	else:
		bot.reply_to(message, "I dont know")

		
def help_ai_on_themes(message , material):
	prompt_with_material = f"{prompt}\nMaterial: {material}\nAnswer:"
	response = openai.Completion.create(
		engine="text-davinci-003",
		prompt=prompt_with_material,
		max_tokens=150,
		temperature=0.7,
		stop=stop
	)

	answer = response.choices[0].text.strip()
	return answer


def help_ai(message):
	try:
		completion = client.chat.completions.create(
			model="gpt-3.5-turbo",
			messages=[
				{"role": "system", "content": "You are a self-improvement assistant."},
				{"role": "user", "content": f"{message.text}"}
			]
		)
		response_message = completion.choices[0].message.content  # Accessing the content directly
		bot.reply_to(message, response_message)
		print(response_message)  # For debugging

	except Exception as e:
		bot.reply_to(message, f"An error occurred: {str(e)}")


@bot.message_handler(commands=['report'])
def report(msg):
	chat_id = msg.chat.id
	user_id = msg.from_user.id
	text = msg.text

	report_text = f"New report from user {user_id} in chat {chat_id}:\n\n{text}"
	bot.send_message(admin_id, report_text)
	bot.send_message(chat_id, "Thank you for your report. We will review it as soon as possible.")



#tts and stt

def text_to_speech (message):
	# Get the text message
	text = message.text
	# Generate audio file using the Google TTS API
	tts = gTTS(text=text)
	audio_file = TemporaryFile()
	tts.write_to_fp(audio_file) 
	audio_file.seek(0)
	# Convert audio file to ogg format and send to user
	audio = AudioSegment.from_file (audio_file, format="mp3")
	ogg_file = TemporaryFile()
	audio.export(ogg_file, format="ogg")
	ogg_file.seek(0)
	bot.send_voice (message.chat.id, ogg_file)
def voice_query(message): 

	if message.voice:
		# Get the voice recording file
		file_info = bot.get_file(message.voice.file_id)
		file_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path) 
		voice_file = requests.get(file_url)
		# Convert voice file to audio and then to text using the Google TTS API
		audio = AudioSegment.from_file(io.BytesIO(voice_file.content))
		audio_file = TemporaryFile()
		audio.export(audio_file, format="wav")
		audio_file.seek(0)
		r = sr.Recognizer()
		with sr.AudioFile(audio_file) as source: audio_data = r.record(source)
		text=r.recognize_google (audio_data)
		# Send the text message back to the user response = generate_response(text) bot.reply_to(message, response)
	else:
		bot.reply_to(message, "Please send a voice recording.")



bot.polling(none_stop=True)

