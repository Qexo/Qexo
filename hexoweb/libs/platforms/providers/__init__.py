from . import gitHub
from . import gitLab
from . import local

_all_providers = {
    gitHub.Github.name: gitHub.Github,
    gitLab.Gitlab.name: gitLab.Gitlab,
    local.Local.name: local.Local
}
