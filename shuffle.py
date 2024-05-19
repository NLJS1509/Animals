import json
import random

with open("result.json", encoding="utf8") as result:
    posts = json.load(result)
    random.shuffle(posts["messages"])
    json.dump(posts, result)
