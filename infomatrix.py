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
import json

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
	bot.reply_to(message, '''
Сәлеметсіз бе, мен информатика бойынша ҰБТ-ға дайындалуға көмектесетін AI-ботпын!
Сізбен жұмыс істейік!
Нақты не істегіңіз келетінін таңдаңыз;

Ботта қол жетімді командалар:
/start /help - сіз Бұл хабарламаны көресіз және мәзірдің негізгі бетіне өтесіз
/report - сіз ботты жақсартуға немесе мәселеге өтініш бере аласыз.
		''', reply_markup=home_menu())


@bot.message_handler(func=lambda message: True)
def response(message):
	if message.text == "Курстар ҰБТ":
		bot.reply_to(message, "Course on ENT", reply_markup=menu(2,
			'Тақырыптың ҰБТ'
			'Тапсырмалар ҰБТ'
			'AI сұраңыз' ))

	elif message.text == "Бағдарламалау курстары":
		msg_bot = bot.send_message(message.chat.id,"Course prog\n Choose Theme", reply_markup=menu(1,
			'Theme 1'
			'Theme 2'
			'Theme 3'
			'Theme 4'))
		bot.register_next_step_handler(msg_bot,)

	elif message.text == "Тақырыптың ҰБТ":
		msg_bot = bot.send_message(message.chat.id,"Please choose theme", reply_markup=menu(1,
			'1.ENT. Системы исчисления в информатике: перевод чисел',
			'2.ENT. Хранение данных и Память в Информатике',
			'3.ENT. Сети и Их Топологии в Информатике',
			'4.ENT. Основы Баз Данных и Реляционные Системы Управления Базами Данных (СУБД)'))

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

		msg_bot = bot.send_message(message.chat.id, text , reply_markup = menu(2,
																	'Тапсырма',
																	'AI сұраңыз',
																	'Артқа'))

		def func(message):
			nonlocal spl_txt
			theme_kb(message, spl_txt[2])

		bot.register_next_step_handler(msg_bot, func)

	elif message.text == "Артқа":
		msg_bot = bot.send_message(message.chat.id , "Home" , reply_markup = home_menu())

	elif message.text == "Тапсырмалар ҰБТ":
		msg_bot = bot.send_message(message.chat.id,"Please choose theme", reply_markup=menu(1, 
			'1.Задания ЕНТ. Санды өлшемдері және оларды басқару жолдары'
			'2.Задания ЕНТ. Хранение данных и Память',
			'3.Задания ЕНТ. Сети и Их Топологии', 
			'4.Задания ЕНТ. Основы Баз Данных и Реляционные Системы Управления Базами Данных (СУБД)'))

	elif message.text == "Көмек AI":
		msg_bot = bot.send_message(message.chat.id,"Please write question")
		bot.register_next_step_handler(msg_bot,help_ai)

	elif message.text == "AI сұраңыз":
		msg_bot = bot.send_message(message.chat.id,"Please write question")
		bot.register_next_step_handler(msg_bot,help_ai)

	else:
		bot.reply_to(message, "I dont know")

		
# def help_ai_on_themes(message , material):
# 	prompt_with_material = f"{prompt}\nMaterial: {material}\nAnswer:"
# 	response = openai.Completion.create(
# 		engine="text-davinci-003",
# 		prompt=prompt_with_material,
# 		max_tokens=150,
# 		temperature=0.7,
# 		stop=stop
# 	)

# 	answer = response.choices[0].text.strip()
# 	return answer

def theme_kb(message, theme):
	if message.text == "Артқа":
		bot.send_message(message.chat.id,"Басты бет" ,markup = home_menu())
	elif message.text == "AI сұраңыз":
		help_ai(message)
	elif message.text == "Тапсырма":
		q_test(message, theme)


def q_test(message, theme):
	text = f'''
Сгенерируй мне тест по теме {theme}, но выйдай его в определенном виде для парсинга: 
создай json объект вне массива в котором есть массив test, 
в котором есть 6 вопросов-объектов сотоящий из полей quest- сам текст вопроса, массив ответов answers- массив вариантов ответов состоящий из полей code и text;
и еще поле true_ans которое должно быть в объекте вопроса и содержать код правельного ответа, а не в объекте ответа;
НЕ ПИШИ НИЧЕГО КРОМЕ JSON ФАЙЛА.'''

	print(text)

	user_score = 0

	try:
		completion = client.chat.completions.create(
			model="gpt-3.5-turbo",
			messages=[
				{"role": "system", "content": "You are a self-improvement assistant."},
				{"role": "user", "content": f"{text}"}
			]
		)
		response_message = completion.choices[0].message.content  # Accessing the content directly
		print(response_message)  # For debugging
	except Exception as e:
		bot.reply_to(message, f"An error occurred: {str(e)}")

	quest = json.loads(response_message)

	def func(msg, ans):
		nonlocal quest
		nonlocal user_score

		if ans == len(quest["test"]):
			if quest["test"][ans-1]["true_ans"] == msg.text.split(".")[0]:
				bot.send_message(msg.chat.id, "Молодец!")
				user_score+=1
			else:
				bot.send_message(msg.chat.id, "В следущий раз получиться!")

			bot.send_message(msg.chat.id, f'Вы закончили тест! Ваш результат {user_score}/{(len(quest["test"]))}',
				reply_markup = menu(1,"Артқа"))
			return
		elif ans > 0:
			if quest["test"][ans-1]["true_ans"] == msg.text.split(".")[0]:
				bot.send_message(msg.chat.id, "Молодец!")
				user_score+=1
			else:
				bot.send_message(msg.chat.id, "В следущий раз получиться!")

		print(quest["test"][ans-1]["true_ans"])
		print(msg.text.split(".")[0])

		answers = []
		for qst in quest["test"][ans]["answers"]:
			answers.append(f'{qst["code"]}. {qst["text"]}')

		msg_bot = bot.send_message(msg.chat.id, 
						f'{ans+1}. {quest["test"][ans]["quest"]}',
						reply_markup = menu(2, *answers))

		bot.register_next_step_handler(msg_bot, lambda msg: func(msg, ans+1))

	func(message, 0)





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
	bot.send_message(chat_id, "Есеп бергеніңіз үшін рахмет. Біз оны мүмкіндігінше тезірек қарастырамыз.")


def home_menu():
	return menu(2, 'Тақырыптың ҰБТ' , 'Тапсырмалар ҰБТ' , 'AI сұраңыз')

def menu(rows, *text_buttons):
	markup = types.ReplyKeyboardMarkup(row_width=rows)
	btns = []

	for btn in text_buttons:
		btns.append(types.KeyboardButton(btn))

	markup.add(*btns)
	return markup


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

