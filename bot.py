import time
import logging
import re

from aiogram import Bot, Dispatcher, executor, types

from database import BotDB

TOKEN = '5982878085:AAFm4tJUlFMQW_tYwXGnT4NkLLC5AjJNgWc'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
db = 'BOT_database.db'

Bot_DB = BotDB(db)

@dp.message_handler(commands = 'start')
async def start(message: types.Message):
    user_full_name = message.from_user.full_name
    logging.info(f'{message.from_user.id} {user_full_name=} {time.asctime()}')
    if(not Bot_DB.user_exists(message.from_user.id)):
        Bot_DB.add_user(message.from_user.id)
    await message.reply(f"Привет, {user_full_name} 🙂\nЯ к твоим услугам!\n\nИспользуй /help для изучения моих команд")

@dp.message_handler(commands = ('help'), commands_prefix = '/!')
async def hepl(message: types.Message):
    await message.reply('🆘 Команды бота:\n/spent (сумма) (категория расходов) - добавление расходов\n/earned (сумма) (категория доходов) - добавление доходов\n❕ Сумму и категорию вводите через пробел\n❕ Пожалуйста, подумайте, какие категории расходов и доходов будут использованы в моих расчётах, и придерживайтесь их\n/statistics - вывод статистики расходов и доходов\n/total - вывод текущего баланса\n/history - вывод истории операций\n/delete (номер строки из Истории операций) - удаление записи\n❕ Если хотите удалить все записи используйте /delete all')

@dp.message_handler(commands = ('spent', 'earned'),  commands_prefix = '/!') #можно ли без префикса
async def record(message: types.Message):
    commands_var = (('/spent', '!spent'), ('/earned', '!earned'))
    operation = '-' if message.text.startswith(commands_var[0]) else '+'
    mes =  message.text
    if len(list(mes.split(' '))) == 3:
        value, category = mes.split(' ')[1], mes.split(' ')[2].strip()
        if len(value) > 0 and len(category) > 0:
            x = re.findall(r"\d+(?:.\d+)?", value)
            if(len(x)):
                value = float(x[0].replace(',', '.'))
                Bot_DB.add_record(message.from_user.id, operation, value, category)
                if operation == '-': #сбилось условие, всегда выбивает доход
                    await message.reply('✅ Запись о расходе успешно внесена')
                else:
                    await message.reply('✅ Запись о доходе успешно внесена')
            else:
                await message.reply('❕ Не удалось определить сумму. Пожалуйста, повторите ввод')
    else:
        await message.reply('❕ Не введена сумма либо категория. Пожалуйста, повторите ввод')

@dp.message_handler(commands = ('history', 'h'), commands_prefix = '/!') #можно ли без префикса
async def history(message: types.Message):
    records = Bot_DB.get_records(message.from_user.id)
    if len(records) > 0:
        answer = f'🕜 История операций:\n\n'
        for r in records:
            answer += f'{records.index(r) + 1}. '
            answer += '➖' if r[2] == '-' else '➕'
            answer += f'{r[3]} zł.\n    Категория: {r[5]}\n    Дата: {r[4]}\n'
        await message.reply(answer)
    else:
        await message.reply('❕ Записей не обнаружено')

@dp.message_handler(commands = ('statistics'), commands_prefix = '/!')
async def statistics(message: types.Message):
    records = Bot_DB.get_records(message.from_user.id)
    if len(records) > 0:
        answer = f'Статистика расходов и доходов:\n\n'
        res_p = {}
        res_l = {}
        p = 0
        l = 0
        for r in records:
            if r[2] == '+':
                p += r[3]
                res_p[r[5]] = res_p.get(r[5], 0) + r[3]
            else:
                l += r[3]
                res_l[r[5]] = res_l.get(r[5], 0) + r[3]
        max_p = [i for i in res_p if res_p[i] == max(res_p.values())]
        max_l = [j for j in res_l if res_l[j] == max(res_l.values())]
        await message.reply(f"📊 Статистика расходов и доходов:\n\nПолучено всего: {p} zł\nИзрасходовано всего: {l}zł\nНаибольшая доля доходов приходится на категорию/и: {', '.join(max_p)}\nНаибольшая доля расходов приходится на категорию/и: {', '.join(max_l)}\n")
    else:
        await message.reply('❕ Записей не обнаружено')

@dp.message_handler(commands = ('total'), commands_prefix = '/!')
async def total(message: types.Message):
    records = Bot_DB.get_records(message.from_user.id)
    result = 0
    if len(records) > 0:
        for r in records:
            if r[2] == '+':
                result += r[3]
            else:
                result -= r[3]
        await message.reply(f"💸 Всего: {result} zł")
    else:
        await message.reply('❕ Записей не обнаружено')

@dp.message_handler(commands = ('delete'), commands_prefix = '/!')
async def total(message: types.Message):
    records = Bot_DB.get_records(message.from_user.id)
    delete_record = message.text.split(' ')[1].strip()
    if delete_record == 'all':
        answer = Bot_DB.delete_all(message.from_user.id)
        await message.reply(answer)
    elif delete_record.isdigit() and int(delete_record) <= len(records) + 1:
        record_date = records[int(delete_record)-1][4]
        answer = Bot_DB.delete_record(message.from_user.id, record_date)
        await message.reply(answer)
    else:
        await message.reply('❕ Пожалуйста, уточните, какую запись вы хотите удалить')

if __name__ == '__main__':
    executor.start_polling(dp)