from datetime import datetime, time

import json
import pytz
from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from commands import set_commands
from config import ADMIN_ID
from keyboards import admin_panel
from main import dp, db, send_message, bot
from states import UserState


async def is_work_time(start_time: str, end_time: str):
    now = pytz.timezone('Europe/Moscow').localize(datetime.now()).time()
    start = time.fromisoformat(start_time)
    end = time.fromisoformat(end_time)
    return any([now <= end, now >= start]) if not start < end else (start <= now <= end)


@dp.message(Command('ap'))
async def ap(msg: types.Message):
    if msg.from_user.id in ADMIN_ID:
        await set_commands(bot)
        launch = await db.get_launched()

        if launch[0] == 1:
            admin_panel.inline_keyboard[4][0].text = "Закончить рассылку"
        else:
            admin_panel.inline_keyboard[4][0].text = "Начать рассылку"
        await msg.answer("йоу", reply_markup=admin_panel)


# info
@dp.callback_query(F.data.startswith('info'))
async def info(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id in ADMIN_ID:
        with open("result.json", encoding="utf8") as result:
            posts_clear = json.load(result)
        period = await db.get_period()
        time_to_sleep = await db.get_sleep()
        time_to_up = await db.get_up()
        start_newsletter = await db.get_start()
        if start_newsletter[0] == '0':
            start_newsletter = "не установлено"
        else:
            start_newsletter = start_newsletter[0]
        await call.message.answer(
            f"Количество постов: <b>{len(posts_clear['messages'])}</b> шт.\nВремя начала рассылки: <b>{start_newsletter}</b>\nПериод рассылки <b>{period[0]}</b> сек. ({round(int(period[0]) / 60, 1)} мин.)\nБот просыпается в <b>{time_to_up[0]}</b>\nУходит спать в <b>{time_to_sleep[0]}</b>")


# time to start
@dp.callback_query(F.data.startswith('time_to_start'))
async def set_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id in ADMIN_ID:
        launched = await db.get_launched()
        if launched[0] == 0:
            start_newsletter = await db.get_start()
            if start_newsletter[0] != '0':
                await call.message.answer(
                    f"В данный момент время начала рассылки: <b>{start_newsletter}<b>\nОтправь новое время начала рассылки ниже\n<i>(23:10, 21:45, 00:15, ...)</i>\n\n<i>Если хочешь отключить этот параметр, то отправь 0</i>", )
            else:
                await call.message.answer(
                    f"В данный момент время начала рассылки <b>не установлено</b>.\nОтправь время начала рассылки ниже\n<i>(23:10, 21:45, 00:15, ...)</i>", )
            await state.set_state(UserState.wait_start)
        else:
            await call.answer("Во время рассылки настройка невозможна ❌")


@dp.message(UserState.wait_start)
async def set_start2(msg: types.Message, state: FSMContext):
    await db.set_start(msg.text)
    await msg.answer(f"Отлично!\nРассылка будет запущена в {msg.text}")
    await state.clear()


# Start newsletter
@dp.callback_query(F.data.startswith('start'))
async def start(call: types.CallbackQuery):
    launched = await db.get_launched()
    if call.from_user.id in ADMIN_ID:
        if launched[0] == 0:
            admin_panel.inline_keyboard[4][0].text = "Закончить рассылку"
            await call.message.edit_reply_markup(reply_markup=admin_panel)
            await db.set_launched(1)
            await send_message()
        else:
            admin_panel.inline_keyboard[4][0].text = "Начать рассылку"
            await call.message.edit_reply_markup(reply_markup=admin_panel)
            await db.set_launched(0)
            await call.message.answer("Рассылка выключена!")


# Установить период рассылки
@dp.callback_query(F.data.startswith('mailing_period'))
async def mailing_period(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id in ADMIN_ID:
        period = await db.get_period()
        await call.message.answer(
            f"В данный момент установлен период: <b>{period[0]}</b> сек. ({round(int(period[0]) / 60, 1)} мин.)\nОтправь новый период рассылки в <b>СЕКУНДАХ</b>", )
        await state.set_state(UserState.wait_send_seconds)


@dp.message(UserState.wait_send_seconds)
async def mailing_period_2(msg: types.Message, state: FSMContext):
    try:
        await db.set_period(msg.text)
        await msg.answer(f"Период в <b>{msg.text}</b> сек. успешно установлен")
    except:
        await msg.answer("Произошла ошибка =(")
    await state.clear()


# Добавить в WL
@dp.callback_query(F.data.startswith('add_wl'))
async def add_wl(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id in ADMIN_ID:
        wl = []
        white_list = await db.get_wl()
        launched = await db.get_launched()
        if launched[0] == 0:
            for lists in white_list:
                wl.append(lists[0])
            await call.message.answer(
                f"В данный момент в списке ссылки:\n{wl}\nОтправь ссылку, чтобы ее добавить", disable_web_page_preview=True)
            await state.set_state(UserState.wait_link)
        else:
            await call.answer("Во время рассылки настройка невозможна ❌")


@dp.message(UserState.wait_link)
async def add_wl2(msg: types.Message, state: FSMContext):
    try:
        await db.set_wl(msg.text)
        wl = []
        white_list = await db.get_wl()
        for lists in white_list:
            wl.append(lists[0])
        await msg.answer(f"Ссылка '<b>{msg.text}</b>' успешно добавлена!!!\nТеперь список выглядит так:\n{wl}",
                         disable_web_page_preview=True)
    except:
        await msg.answer("Произошла ошибка =(")
    await state.clear()


# Удалить из WL
@dp.callback_query(F.data.startswith('del_wl'))
async def del_wl(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id in ADMIN_ID:
        wl = []
        white_list = await db.get_wl()
        launched = await db.get_launched()
        if launched[0] == 0:
            for lists in white_list:
                wl.append(lists[0])
            await call.message.answer(
                f"В данный момент в списке ссылки:\n{wl}\nОтправь <b>ссылку</b>, которую нужно удалить",
                disable_web_page_preview=True)
            await state.set_state(UserState.wait_index)
        else:
            await call.answer("Во время рассылки настройка невозможна ❌")


@dp.message(UserState.wait_index)
async def del_wl2(msg: types.Message, state: FSMContext):
    try:
        await db.del_wl(msg.text)
        wl = []
        white_list = await db.get_wl()
        for lists in white_list:
            wl.append(lists[0])
        await msg.answer(f"Ссылка '<b>{msg.text}</b>' успешно удалена!!!\n\nТеперь список выглядит так:\n{wl}",
                         disable_web_page_preview=True)
    except:
        await msg.answer("Произошла ошибка =(")
    await state.clear()


# Во сколько спать?
@dp.callback_query(F.data.startswith('time_to_sleep'))
async def sleep(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id in ADMIN_ID:
        time_to_sleep = await db.get_sleep()
        launched = await db.get_launched()
        if launched[0] == 0:
            await call.message.answer(
                f"В данный момент бот уходит спать в <b>{time_to_sleep[0]}</b>\nОтправь время, в которое бот должен уйти спать\n(23:10, 21:45, 00:15, ...)")
            await state.set_state(UserState.wait_sleep)
        else:
            await call.answer("Во время рассылки настройка невозможна ❌")


@dp.message(UserState.wait_sleep)
async def sleep2(msg: types.Message, state: FSMContext):
    await db.set_sleep(msg.text)
    await msg.answer(f"Отлично!\nТеперь бот уходит спать в <b>{msg.text}</b>")
    await state.clear()


# Во сколько вставать?
@dp.callback_query(F.data.startswith('time_to_up'))
async def up(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id in ADMIN_ID:
        launched = await db.get_launched()
        if launched[0] == 0:
            time_to_up = await db.get_up()
            await call.message.answer(
                f"В данный момент бот просыпается в <b>{time_to_up[0]}</b>\nОтправь время, в которое бот должен просыпаться\n(08:00, 08:30, 09:15, ...)")
            await state.set_state(UserState.wait_up)
        else:
            await call.answer("Во время рассылки настройка невозможна ❌")


@dp.message(UserState.wait_up)
async def up2(msg: types.Message, state: FSMContext):
    await db.set_up(msg.text)
    await msg.answer(f"Отлично!\nТеперь бот просыпается в <b>{msg.text}</b>")
    await state.clear()
