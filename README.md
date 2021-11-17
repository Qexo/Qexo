# Qexo
一个快速、强大、漂亮的在线 Hexo 编辑器。 文档正在施工中...
![](https://user-images.githubusercontent.com/51912589/142183851-7428c3ef-8d38-4029-9ca4-0f5e0f3ccfc0.png)


## 如何部署
- 安装vercel-cli
```bash
npm i -g vercel
```
- 申请 [MongoDB 账号](https://www.mongodb.com/cloud/atlas/register) 创建免费 MongoDB 数据库，区域推荐选择 AWS / N. 
  Virginia (us-east-1) 在 Clusters 页面点击 CONNECT，按步骤设置允许所有 IP 地址的连接），创建数据库用户，并记录数据库连接信息
![image](https://user-images.githubusercontent.com/51912589/140946317-bafeac24-fe3f-408b-927a-ca9a88168fa8.png)

- 修改Configs
  将configs.example.py的文件名修改为configs.py，并根据注释修改数据库配置信息


- 在目录下执行命令部署
```bash
vercel --prod
```

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
