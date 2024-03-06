build:
    rm -r -f dist
    pyside6-uic ./src/omnipkg/mainwindow.ui -o ./src/omnipkg/ui_mainwindow.py
    python3 -m build

install: build
    python3 -m pip install --force-reinstall ./dist/*.whl

run:
    python3 -m src/omnipkg/gui.py