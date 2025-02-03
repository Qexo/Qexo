from . import gitHub
from . import gitLab
from . import gitEa
from . import local

_all_providers = {
    gitHub.Github.name: gitHub.Github,
    gitLab.Gitlab.name: gitLab.Gitlab,
    gitEa.GitEa.name: gitEa.GitEa,
    local.Local.name: local.Local
}
