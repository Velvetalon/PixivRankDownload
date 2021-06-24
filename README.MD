## 如何使用？

+ 登陆你的Pixiv账号，在开发者控制台中取得你的cookie， 写入pixiv_cookie.ini中。 该文件仅需填写一次，此后该文件将会自动更新。

+ 打开settings.py，根据你的网络环境配置代理和下载速度。 注：过快的下载速度将可能导致你的IP/账号被封锁。

+ 启动main.py。它会将当天的排行榜下载至指定的位置（默认为当前目录下的Image文件夹。）

---

## 如何反馈bug

发送邮件至stardust.whc@gmail.com，或使用issue。

---

## 常见问题

Q：提示JSON格式错误，何解？

A：导致这种情况可能的原因：你的账号在其他位置登陆；你的账号被封锁；你的IP被禁用等。 请尝试重新获取并写入cookie或切换代理。

Q：提示 “Max retries exceeded with url...” ，何解？

A：通常原因：你的IP被封锁/你的代理不稳定。请尝试切换代理。

Q：手动启动太麻烦了，有没有其他方式？

A：你可以关注我的另一个项目：[QQRobot](https://github.com/Velvetalon/QQRobot) 。
它是一个基于Simbot框架、使用Java语言编写的QQ聊天机器人，内置了Pixiv下载器，计划中还将提供订阅、定时下载等功能。 使用它，你可以在群聊中下载图片，而不必亲自安装Python环境（运行.py总是比java
-jar更麻烦，对吧？）

其他问题等待补充...
