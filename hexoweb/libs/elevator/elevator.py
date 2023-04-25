from importlib import import_module


def parse_version(version):
    if len(version.split(".")) == 3:
        return tuple(map(int, version.split(".")))
    elif len(version.split(".")) == 2:
        return tuple(map(int, version.split(".") + ["0"]))
    return None


def elevator(from_version, to_version):
    from_version = parse_version(from_version)
    to_version = parse_version(to_version)
    if from_version == to_version:
        return 0
    if from_version < to_version:
        for i in range(from_version[0], to_version[0] + 1):
            for j in range(from_version[1] if from_version[0] == to_version[0] else 0, 15):
                for k in range(from_version[2] if (from_version[0] == to_version[0]) and (from_version[1] == to_version[1]) else 0, 20):
                    try:
                        import_module(".updater.%s_%s_%s" % (i, j, k), "hexoweb.libs.elevator")
                    except:
                        pass
    return 1
