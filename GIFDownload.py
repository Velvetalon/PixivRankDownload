import requests
import json
import zipfile
import os
import imageio
import bs4
import requests
from settings import *
from fake_useragent import UserAgent

class GIFDownload(object) :
    login_post_url = "https://accounts.pixiv.net/api/login?lang=zh"
    login_data_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
    headers = {"user-agent": UserAgent().random}
    gif_info_url = "https://www.pixiv.net/ajax/illust/{pid}/ugoira_meta"
    referer_url = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={pid}"
    path = ""

    def __init__(self):
        self.session = requests.session()
        self.log_flag = True

    def set_path(self,file_path = IMAGE_PATH):
        self.path = file_path

    def log(self,*log_info):
        if self.log_flag :
            str_log = ""
            for info in log_info :
                str_log += str(info)
            print(str_log)

    def set_log(self,flag:bool):
        assert isinstance(flag,bool)
        self.log_flag = flag

    def set_headers(self,headers:dict):
        assert isinstance(headers,dict)
        self.headers = headers

    def login(self):
        self.log("正在登陆")
        data = self.session.get(url=self.login_data_url,headers=self.headers).content.decode("utf8")
        post_key = bs4.BeautifulSoup(data,"lxml").find(attrs={"name":"post_key"})["value"]
        login_data = {
            "pixiv_id": PIXIV_ID,
            "password": PASSWORD,
            "post_key": post_key,
            "source": "pc",
            "ref": "wwwtop_accounts_index",
            "return_to": "https://www.pixiv.net/",
        }
        self.session.post(url=self.login_post_url,data=login_data)
        cookey = requests.utils.dict_from_cookiejar(self.session.cookies)
        cookie = ""
        for k,v in cookey.items() :
            cookie += k + "=" + v + "; "
        self.headers["cookie"] = cookie[:-2]
        self.log("登录完成")

    def show(self):
        while True :
            data = input("输入GIF PID或URL：")
            if not data.isdigit() and not data.startswith("http") :
                print("输入有误，请重新输入。")
                continue
            if data.isdigit():
                pid = int(data)
            else :
                data = data.strip("/")
                pid = data.split("=")[-1]
                if not pid.isdigit():
                    print("输入有误，请重新输入。")
                    continue
            self.download(pid)
            print(pid,"下载成功")

    def download(self,pid):
        self.headers["referer"] = self.referer_url.format(pid=pid)
        file_path = os.path.join(self.path,str(pid))

        self.log("开始下载")
        #获取gif信息，提取zip url
        gif_info = json.loads(requests.get(self.gif_info_url.format(pid=pid), headers=self.headers).text)
        delay = [item["delay"] for item in gif_info["body"]["frames"]]
        delay = sum(delay) / len(delay)
        zip_url = gif_info["body"]["originalSrc"]

        #下载压缩包
        gif_data = requests.get(zip_url, headers=self.headers)
        gif_data=gif_data.content
        try :
            os.mkdir(file_path)
        except Exception:
            pass
        zip_path = os.path.join(file_path, "temp.zip")
        with open(zip_path,"wb+") as fp :
            fp.write(gif_data)
        self.log("生成临时文件")
        #生成文件
        temp_file_list = []
        zipo = zipfile.ZipFile(zip_path, "r")
        for file in zipo.namelist():
            temp_file_list.append(os.path.join(file_path, file))
            zipo.extract(file, file_path)
        zipo.close()
        self.log("生成GIF")
        #读取所有静态图片，合成gif
        image_data = []
        for file in temp_file_list:
            image_data.append(imageio.imread(file))
        imageio.mimsave(os.path.join(file_path, str(pid) + ".gif"), image_data, "GIF", duration=delay / 1000)
        self.log("清除临时文件")
        #清除所有中间文件。
        for file in temp_file_list:
            os.remove(file)
        os.remove(zip_path)
        self.log(pid,"下载完成")

if __name__ == "__main__" :
    test = GIFDownload()
    test.login()
    test.show()
    #main(73252345)