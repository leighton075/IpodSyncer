import os
import sys
sys.stdout.reconfigure(encoding='utf-8')


IPOD_DRIVE = r"E:\\"  

def print_tree(startpath, prefix=""):
    items = os.listdir(startpath)
    for index, item in enumerate(items):
        path = os.path.join(startpath, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item)
        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            print_tree(path, prefix + extension)

print_tree(IPOD_DRIVE)
