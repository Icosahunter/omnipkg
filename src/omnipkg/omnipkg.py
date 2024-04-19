import appdirs
from pathlib import Path
import omnipkg.dirs as dirs
import omnipkg.icon_cache as icon_cache
from omnipkg.package_manager import PackageManager
import json
import shutil

class Omnipkg:

    def __init__(self):
        self.pms = {}
        self.icon_cache = None
    
    def init(self):
        self._create_dirs()
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
    
    def run(self, command, package=None, pm=None, **kwargs):
        results = []
        if pm is None:
            for pm in self.pms.values():
                results.extend(pm.run(command, package))
        else:
            results = self.pms[pm].run(command, package)
        return results
    
    def clear_package_indexes(self):
        for pm in self.pms.values():
            pm.pkg_cache.clear()
    
    def clear_icon_cache(self):
        icon_cache.clear()
    
    def index_packages(self):
        for pm in self.pms.values():
            pm.index_packages()