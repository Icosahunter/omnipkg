import appdirs
from pathlib import Path
import omnipkg.dirs as dirs
from omnipkg.icon_cache import IconCache
from omnipkg.package_cache import PackageCache
from omnipkg.package_manager import PackageManager
import json
import tomllib
import shutil
import requests_cache

class Omnipkg:

    def __init__(self):
        self.pms = {}
        self.config = {}
        self.package_details_template = ''
        self.pkg_cache = PackageCache(dirs.pkg_cache_dir)
        self.icon_cache = IconCache(dirs.icon_cache_dir)

    def init(self):
        self._create_dirs()
        self._load_config()
        self._load_categories()
        self._load_package_details_template()
        self._load_pms()
        requests_cache.install_cache(dirs.cache_dir / 'requests_cache.sqlite')

    def _create_dirs(self):
        dirs.data_dir.mkdir(exist_ok=True)
        dirs.config_dir.mkdir(exist_ok=True)
        dirs.cache_dir.mkdir(exist_ok=True)
        dirs.pm_defs_dir.mkdir(exist_ok=True)
        dirs.icon_cache_dir.mkdir(exist_ok=True)

    def _load_package_details_template(self):
        if not (dirs.config_dir / 'package-details-template.md').exists():
            self.reset_package_details_template()
        with open(dirs.config_dir / 'package-details-template.md', 'r') as f:
            self.package_details_template = f.read()

    def _load_config(self):
        if not (dirs.config_dir / 'config.toml').exists():
            self.reset_config()
        with open(dirs.config_dir / 'config.toml', 'rb') as f:
            self.config = tomllib.load(f)

    def _load_categories(self):
        if not (dirs.config_dir / 'categories.toml').exists():
            self.reset_categories()
        with open(dirs.config_dir / 'categories.toml', 'rb') as f:
            self.config['categories'] = tomllib.load(f)

    def _load_pms(self):
        if len(list(dirs.pm_defs_dir.glob('*.toml'))) == 0:
            self.reset_pm_defs()
        for path in dirs.pm_defs_dir.glob('*.toml'):
            with open(path, 'rb') as f:
                pm_def = tomllib.load(f)
                if shutil.which(pm_def['name']):
                    self.pms[pm_def['name']] = (PackageManager(pm_def, self))

    def reset_pm_defs(self):
        for path in (dirs.installed_dir / 'data/pm-defs').glob('*.toml'):
            shutil.copy(path, dirs.pm_defs_dir / path.name)

    def reset_config(self):
        shutil.copy(dirs.installed_dir / 'data/config.toml', dirs.config_dir / 'config.toml')

    def reset_categories(self):
        shutil.copy(dirs.installed_dir / 'data/categories.toml', dirs.config_dir / 'categories.toml')

    def reset_package_details_template(self):
        shutil.copy(dirs.installed_dir / 'data/package-details-template.md', dirs.config_dir / 'package-details-template.md')

    def reset_all_config(self):
        self.reset_pm_defs()
        self.reset_config()
        self.reset_categories()
        self.reset_package_details_template()

    def run(self, command, package=None, pm=None, **kwargs):
        results = []
        if pm is None:
            for pm in self.pms.values():
                results.extend(pm.run(command, package))
        else:
            results = self.pms[str(pm)].run(command, package)
        return results

    def index_packages(self):
        for pm in self.pms.values():
            pm.index_packages()
