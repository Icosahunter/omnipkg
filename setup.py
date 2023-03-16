import sys
import common as omni
from cx_Freeze import setup, Executable

base = 'Win32GUI' if sys.platform == 'win32' else None

setup(
    name=omni.app_name,
    version='0.1',
    description='A simple GUI and command-line tool wrapper around many package managers.',
    executables=[Executable('gui.py', base=base), Executable('common.py')]
)