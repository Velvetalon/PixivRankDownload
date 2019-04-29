import download_image
import time
import pixiv
import settings

if __name__ == "__main__" :
    d = download_image.Download(settings.RANK_TYPE)
    p = pixiv.Pixiv()
    p.login()
    pid_list = p.get_rank_list()
    d.download(pid_list,block=True)
    print(time.strftime("%Y-%m-%d", time.localtime()),"排行榜前",settings.DOWNLOAD_QUANTITY,"下载完成。")
    print("回车键退出程序。")
    input()