venv:
	python3.13 -m venv .venv
	source .venv/bin/activate && pip install Pillow lazydocs

api-reference:
	source .venv/bin/activate && python ./Keyhac/BuildScripts/generate_api_reference.py

icon-sizes:
	source .venv/bin/activate && python ./Keyhac/BuildScripts/generate_icon_sizes.py