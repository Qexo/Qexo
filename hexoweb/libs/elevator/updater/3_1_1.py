import logging
from hexoweb.functions import get_setting, save_setting
import json

logging.info("开始执行3.1.1版本的更新程序")

# 新增国内代理的更新节点
all_updates = get_setting('ALL_UPDATES')
logging.info("获取ALL_UPDATES => " + all_updates)
all_updates = json.loads(all_updates)
new = [{"name": "master_ghproxy", "url": "https://mirror.ghproxy.com/https://github.com/Qexo/Qexo/archive/master.tar.gz"},
       {"name": "dev_ghproxy", "url": "https://mirror.ghproxy.com/https://github.com/Qexo/Qexo/archive/dev.tar.gz"}]
for i in new:
    if i not in all_updates:
        all_updates.append(i)
save_setting('ALL_UPDATES', json.dumps(all_updates))
logging.info("执行完成3.1.1版本的更新程序")
