import json

from kleeneup import Symbol

load = json.load


def dump(obj, f):
    return json.dump(obj, f, default=default, indent=2, sort_keys=True)


def default(obj):
    if isinstance(obj, Symbol):
        return obj.value

    if isinstance(obj, set):
        return list(obj)

    raise TypeError
