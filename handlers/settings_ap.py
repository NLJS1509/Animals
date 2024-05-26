from main import dp, db, send_message
from config import wl
from keyboards import admin_panel
from aiogram.filters import Command
from aiogram import types, F


from states import UserState
from aiogram.fsm.context import FSMContext


@dp.message(Command('ap'))
async def settings_newsletter(msg: types.Message):
    if msg.from_user.id == 498975827:
        delete = await db.get_delete()

        if delete[0] == 1:
            admin_panel.inline_keyboard[2][0].text = "Удаление медиа 🟢"
        else:
            admin_panel.inline_keyboard[2][0].text = "Удаление медиа 🔴"

        launch = await db.get_launched()
        if launch[0] == 1:
            admin_panel.inline_keyboard[3][0].text = "Закончить рассылку"
        else:
            admin_panel.inline_keyboard[3][0].text = "Начать рассылку"
        await msg.answer("йоу", reply_markup=admin_panel)


# Сбросить данные
@dp.callback_query(F.data.startswith('restart'))
async def restart(call: types.CallbackQuery):
    if call.from_user.id == 498975827:
        launch = await db.get_launched()
        if launch[0] == 1:
            await call.answer(text="Сброс невозможен, так как включена рассылка!")
        else:
            await db.set_stop(0)
            await db.set_delete(0)
            if admin_panel.inline_keyboard[2][0].text != "Удаление медиа 🔴":
                admin_panel.inline_keyboard[2][0].text = "Удаление медиа 🔴"
                await call.message.edit_reply_markup(reply_markup=admin_panel)
            await call.answer("Данные сброшены!")



# Начать рассылку
@dp.callback_query(F.data.startswith('start'))
async def start(call: types.CallbackQuery):
    launched = await db.get_launched()
    if call.from_user.id == 498975827 and launched[0] == 0:
        delete = await db.get_delete()
        if delete[0] == 0:
            admin_panel.inline_keyboard[2][0].text = "Удаление медиа 🔴"
        else:
            admin_panel.inline_keyboard[2][0].text = "Удаление медиа 🟢"
        admin_panel.inline_keyboard[3][0].text = "Закончить рассылку"
        await call.message.edit_reply_markup(reply_markup=admin_panel)
        await db.set_launched(1)
        await db.set_stop(0)
        await send_message()
    else:
        await db.set_launched(0)
        admin_panel.inline_keyboard[3][0].text = "Начать рассылку"
        await call.message.edit_reply_markup(reply_markup=admin_panel)
        await call.message.answer("Рассылка завершена!")
        await db.set_stop(1)


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
            admin_panel.inline_keyboard[2][0].text = "Удаление медиа 🟢"
            await call.message.edit_reply_markup(reply_markup=admin_panel)
            await call.answer("Удаление медиа включено!")
        else:
            await db.set_delete(0)
            admin_panel.inline_keyboard[2][0].text = "Удаление медиа 🔴"
            await call.message.edit_reply_markup(reply_markup=admin_panel)
            await call.answer("Удаление медиа отключено!")


# Добавить в WL
@dp.callback_query(F.data.startswith('add_wl'))
async def add_wl(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        f"В данный момент в списке ссылки:\n{wl}\nОтправь ссылку, чтобы ее добавить")
    await state.set_state(UserState.wait_link)


@dp.message(UserState.wait_link)
async def add_wl2(msg: types.Message, state: FSMContext):
    try:
        wl.append(msg.text)
        await msg.answer(f"Ссылка '<b>{msg.text}</b>' успешно добавлена!!!\nТеперь список выглядит так:\n{wl}")
    except:
        await msg.answer("Произошла ошибка =(")
    await state.clear()


# Удалить из WL
@dp.callback_query(F.data.startswith('del_wl'))
async def del_wl(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        f"В данный момент в списке ссылки:\n{wl}\nОтправь <b>индекс</b> элемента, который нужно удалить")
    await state.set_state(UserState.wait_index)


@dp.message(UserState.wait_index)
async def del_wl2(msg: types.Message, state: FSMContext):
    try:
        del wl[int(msg.text)]
        await msg.answer(f"Элемент '<b>{msg.text}</b>' успешно удален!!!\n\nТеперь список выглядит так:\n{wl}")
    except:
        await msg.answer("Произошла ошибка =(")
    await state.clear()


# Во сколько спать?
@dp.callback_query(F.data.startswith('time_to_sleep'))
async def sleep(call: types.CallbackQuery, state: FSMContext):
    time = await db.get_time()
    await call.message.answer(
        f"В данный момент бот уходит спать в <b>{time[0]}</b>\nОтправь время, в которое бот должен уйти спать\n(23:15, 21:05, 00:45 ...")
    await state.set_state(UserState.wait_time)


@dp.message(UserState.wait_time)
async def sleep2(msg: types.Message, state: FSMContext):
    await db.set_time(msg.text)
    await msg.answer(f"Отлично!\nТеперь бот уходит спать в <b>{msg.text}</b>")
    await state.clear()