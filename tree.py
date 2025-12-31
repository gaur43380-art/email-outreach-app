import os

EXCLUDE = {"venv", ".venv"}
MAX_DEPTH = 2

def walk(path=".", prefix="", level=0):
    if level > MAX_DEPTH:
        return

    try:
        items = sorted(i for i in os.listdir(path) if i not in EXCLUDE)
    except PermissionError:
        return

    for i, name in enumerate(items):
        full = os.path.join(path, name)
        last = i == len(items) - 1
        print(prefix + ("└── " if last else "├── ") + name)

        if os.path.isdir(full):
            walk(full, prefix + ("    " if last else "│   "), level + 1)

print(".")
walk()
