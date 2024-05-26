from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_panel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Установить период рассылки", callback_data='mailing_period'), InlineKeyboardButton(text="Во сколько спать?", callback_data='time_to_sleep')],
        [InlineKeyboardButton(text="Добавить канал в WL", callback_data='add_wl'), InlineKeyboardButton(text="Убрать канал из WL", callback_data='del_wl')],
        [InlineKeyboardButton(text="Удаление медиа", callback_data='delete'), InlineKeyboardButton(text="Сбросить данные", callback_data='restart')],
        [InlineKeyboardButton(text="Рассылка", callback_data='start')]
    ]
)