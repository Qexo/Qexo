"""
在这里部署配置你的数据库信息
configuration your MongoDB database here
"""

CONFIGS = {
    'DOMAINS': ['qexo.qystudio.ltd', 'setting.qystudio.ltd', '127.0.0.1'],   # allow hosts
    'MONGODB_HOST': mongodb+srv://qystudio:ljs070112@cluster0.3ldqe.mongodb.net',  # your MongoDB host
    'MONGODB_PORT': 27017,  # default is '27017'
    'MONGODB_USER': 'user',  # your MongoDB username
    'MONGODB_DB': 'Cluster0',  # your MongoDB database name
    'MONGODB_PASS': 'ljs070112',  # your MongoDB password
}
