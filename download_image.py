import requests
import json
import time
import queue
from threading import Thread
import GIFDownload
from settings import *
from fake_useragent import UserAgent

class Download(object) :
    referer_template = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={pid}"
    img_info_url = "https://www.pixiv.net/ajax/illust/{pid}"
    replace_template = "_p{page}"

    dir_path = os.path.join(IMAGE_PATH,"{date}/{type}")
    file_name = "{pid}_p{page}.{format}"
    headers = {"user-agent": UserAgent().random}
    max_threads = DOWNLOAD_THREADS

    def __init__(self,img_type:str):
        self.th_pool = []
        self.data_queue = queue.Queue()
        self.img_type = img_type

        self.gif_down = GIFDownload.GIFDownload()
        self.gif_down.set_log(False)
        self.gif_down.login()
        self.date = ""
        self.count = 0
        self.failure = 0
        self.data_size = -1

    def download(self,pid_list:list,block = True) :
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.gif_down.set_path(self.dir_path.format(date=self.date,type=self.img_type))

        self.data_size = len(pid_list)
        # self.fuck = pid_list
        # import copy
        # self.shit = copy.deepcopy(pid_list)
        for pid in pid_list :
            self.data_queue.put(pid)

        for i in range(self.max_threads) :
            i = Thread(target=self.download_thread)
            self.th_pool.append(i)
            i.start()

        if block :
            while not self.data_queue.empty():
                time.sleep(0.1)
            for th in self.th_pool :
                th.join()
            self.th_pool.clear()

    def download_thread(self):
        while True :
            if self.data_queue.empty() :
                break
            pid = self.data_queue.get()
            #self.shit.remove(pid)
            self._download(pid)

    def _download(self,pid) :
        dir_path = os.path.join(self.dir_path.format(date=self.date,type=self.img_type),str(pid))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_name = os.path.join(dir_path,self.file_name)

        if self.gif_down.isGIF(pid) :
            self.gif_down.download(pid)
        else :
            headers = self.headers.copy()
            info_url = self.img_info_url.format(pid=pid)
            res = requests.get(info_url, headers=headers)
            js = json.loads(res.text)
            img_url = js["body"]["urls"]["original"]

            count = -1
            while True:
                img_url = img_url.replace(self.replace_template.format(page=count), self.replace_template.format(page=count + 1))
                res = requests.get(img_url, headers=headers)
                count += 1
                if res.status_code != 200:
                    break
                with open(str(count) + ".jpg", "wb+") as fp:
                    fp.write(res.content)

            count = -1
            while True :
                headers["referer"] = self.referer_template.format(pid=pid)
                img_url = img_url.replace(self.replace_template.format(page=count), self.replace_template.format(page=count + 1))
                img_res = requests.get(img_url, headers=headers)
                if img_res.status_code != 200 :
                    break
                image_format = img_url.split(".")[-1]
                with open(file_name.format(pid=pid,page=count,format=image_format),"wb+") as fp :
                    fp.write(img_res.content)
                count += 1
        self.count += 1
        print(pid,"下载完成。当前进度：",self.count,"/",self.data_size,)

if __name__ == "__main__" :
    # fuck = Download("r-18")
    # getattr(fuck,"_download")(74478683)
    pass