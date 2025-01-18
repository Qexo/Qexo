import logging
from hexoweb.functions import get_setting, save_setting
import json

logging.info("开始执行3.5.4版本的更新程序")

# 修改CDN为新的CDN格式
cdn_prev = get_setting('CDN_PREV')
if not "{version}" in cdn_prev:
    if "jsdelivr" in cdn_prev:
        cdn_prev = "https://cdn.jsdelivr.net/npm/qexo-static@{version}/qexo"
        logging.info("已更新CDN前缀为Jsdelivr")
    elif "unpkg" in cdn_prev:
        cdn_prev = "https://unpkg.com/qexo-static@{version}/qexo"
        logging.info("已更新CDN前缀为Unpkg")
    else:
        cdn_prev = "https://registry.npmmirror.com/qexo-static/{version}/files/qexo"
        logging.info("已更新CDN前缀为CNPM")
    save_setting('CDN_PREV', cdn_prev)

# 修改CDN列表
all_cdn = [
    {"name": "CNPM", "url": "https://registry.npmmirror.com/qexo-static/{version}/files/qexo"},
    {"name": "Jsdelivr", "url": "https://cdn.jsdelivr.net/npm/qexo-static@{version}/qexo"},
    {"name": "Unpkg", "url": "https://unpkg.com/qexo-static@{version}/qexo"},
    # {"name": "渺软公益 CDN", "url": "https://npm.onmicrosoft.cn/qexo-static@{version}/qexo"},
    # {"name": "初七云", "url": "https://cdn.chuqis.com/npm/"}
]
save_setting('ALL_CDN_PREV', json.dumps(all_cdn))

logging.info("执行完成3.5.4版本的更新程序")
