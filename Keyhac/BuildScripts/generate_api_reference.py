import sys
import os

# https://github.com/ml-tooling/lazydocs
from lazydocs import MarkdownGenerator

this_directory = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(this_directory, "../Python"))
sys.path.insert(0, os.path.join(this_directory, "../DocumentSource"))

generator = MarkdownGenerator()


header = """
## Keyhac API reference
---
"""

footer = """
Copyright 2024 craftware@gmail.com. All rights reserved.
"""


import keyhac

api_names = [
    "Keymap",
    "KeyTable",
    "KeyCondition",
    "FocusCondition",
    "InputContext",
    "MoveWindow",
    "LaunchApplication",
    "ThreadedAction",
    "ShowClipboardHistory",
    "ShowClipboardSnippets",
    "StartRecordingKeys",
    "StopRecordingKeys",
    "ToggleRecordingKeys",
    "PlaybackRecordedKeys",
    "ChooserAction",
    "UIElement",
    "ClipboardHistory",
    "Console",
    "Hook",
    "Clipboard",
    "Chooser",
    "getLogger",
]

lines = []

for api_name in api_names:

    print(f"Generating API reference for {api_name}")

    api_obj = getattr(keyhac, api_name)

    markdown = generator.import2md(api_obj, depth=3)

    for line in markdown.splitlines(keepends=True):
        lines.append(line)

    lines.append("\n")
    lines.append("---\n")
    lines.append("\n")

output_filename = os.path.join(this_directory, "../../docs/api_reference.md")

with open(output_filename, "w") as fd:
    fd.write(header)
    for line in lines:
        fd.write(line)
    fd.write(footer)

print(f"Wrote {os.path.abspath(output_filename)}")
