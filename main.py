from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

import asyncio
import logging
import json
import re
import random
import os

logging.basicConfig(level=logging.INFO)

channel_id = -1002042076267

bot = Bot("7077531566:AAG8BoIxXmjy-A7t7O9T9iMdzJvBI3Iqqlo", default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


async def send_message():
    a = 0
    temp = {}

    with open("result.json", encoding="utf8") as result:
        posts = json.load(result)

        # Shuffle
        random.shuffle(posts["messages"])

        json.dump(posts["messages"], result)

    # removal of advertising
    for post in posts["messages"]:
        # inline button
        if post["inline_bot_buttons"] is not None:
            if "photo" in post:
                os.remove(post["photo"])
            elif "media_type" in post:
                os.remove(post["file"])
                os.remove(post["thumbnail"])
            del post

        elif


    # MediaGroup mark
    for post in posts["messages"]:
        time = post["date_unixtime"]
        temp[time] = temp.get(time, 0) + 1

    for post in posts["messages"]:

        # Message type
        if "photo" in post:
            post_type = "photo"
        elif "media_type" in post:
            post_type = "video"
        else:
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
                    os.remove(path)
                except:
                    await bot.send_photo(channel_id, FSInputFile(path))
                    del temp[post["date_unixtime"]]
                    os.remove(path)
            elif post_type == "video":
                path = post["file"]
                try:
                    caption = post["text"][0]
                    await bot.send_video(channel_id, FSInputFile(path), caption=caption, width=post["width"],
                                         height=post["height"], thumbnail=FSInputFile(post["thumbnail"]))
                    del temp[post["date_unixtime"]]
                    os.remove(path)
                except:
                    await bot.send_video(channel_id, FSInputFile(path), width=post["width"], height=post["height"],
                                         thumbnail=FSInputFile(post["thumbnail"]))
                    del temp[post["date_unixtime"]]
                    os.remove(path)
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
                    mg.add(type="video", media=FSInputFile(path), width=post["width"], height=post["height"],
                           caption=caption, thumbnail=FSInputFile(post["thumbnail"]))
                except:
                    mg.add(type="video", media=FSInputFile(path), width=post["width"], height=post["height"],
                           thumbnail=FSInputFile(post["thumbnail"]))

            quantity -= 1
            temp[post["date_unixtime"]] = f"{quantity}, MG"

            if quantity == 0:
                print(mg)
                print("\n--------------\n")
                print(mg.build())
                await bot.send_media_group(channel_id, mg.build())
                del temp[post["date_unixtime"]]
                a = 0


async def main():
    try:
        await send_message()
    finally:
        print("[INFO] Bot stopped!!!")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
