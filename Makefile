venv:
	python3.12 -m venv .venv
	source .venv/bin/activate && pip install Pillow lazydocs

api-reference:
	source .venv/bin/activate && python ./Keyhac/BuildScripts/generate_document.py

icon-sizes:
	source .venv/bin/activate && python ./Keyhac/BuildScripts/generate_icon_sizes.py