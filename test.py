import json

with open("Шерстяные_проказники_10.05_17.05/result.json", encoding="utf8") as result:
    posts = json.load(result)


temp = {}

# запись групп
for post in posts["messages"]:
    time = post["date_unixtime"]
    temp[time] = temp.get(time, 0) + 1


for post in posts["messages"]:

    if "photo" in post:
        # print(f'Фото\n--------\n{post["id"]}\n--------\n')
        post_type = "photo"
    elif "media_type" in post:
        # print(f'Видео\n--------\n{post["id"]}\n--------\n')
        post_type = "video"
    else:
        # print(f'Текст\n--------\n{post["id"]}\n--------\n')
        post_type = "text"

    time = post["date_unixtime"]

    if temp[time] > 1:
        print(f'{post_type}\n--------\n{post["id"]}\n--------\nгруппа\n--------\n\n')
    else:
        print(f'{post_type}\n--------\n{post["id"]}\n--------\nне группа\n--------\n\n')










quantity = temp[post["date_unixtime"]]
            # if not in MediaGroup
            if quantity == 1:
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
            else:   #in MediaGroup
                caption = post["text"][0]
                try:
                    mg = MediaGroupBuilder(caption=caption)
                except:
                    mg = MediaGroupBuilder()
                if post_type == "photo":
                    path = post["photo"]
                    mg.add(type="photo", media=FSInputFile(path))
                elif post_type == "video":
                    path = post["file"]
                    mg.add(type="video", media=FSInputFile(path))
                quantity -= 1
                if quantity == 0:
                    await bot.send_media_group(channel_id, mg.build())
