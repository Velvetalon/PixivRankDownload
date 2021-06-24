import settings
import os
import threading


class CookieManager(object):
    cookie_file = settings.COOKIE_FILE
    cookie_map = {}
    _instance_lock = threading.Lock()
    write_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(CookieManager, "_instance"):
            with CookieManager._instance_lock:
                if not hasattr(CookieManager, "_instance"):
                    CookieManager._instance = object.__new__(cls)
        return CookieManager._instance

    def __init__(self):
        if not os.path.exists(self.cookie_file):
            raise FileNotFoundError("cookie文件：{} 不存在".format(self.cookie_file))
        with open(self.cookie_file, "r") as fp:
            self.update(fp.read())

    def update(self, cookie):
        if (isinstance(cookie, list) or isinstance(cookie, tuple)) and cookie:
            for i in cookie:
                self.update_with_str(i)
        elif isinstance(cookie, str):
            self.update_with_str(cookie)
        self.flush_to_file()

    def update_with_str(self, cookie_str: str):
        split = cookie_str.split(";")
        if len(split) < 1:
            return
        for i in split:
            kv = i.split("=")
            if len(kv) < 2:
                continue
            self.cookie_map[kv[0]] = kv[1]

    def get_cookie(self):
        return ";".join([key + "=" + self.cookie_map[key] for key in self.cookie_map.keys()])

    def flush_to_file(self):
        with self.write_lock:
            with open(self.cookie_file, "w+") as fp:
                fp.write(self.get_cookie())
