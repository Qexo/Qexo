import json
import random

QEXO_VERSION = "3.5.3"
QEXO_STATIC = "2.4.0"

DEFAULT_EMOJI = {"微笑": "🙂", "撇嘴": "😦", "色": "😍", "发呆": "😍", "得意": "😎",
                 "流泪": "😭", "害羞": "😊", "闭嘴": "😷", "睡": "😴",
                 "大哭 ": "😡", "尴尬": "😡", "发怒": "😛", "调皮": "😀", "呲牙": "😯",
                 "惊讶": "🙁", "难过": "😎", "酷": "😨", "冷汗": "😱", "抓狂": "😵", "吐 ": "😋",
                 "偷笑": "☺", "愉快": "🙄", "白眼": "🙄", "傲慢": "😋", "饥饿": "😪", "困": "😫",
                 "惊恐": "😓", "流汗": "😃", "憨笑": "😃", "悠闲 ": "😆", "奋斗": "😆",
                 "咒骂": "😆", "疑问": "😆", "嘘": "😵", "晕": "😆", "疯了": "😆", "衰": "😆",
                 "骷髅": "💀", "敲打": "😬", "再见 ": "😘", "擦汗": "😆", "抠鼻": "😆",
                 "鼓掌": "👏", "糗大了": "😆", "坏笑": "😆", "左哼哼": "😆", "右哼哼": "😆",
                 "哈欠": "😆", "鄙视": "😆", "委屈 ": "😆", "快哭了": "😆", "阴险": "😆",
                 "亲亲": "😘", "吓": "😓", "可怜": "😆", "菜刀": "🔪", "西瓜": "🍉", "啤酒": "🍺",
                 "篮球": "🏀", "乒乓 ": "⚪", "咖啡": "☕", "饭": "🍚", "猪头": "🐷", "玫瑰": "🌹",
                 "凋谢": "🌹", "嘴唇": "👄", "爱心": "💗", "心碎": "💔", "蛋糕": "🎂", "闪电 ": "⚡",
                 "炸弹": "💣", "刀": "🗡", "足球": "⚽", "瓢虫": "🐞", "便便": "💩", "月亮": "🌙",
                 "太阳": "☀", "礼物": "🎁", "拥抱": "🤗", "强 ": "👍", "弱": "👎", "握手": "👍",
                 "胜利": "✌", "抱拳": "✊", "勾引": "✌", "拳头": "✊", "差劲": "✌", "爱你": "✌",
                 "NO": "✌", "OK": "🙂", "嘿哈": "🙂", "捂脸": "🙂", "奸笑": "🙂", "机智": "🙂",
                 "皱眉": "🙂", "耶": "🙂", "吃瓜": "🙂", "加油": "🙂", "汗": "🙂", "天啊": "👌",
                 "社会社会": "🙂", "旺柴": "🙂", "好的": "🙂", "哇": "🙂"}

# DEFAULT_CDN = [  # CDNJS 已废除
#     {"name": "Cloudflare", "url": "https://cdnjs.cloudflare.com/ajax/libs/"},
#     {"name": "Loli", "url": "https://cdnjs.loli.net/ajax/libs/"},
#     {"name": "七牛云", "url": "https://cdn.staticfile.org/"},
#     {"name": "75CDN", "url": "https://lib.baomitu.com/"},
#     {"name": "BootCDN", "url": "https://cdn.bootcdn.net/ajax/libs/"},
#     # {"name": "重庆邮电大学", "url": "https://mirrors.cqupt.edu.cn/cdnjs/ajax/libs/"},  # 更新不及时
#     {"name": "南方科技大学", "url": "https://mirrors.sustech.edu.cn/cdnjs/ajax/libs/"},
#     {"name": "渺软公益 CDN", "url": "https://cdnjs.onmicrosoft.cn/ajax/libs/"}
# ]

DEFAULT_CDN = [
    {"name": "Jsdelivr", "url": "https://cdn.jsdelivr.net/npm/"},
    {"name": "Unpkg", "url": "https://unpkg.com/"},
    {"name": "渺软公益 CDN", "url": "https://npm.onmicrosoft.cn/"}
    # {"name": "初七云", "url": "https://cdn.chuqis.com/npm/"}
]

DEFAULT_UPDATES = [
    {"name": "master", "url": "https://github.com/Qexo/Qexo/tarball/master/"},
    {"name": "dev", "url": "https://github.com/Qexo/Qexo/tarball/dev/"},
    {"name": "master_ghproxy", "url": "https://mirror.ghproxy.com/https://github.com/Qexo/Qexo/archive/master.tar.gz"},
    {"name": "dev_ghproxy", "url": "https://mirror.ghproxy.com/https://github.com/Qexo/Qexo/archive/dev.tar.gz"}
]

ALL_SETTINGS = [  # [名称, 默认值, 是否在尝试修复时重置, 简介]
    ["ABBRLINK_ALG", "crc16", False, "短链接算法"],
    ["ABBRLINK_REP", "dec", False, "短链接格式dec/hex"],
    ["CDN_PREV", "https://cdn.jsdelivr.net/npm/", True, "调用NPM的CDN前缀"],
    # ["CDNJS", "https://cdn.staticfile.org/", True, "调用CDNJS的CDN前缀"],
    ["INIT", "2", False, "初始化标识"],
    ["QEXO_ICON", "/static/qexo-static@" + QEXO_STATIC + "/qexo/images/icon.png", False, "站点ICON"],
    ["QEXO_LOGO", "/static/qexo-static@" + QEXO_STATIC + "/qexo/images/qexo.png", False, "站点LOGO"],
    ["QEXO_LOGO_DARK", "https://unpkg.com/qexo-static@" + QEXO_STATIC + "/qexo/images/qexo-dark.png", False, "暗色站点LOGO"],
    ["QEXO_NAME", "博客管理面板", False, "站点名"],
    ["QEXO_SPLIT", "-", False, "站点分隔符"],
    ["VDITOR_EMOJI", json.dumps(DEFAULT_EMOJI), True, "自定义表情"],
    ["WEBHOOK_APIKEY", ''.join(random.choice("qwertyuiopasdfghjklzxcvbnm1234567890") for x in range(12)), False, "API密钥"],
    ["VERCEL_TOKEN", "", False, "Vercel密钥"],
    ["PROJECT_ID", "", False, "Qexo项目ID"],
    ["ALLOW_FRIEND", "否", False, "是否允许友链申请 是/否"],
    ["LAST_LOGIN", "", True, "博主最后上线时间(无需更改)"],
    ["IMG_HOST", "{\"type\":\"关闭\",\"params\":{}}", False, "2.0之后的图床设置JSON"],
    ["ONEPUSH", "", False, "OnePush消息通知"],
    ["PROVIDER", "", False, "2.0之后的平台JSON"],
    ["STATISTIC_ALLOW", "否", False, "是否开启统计功能 是/否"],
    ["STATISTIC_DOMAINS", "", False, "统计安全域名 英文半角逗号间隔"],
    ["FRIEND_RECAPTCHA", "否", False, "启用友链验证码reCaptcha 关闭/v2/v3"],
    ["RECAPTCHA_TOKEN", "", False, "用于友链reCaptcha服务器端密钥"],
    ["LOGIN_RECAPTCHA_SITE_TOKEN", "", False, "用于登录验证的reCaptchaV3网站密钥"],
    ["LOGIN_RECAPTCHA_SERVER_TOKEN", "", False, "用于登录验证的reCaptchaV3服务端密钥"],
    ["LOGIN_RECAPTCHAV2_SITE_TOKEN", "", False, "用于登录验证的reCaptchaV2网站密钥"],
    ["LOGIN_RECAPTCHAV2_SERVER_TOKEN", "", False, "用于登录验证的reCaptchaV2服务端密钥"],
    ["POST_SIDEBAR",
     "[{\"search\":\"title\",\"name\":\"标题\",\"icon\":\"fas fa-heading\"},{\"search\":\"abbrlink\",\"name\":\"缩写\",\"icon\":\"fas fa-id-card\"},{\"search\":\"date\",\"name\":\"发布于\",\"icon\":\"fas fa-globe-americas\"},{\"search\":\"updated\",\"name\":\"更新于\",\"icon\":\"fas fa-calendar-alt\"},{\"search\":\"tags\",\"name\":\"标签\",\"icon\":\"fas fa-tags\"},{\"search\":\"categories\",\"name\":\"分类\",\"icon\":\"fas fa-folder-open\"}]",
     False, "文章侧边栏配置JSON"],
    ["PAGE_SIDEBAR",
     "[{\"search\":\"title\",\"name\":\"标题\",\"icon\":\"fas fa-heading\"},{\"search\":\"date\",\"name\":\"发布于\",\"icon\":\"fas fa-globe-americas\"},{\"search\":\"updated\",\"name\":\"更新于\",\"icon\":\"fas fa-calendar-alt\"}]",
     False, "页面侧边栏配置JSON"],
    ["TALK_SIDEBAR", "[]", False, "说说侧边栏配置JSON"],
    # ["EXCERPT_POST", "否", False, "是否开启在摘录为空时自动截取文章 是/否"],   # 弃用
    # ["EXCERPT_LENGTH", "200", False, "自动截取文章的长度"],  # 弃用
    # ["ALL_CDN", json.dumps(DEFAULT_CDN), True, "CDN列表"],
    ["ALL_CDN_PREV", json.dumps(DEFAULT_CDN), True, "CDN列表New"],
    ["ALL_UPDATES", json.dumps(DEFAULT_UPDATES), True, "更新源列表"],
    ["UPDATE_FROM", "false", False, "是否更新过"],
    ["JUMP_UPDATE", "false", False, "是否转跳到更新界面"],
    ["AUTO_EXCERPT_CONFIG", '{"method":"本地","auto":"关闭","save_key":"excerpt","params":{"save_key":"excerpt","length":"200"}}', False,
     "文章截取配置JSON"],
    ["LANGUAGE", "zh_CN", True, "语言"],
]

VDITOR_LANGUAGES = ["zh_CN", "en_US", "zh_TW", "fr_FR", "ja_JP", "ko_KR", "pt_BR", "ru_RU", "sv_SE"]
