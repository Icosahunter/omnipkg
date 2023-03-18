import appdirs
from setuptools import setup

setup(
    data_files=[
        (appdirs.user_config_dir('omnipkg', 'Nathaniel Markham'), 
        [
            'data/pm-defs/eopkg.json',
            'data/pm-defs/flatpak.json',
            'data/pm-defs/pacman.json'
        ])
    ]
)