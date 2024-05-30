from main import dp, db, send_message, bot
from config import wl, ADMIN_ID
from keyboards import admin_panel
from aiogram.filters import Command
from aiogram import types, F
from commands import set_commands


from states import UserState
from aiogram.fsm.context import FSMContext
from datetime import datetime, time, timedelta
import pytz
import asyncio


async def is_work_time(start_time: str, end_time: str):
    now = pytz.timezone('Europe/Moscow').localize(datetime.now()).time()
    start = time.fromisoformat(start_time)
    end = time.fromisoformat(end_time)
    return any([now <= end, now >= start]) if not start < end else (start <= now <= end)

async def wating_to_wake_up(start_time, end_time):
    start = datetime.strptime(start_time, '%H:%M')
    end = datetime.strptime(end_time, '%H:%M')
    hours = datetime.strptime("00:00", "%H:%M")
    result = datetime.strftime(hours - (end - start), '%H:%M')
    asd = timedelta(hours=int(result[0] + result[1]), minutes=int(result[3] + result[4]))
    return round(asd.total_seconds())


@dp.message(Command('ap'))
async def settings_newsletter(msg: types.Message):
    if msg.from_user.id in ADMIN_ID:
        await set_commands(bot)

        delete = await db.get_delete()
        launch = await db.get_launched()

        if delete[0] == 1:
            admin_panel.inline_keyboard[2][0].text = "Удаление постов 🟢"
        else:
            admin_panel.inline_keyboard[2][0].text = "Удаление постов 🔴"

        if launch[0] == 1:
            admin_panel.inline_keyboard[4][0].text = "Закончить рассылку"
        else:
            admin_panel.inline_keyboard[4][0].text = "Начать рассылку"
        await msg.answer("йоу", reply_markup=admin_panel)


# Сбросить данные
@dp.callback_query(F.data.startswith('restart'))
async def restart(call: types.CallbackQuery):
    if call.from_user.id in ADMIN_ID:
        launch = await db.get_launched()

        if launch[0] == 1:
            await call.answer(text="Сброс невозможен, так как включена рассылка!")
        else:
            await db.set_stop(0)
            await db.set_delete(0)
            if admin_panel.inline_keyboard[2][0].text != "Удаление постов 🔴":
                admin_panel.inline_keyboard[2][0].text = "Удаление постов 🔴"
                await call.message.edit_reply_markup(reply_markup=admin_panel)
            await call.answer("Данные сброшены!")


# Начать рассылку
@dp.callback_query(F.data.startswith('start'))
async def start(call: types.CallbackQuery):
    launched = await db.get_launched()
    if call.from_user.id in ADMIN_ID and launched[0] == 0:
        delete = await db.get_delete()
        if delete[0] == 0:
            admin_panel.inline_keyboard[2][0].text = "Удаление постов 🔴"
        else:
            admin_panel.inline_keyboard[2][0].text = "Удаление постов 🟢"
        admin_panel.inline_keyboard[4][0].text = "Закончить рассылку"
        await call.message.edit_reply_markup(reply_markup=admin_panel)
        await db.set_launched(1)
        await send_message()
    else:
        delete = await db.get_delete()
        if delete[0] == 0:
            admin_panel.inline_keyboard[2][0].text = "Удаление постов 🔴"
        else:
            admin_panel.inline_keyboard[2][0].text = "Удаление постов 🟢"
        admin_panel.inline_keyboard[4][0].text = "Начать рассылку"
        await call.message.edit_reply_markup(reply_markup=admin_panel)
        await call.message.answer("Рассылка завершена!")
        await db.set_launched(0)


# Установить период рассылки
@dp.callback_query(F.data.startswith('mailing_period'))
async def mailing_period(call: types.CallbackQuery, state: FSMContext):
    period = await db.get_period()
    await call.message.answer(f"В данный момент установлен период: <b>{period[0]}</b> сек. ({round(int(period[0])/60, 1)} мин.)\nОтправь новый период рассылки в <b>СЕКУНДАХ</b>", )
    await state.set_state(UserState.wait_send_seconds)


@dp.message(UserState.wait_send_seconds)
async def mailing_period_2(msg: types.Message, state: FSMContext):
    try:
        await db.set_period(msg.text)
        await msg.answer(f"Период в <b>{msg.text}</b> сек. успешно установлен")
    except:
        await msg.answer("Произошла ошибка =(")
    await state.clear()


# Удаление
@dp.callback_query(F.data.startswith('delete'))
async def stop_func(call: types.CallbackQuery):
    delete = await db.get_delete()
    launch = await db.get_launched()
    if launch[0] == 1:
        await call.answer(text="Удаление невозможно, так как включена рассылка!")
    else:
        if delete[0] == 0:
            await db.set_delete(1)
            admin_panel.inline_keyboard[2][0].text = "Удаление постов 🟢"
            await call.message.edit_reply_markup(reply_markup=admin_panel)
            await call.answer("Удаление медиа включено!")
        else:
            await db.set_delete(0)
            admin_panel.inline_keyboard[2][0].text = "Удаление постов 🔴"
            await call.message.edit_reply_markup(reply_markup=admin_panel)
            await call.answer("Удаление медиа отключено!")


# Добавить в WL
@dp.callback_query(F.data.startswith('add_wl'))
async def add_wl(call: types.CallbackQuery, state: FSMContext):
    wl = []
    white_list = await db.get_wl()
    for lists in white_list:
        wl.append(lists[0])
    await call.message.answer(
        f"В данный момент в списке ссылки:\n{wl}\nОтправь ссылку, чтобы ее добавить", disable_web_page_preview=True)
    await state.set_state(UserState.wait_link)


@dp.message(UserState.wait_link)
async def add_wl2(msg: types.Message, state: FSMContext):
    try:
        await db.set_wl(msg.text)
        wl = []
        white_list = await db.get_wl()
        for lists in white_list:
            wl.append(lists[0])
        await msg.answer(f"Ссылка '<b>{msg.text}</b>' успешно добавлена!!!\nТеперь список выглядит так:\n{wl}", disable_web_page_preview=True)
    except:
        await msg.answer("Произошла ошибка =(")
    await state.clear()


# Удалить из WL
@dp.callback_query(F.data.startswith('del_wl'))
async def del_wl(call: types.CallbackQuery, state: FSMContext):
    wl = []
    white_list = await db.get_wl()
    for lists in white_list:
        wl.append(lists[0])
    await call.message.answer(
        f"В данный момент в списке ссылки:\n{wl}\nОтправь <b>ссылку</b>, которую нужно удалить", disable_web_page_preview=True)
    await state.set_state(UserState.wait_index)


@dp.message(UserState.wait_index)
async def del_wl2(msg: types.Message, state: FSMContext):
    try:
        await db.del_wl(msg.text)
        wl = []
        white_list = await db.get_wl()
        for lists in white_list:
            wl.append(lists[0])
        await msg.answer(f"Ссылка '<b>{msg.text}</b>' успешно удалена!!!\n\nТеперь список выглядит так:\n{wl}", disable_web_page_preview=True)
    except:
        await msg.answer("Произошла ошибка =(")
    await state.clear()


# Во сколько спать?
@dp.callback_query(F.data.startswith('time_to_sleep'))
async def sleep(call: types.CallbackQuery, state: FSMContext):
    time_to_sleep = await db.get_sleep()
    await call.message.answer(
        f"В данный момент бот уходит спать в <b>{time_to_sleep[0]}</b>\nОтправь время, в которое бот должен уйти спать\n(23:10, 21:45, 00:15, ...)")
    await state.set_state(UserState.wait_sleep)


@dp.message(UserState.wait_sleep)
async def sleep2(msg: types.Message, state: FSMContext):
    await db.set_sleep(msg.text)
    await msg.answer(f"Отлично!\nТеперь бот уходит спать в <b>{msg.text}</b>")
    await state.clear()


# Во сколько вставать?
@dp.callback_query(F.data.startswith('time_to_up'))
async def up(call: types.CallbackQuery, state: FSMContext):
    time_to_up = await db.get_up()
    await call.message.answer(
        f"В данный момент бот просыпается в <b>{time_to_up[0]}</b>\nОтправь время, в которое бот должен просыпаться\n(08:00, 08:30, 09:15, ...)")
    await state.set_state(UserState.wait_up)


@dp.message(UserState.wait_up)
async def up2(msg: types.Message, state: FSMContext):
    await db.set_up(msg.text)
    await msg.answer(f"Отлично!\nТеперь бот просыпается в <b>{msg.text}</b>")
    await state.clear()


