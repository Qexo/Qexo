"""
@Project   : image
@Author    : abudu
@Blog      : https://www.oplog.cn
"""
from datetime import datetime
from hashlib import md5


def replace_path(path: str, file, file_md5, now=datetime.now()):
    """替换图片url的函数"""
    timestamp = str(datetime.timestamp(now))
    now = now.date()
    # {year} 23
    # {month} 6
    # {day}   3
    path = path.replace("{year}", str(now.year)[-2:]).replace("{month}", str(now.month)).replace("{day}", str(now.day)).replace(
        "{filename}", file.name[0:-len(file.name.split(".")[-1]) - 1]).replace("{extName}", file.name.split(".")[-1]).replace("{md5}",
                                                                                                                              file_md5).replace(
        "{time}", timestamp)
    # {YEAR} 2023
    # {MONTH} 06
    # {DAY}   03
    path = path.replace("{YEAR}", str(now.year)).replace("{MONTH}", str(now.month).zfill(2)).replace(
        "{DAY}", str(now.day).zfill(2))

    return path

def replace_folder_path(path: str, now=None):
    """仅替换文件夹url的日期通配符的函数"""
    if now is None:
        now = datetime.now()
    now_date = now.date()
    
    # {year} 23
    # {month} 6
    # {day}   3
    path = path.replace("{year}", str(now_date.year)[-2:]).replace("{month}", str(now_date.month)).replace("{day}", str(now_date.day))
    
    # {YEAR} 2023
    # {MONTH} 06
    # {DAY}   03
    path = path.replace("{YEAR}", str(now_date.year)).replace("{MONTH}", str(now_date.month).zfill(2)).replace("{DAY}", str(now_date.day).zfill(2))

    return path
