from parse import parse
from omnipkg.command import Command
from omnipkg.cache import ObjectCache
import omnipkg.dirs as dirs
import omnipkg.icon_cache as icon_cache
from pathlib import Path
import requests
from lxml import etree
from urllib.parse import urlsplit
import string

class PackageManager():

    def __init__(self, pm_def):
        self.commands = {}
        self.privileged_commands = [ 'install', 'uninstall', 'update', 'update_all' ]
        for k, v in pm_def.items():
            if k=='name':
                self.name = v
            elif k=='rev-dns':
                self.rev_dns = v
            else:
                self._add_command(k, v)
        (dirs.cache_dir / self.name).mkdir(exist_ok=True)
        self.pkg_cache = ObjectCache(dirs.cache_dir / self.name / 'index.json')
        self.installed_pkgs = None
        self.updatable_pkgs = None
    
    def __str__(self):
        return self.name

    def _add_command(self, name, data):
        cmd = None
        parser = None
        privileged = name in self.privileged_commands
        if type(data) is list:
            cmd = data[0]
            parser = data[1]
        else:
            cmd = data
        self.commands[name] = Command(cmd, parser, privileged)
        #if not self.hasattr(name):
        #    self.setattr(name, self.commands[name])

    def index_packages(self):
        for query in string.ascii_letters + string.digits:
            for package in self.run('search', query):
                package._fill_missing_info()
        for package in self.run('installed'):
            package._fill_missing_info()

    def package_installed(self, id):
        if self.installed_pkgs == None:
            self.installed_pkgs = [x['id'] for x in self.commands['installed']()]
        return id in self.installed_pkgs
    
    def package_updatable(self, id):
        if self.updatable_pkgs == None:
            self.updatable_pkgs = [x['id'] for x in self.commands['updatable']()]
        return id in self.updatable_pkgs
    
    def package_exists(self, id):
        return id in [x['id'] for x in self.commands['search'](package=id)]
    
    def run(self, cmd, package):
        if cmd in ['install', 'uninstall']:
            self.installed_pkgs = None
        if cmd in ['install', 'uninstall', 'update', 'update-all']:
            self.updatable_pkgs = None
        result = self.commands[cmd](package=package)
        result = [Package(pm=self, **x) for x in result if x['id'] != 'Name']
        return result

class Package(dict):

    def __init__(self, *args, **kwargs):
        self.data = {}
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.data.update(dict(*args, **kwargs))
    
    def keys(self):
        return self.data.keys()
    
    def values(self):
        return self.data.values()
    
    def items(self):
        return self.data.items()
    
    def __str__(self):
        return self.data['id']

    def __repr__(self):
        return repr(self.data)

    def __getitem__(self, key):
        if key == 'installed':
            return self.data['pm'].package_installed(self.data['id'])
        if key == 'updatable':
            return self.data['pm'].package_updatable(self.data['id'])
        if key in self.data:
            return self.data[key]
        self._fill_missing_info()
        if key in self.data:
            return self.data[key]
        return None
    
    def __contains__(self, key):
        if key in self.data:
            return True
        else:
            self._fill_missing_info()
            if key in self.data:
                return True
        return False
    
    def _fill_missing_info(self):
        if self.data['id'] in self.data['pm'].pkg_cache:
            pm = self.data['pm']
            self.data.update(**{k:v for k,v in self.data['pm'].pkg_cache[self.data['id']].items() if k != 'pm'})
        else:
            info = self.data['pm'].commands['info'](package=self.data['id'])
            if len(info) > 0: 
                self.data.update(info[0])
            if not 'name' in self.data:
                self.data['name'] = self._id_to_name(self.data['id'])
            if not 'website' in self.data and self.data['pm'].rev_dns:
                self.data['website'] = self._id_to_url(self.data['id'])
            if not 'icon_url' in self.data and 'website' in self.data:
                icon_url = self._website_to_icon_url(self.data['website'])
                if icon_url is not None:
                    self.data['icon_url'] = icon_url
            if not 'icon' in self.data and 'icon_url' in self.data:
                self.data['icon'] = icon_cache.get_icon(self)
            if not 'description' in self.data and 'summary' in self.data:
                self.data['description'] = self.data['summary']
        self.data['pm'].pkg_cache[self.data['id']] = self.data

    def _website_to_icon_url(self, url):
        icon_url = None
        try:
            html = requests.get(url).text
            tree = etree.fromstring(html, etree.HTMLParser())
            icon_url = tree.xpath('//link[contains(@rel, "icon")]/@href')[0]
            if not icon_url.startswith('http'):
                split_url = urlsplit(url)
                netloc = split_url.netloc
                if netloc.startswith('www.'):
                    netloc = netloc[4:]
                icon_url = 'https://' + netloc + '/' + icon_url
        except:
            pass
        return icon_url

    def _id_to_url(self, id):
        url = id.split('.')
        url.reverse()
        url = 'https://' + '.'.join(url[-2:])
        return url
    
    def _id_to_name(self, id):

        name = id
        
        if self.data['pm'].rev_dns:
            name = name.split('.')[-1]
        else:
            if '-' in id:
                name = name.replace('-', ' ')
            elif '_' in id:
                name = name.replace('_', ' ')
            elif '.' in id:
                name = name.replace('.', ' ')
            name = name.title()

        return name