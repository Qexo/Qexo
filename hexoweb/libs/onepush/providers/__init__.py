"""
@Project   : onepush
@Author    : y1ndan
@Blog      : https://www.yindan.me
"""

from . import bark
from . import custom
from . import gocqhttp
from . import dingtalk
from . import discord
from . import pushplus
from . import pushdeer
from . import qmsg
from . import serverchan
from . import serverchanturbo
from . import telegram
from . import wechatworkapp
from . import wechatworkbot
from . import smtp

_all_providers = {
    bark.Bark.name: bark.Bark,
    custom.Custom.name: custom.Custom,
    gocqhttp.Gocqhttp.name: gocqhttp.Gocqhttp,
    dingtalk.DingTalk.name: dingtalk.DingTalk,
    discord.Discord.name: discord.Discord,
    pushplus.PushPlus.name: pushplus.PushPlus,
    pushdeer.PushDeer.name: pushdeer.PushDeer,
    qmsg.Qmsg.name: qmsg.Qmsg,
    serverchan.ServerChan.name: serverchan.ServerChan,
    serverchanturbo.ServerChanTurbo.name: serverchanturbo.ServerChanTurbo,
    smtp.Smtp.name: smtp.Smtp,
    telegram.Telegram.name: telegram.Telegram,
    wechatworkapp.WechatWorkApp.name: wechatworkapp.WechatWorkApp,
    wechatworkbot.WechatWorkBot.name: wechatworkbot.WechatWorkBot
}
