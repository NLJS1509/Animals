from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.methods.send_media_group import SendMediaGroup

import asyncio
import logging
import time
import json
import re

logging.basicConfig(level=logging.INFO)

channel_id = -1002042076267

bot = Bot("7077531566:AAG8BoIxXmjy-A7t7O9T9iMdzJvBI3Iqqlo", default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


async def send_message():
    a = 0

    with open("result.json", encoding="utf8") as result:
        posts = json.load(result)

    temp = {}

    # MediaGroup mark
    for post in posts["messages"]:
        time = post["date_unixtime"]
        temp[time] = temp.get(time, 0) + 1

    for post in posts["messages"]:
        # post type
        if "photo" in post:
            # print(f'Фото\n--------\n{post["id"]}\n--------\n')
            post_type = "photo"
        elif "media_type" in post:
            # print(f'Видео\n--------\n{post["id"]}\n--------\n')
            post_type = "video"
        else:
            # print(f'Текст\n--------\n{post["id"]}\n--------\n')
            post_type = "text"

        if isinstance(temp[post["date_unixtime"]], int):
            temp[post["date_unixtime"]] = str(temp[post["date_unixtime"]])


        # MediaGroup add mark
        if temp[post["date_unixtime"]] != "1" and temp[post["date_unixtime"]][-1] != "G":
            temp[post["date_unixtime"]] = f"{temp[post['date_unixtime']]}, MG"


        # if not in MediaGroup
        if temp[post["date_unixtime"]] == "1":
            if post_type == "photo":
                path = post["photo"]
                try:
                    caption = post["text"][0]
                    await bot.send_photo(channel_id, FSInputFile(path), caption=caption)
                    del temp[post["date_unixtime"]]
                except:
                    await bot.send_photo(channel_id, FSInputFile(path))
                    del temp[post["date_unixtime"]]
            elif post_type == "video":
                path = post["file"]
                try:
                    caption = post["text"][0]
                    await bot.send_video(channel_id, FSInputFile(path), caption=caption)
                    del temp[post["date_unixtime"]]
                except:
                    await bot.send_video(channel_id, FSInputFile(path))
                    del temp[post["date_unixtime"]]
            elif post_type == "text":
                text = post["text"][0]
                await bot.send_message(channel_id, text)
                del temp[post["date_unixtime"]]
        # if in MediaGroup
        else:
            quantity = int(re.sub('\D', '', temp[post["date_unixtime"]]))

            if a == 0:
                try:
                    caption = post["text"][0]
                    mg = MediaGroupBuilder(caption=caption)
                except:
                    mg = MediaGroupBuilder()
                a = 1

            if post_type == "photo":
                path = post["photo"]
                try:
                    caption = post["text"][0]
                    mg.add(type="photo", media=FSInputFile(path), width=post["width"], height=post["height"],
                           caption=caption)
                except:
                    mg.add(type="photo", media=FSInputFile(path), width=post["width"], height=post["height"])
            elif post_type == "video":
                path = post["file"]
                try:
                    caption = post["text"][0]
                    mg.add(type="video", media=FSInputFile(path), width=post["width"], height=post["height"], caption=caption, thumbnail=FSInputFile(post["thumbnail"]))
                except:
                    mg.add(type="video", media=FSInputFile(path), width=post["width"], height=post["height"], thumbnail=post["thumbnail"])

            quantity -= 1
            temp[post["date_unixtime"]] = f"{quantity}, MG"

            if quantity == 0:
                await bot.send_media_group(channel_id, mg.build())
                a = 0
                del temp[post["date_unixtime"]]

async def main():
    try:
        await send_message()
    finally:
        print("[INFO] Bot stopped!!!")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())