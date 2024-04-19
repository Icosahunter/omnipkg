setup:
    #!/usr/bin/env sh
    python3 -m venv venv 
    source venv/bin/activate
    python3 -m pip install -r requirements.txt

build: setup
    #!/usr/bin/env sh
    source venv/bin/activate
    pyside6-uic ./src/omnipkg/mainwindow.ui -o ./src/omnipkg/ui_mainwindow.py
    rm -r -f dist
    python3 -m build

install: build
    python3 -m pip install --force-reinstall ./dist/*.whl

run:
    #!/usr/bin/env sh
    source venv/bin/activate
    cd src
    python3 -m omnipkg.gui