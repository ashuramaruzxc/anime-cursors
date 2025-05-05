import json
import os
import shutil
import sys
from glob import glob

root_dir = "CursorConverter/Assets/win"
all_dirs = glob(root_dir + "/**/*", recursive=True)

print(all_dirs)
final_dict = {}
for directory in all_dirs:
    if os.path.isdir(directory) and len(glob(directory + "/*.ani")) and not directory.endswith("アニメーション"):
        print(directory)
        print("root_name", directory.split("CursorConverter/Assets/win/")[-1].split("/")[0])
        print("directory in root:", directory.split("/")[-1])

        root_name = directory.split("CursorConverter/Assets/win/")[-1].split("/")[0]
        directory_name = directory.split("/")[-1]
        if root_name not in final_dict:
            final_dict[root_name] = {}
        final_dict[root_name][directory_name] = {
            "path": directory.rsplit("/", 1)[0],
            "name": directory_name,
            "en_name": "example",
            "character_name": "example",  # usually will be directory name
            "en_character_name": "example",
            "short_character_name": "example",
        }

with open("output.json", "wb") as f:
    f.write(json.dumps(final_dict, ensure_ascii=False, indent=1).encode("utf8"))
