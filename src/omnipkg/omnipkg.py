import appdirs
from pathlib import Path
import omnipkg.dirs as dirs
from omnipkg.icon_cache import IconCache
from omnipkg.serdir import SerDir
from omnipkg.package_manager import PackageManager
import json
import shutil
import requests_cache

class Omnipkg:

    def __init__(self):
        self.pms = {}
        self.config = {
            'requests_timeout': 0.5,
            'filter_search': True,
            'search_results_limit': 20,
            'columns': ['icon', 'name', 'id', 'pm', 'remote', 'summary'],
            'pkg_cache_format': '.json',
            'prefetch': True,
            'categories': ['Audio', 'Video', 'Development', 'Education', 'Game', 'Graphics', 'Network', 'Office', 'Utilities'],
            'category_keywords': {},
            'category_icons': {}
        }
        self.pkg_cache = SerDir(dirs.pkg_cache_dir, self.config['pkg_cache_format'])
        self.icon_cache = IconCache(dirs.icon_cache_dir)
    
    def init(self):
        self._create_dirs()
        self._load_pms()
        requests_cache.install_cache(dirs.cache_dir / 'requests_cache.sqlite')
    
    def _create_dirs(self):
        dirs.data_dir.mkdir(exist_ok=True)
        dirs.config_dir.mkdir(exist_ok=True)
        dirs.cache_dir.mkdir(exist_ok=True)
        dirs.pm_defs_dir.mkdir(exist_ok=True)
        dirs.icon_cache_dir.mkdir(exist_ok=True)
    
    def _load_pms(self):
        #for path in dirs.pm_defs_dir.glob('*'):
        #    with open(path) as f:
        #        pm_def = json.load(f)
        #        if shutil.which(pm_def['name']):
        #            self.pms[pm_def['name']] = (PackageManager(pm_def, self))

        for pm_def in SerDir(dirs.installed_dir / 'data/pm-defs').values():
            if not pm_def['name'] in self.pms:
                if shutil.which(pm_def['name']):
                    self.pms[pm_def['name']] = (PackageManager(pm_def, self))
    
    def run(self, command, package=None, pm=None, **kwargs):
        results = []
        if pm is None:
            for pm in self.pms.values():
                results.extend(pm.run(command, package))
        else:
            results = self.pms[pm].run(command, package)
        return results
    
    def index_packages(self):
        for pm in self.pms.values():
            pm.index_packages()