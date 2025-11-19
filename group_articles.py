import os
import shutil

articles = os.listdir("./news/")


for (root, dirs, files) in os.walk("./news/"):
    for f in files:
        with open(f"news/{f}", "r", encoding="utf-8", errors="ignore") as file:
            category = file.readlines()[2]
            name = category.split()[1]
            if not os.path.exists(f"./grouped_news/{name}"):
                os.makedirs(f"./grouped_news/{name}")
            shutil.copyfile(f"news/{f}", f"./grouped_news/{name}/{f}")
