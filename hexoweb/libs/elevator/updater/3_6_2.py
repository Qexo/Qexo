import logging
from hexoweb.functions import get_setting, save_setting
import json

logging.info("开始执行3.6.2版本的更新程序")

# 删除国内代理的更新节点 ghproxy
all_updates = get_setting('ALL_UPDATES')
logging.info("获取ALL_UPDATES => " + all_updates)
all_updates = json.loads(all_updates)
all_updates = [update for update in all_updates if not update['name'].endswith('_ghproxy')]
# 添加新的 cnb 更新节点
new = [{"name": "master_cnb", "url": "https://cnb.cool/qexo/Qexo/-/git/archive/master.tar.gz"},
       {"name": "dev_cnb", "url": "https://cnb.cool/qexo/Qexo/-/git/archive/dev.tar.gz"}]
for i in new:
    if i not in all_updates:
        all_updates.append(i)

save_setting('ALL_UPDATES', json.dumps(all_updates))
logging.info("执行完成3.6.2版本的更新程序")
