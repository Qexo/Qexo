"""
@Project   : i18n
@Author    : abudu
@Blog      : https://www.oplog.cn
"""
from . import zh_CN
from . import zh_TW
from . import en_US
from . import en_UK
from . import fr_FR
from . import ja_JP
from . import ko_KR

_all_languages = {
    zh_CN.Main.name: zh_CN,
    zh_TW.Main.name: zh_TW,
    en_UK.Main.name: en_UK,
    en_US.Main.name: en_US,
    fr_FR.Main.name: fr_FR,
    ja_JP.Main.name: ja_JP,
    ko_KR.Main.name: ko_KR
}
