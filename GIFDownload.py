import json
import os
import zipfile
import imageio
from fake_useragent import UserAgent
import pixiv_request_manager
from settings import *


class GIFDownload(object):
    headers = {
        "user-agent": UserAgent().random,
        "Referer": "https://www.pixiv.net/"
    }
    gif_info_url = "https://www.pixiv.net/ajax/illust/{pid}/ugoira_meta"
    referer_url = "https://www.pixiv.net/me"
    pixiv_manager = pixiv_request_manager.PixivRequestManager()

    def show(self):
        while True:
            data = input("输入GIF PID或URL：")
            if not data.isdigit() and not data.startswith("http"):
                print("输入有误，请重新输入。")
                continue
            if data.isdigit():
                pid = int(data)
            else:
                data = data.strip("/")
                pid = data.split("=")[-1]
                if not pid.isdigit():
                    print("输入有误，请重新输入。")
                    continue
            self.download(pid)
            print(pid, "下载成功")

    def isGIF(self, pid):
        headers = self.headers.copy()
        headers["referer"] = self.referer_url.format(pid=pid)
        gif_info = json.loads(self.pixiv_manager.get(self.gif_info_url.format(pid=pid)).text)
        return not gif_info["error"]

    def download(self, pid, save_path):
        headers = self.headers.copy()
        headers["referer"] = self.referer_url.format(pid=pid)
        file_path = os.path.join(save_path, str(pid))

        print("开始下载")
        # 获取gif信息，提取zip url
        resp = self.pixiv_manager.get(self.gif_info_url.format(pid=pid))
        gif_info = json.loads(resp.text)
        delay = [item["delay"] for item in gif_info["body"]["frames"]]
        delay = sum(delay) / len(delay)
        zip_url = gif_info["body"]["originalSrc"]

        # 下载压缩包
        gif_data = self.pixiv_manager.get(zip_url)
        gif_data = gif_data.content
        try:
            os.makedirs(file_path)
        except Exception:
            pass
        zip_path = os.path.join(file_path, "temp.zip")
        with open(zip_path, "wb+") as fp:
            fp.write(gif_data)
        print("生成临时文件")
        # 生成文件
        temp_file_list = []
        zipo = zipfile.ZipFile(zip_path, "r")
        for file in zipo.namelist():
            temp_file_list.append(os.path.join(file_path, file))
            zipo.extract(file, file_path)
        zipo.close()
        print("生成GIF")
        # 读取所有静态图片，合成gif
        image_data = []
        for file in temp_file_list:
            image_data.append(imageio.imread(file))
        imageio.mimsave(os.path.join(file_path, str(pid) + ".gif"), image_data, "GIF", duration=delay / 1000)
        print("清除临时文件")
        # 清除所有中间文件。
        for file in temp_file_list:
            os.remove(file)
        os.remove(zip_path)
        print(pid, "下载完成")
