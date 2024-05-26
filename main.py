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
import time

logging.basicConfig(level=logging.INFO)

channel_id = -1001318027822

bot = Bot("7077531566:AAG8BoIxXmjy-A7t7O9T9iMdzJvBI3Iqqlo", default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


async def send_message():
    a = 0
    date = {}
    white_list = ['https://t.me/hedgehogiki', 'https://t.me/+EdTVCcf9RTVkZjZi', 'https://t.me/+jY-C4oLVuJZiZjQy',
                  'https://t.me/+YyZAC53UIwk4MTFi']
    posts_clear = {"messages": []}

    # open json
    with open("result.json", encoding="utf8") as result:
        posts_json = json.load(result)

    # removal of advertising
    for post in posts_json["messages"]:
        try:
            # inline button
            if "inline_bot_buttons" in post or post["text_entities"][0]["href"] not in white_list:
                if "photo" in post:
                    try:
                        pass
                        os.remove(post["photo"])
                    except FileNotFoundError:
                        logging.warning(f"File '{post['photo']}' not found !!!")
                elif "media_type" in post:
                    try:
                        pass
                        os.remove(post["file"])
                        os.remove(post["thumbnail"])
                    except FileNotFoundError:
                        logging.warning(f"File '{post['file']}' not found !!!")
            else:
                posts_clear["messages"].append(post)
        except:
            try:
                if post["text_entities"][1]["href"] not in white_list:
                    if "photo" in post:
                        try:
                            os.remove(post["photo"])
                        except FileNotFoundError:
                            logging.warning(f"File '{post['photo']}' not found !!!")
                    elif "media_type" in post:
                        try:
                            pass
                            os.remove(post["file"])
                            os.remove(post["thumbnail"])
                        except FileNotFoundError:
                            logging.warning(f"File '{post['file']}' not found !!!")
                else:
                    posts_clear["messages"].append(post)
            except:
                posts_clear["messages"].append(post)

    # MediaGroup mark
    for post in posts_clear["messages"]:
        date[post["date_unixtime"]] = date.get(post["date_unixtime"], 0) + 1

    # Shuffle
    random.shuffle(posts_clear["messages"])

    # Send message
    for post in posts_clear["messages"]:

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
                        caption = post["text"][0]
                    else:
                        caption = post["text"]
                    try:
                        await bot.send_photo(channel_id, FSInputFile(path), caption=caption)
                    except:
                        logging.warning("PHOTO NOT SEND")
                    del date[post["date_unixtime"]]
                    os.remove(path)
                    time.sleep(600)
                except:
                    try:
                        await bot.send_photo(channel_id, FSInputFile(path))
                    except:
                        logging.warning("PHOTO NOT SEND")
                    del date[post["date_unixtime"]]
                    os.remove(path)
                    time.sleep(600)
            elif post_type == "video":
                path = post["file"]
                try:
                    if isinstance(post["text"], list):
                        caption = post["text"][0]
                    else:
                        caption = post["text"]
                    try:
                        await bot.send_video(channel_id, FSInputFile(path), caption=caption, width=post["width"],
                                         height=post["height"], thumbnail=FSInputFile(post["thumbnail"]))
                    except:
                        logging.warning("VIDEO NOT SEND")
                    del date[post["date_unixtime"]]
                    os.remove(post["thumbnail"])
                    os.remove(path)
                    time.sleep(600)
                except:
                    try:
                        await bot.send_video(channel_id, FSInputFile(path), width=post["width"], height=post["height"],
                                         thumbnail=FSInputFile(post["thumbnail"]))
                    except:
                        logging.warning("VIDEO NOT SEND")
                    del date[post["date_unixtime"]]
                    os.remove(post["thumbnail"])
                    os.remove(path)
                    time.sleep(600)
            elif post_type == "text":
                text = post["text"][0]
                try:
                    await bot.send_message(channel_id, text)
                except:
                    logging.warning("TEXT NOT SEND")
                del date[post["date_unixtime"]]
                time.sleep(600)
        # if in MediaGroup
        else:
            quantity = int(re.sub('\D', '', date[post["date_unixtime"]]))

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
                    if isinstance(post["text"], list):
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
                    caption = post["text"][0]
                    mg.add(type="video", media=FSInputFile(path), width=post["width"], height=post["height"],
                           caption=caption, thumbnail=FSInputFile(post["thumbnail"]))
                except:
                    mg.add(type="video", media=FSInputFile(path), width=post["width"], height=post["height"],
                           thumbnail=FSInputFile(post["thumbnail"]))

            quantity -= 1
            date[post["date_unixtime"]] = f"{quantity}, MG"

            if quantity == 0:
                try:
                    await bot.send_media_group(channel_id, mg.build())
                except:
                    logging.warning("MediaGroup NOT SEND")
                del date[post["date_unixtime"]]
                a = 0
                time.sleep(600)


async def main():
    try:
        await send_message()
    finally:
        print("[INFO] Bot stopped!!!")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())