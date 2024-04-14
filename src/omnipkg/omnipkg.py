import appdirs
from pathlib import Path
import omnipkg.dirs as dirs
from omnipkg.package_manager import PackageManager
from omnipkg.cache import FileCache
import requests
import json
import shutil
import base64

class Omnipkg:

    def __init__(self):
        self.pms = {}
        self.icon_cache = None
    
    def init(self):
        self._create_dirs()
        self.icon_cache = FileCache(dirs.icon_cache_dir, binary=True)
        self._load_pms()
    
    def _create_dirs(self):
        dirs.data_dir.mkdir(exist_ok=True)
        dirs.config_dir.mkdir(exist_ok=True)
        dirs.cache_dir.mkdir(exist_ok=True)
        dirs.pm_defs_dir.mkdir(exist_ok=True)
        dirs.icon_cache_dir.mkdir(exist_ok=True)
    
    def _load_pms(self):
        for path in dirs.pm_defs_dir.glob('*'):
            with open(path) as f:
                pm_def = json.load(f)
                if shutil.which(pm_def['name']):
                    self.pms[pm_def['name']] = (PackageManager(pm_def))

        for path in (dirs.installed_dir / 'data/pm-defs').glob('*'):
            with open(path) as f:
                pm_def = json.load(f)
                if not pm_def['name'] in self.pms:
                    if shutil.which(pm_def['name']):
                        self.pms[pm_def['name']] = (PackageManager(pm_def))
    
    def run(self, command, package=None, pm=None):
        results = []
        if pm is None:
            for pm in self.pms.values():
                results.extend(pm.run(command, package))
        else:
            results = self.pms[pm].run(command, package)
        return results
    
    def get_icon(self, package):
        if 'icon_url' in package:
            icon_file = base64.b64encode(package['icon_url'].encode('ascii')).decode('ascii')
            if not icon_file in self.icon_cache:
                img_data = requests.get(package['icon_url']).content
                self.icon_cache[icon_file] = img_data
            return self.icon_cache.dir / icon_file
        return None