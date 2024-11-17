import sys
import os

# https://github.com/ml-tooling/lazydocs
from lazydocs import MarkdownGenerator

sys.path.insert(0, os.path.abspath("./Python"))
sys.path.insert(0, os.path.abspath("./DocumentSource"))

generator = MarkdownGenerator()

import keyhac

markdown_sections = []

for api_name in dir(keyhac):

    if api_name.startswith("_"):
        continue

    api_obj = getattr(keyhac, api_name)

    print(api_obj)

    markdown = generator.import2md(api_obj)
    markdown_sections.append(markdown)

markdown_joint = "\n".join(markdown_sections)

with open("../docs/api_reference.md", "w") as fd:
    fd.write(markdown_joint)