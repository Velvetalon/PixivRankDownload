from fake_useragent import UserAgent
import requests
import json
import settings
import proxy_manager
import cookie_manager
import urllib.parse


class PixivRequestManager(object):
    _rank_page = {
        "r-18": "https://www.pixiv.net/ranking.php?mode=daily_r18&p={count}&format=json",
        "safe": "https://www.pixiv.net/ranking.php?mode=daily&p={count}&format=json"
    }
    headers = {"user-agent": UserAgent().random}
    session = None
    quantity = settings.QUANTITY
    proxies = proxy_manager.get_proxy()
    cookie_manager = cookie_manager.CookieManager()

    def __init__(self):
        self.session = requests.session()
        self.session.keep_alive = False

    def get(self, url):
        headers = self.headers.copy()
        headers["cookie"] = self.cookie_manager.get_cookie()
        headers["host"] = urllib.parse.urlparse(url).hostname
        headers["referer"] = "https://www.pixiv.net/"
        resp = self.session.get(url, headers=headers, proxies=self.proxies)
        resp_cookie = resp.headers.get("set-cookie")
        self.cookie_manager.update(resp_cookie)
        return resp

    def get_rank(self):
        print("正在拉取排行榜数据")
        count = 1
        safe_list = []
        for page in range(1, self.quantity + 1, 50):
            resp = self.get(url=self._rank_page["safe"].format(count=count))
            json_data = json.loads(resp.text)
            for item in json_data["contents"]:
                if item["rank"] < page + min(self.quantity, 50):
                    safe_list.append(item["illust_id"])
            count += 1

        count = 1
        r18_list = []
        for page in range(1, self.quantity + 1, 50):
            resp = self.get(self._rank_page["r-18"].format(count=count))
            try:
                json_data = json.loads(resp.text)
            except:
                print("因账号限制，仅获取safe rank。")
                break
            for item in json_data["contents"]:
                if item["rank"] < page + min(self.quantity, 50):
                    r18_list.append(item["illust_id"])
            count += 1
        print("排行榜数据拉取完成")
        return safe_list, r18_list
