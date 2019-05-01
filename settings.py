import configparser
import os

config_path = os.path.join(os.getcwd(),"config.txt")
cf = configparser.ConfigParser()
cf.read(config_path)

PIXIV_ID = cf.get(section="pixiv",option="pixiv_id")
PASSWORD = cf.get(section="pixiv",option="password")

RANK_TYPE = cf.get(section="image",option="rank_type")

DOWNLOAD_THREADS = cf.getint(section="download",option="max_threads")

IMAGE_PATH = cf.get(section="image",option="image_path")

DOWNLOAD_QUANTITY = cf.getint(section="image",option="download_quantity")

WELCOME = "欢迎使用PixivRankDownload"
VERSION = "1.0"