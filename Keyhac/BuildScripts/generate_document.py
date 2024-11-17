import sys
import os

# https://github.com/ml-tooling/lazydocs
from lazydocs import MarkdownGenerator

sys.path.insert(0, os.path.abspath("./Python"))
sys.path.insert(0, os.path.abspath("./DocumentSource"))

generator = MarkdownGenerator()

import keyhac

api_names = [
    "Keymap",
    "KeyTable",
    "KeyCondition",
    "FocusCondition",
    "ThreadedAction",
    "UIElement",
    "Console",
    "Hook",
    "getLogger",
]

lines = []

for api_name in api_names:

    print(f"Generating API reference for {api_name}")

    api_obj = getattr(keyhac, api_name)

    markdown = generator.import2md(api_obj)

    for line in markdown.splitlines(keepends=True):
        lines.append(line)

    lines.append("\n")
    lines.append("---\n")
    lines.append("\n")

output_filename = "../docs/api_reference.md"

with open(output_filename, "w") as fd:
    for line in lines:
        fd.write(line)

print(f"Wrote {os.path.abspath(output_filename)}")