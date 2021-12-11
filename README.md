# Qexo
一个快速、强大、漂亮的在线 Hexo 编辑器，您的 Star 是对我最大的支持。
![](https://user-images.githubusercontent.com/51912589/142183851-7428c3ef-8d38-4029-9ca4-0f5e0f3ccfc0.png)
## 特色功能
- 自定义图床上传图片
- 在线配置编辑
- 在线文章管理
- 在线页面管理
- 较为完善的缓存功能
- Webhook 清除缓存
- 自动检查更新
- 实验性的在线更新
- 自动填充date模板

## 如何部署
### 申请 MongoDB 
[注册 MongoDB 账号](https://www.mongodb.com/cloud/atlas/register) 创建免费 MongoDB 数据库，区域推荐选择 AWS / N. 
  Virginia (us-east-1) 在 Clusters 页面点击 CONNECT，按步骤设置允许所有 IP 地址的连接），创建数据库用户，并记录数据库连接信息，密码即为你所设置的值
![](https://user-images.githubusercontent.com/51912589/140946317-bafeac24-fe3f-408b-927a-ca9a88168fa8.png)
### Fork 本项目
打开 [项目主页](https://github.com/am-abudu/Qexo) 点击 Fork 将项目复刻到您的账户下
### 创建 Vercel 项目
打开 [Vercel](https://vercel.com) 注册账号并绑定 Github 新建一个项目并绑定 Fork 的仓库
### 部署
在项目部署界面添加环境变量 Environment Variables
| 名称 | 意义 | 示例 |
| --- | --- | --- |
| DOMAINS | 你所允许通信的安全域名 注意双引号 | [".vercel.app", "127.0.0.1", ".yoursite.com"] |
| MONGODB_HOST | MongoDB 连接地址 | mongodb+srv://cluster0.xxxx.mongodb.net |
| MONGODB_PORT | MongoDB 通信端口 默认应填写 27017 | 27017 |
| MONGODB_USER | MongoDB 用户名 | abudu |
| MONGODB_DB | MongoDB 数据库名 | Cluster0 |
| MONGODB_PASS | MongoDB 密码 | JWo0xxxxxxxx |

点击 Deploy 开始部署，若没有 Error 信息即可打开域名进入初始化引导
## 鸣谢
- [Ace](https://ace.c9.io/)
- [Argon-Dashboard-Django](https://github.com/creativetimofficial/argon-dashboard-django)
- [Bootstrap](https://getbootstrap.com/)
- [Bootstrap-Notify](https://github.com/mouse0270/bootstrap-notify)
- [Django](https://github.com/django/django)
- [Djongo](https://github.com/nesdis/djongo)
- [HexoPlusPlus](https://github.com/HexoPlusPlus/HexoPlusPlus)
- [jQuery](https://jquery.com/)
- [Vercel-Python-WSGI](https://github.com/ardnt/vercel-python-wsgi)
