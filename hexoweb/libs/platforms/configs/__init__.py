from . import hexo
from . import hugo
from . import valaxy

_all_configs = {
    hexo.config["name"]: hexo.config,
    hugo.config["name"]: hugo.config,
    valaxy.config["name"]: valaxy.config
}
