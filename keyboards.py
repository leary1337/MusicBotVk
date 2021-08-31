from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton(text='Популярные песни'),
        KeyboardButton(text='Новые песни')).row(
        KeyboardButton(text='Песни по ссылке'),
        KeyboardButton(text='Поиск')
    )
    return kb


def get_more_kb(offset, type_tracks, owner_id='', album_id='', access_hash='', search=''):
    kb = InlineKeyboardMarkup(resize_keyboard=True)
    kb.add(InlineKeyboardButton(
        text='Загрузить еще 10',
        callback_data=f'getMore:{type_tracks}:{offset}:{owner_id}:{album_id}:{access_hash}:{search}'
    ))
    return kb
