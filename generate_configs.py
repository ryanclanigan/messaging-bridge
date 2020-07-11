from shutil import copyfile
import glob
import os

if not os.path.exists("config"):
    os.mkdir("config")

for file in glob.glob("example-config/*.json"):
    copyfile(file, os.path.join("config", file.split("example-")[-1]))

