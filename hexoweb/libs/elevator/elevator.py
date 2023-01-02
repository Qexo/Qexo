import logging


def parse_version(version):
    return tuple(
        map(int, (version.split(".") if len(version.split(".")) == 3 else version.split(".") + ["0"]))) if len(
        version.split(".")) == 3 else None


def elevator(from_version, to_version):
    from_version = parse_version(from_version)
    to_version = parse_version(to_version)
    if from_version == to_version:
        return 0
    if from_version < to_version:
        for i in range(from_version[0], to_version[0] + 1):
            for j in range(from_version[1], to_version[1] + 1):
                for k in range(from_version[2], to_version[2] + 1):
                    try:
                        logging.info("Elevator: %s.%s.%s" % (i, j, k))
                        exec(f"from {i}_{j}_{k} import elevator")
                    except:
                        pass
    return
