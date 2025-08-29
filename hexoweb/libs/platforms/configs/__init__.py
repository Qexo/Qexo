from . import hexo
from . import hugo
from . import valaxy
from . import vuepress
from . import vitepress
from . import nuxt
from . import astro

_all_configs = {
    hexo.config["name"]: hexo.config,
    hugo.config["name"]: hugo.config,
    valaxy.config["name"]: valaxy.config,
    vuepress.config["name"]: vuepress.config,
    vitepress.config["name"]: vitepress.config,
    nuxt.config["name"]: nuxt.config,
    astro.config["name"]: astro.config
}
