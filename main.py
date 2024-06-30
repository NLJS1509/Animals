# aiogram
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

# lib
import pytz
import asyncio
import logging
import json
import re
import os
import random
from datetime import datetime, time, timedelta

# project files
from db import Database
from config import ADMIN_ID

logging.basicConfig(level=logging.DEBUG)

channel_id = -1002042076267

bot = Bot("7077531566:AAG8BoIxXmjy-A7t7O9T9iMdzJvBI3Iqqlo", default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
db = Database('database.db')


async def is_work_time(start_time: str, end_time: str):
    now = pytz.timezone('Europe/Moscow').localize(datetime.now()).time()
    start = time.fromisoformat(start_time)
    end = time.fromisoformat(end_time)
    return any([now <= end, now >= start]) if not start < end else (start <= now <= end)


def waiting_to_wake_up(start_time, end_time):
    start = datetime.strptime(start_time, '%H:%M')
    end = datetime.strptime(end_time, '%H:%M')
    hours = datetime.strptime("00:00", "%H:%M")
    result = datetime.strftime(hours - (start - end), '%H:%M')
    asd = timedelta(hours=int(result[0] + result[1]), minutes=int(result[3] + result[4]))
    return round(asd.total_seconds())


async def send_message():
    # open json
    with open("result.json", "r", encoding="utf8") as result:
        posts_json = json.load(result)

    # create variables for work script
    a = 0
    b = 0
    date = {}
    posts_clear = {"messages": []}
    period = await db.get_period()

    wl = []
    white_list = await db.get_wl()
    for lists in white_list:
        wl.append(lists[0])

    # removal of advertising
    for post in posts_json['messages']:
        try:
            # inline button
            if "inline_bot_buttons" in post or post["text_entities"][0]["href"] not in wl:
                if "photo" in post:
                    try:
                        os.remove(post["photo"])
                    except FileNotFoundError:
                        logging.warning(f"File '{post['photo']}' not found !!!")
                elif "media_type" in post:
                    try:
                        os.remove(post["file"])
                        os.remove(post["thumbnail"])
                    except FileNotFoundError:
                        logging.warning(f"File '{post['file']}' not found !!!")
            else:
                posts_clear["messages"].append(post)
        except:
            try:
                if post["text_entities"][1]["href"] not in wl:
                    if "photo" in post:
                        try:
                            os.remove(post["photo"])
                        except FileNotFoundError:
                            logging.warning(f"File '{post['photo']}' not found !!!")
                    elif "media_type" in post:
                        try:
                            os.remove(post["file"])
                            os.remove(post["thumbnail"])
                        except FileNotFoundError:
                            logging.warning(f"File '{post['file']}' not found !!!")
                else:
                    posts_clear["messages"].append(post)
            except:
                posts_clear["messages"].append(post)

    # write clear list in json file
    with open("result.json", "w") as result:
        json.dump(posts_clear, result)

    # MediaGroup mark
    for post in posts_clear['messages']:
        date[post["date_unixtime"]] = date.get(post["date_unixtime"], 0) + 1

    # bot goes on break
    time_to_sleep = await db.get_sleep()
    time_to_up = await db.get_up()
    if not await is_work_time(time_to_up[0], time_to_sleep[0]):
        for i in ADMIN_ID:
            await bot.send_message(i, f"Бот спит 😴\nОн проснется в {time_to_up[0]} и начнет рассылку",
                                   disable_notification=True)
        time_now = pytz.timezone('Europe/Moscow').localize(datetime.now()).strftime('%H:%M')
        await asyncio.sleep(waiting_to_wake_up(time_now, time_to_up[0]))

    # open json
    with open("result.json", "r", encoding="utf8") as result:
        posts = json.load(result)

    if len(posts['messages']) > 0:
        start_newsletter = await db.get_start()

        if start_newsletter[0] != '0':
            for i in ADMIN_ID:
                await bot.send_message(i,
                                       f"Установлено время начала рассылки. Она начнется в <b>{start_newsletter[0]}</b>",
                                       disable_notification=True)
            time_now = pytz.timezone('Europe/Moscow').localize(datetime.now()).strftime('%H:%M')
            await asyncio.sleep(waiting_to_wake_up(time_now, start_newsletter[0]))
            await db.set_start("0")

        # mailing launch message
        for i in ADMIN_ID:
            await bot.send_message(i,
                                   f"Рассылка запущена!\nВсего постов: <b>{len(posts['messages'])}</b> шт.\nПериод рассылки: <b>{period[0]}</b> сек. ({round(int(period[0]) / 60, 1)} мин.)\nБот просыпается в <b>{time_to_up[0]}</b>\nУходит спать в <b>{time_to_sleep[0]}</b>")

        # Shuffle
        random.shuffle(posts["messages"])

        # Send message
        for post in posts['messages']:
            launch = await db.get_launched()
            if launch[0] == 1:
                with open("result.json", "r", encoding="utf8") as result:
                    f = json.load(result)

                # GET PERIOD
                try:
                    period = await db.get_period()
                except:
                    for i in ADMIN_ID:
                        await bot.send_message(i, "🟡 [WARNING] Не получилось получить данные периода рассылки")
                    logging.warning("Не получилось получить данные периода рассылки")
                    period = 600

                # bot goes on break
                time_to_sleep = await db.get_sleep()
                time_to_up = await db.get_up()

                if not await is_work_time(time_to_up[0], time_to_sleep[0]):
                    for i in ADMIN_ID:
                        await bot.send_message(i, f"🔵 [INFO] Я ушел спать😴\nБуду в {time_to_up[0]}",
                                               disable_notification=True)
                    time_now = pytz.timezone('Europe/Moscow').localize(datetime.now()).strftime('%H:%M')
                    await asyncio.sleep(waiting_to_wake_up(time_now, time_to_up[0]))
                    for i in ADMIN_ID:
                        await bot.send_message(i, f"🔵 [INFO] Я проснулся\n Начинаю работу 🤓", disable_notification=True)

                # Notifications about the number of remaining posts
                if len(f['messages']) == 50:
                    for i in ADMIN_ID:
                        await bot.send_message(i, "🔵 [INFO] Осталось 50 постов")
                elif len(f['messages']) == 40:
                    for i in ADMIN_ID:
                        await bot.send_message(i, "🔵 [INFO] Осталось 40 постов")
                elif len(f['messages']) == 30:
                    for i in ADMIN_ID:
                        await bot.send_message(i, "🔵 [INFO] Осталось 30 постов")
                elif len(f['messages']) == 20:
                    for i in ADMIN_ID:
                        await bot.send_message(i, "🔵 [INFO] Осталось 20 постов")
                elif len(f['messages']) == 10:
                    for i in ADMIN_ID:
                        await bot.send_message(i, "🔵 [INFO] Осталось 10 постов")
                elif len(f['messages']) == 5:
                    for i in ADMIN_ID:
                        await bot.send_message(i, "🔵 [INFO] Осталось 5 постов")
                elif len(f['messages']) < 5:
                    for i in ADMIN_ID:
                        await bot.send_message(i, "🔵 [INFO] Осталось меньше 5 постов!!!")

                # Message type
                if "photo" in post:
                    post_type = "photo"
                elif "media_type" in post:
                    post_type = "video"
                else:
                    post_type = "text"

                if isinstance(date[post["date_unixtime"]], int):
                    date[post["date_unixtime"]] = str(date[post["date_unixtime"]])

                # MediaGroup add mark
                if date[post["date_unixtime"]] != "1" and date[post["date_unixtime"]][-1] != "G":
                    date[post["date_unixtime"]] = f"{date[post['date_unixtime']]}, MG"

                # if not in MediaGroup
                if date[post["date_unixtime"]] == "1":
                    if post_type == "photo":
                        path = post["photo"]
                        try:
                            if isinstance(post["text"], list):
                                try:
                                    types = post["text"][0]["type"]
                                    if types == "text_link":
                                        caption = ""
                                    else:
                                        caption = ""
                                except:
                                    caption = post["text"][0]
                            else:
                                caption = post["text"]
                            try:
                                await bot.send_photo(channel_id, FSInputFile(path), caption=caption)
                            except:
                                logging.warning(f"PHOTO NOT FOUND\n")
                                for i in ADMIN_ID:
                                    await bot.send_message(i, f"🟡 [WARNING] Фото не отправлено\nID: {post['id']}")
                            try:
                                del date[post["date_unixtime"]]
                            except:
                                logging.warning(f"PHOTO NOT FOUND\n")
                                for i in ADMIN_ID:
                                    await bot.send_message(i, f"🟡 [WARNING] Фото не отправлено\nID: {post['id']}")
                            await asyncio.sleep(period[0])
                        except:
                            try:
                                await bot.send_photo(channel_id, FSInputFile(path))
                            except:
                                logging.warning(f"PHOTO NOT FOUND\n")
                                for i in ADMIN_ID:
                                    await bot.send_message(i, f"🟡 [WARNING] Фото не отправлено\nID: {post['id']}")
                            try:
                                del date[post["date_unixtime"]]
                            except:
                                logging.warning(f"PHOTO NOT FOUND\n")
                                for i in ADMIN_ID:
                                    await bot.send_message(i, f"🟡 [WARNING] Видео не отправлено\nID: {post['id']}\n")
                            await asyncio.sleep(period[0])

                    elif post_type == "video":
                        path = post["file"]
                        try:
                            if not isinstance(post["text"], list):
                                caption = post["text"]
                            else:
                                try:
                                    types = post["text"][0]["type"]
                                    if types == "text_link":
                                        caption = ""
                                    else:
                                        caption = ""
                                except:
                                    caption = post["text"][0]
                            try:
                                await bot.send_video(channel_id, FSInputFile(path), caption=caption,
                                                     width=post["width"],
                                                     height=post["height"], thumbnail=FSInputFile(post["thumbnail"]))
                            except:
                                logging.warning(f"VIDEO NOT FOUND\n")
                                for i in ADMIN_ID:
                                    await bot.send_message(i, f"🟡 [WARNING] Видео не отправлено\nID: {post['id']}\n")
                            try:
                                del date[post["date_unixtime"]]
                            except:
                                logging.warning(f"VIDEO NOT FOUND\n")
                                for i in ADMIN_ID:
                                    await bot.send_message(i, f"🟡 [WARNING] Видео не отправлено\nID: {post['id']}\n")
                            await asyncio.sleep(period[0])

                        except:
                            try:
                                await bot.send_video(channel_id, FSInputFile(path), width=post["width"],
                                                     height=post["height"],
                                                     thumbnail=FSInputFile(post["thumbnail"]))
                            except:
                                logging.warning(f"VIDEO NOT FOUND\n")
                                for i in ADMIN_ID:
                                    await bot.send_message(i, f"🟡 [WARNING] Видео не отправлено\nID: {post['id']}\n")
                            try:
                                del date[post["date_unixtime"]]
                            except:
                                logging.warning(f"VIDEO NOT FOUND\n")
                                for i in ADMIN_ID:
                                    await bot.send_message(i, f"🟡 [WARNING] Видео не отправлено\nID: {post['id']}\n")
                            await asyncio.sleep(period[0])
                    elif post_type == "text":
                        text = post["text"][0]
                        try:
                            await bot.send_message(channel_id, text)
                        except:
                            logging.warning("TEXT NOT SEND")
                            for i in ADMIN_ID:
                                await bot.send_message(i, f"🟡 [WARNING] Текст не отправлен\nID: {post['id']}")
                        del date[post["date_unixtime"]]
                        await asyncio.sleep(period[0])
                # if in MediaGroup
                else:
                    quantity = int(re.sub('\D', '', date[post["date_unixtime"]]))

                    if a == 0:
                        try:
                            try:
                                types = post["text"][0]["type"]
                                if types == "text_link":
                                    caption = ""
                                else:
                                    caption = ""
                            except:
                                caption = post["text"][0]
                            mg = MediaGroupBuilder(caption=caption)
                        except:
                            mg = MediaGroupBuilder()
                        a = 1

                    if post_type == "photo":
                        path = post["photo"]
                        try:
                            if isinstance(post["text"], list):
                                try:
                                    types = post["text"][0]["type"]
                                    if types == "text_link":
                                        caption = ""
                                    else:
                                        caption = ""
                                except:
                                    caption = post["text"][0]
                            else:
                                caption = post["text"]
                            mg.add(type="photo", media=FSInputFile(path), width=post["width"], height=post["height"],
                                   caption=caption)
                        except:
                            mg.add(type="photo", media=FSInputFile(path), width=post["width"], height=post["height"])
                    elif post_type == "video":
                        path = post["file"]
                        try:
                            if isinstance(post["text"], list):
                                try:
                                    types = post["text"][0]["type"]
                                    if types == "text_link":
                                        caption = ""
                                    else:
                                        caption = ""
                                except:
                                    caption = post["text"][0]
                            else:
                                caption = post["text"]
                            mg.add(type="video", media=FSInputFile(path), width=post["width"], height=post["height"],
                                   caption=caption, thumbnail=FSInputFile(post["thumbnail"]))
                        except:
                            mg.add(type="video", media=FSInputFile(path), width=post["width"], height=post["height"],
                                   thumbnail=FSInputFile(post["thumbnail"]))

                    quantity -= 1
                    b += 1
                    date[post["date_unixtime"]] = f"{quantity}, MG"

                    if quantity == 0 or b == 9:
                        try:
                            await bot.send_media_group(channel_id, mg.build())
                        except:
                            logging.warning("MediaGroup NOT SEND")
                            for i in ADMIN_ID:
                                await bot.send_message(i, f"🟡 [WARNING] Медиа группа не отправлена\nID: {post['id']}")
                        del date[post["date_unixtime"]]
                        a = 0
                        b = 0
                        await asyncio.sleep(period[0])

                # del post from json
                index = f["messages"].index(post)
                del f["messages"][index]
                with open("result.json", "w") as result:
                    json.dump(f, result, indent=2)
            else:
                break

        # newsletter that posts are over
        with open("result.json", "r", encoding="utf8") as result:
            check = json.load(result)

        if len(check["messages"]) == 0:
            for i in ADMIN_ID:
                await bot.send_message(i, "🔴 [WARNING] ПОСТЫ ЗАКОНЧИЛИСЬ ❗️")
            await db.set_launched(0)
    else:
        for i in ADMIN_ID:
            await bot.send_message(i, "🔴 [WARNING] ПОСТЫ ЗАКОНЧИЛИСЬ ❗️")
            await db.set_launched(0)


async def main():
    from handlers import dp
    try:
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot)
    finally:
        launch = await db.get_launched()
        if launch[0] == 1:
            for i in ADMIN_ID:
                await bot.send_message(i, f"Бот выключен!")
            await db.set_launched(0)
        print("[INFO] Bot stopped!!!")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
