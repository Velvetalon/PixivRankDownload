import requests
import bs4
import time
import queue
from threading import Thread
import GIFDownload
from settings import *
from fake_useragent import UserAgent

class Download(object) :
    url_template = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={pid}"
    image_template = "https://i.pximg.net/img-original/img/{data}/{pid}_p{count}.{format}"
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

    def download(self,pid_list:list,block = True) :
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.gif_down.set_path(self.dir_path.format(date=self.date,type=self.img_type))

        self.count = 0
        self.failure = 0
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

        headers = self.headers
        res = requests.get(self.url_template.format(pid=pid),headers=headers)

        soup = bs4.BeautifulSoup(res.text,"lxml")
        try :
            src_url = soup.find(class_="sensored").img["src"]
        except TypeError :
            self.gif_down.download(pid)
        else :
            time_data = src_url.split("/")[7:13]
            image_format = src_url.split(".")[-1]

            count = 0
            while True :
                headers["referer"] = self.url_template.format(pid=pid)
                img_res = requests.get(url = self.image_template.format(data="/".join(time_data),pid=pid,count=count,format=image_format),
                                       headers=headers,)
                if img_res.status_code != 200 :
                    break
                with open(file_name.format(pid=pid,page=count,format=image_format),"wb+") as fp :
                    fp.write(img_res.content)
                count += 1
        self.count += 1
        print(pid,"下载完成。当前进度：",self.count,"/",self.data_size,)
        # self.fuck.remove(pid)
        # print("未被获取数据：",self.shit)
        # print("未下载完成数据：",self.fuck)
if __name__ == "__main__" :
    pass