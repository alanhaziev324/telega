import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

import psycopg2
from filters import host, user, password, db_name

from filters import IsAdminFilter

bot = Bot(token="5474658841:AAHJ_VHfPRkUuJBPEy8ig39GR2Q53aPBPMk")
chat_id = "730684252"
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.filters_factory.bind(IsAdminFilter)
logging.basicConfig(level=logging.INFO)
x = []
ban = open('mat.txt', 'r+', encoding="utf8")
with ban as file:
    for line in file:
        x.append(line[0:-1])
print(x)


class Form(StatesGroup):
    name = State()
    file = State()


def ban_input(t):
    my_file = open("mat.txt", "a", encoding="utf8")
    ban = str(t).split()
    my_file.write(ban[1])
    my_file.write("\n")
    my_file.close()


@dp.message_handler(commands="prog")
async def start(message: types.Message):
    await Form.name.set()
    await message.reply('Опишите свою программу')


@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Cancelled.')


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        data['id'] = message.from_user.id
        print(data['id'], data['name'])

    await Form.next()
    await message.reply("Отправьте файл с кодом или напишите /cancel если хотите отменить")


@dp.message_handler(content_types=["document"], state=Form.file)
async def process_age_invalid(message: types.Message, state: FSMContext):
    await message.reply("Готово!")
    async with state.proxy() as data:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT version();"
            )
            print(f"version: {cursor.fetchone()}")

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (idtg, description, idfile) VALUES (%s,%s,%s)",
                           (data['id'], data['name'], message.document.file_id))


@dp.message_handler(is_admin=True, commands=["ban"])
async def cmd_ban(messag: types.Message):
    if not messag.reply_to_message:
        await messag.reply("Эта команда должна быть ответом на сообщение")
        return
    await bot.kick_chat_member(chat_id=messag.chat.id, user_id=messag.reply_to_message.from_user.id)
    await messag.delete()


@dp.message_handler(commands=['mat'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.from_user.id, message.text)
    print(message.text)
    ban_input(message.text)


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    mes = str(msg.text.lower()).split()
    print(*mes)
    if set(mes) & set(x):
        await bot.kick_chat_member(chat_id=msg.chat.id, user_id=msg.from_user.id)
        await msg.delete()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
