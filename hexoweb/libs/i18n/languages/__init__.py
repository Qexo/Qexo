"""
@Project   : i18n
@Author    : abudu
@Blog      : https://www.oplog.cn
"""
from . import zh_CN
from . import zh_TW
from . import en_US

_all_languages = {
    zh_CN.Main.name: zh_CN,
    zh_TW.Main.name: zh_TW,
    en_US.Main.name: en_US
}
