from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
import config as cfg
import logging
from aiogram.dispatcher import FSMContext
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from db import Sqlite
from states import Audio1, Audio2


logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=cfg.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
db = Sqlite('vodcast.db')


@dp.message_handler(commands='start')
async def start(message: types.Message):
    msg_arg = message.get_args()
    if msg_arg != '':
        if int(msg_arg) in db.get_group_id():
            print('true')
            for msg_id in db.get_by_group_id(int(msg_arg)):
                    requests.post(
                url=f'https://api.telegram.org/bot{cfg.TOKEN}/forwardMessage',
                data={f'chat_id': {message.from_user.id}, 'from_chat_id': {cfg.CHANELID}, 'message_id': {msg_id}}
                ).json()
        else:
            requests.post(
            url=f'https://api.telegram.org/bot{cfg.TOKEN}/forwardMessage',
            data={f'chat_id': {message.from_user.id}, 'from_chat_id': {cfg.CHANELID}, 'message_id': {msg_arg}}
            ).json()
    
    elif msg_arg == '':
        chanel_ = InlineKeyboardButton("КАНАЛ", url='t.me/tiktopaudio')
        chanel_menu = InlineKeyboardMarkup(row_width=1).add(chanel_)
        await bot.send_message(chat_id=message.from_user.id, text='Перейдите в канал для выбора', reply_markup=chanel_menu)


@dp.message_handler(commands='vodcast2')
async def audio1(message: types.Message):
    await message.answer('Отправьте фото')
    await Audio1.photo.set()

@dp.message_handler(state=Audio1.photo, content_types='photo')
async def get_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo_id=message.photo[-1].file_id)
    await message.answer('Отправьте описание')
    await Audio1.caption.set()

@dp.message_handler(state=Audio1.caption, content_types='text')
async def get_caption(message: types.Message, state: FSMContext):
    await state.update_data(caption = message.text)
    donebtn = KeyboardButton('Готово')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(donebtn)
    await message.answer('Отправьте аудио, а затем нажмите на кнопку ниже.', reply_markup=keyboard)
    await Audio1.file.set()

@dp.message_handler(state=Audio1.file, content_types="audio")
async def get_audio(message: types.Message, state: FSMContext):
    if message.media_group_id:
        response = requests.post(
        url=f'https://api.telegram.org/bot{cfg.TOKEN}/forwardMessage',
        data={f'chat_id': {cfg.CHANELID}, 'from_chat_id': {message.from_user.id}, 'message_id': {message.message_id}}
    ).json()
        db.add_music(response['result']['message_id'], message.media_group_id)
        btn = InlineKeyboardButton('Слушать', url=f"https://t.me/vodcastbot?start={ message.media_group_id}")
    else:
        response = requests.post(
        url=f'https://api.telegram.org/bot{cfg.TOKEN}/forwardMessage',
        data={f'chat_id': {cfg.CHANELID}, 'from_chat_id': {message.from_user.id}, 'message_id': {message.message_id}}
    ).json()
        btn = InlineKeyboardButton('Слушать', url=f"https://t.me/vodcastbot?start={response['result']['message_id']}")

    down_btn = InlineKeyboardMarkup(row_width=1).add(btn)
    await state.update_data(keyboard=down_btn)


@dp.message_handler(state=Audio1.file, text='Готово')
async def done(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.send_photo(chat_id= -1001174615692, photo=data['photo_id'], caption=data['caption'], reply_markup=data['keyboard'])
    await message.answer('Готово',reply_markup='')
    await state.finish()



@dp.message_handler(commands='vodcast1')
async def audio1(message: types.Message):
    await message.answer('Отправьте фото')
    await Audio2.photo.set()

@dp.message_handler(state=Audio2.photo, content_types='photo')
async def get_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo_id=message.photo[-1].file_id)
    await message.answer('Отправьте описание')
    await Audio2.caption.set()

@dp.message_handler(state=Audio2.caption, content_types='text')
async def get_caption(message: types.Message, state: FSMContext):
    await state.update_data(caption = message.text)
    await message.answer('Отправьте файл')
    await Audio2.file.set()

@dp.message_handler(state=Audio2.file, content_types='document')
async def get_doc(message: types.Message, state: FSMContext):
    response = requests.post(
        url=f'https://api.telegram.org/bot{cfg.TOKEN}/forwardMessage',
        data={f'chat_id': {cfg.CHANELID}, 'from_chat_id': {message.from_user.id}, 'message_id': {message.message_id}}
    ).json()
    btn = InlineKeyboardButton('Скачать книгу', url=f"https://t.me/vodcastbot?start={response['result']['message_id']}")
    await state.update_data(file_btn=btn)
    donebtn = KeyboardButton('Готово')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(donebtn)
    await message.answer('Отправьте аудио, а затем нажмите на кнопку ниже.', reply_markup=keyboard)
    await Audio2.audio.set()

@dp.message_handler(state=Audio2.audio, content_types="audio")
async def get_audio(message: types.Message, state: FSMContext):
    if message.media_group_id:
        response = requests.post(
        url=f'https://api.telegram.org/bot{cfg.TOKEN}/forwardMessage',
        data={f'chat_id': {cfg.CHANELID}, 'from_chat_id': {message.from_user.id}, 'message_id': {message.message_id}}
    ).json()
        db.add_music(response['result']['message_id'], message.media_group_id)
        btn = InlineKeyboardButton('Слушать', url=f"https://t.me/vodcastbot?start={ message.media_group_id}")
    else:
        response = requests.post(
        url=f'https://api.telegram.org/bot{cfg.TOKEN}/forwardMessage',
        data={f'chat_id': {cfg.CHANELID}, 'from_chat_id': {message.from_user.id}, 'message_id': {message.message_id}}
    ).json()
        btn = InlineKeyboardButton('Слушать', url=f"https://t.me/vodcastbot?start={response['result']['message_id']}")

    await state.update_data(keyboard=btn)

@dp.message_handler(state=Audio2.audio, text='Готово')
async def done(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = InlineKeyboardMarkup(row_width=1).add(data['keyboard'], data['file_btn'])
    await bot.send_photo(chat_id= -1001174615692, photo=data['photo_id'], caption=data['caption'], reply_markup=keyboard)
    await message.answer('Готово',reply_markup='')
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp)

