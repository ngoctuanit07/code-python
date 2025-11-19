import importlib

modules = ["tests.test_units", "tests.test_cli_units"]

for name in modules:
    m = importlib.import_module(name)
    importlib.reload(m)
    for attr in dir(m):
        if attr.startswith("test_"):
            print("Running", name + "." + attr)
            getattr(m, attr)()

print("ALL OK")
