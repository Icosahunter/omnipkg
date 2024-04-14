setup:
    python3 -m pip install -r requirements.txt

build: setup
    rm -r -f dist
    pyside6-uic ./src/omnipkg/mainwindow.ui -o ./src/omnipkg/ui_mainwindow.py
    python3 -m build

install: build
    python3 -m pip install --force-reinstall ./dist/*.whl

run:
    cd src
    python3 -m omnipkg.gui