# Qexo
一个快速、强大、漂亮的在线 Hexo 编辑器，您的 Star 是对我最大的支持。 [Wiki](https://github.com/Qexo/Qexo/wiki)
![](https://user-images.githubusercontent.com/51912589/159258766-19a1ce22-d34b-4b29-b291-7d70e8942859.png)
## 特色功能
- 自定义图床上传图片
- 在线配置编辑
- 在线页面管理
- 开放 API
- 自动检查更新
- 实验性的在线更新
- 自动填充 date 模板
- 基于时间戳的 abbrlink
## 你可能需要
* [文档](https://github.com/Qexo/Qexo/wiki)
### 快速上手
* [Vercel 部署](https://github.com/am-abudu/Qexo/wiki/Vercel-%E9%83%A8%E7%BD%B2)
* [服务器部署](https://github.com/am-abudu/Qexo/wiki/%E6%9C%8D%E5%8A%A1%E5%99%A8%E9%83%A8%E7%BD%B2)
* [版本更新](https://github.com/am-abudu/Qexo/wiki/%E5%A6%82%E4%BD%95%E6%9B%B4%E6%96%B0)
## 常见问题
这里汇集了一些常见的问题，如果你遇到同样的问题，请先尝试如下的回答
### 什么是 API 密钥
在您完成初始化之后可在设置界面修改/创建 API 密钥，用于 Webhook 中的身份验证。若留空系统会随机生成一个 API 密钥
### Webhook 是什么
Qexo 中的 Webhook 指 /api/webhook 用于自动化操作，目前可用于自动清除缓存
### 安装后出现 504 Time out
1. 您的数据库没有正确配置或没有允许所有 IP 白名单访问，可在 MongoDB 控制台进行修改，修改完成后**一定要重新部署**
2. 删除并重建数据库，注意区域**一定要选择 AWS / N. Virginia (us-east-1)**
### 安装/更新后出现 5xx 错误
Qexo 每个 Release 都经过 Dev 分支的测试，一般情况下不会出现较大问题，如果你遇到了500等错误，请尝试以下步骤
1. 检查数据库配置
2. 清除浏览器缓存
3. 在高级设置中点击“修复”按钮
4. 若无法登录请使用API: yoursite.com/pub/fix?token={$APIKEY}
5. 保留数据库配置的环境变量并重新 Fork 仓库部署
6. 重新部署整个程序
7. 尝试 Dev 分支
### AssertionError("xxx object ... its id attribute is set to None.")
请检查你是否曾使用过0.01或0.1版本，这两个版本有严重问题，请重新创建数据库并部署
### 如何创建子目录下的文章
在文章名一栏填写 dir/filename 例如您希望创建 source/_posts/about/me.md 则需要输入 about/me
### KeyError: 'XXX'
表示并没有获取到 "XXX" 这个环境变量，请根据表格添加后 Redeploy
| 名称 | 意义 | 示例 |
| --- | --- | --- |
| DOMAINS | 你所允许通信的安全域名 注意双引号而且是英文半角 | [".vercel.app", "127.0.0.1", ".yoursite.com"] |
| MONGODB_HOST | MongoDB 数据库连接地址 | mongodb+srv://cluster0.xxxx.mongodb.net |
| MONGODB_PORT | MongoDB 数据库通信端口 默认应填写 27017 | 27017 |
| MONGODB_USER | MongoDB 数据库用户名 | abudu |
| MONGODB_DB | MongoDB 数据库名 | Cluster0 |
| MONGODB_PASS | MongoDB 数据库密码 | JWo0xxxxxxxx |
### Github 配置校验错误
如果配置中遇到问题，可以访问 [HPP校验助手](https://hexoplusplus.cronfly.workers.dev/?step=start) 自检配置，若确认无误，可检查仓库内是否有已经发布的文章

注意：Github 仓库一定为您 Hexo **自动化部署**所在的仓库
### Vercel 用量问题
Vercel 的无服务器函数用量对于 Qexo 来说是充裕的，但这依然抵挡不住有心之人的攻击行为，所以要保护好自己后台地址，不过好在 Vercel 不会随意扣费，所以在资源用完之后并不会产生费用，若依然不放心可以考虑部署在自己的服务器上 [#服务器部署#](https://github.com/am-abudu/Qexo/wiki/%E6%9C%8D%E5%8A%A1%E5%99%A8%E9%83%A8%E7%BD%B2)
### 在线更新失败了
检查高级设置中的 VERCEL_TOKEN 和 PROJECT_ID 是否正确为 Qexo 的部署项目
### 其他问题
如果还有问题，可以发 [issue](https://github.com/am-abudu/Qexo/issues) 或加入 [HexoPlusPlus交流群](https://jq.qq.com/?_wv=1027&k=rAcnhzqK) 询问

## 鸣谢
- [Ace](https://ace.c9.io/)
- [Argon-Dashboard-Django](https://github.com/creativetimofficial/argon-dashboard-django)
- [Bootstrap](https://getbootstrap.com/)
- [Notyf](https://github.com/caroso1222/notyf)
- [Django](https://github.com/django/django)
- [Djongo](https://github.com/nesdis/djongo)
- [HexoPlusPlus](https://github.com/HexoPlusPlus/HexoPlusPlus)
- [jQuery](https://jquery.com/)
- [OnePush](https://github.com/y1ndan/onepush)
- [Vercel-Python-WSGI](https://github.com/ardnt/vercel-python-wsgi)
