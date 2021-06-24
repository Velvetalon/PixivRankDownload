import download_image
import time
import settings
import pixiv_request_manager

if __name__ == "__main__":
    print(settings.WELCOME)
    print("当前版本：", settings.VERSION)
    print("如果觉得好用的话，请在Github上为此项目点击Star：", settings.GITHUB)
    print("当然，也可以issue反馈Bug")
    d = download_image.Downloader()
    p = pixiv_request_manager.PixivRequestManager()
    pid_tuple = p.get_rank()
    d.download(pid_tuple[0], type="safe", block=True)
    if pid_tuple[1] :
        print("数据源切换")
        d.download(pid_tuple[1], type="r-18", block=True)
    print(time.strftime("%Y-%m-%d", time.localtime()), "排行榜前", settings.QUANTITY, "下载完成。")
    print("回车键退出程序。")
    input()
