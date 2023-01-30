from aiogram import types, executor
from dispatcher import dp
import config
import re
from bot import Bot_DB


@dp.message_handler(commands = 'start') #можно ли без префикса
async def start(message: types.Message):
	if(not Bot_DB.user_exists(message.from_user_id)):
		Bot_DB.add_user(message.from_user_id)
	await message.bot.send_message(message.from_user_id, 'Добро пожаловать!')

@dp.message_hansler(commands = ('spend', 's', 'earned', 'e'), commands_prefix = '/!')
async def record(message: types.Message):
	commands_var = ('/spent', '/s'), ('/earned', 'e') #убрала некоторые варианты
	operation = '-' if message.text.startwith(commands_var[0]) else '+'
	value = message.text
	for i in commands_var:
		for j in i:
			value = value.replace(j, '').strip()
	if(len(value)):
		x = re.findall(r'\d+(?:.\d+)?')
		if(len(x)):
			value = float(x[0].replace(',', '.'))
			Bot_DB.add_record(message.from_user.id, operation, value)
			if(operation == '-'):
				await message.reply('✔ Запись о расходе успешно внесена')
			else:
				await message.reply('✔ Запись о доходе успешно внесена')
		else:
			message.reply('❌ Не удалось определить сумму. Пожалуйста, повторите ввод')
	else:
		await message.reply('❌ Сумма не введена. Пожалуйста, повторите ввод')

@dp.message_handler(commands = ('histiry', 'h'), commands_prefix = '/!') #можно ли без префикса
async def history(essage: types.Message):
	commands_var = ('/history', '/h')
	within_all = {'day': ('today', 'day'), 'week': ('week'), 'month': ('month'), 'year': ('year')}
	command = message.text
	for r in commands_var:
		command = command.replace(r, '').strip()
	within = 'day' #default
	if(len(command)):
		for k in within_all:
			for el in within_all[k]:
				if(el == command):
					within = k
					el_foranswer = el
	records = Bot_DB.get_records(message.from_user.id, within)
	if(len(records)):
		answer = f'🕜 История операций за {el_foranswer}'
		for r in records:
			answer +=  '➖ Расход' if not r[2] else '➕ Доход'
			answer += f' - {r[3]}'
			answer += r[4] #пропустила много
		await message.reply(answer)
	else:
		await message.reply('Записей не обнаружено')