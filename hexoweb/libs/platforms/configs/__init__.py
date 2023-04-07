from . import hexo
from . import hugo
from . import valaxy
from . import vuepress
from . import vitepress

_all_configs = {
    hexo.config["name"]: hexo.config,
    hugo.config["name"]: hugo.config,
    valaxy.config["name"]: valaxy.config,
    vuepress.config["name"]: vuepress.config,
    vitepress.config["name"]: vitepress.config
}
