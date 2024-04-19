from omnipkg.cache import FileCache
import omnipkg.dirs as dirs
import requests
import base64

cache = FileCache(dirs.icon_cache_dir, binary=True)

def get_icon(package):
    if 'icon_url' in package:
        icon_file = base64.b64encode(package['icon_url'].encode('ascii')).decode('ascii')
        if not icon_file in cache:
            try:
                img_data = requests.get(package['icon_url']).content
                cache[icon_file] = img_data
            except:
                return None
        return cache.dir / icon_file
    return None