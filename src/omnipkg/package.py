import re
from urllib.parse import urlsplit, urljoin
from lxml import etree
import requests

class Package():

    def __init__(self, data):
        self.data = data
        if 'remote' not in self.data:
            self._get_remote()
        self.data['omnipkg_id'] = '{pm}/{remote}/{id}'.format(**self.data)

    def update(self, data):
        self.data.update(data)
    
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
    
    def _get_remote(self):
        if 'remote' in self.data['pm'].commands['info'].provides:
            info = self.data['pm'].commands['info'](package=self.data['id'])
            if len(info) > 0: 
                self.data.update(info[0])
        if 'remote' not in self.data:
            if len(self.data['pm'].remotes) == 1:
                self.data['remote'] = self.data['pm'].remotes[0]
        if 'remote' not in self.data:
            self.data['remote'] = 'default'
    
    def _fill_missing_info(self):
        if self.data['omnipkg_id'] in self.data['pm'].omnipkg.pkg_cache:
            self.data.update(**{k:v for k,v in self.data['pm'].omnipkg.pkg_cache[self.data['omnipkg_id']].items() if k != 'pm'})
        else:
            info = self.data['pm'].commands['info'](package=self.data['id'])
            if len(info) > 0: 
                self.data.update(info[0])
            if not 'name' in self.data:
                self.data['name'] = self._id_to_name()
            if not 'website' in self.data and self._id_is_rev_dns():
                self.data['website'] = self._id_to_url()
            if 'website' in self.data:
                self.data['website'] = self._get_redirected_website()
            if not 'icon_url' in self.data and 'website' in self.data:
                icon_url = self._website_to_icon_url()
                if icon_url is not None:
                    self.data['icon_url'] = icon_url
            if not 'icon' in self.data and 'icon_url' in self.data:
                self.data['icon'] = self.data['pm'].omnipkg.icon_cache.get_icon(self)
            if not 'description' in self.data and 'summary' in self.data:
                self.data['description'] = self.data['summary']
        self.data['pm'].omnipkg.pkg_cache[self.data['omnipkg_id']] = self.data

    def _get_redirected_website(self):
        try:
            response = requests.get(self.data['website'], timeout=self.data['pm'].omnipkg.config['requests_timeout'])
            if response.status_code < 400:
                return response.url
        except:
            pass

        return self.data['website']

    def _website_to_icon_url(self):

        spliturl = urlsplit(self.data['website'])
        if spliturl.netloc == 'github.com' and spliturl.path != '/':
            return self._icon_url_from_github()

        try:
            icon_url = self.data['website'] + '/favicon.ico'
            if self._url_is_valid(icon_url):
                return icon_url
        except:
            pass
        
        try:
            html = requests.get(self.data['website'], allow_redirects=True, timeout=self.data['pm'].omnipkg.config['requests_timeout']).text
            tree = etree.fromstring(html, etree.HTMLParser())
            icon_url = tree.xpath('//link[contains(@rel, "icon")]/@href')[0]
            return self._fix_relative_url(self.data['website'], icon_url)
        except:
            pass
        
        return None
    
    def _fix_relative_url(self, base_url, relative_url):
        spliturl = urlsplit(base_url)
        url = relative_url
        if not url.startswith('http'):
            netloc = spliturl.netloc
            if netloc.startswith('www.'):
                netloc = netloc[4:]
            
            url = urljoin('https://' + netloc + spliturl.path, url)
            return url
        else:
            return url
    
    def _id_is_rev_dns(self):
        return self.data['pm'].rev_dns or (self.data['id'].count('.') >= 2 and len(self.data['id'].split('.')[0]) in [2, 3])

    def _id_to_url(self):
        spliturl = self.data['id'].split('.')
        spliturl.reverse()
        url = 'https://' + '.'.join(spliturl)
        while not self._url_is_valid(url) and len(spliturl) > 2:
            spliturl.pop(0)
            url = 'https://' + '.'.join(spliturl[-2:])
        return url
    
    def _icon_url_from_github(self):
        url_path = urlsplit(self.data['website']).path
        name_keywords = '|'.join(self.data['name'].lower().split(' '))
        readme_re = f'(?:"|\'|\()((?!.*(shields|backer|badge|indicator|status|build|screenshot).*)(\w|[/\.:-~])*/\S*(icon|logo|{name_keywords})\S*\.(png|jpg|svg|ico))'
        try:
            for branch in ['master', 'main']:
                readme_url = f'https://github.com{url_path}/raw/{branch}/README.md'
                response = requests.get(readme_url, allow_redirects=True, timeout=self.data['pm'].omnipkg.config['requests_timeout'])
                if response.status_code < 400:
                    icon_url = re.compile(readme_re, re.IGNORECASE).search(response.text).group(1)
                    icon_url = self._fix_relative_url(f'https://github.com{url_path}/raw/{branch}/', icon_url)
                    return icon_url
        except:
            pass
        
        #html = requests.get(self.data['website'], allow_redirects=True).text
        #tree = etree.fromstring(html, etree.HTMLParser())
        #with open('./test.html', 'w+') as f:
        #    f.write(html)
        #icon_url = tree.xpath('//*[@id="repo-title-component"]')[0]

        return None
    
    def _url_is_valid(self, url):
        try:
            return requests.get(url, timeout=self.data['pm'].omnipkg.config['requests_timeout']).status_code < 400
        except:
            return False
    
    def _id_to_name(self):

        name = self.data['id']
        
        if self.data['pm'].rev_dns:
            name = name.split('.')[-1]
        else:
            if '-' in self.data['id']:
                name = name.replace('-', ' ')
            elif '_' in self.data['id']:
                name = name.replace('_', ' ')
            elif '.' in self.data['id']:
                name = name.replace('.', ' ')
            name = name.title()

        return name