import logging
from hexoweb.functions import get_setting, save_setting

logging.info("开始执行3.7.0版本的更新程序")

current_key = get_setting("WEBHOOK_APIKEY")
if current_key and len(current_key) != 64:
    save_setting("WEBHOOK_APIKEY", current_key)
    logging.info("更新 WEBHOOK_APIKEY 到哈希形式")

logging.info("执行完成3.7.0版本的更新程序")