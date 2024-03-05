build:
    rm -r dist
    python3 -m build

install: build
    python3 -m pip install --force-reinstall ./dist/*.whl

run:
    python3 -m src/omnipkg/gui.py