import os
import re

import requests
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import vk_api
from vk_api.audio import VkAudio

from keyboards import main_kb, get_more_kb

TOKEN_BOT = '111'
USER_ID = 111

bot = Bot(token=TOKEN_BOT, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

account = '1:1'.split(':')
login, password = account[0], account[1]
vk_session = vk_api.VkApi(token='', app_id=2685278, scope=1073737727, api_version=5.92)
# vk_session.auth()
vk = vk_session.get_api()
vk_a = VkAudio(vk_session)


@dp.message_handler(CommandStart())
async def bot_start(m: Message):
    await m.answer('NAVALI MUZLA', reply_markup=main_kb())


# === Popular tracks ===
@dp.message_handler()
async def send_tracks(m: Message):
    owner_id = ''
    album_id = ''
    access_hash = ''
    search = ''

    if 'Популярные' in m.text:
        audios = vk_a.get_popular_iter()
        type_tracks = 'pop'
    elif 'Новые' in m.text:
        audios = vk_a.get_news_iter()
        type_tracks = 'new'
    elif 'Песни по' in m.text:
        await m.answer('Пришлите ссылку на профиль, плейлист')
        return
    elif 'Поиск' in m.text:
        await m.answer('Напишите название песни, которую ищем')
        return
    elif 'https' in m.text:
        if 'audio_playlist' in m.text:
            playlist = m.text.split('audio_playlist')[-1].split('/')
            user_data = playlist[0].split('_')
            owner_id = user_data[0]
            album_id = int(user_data[1]) if len(user_data) == 2 else None
            access_hash = playlist[1]
        else:
            user_id = m.text.replace('https://vk.com/', '').replace('id', '')
            vk = vk_session.get_api()
            owner_id = vk.users.get(user_ids=user_id)[0]['id']
        if not album_id:
            audios = vk_a.get_iter(owner_id=owner_id)
        else:
            audios = vk_a.get_iter(owner_id=owner_id, album_id=album_id, access_hash=access_hash)
        type_tracks = 'al'
    else:
        audios = vk_a.search(q=m.text, count=10)
        search = m.text
        type_tracks = 'se'

    count = 0
    try:
        for a in audios:
            link = a['url']
            audio = requests.get(link).content

            await bot.send_chat_action(chat_id=m.from_user.id, action='upload_audio')

            if count == 9:
                await bot.send_audio(chat_id=m.from_user.id, audio=audio, title=a['title'],
                                     performer=a['artist'],
                                     reply_markup=get_more_kb(10, type_tracks, owner_id, album_id, access_hash, search),
                                     disable_notification=True)
                break

            await bot.send_audio(chat_id=m.from_user.id, audio=audio, title=a['title'],
                                 performer=a['artist'],
                                 disable_notification=True)
            count += 1
    except:
        await m.answer(
            'Не удалось получить аудиозаписи! Возможно Ваш профиль закрыт, аудио скрыты, несуществует такого альбома')
        return


@dp.callback_query_handler(text_contains='getMore:')
async def get_more(c: CallbackQuery):
    splitter = c.data.replace('getMore:', '').split(':')
    type_tracks = splitter[0]
    offset = int(splitter[1])
    owner_id = splitter[2]
    album_id = splitter[3]
    access_hash = splitter[4]
    search = splitter[5]

    if type_tracks == 'pop':
        audios = vk_a.get_popular_iter(offset=offset)
    elif type_tracks == 'new':
        audios = vk_a.get_news_iter(offset=offset)
    elif owner_id:
        audios = vk_a.get_iter(owner_id=owner_id, album_id=album_id, access_hash=access_hash)
    else:
        audios = vk_a.search_iter(q=search, offset=offset)

    await c.message.delete_reply_markup()
    await c.answer()

    count = 0 if not owner_id else offset
    i = -1
    for a in audios:
        i += 1
        if owner_id and i < count:
            continue

        link = a['url']
        audio = requests.get(link).content

        await bot.send_chat_action(chat_id=c.from_user.id, action='upload_audio')

        if count == 9 or (owner_id and count == offset + 9):
            await bot.send_audio(chat_id=c.from_user.id, audio=audio, title=a['title'],
                                 performer=a['artist'],
                                 reply_markup=get_more_kb(offset+10, type_tracks, owner_id, album_id, access_hash, search),
                                 disable_notification=True)
            break

        await bot.send_audio(chat_id=c.from_user.id, audio=audio, title=a['title'],
                             performer=a['artist'],
                             disable_notification=True)
        count += 1


if __name__ == '__main__':
    executor.start_polling(dp)
