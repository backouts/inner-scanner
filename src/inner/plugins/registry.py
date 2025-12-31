import importlib

MODULE_PATHS = [
    "inner.plugins.web.dir_bruteforce",
]

def load_modules():
    modules = {}
    for path in MODULE_PATHS:
        m = importlib.import_module(path)
        meta = m.MODULE
        modules[meta["id"]] = m
    return modules
