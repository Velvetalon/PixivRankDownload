import requests
import json
import time
import queue
from threading import Thread
from settings import *
from fake_useragent import UserAgent
import os
import GIFDownload
import settings


class Downloader(object):
    referer_template = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={pid}"
    img_info_url = "https://www.pixiv.net/ajax/illust/{pid}"
    replace_template = "_p{page}"

    dir_path = os.path.join(IMAGE_PATH, "{date}/{type}")
    headers = {
        "user-agent": UserAgent().random,
        "Referer": "https://www.pixiv.net/"
    }
    gif_downloader = GIFDownload.GIFDownload()
    max_threads = DOWNLOAD_THREADS

    download_quota = []

    def __init__(self):
        self.th_pool = []
        self.data_queue = queue.Queue()

        self.date = ""
        self.count = 0
        self.failure = 0
        self.data_size = -1

    def download(self, pid_list: list, type: str, block=True):
        if not pid_list:
            return

        self.date = time.strftime("%Y-%m-%d", time.localtime())
        # self.gif_downloader.set_path(self.dir_path.format(date=self.date, type=self.img_type))

        self.data_size = len(pid_list)
        for pid in pid_list:
            self.data_queue.put(pid)

        for i in range(self.max_threads):
            i = Thread(target=self.download_thread, args=(type,))
            self.th_pool.append(i)
            i.start()

        if settings.DOWNLOAD_SPEED > 0:
            th = Thread(target=self.quota)
            th.daemon = True
            th.start()

        if block:
            while not self.data_queue.empty():
                time.sleep(0.1)
            for th in self.th_pool:
                th.join()
            self.th_pool.clear()

    def quota(self):
        while True:
            # 休眠时间为下载速度的倒数，如下载速度为0.5时，每秒放出2个限额
            time.sleep(1 / settings.DOWNLOAD_SPEED)
            if len(self.download_quota) < 100:
                self.download_quota.append(True)

    def download_thread(self, type):
        while True:
            if self.data_queue.empty():
                break
            if settings.DOWNLOAD_SPEED > 0:
                if len(self.download_quota) > 0:
                    self.download_quota.pop()
                else:
                    time.sleep(0.1)
                    continue
            pid = self.data_queue.get()
            # self.shit.remove(pid)
            self._download(pid, type)

    def _download(self, pid, type):
        dir_path = os.path.join(self.dir_path.format(date=self.date, type=type), str(pid))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        if self.gif_downloader.isGIF(pid):
            self.gif_downloader.download(pid, dir_path)
        else:
            headers = self.headers.copy()
            info_url = self.img_info_url.format(pid=pid)
            res = requests.get(info_url, headers=headers)
            js = json.loads(res.text)
            img_url = js["body"]["urls"]["original"]

            count = -1
            while True:
                img_url = img_url.replace(self.replace_template.format(page=count),
                                          self.replace_template.format(page=count + 1))
                res = requests.get(img_url, headers=headers)
                count += 1
                file_path = os.path.join(dir_path, str(count))
                if res.status_code != 200:
                    break
                with open(str(file_path) + ".jpg", "wb+") as fp:
                    fp.write(res.content)

            count = -1
            while True:
                headers["referer"] = self.referer_template.format(pid=pid)
                img_url = img_url.replace(self.replace_template.format(page=count),
                                          self.replace_template.format(page=count + 1))
                count += 1
                img_res = requests.get(img_url, headers=headers)
                if img_res.status_code != 200:
                    break
                image_format = img_url.split(".")[-1]
                file_path = os.path.join(dir_path, str(count))
                with open(file_path.format(pid=pid, page=count, format=image_format), "wb+") as fp:
                    fp.write(img_res.content)
                count += 1
        self.count += 1
        print(pid, "下载完成。当前进度：", self.count, "/", self.data_size, )


if __name__ == "__main__":
    pass
