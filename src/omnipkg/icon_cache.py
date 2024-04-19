from omnipkg.cache import FileCache
import omnipkg.dirs as dirs
import requests
import hashlib

cache = FileCache(dirs.icon_cache_dir, binary=True)

def get_icon(package):
    if 'icon_url' in package:
        icon_file = sha256(package['icon_url'])
        if not icon_file in cache:
            try:
                img_data = requests.get(package['icon_url']).content
                cache[icon_file] = img_data
            except:
                return None
        return cache.dir / icon_file
    return None

def sha256(text):
    h = hashlib.sha256()
    h.update(text.encode('ascii'))
    return h.hexdigest()

def clear():
    cache.clear()