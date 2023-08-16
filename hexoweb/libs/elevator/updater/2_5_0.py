import logging
from hexoweb.functions import get_setting, save_setting
import json

logging.info("开始执行2.5.0版本的更新程序")

# 更换Vditor的默认引用CDN
cdn_prev = get_setting('CDN_PREV')
logging.info("获取到CDN_PREV => " + cdn_prev)
if cdn_prev in ["https://unpkg.com/", "https://cdn.jsdelivr.net/npm/"]:
    save_setting('CDN_PREV', "https://npm.onmicrosoft.cn/")
#
# # 添加 渺软公益 CDN
# all_cdnjs = json.loads(get_setting("ALL_CDN"))
# logging.info("获取到ALL_CDN => " + str(all_cdnjs))
# if {"name": "渺软公益 CDN", "url": "https://cdnjs.onmicrosoft.cn/ajax/libs/"} not in all_cdnjs:
#     all_cdnjs.append({"name": "渺软公益 CDN", "url": "https://cdnjs.onmicrosoft.cn/ajax/libs/"})
#     save_setting("ALL_CDN", json.dumps(all_cdnjs))

logging.info("执行完成2.5.0版本的更新程序")
