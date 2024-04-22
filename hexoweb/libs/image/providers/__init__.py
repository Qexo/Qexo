"""
@Project   : image
@Author    : abudu
@Blog      : https://www.oplog.cn
"""
from . import custom
from . import s3
from . import ftp
from . import dogecloudoss
from . import alioss
from . import gitHub
from . import upyun_storage

_all_providers = {
    custom.Main.name: custom,
    s3.Main.name: s3,
    ftp.Main.name: ftp,
    dogecloudoss.Main.name: dogecloudoss,
    alioss.Main.name: alioss,
    gitHub.Main.name: gitHub,
    upyun_storage.Main.name: upyun_storage
}
