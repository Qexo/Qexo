from . import gitHub
from . import local

_all_providers = {
    gitHub.Github.name: gitHub.Github,
    local.Local.name: local.Local
}
