import requests
import bs4
import json
from fake_useragent import UserAgent
from settings import *

_rank_page = {
    "r-18" : "https://www.pixiv.net/ranking.php?mode=daily_r18&p={count}&format=json",
    "normal" : "https://www.pixiv.net/ranking.php?mode=daily&p={count}&format=json"
}

class Pixiv(object) :
    login_post_url = "https://accounts.pixiv.net/api/login?lang=zh"
    login_data_url = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
    rank_url = _rank_page[RANK_TYPE.lower()]
    headers = {"user-agent": UserAgent().random}
    quantity = DOWNLOAD_QUANTITY

    def __init__(self):
        self.session = requests.session()

    def login(self):
        print("正在登陆")
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
        print("登陆完毕")

    def get_rank_list(self):
        print("正在获取排行榜数据")
        count = 1
        pid_list = []
        for page in range(1,self.quantity+1,50) :
            json_data = json.loads(self.session.get(self.rank_url.format(count=count)).text)
            for item in json_data["contents"]:
                if item["rank"] < page + min(self.quantity,50) :
                    pid_list.append(item["illust_id"])
            count+=1
        print("排行榜数据获取完成")
        print("长度：",len(pid_list))
        return pid_list

if __name__ == "__main__" :
    pass