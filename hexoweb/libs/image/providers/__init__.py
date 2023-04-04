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

_all_providers = {
    custom.Custom.name: custom.Custom,
    s3.S3.name: s3.S3,
    ftp.Ftp.name: ftp.Ftp,
    dogecloudoss.DogeCloudOss.name: dogecloudoss.DogeCloudOss,
    alioss.AliOss.name: alioss.AliOss,
    gitHub.Github.name: gitHub.Github
}
