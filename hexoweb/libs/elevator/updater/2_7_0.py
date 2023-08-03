import logging
from hexoweb.functions import get_setting, save_setting
import json

logging.info("开始执行2.7.0版本的更新程序")

# 更换Vditor的默认引用CDN
cdn_prev = get_setting('CDN_PREV')
logging.info("获取到CDN_PREV => " + cdn_prev)
if cdn_prev in ["https://unpkg.com/", "https://cdn.jsdelivr.net/npm/"]:
    save_setting('CDN_PREV', "https://npm.onmicrosoft.cn/")

logging.info("执行完成2.5.0版本的更新程序")
