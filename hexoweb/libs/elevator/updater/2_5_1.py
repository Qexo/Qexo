import logging
from hexoweb.functions import get_setting, save_setting
import json

logging.info("开始执行2.5.1版本的更新程序")

# 为 PROVIDER 添加 config
provider = json.loads(get_setting('PROVIDER'))
logging.info("获取到PROVIDER => " + "********")
if not provider["params"].get("config"):
    provider["params"]["config"] = "Hexo"
save_setting('PROVIDER', json.dumps(provider))

logging.info("执行完成2.5.1版本的更新程序")
