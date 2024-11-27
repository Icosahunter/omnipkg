import re
from urllib.parse import urlsplit, urljoin
from lxml import etree
import requests
from pathlib import Path
from omnipkg import dirs
import string

class Package():

    standard_keys = [
        'id', 'pm', 'omnipkg_id', 'name', 'summary', 'description', 'remote', 'website', 'icon_url', 'icon'
    ]

    def __init__(self, data):
        self.data = data
        self.data['omnipkg_id'] = '{pm}/{id}'.format(**self.data)
        self._loaded = False

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
        if self._fill_missing_info(key):
            return self.data[key]
        return None

    def __contains__(self, key):
        if key in self.data:
            return True
        else:
            self._fill_missing_info(key)
            if key in self.data:
                return True
        return False

    def populate(self):
        for key in Package.standard_keys:
            self._fill_missing_info(key)

    def _fill_missing_info(self, key):

        self.load()
        if key in self.data:
            return self.data[key] is not None

        commands = [x for x in self.data['pm'].commands.values() if key in x.provides]
        if len(commands) > 0:
            results = commands[0](id=self.data['id'])
            if len(results) > 0:
                self.data.update(results[0])
                if 'website' in results[0]:
                    self.data['website'] = self._get_redirected_website(self.data['website'])
                if key in self.data:
                    return True

        if key == 'name':
            self._id_to_name()
        if key == 'description' and self._fill_missing_info('summary'):
            self.data['description'] = self.data['summary']
        if key == 'website':
            self._id_to_website()
        #if key == 'category' and self._fill_missing_info('description'):
        #    self._description_to_category()
        if key == 'icon_url' and self._fill_missing_info('website') and self._fill_missing_info('name'):
            self._website_to_icon_url()
        if key == 'icon':
            if self._fill_missing_info('icon_url'):
                self.data['icon'] = self.data['pm'].omnipkg.icon_cache.get_icon(self)
            #elif self._fill_missing_info('category'):
            #    self._category_to_icon()

        if key in self.data and key is not None:
            return True
        else:
            self.data[key] = None
            return False

    def save(self):
        self.data['pm'].omnipkg.pkg_cache.save_package(self.data['omnipkg_id'], self.data)

    def load(self):
        if not self._loaded and self.data['omnipkg_id'] in self.data['pm'].omnipkg.pkg_cache:
            loaded_data = {k:v for k,v in self.data['pm'].omnipkg.pkg_cache.load_package(self.data['omnipkg_id']).items() if k != 'pm'}
            loaded_data.update(**self.data)
            self.data = loaded_data
            self._loaded = True

    def _description_to_category(self):
        desc_words = self.data['description'].lower().translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))).split()
        categories = {}
        category_reasons = {}

        for category in self.data['pm'].omnipkg.config['categories'].keys():
            categories[category] = 0
            category_reasons[category] = ''
            keywords = self.data['pm'].omnipkg.config['categories'][category]['keywords']
            found_keywords = []
            for i in range(len(keywords)):
                if keywords[i] in desc_words:
                    key_weight = (len(keywords) - i)/len(keywords)
                    categories[category] += 0.25+key_weight #desc_words.count(keywords[i])*key_weight
                    found_keywords.append(keywords[i])
            category_reasons[category] = ', '.join(found_keywords)

        if len(categories) > 0:
            cat_names = list(categories.keys())
            cat_names.sort(key = lambda x: categories[x])
            print(cat_names[-1])
            self.data['category_reason'] = category_reasons[cat_names[-1]]
            self.data['category'] = cat_names[-1]

    def _category_to_icon(self):
        icon_file = self.data['pm'].omnipkg.config['categories'][self.data['category']]['icon']
        if Path(icon_file).exists():
            self.data['icon'] = icon_file
        elif (dirs.installed_dir / 'data/category_icons' / icon_file).exists():
            self.data['icon'] = dirs.installed_dir / 'data/category_icons' / icon_file

    def _website_to_icon_url(self):
        spliturl = urlsplit(self.data['website'])
        icon_url = None
        if spliturl.netloc == 'github.com' and spliturl.path != '/':
            icon_url =  self._get_icon_from_github_page(self.data['website'])
        else:
            icon_url = self._get_favicon(self.data['website'])
        if icon_url is not None:
            self.data['icon_url'] = icon_url

    def _get_favicon(self, website):
        try:
            html = requests.get(self.data['website'], allow_redirects=True, timeout=self.data['pm'].omnipkg.config['requests_timeout']).text
            tree = etree.fromstring(html, etree.HTMLParser())
            icon_url = tree.xpath('//link[contains(@rel, "icon")]/@href')[0]
            return self._fix_relative_url(self.data['website'], icon_url)
        except:
            pass
        try:
            icon_url = website + '/favicon.ico'
            if self._url_is_valid(icon_url):
                return icon_url
        except:
            pass
        try:
            spliturl = urlsplit(website)
            icon_url = spliturl.scheme + '://' + spliturl.netloc + '/favicon.ico'
            if self._url_is_valid(icon_url):
                return icon_url
        except:
            pass
        return None

    def _get_icon_from_github_page(self, repo_url):
        url_path = urlsplit(repo_url).path
        # name_keywords = '|'.join(self.data['name'].lower().split(' '))
        url_regex = r'(?:\"|\'|\()(\S*\.\S*)(?:\"|\'|\))'
        extensions = ['png', 'jpg', 'jpeg', 'ico']
        positive_keywords = [*self.data['name'].lower().split(), 'icon', 'logo']
        negative_keywords = ['shields', 'backer', 'badge', 'indicator', 'status', 'build', 'screenshot', 'coverage', 'circleci', 'travis-ci']

        # readme_re = f'(?:\\"|\'|\\()((?!.*(shields|backer|badge|indicator|status|build|screenshot|coverage|circleci|travis-ci).*)(\\w|[/\\.:-~])*/\\S*(icon|logo|{name_keywords})\\S*\\.(png|jpg|svg|ico))'
        try:
            for branch in ['master', 'main']:
                readme_url = f'https://github.com{url_path}/raw/{branch}/README.md'
                response = requests.get(readme_url, allow_redirects=True, timeout=self.data['pm'].omnipkg.config['requests_timeout'])

                if response.status_code < 400:
                    urls = re.compile(url_regex, re.IGNORECASE).findall(response.text)
                    for url in urls:
                        if any(x in url for x in positive_keywords) and not any(x in url for x in negative_keywords) and any(url.endswith(x) for x in extensions):
                            url = self._fix_relative_url(f'https://github.com{url_path}/raw/{branch}/', url)
                            return url
        except:
            return None

        # html = requests.get(self.data['website'], allow_redirects=True).text
        # tree = etree.fromstring(html, etree.HTMLParser())
        # with open('./test.html', 'w+') as f:
        #     f.write(html)
        # icon_url = tree.xpath('//*[@id="repo-title-component"]')[0]

    def _id_to_website(self):
        if self._id_is_rev_dns():
            spliturl = self.data['id'].split('.')
            spliturl.reverse()
            url = 'https://' + '.'.join(spliturl)
            while not self._url_is_valid(url) and len(spliturl) > 2:
                spliturl.pop(0)
                url = 'https://' + '.'.join(spliturl)
            if self._url_is_valid(url) and url != 'https://github.io':
                print(url)
                self.data['website'] = self._get_redirected_website(url)

    def _id_is_rev_dns(self):
        return self.data['pm'].rev_dns or (self.data['id'].count('.') >= 2 and len(self.data['id'].split('.')[0]) in [2, 3])

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

        self.data['name'] = name

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

    def _url_is_valid(self, url):
        try:
            return requests.get(url, timeout=self.data['pm'].omnipkg.config['requests_timeout']).status_code < 400
        except:
            return False

    def _get_redirected_website(self, url):
        try:
            response = requests.get(url, timeout=self.data['pm'].omnipkg.config['requests_timeout'])
            if response.status_code < 400:
                return response.url
        except:
            pass

        return url
