



def get_icon(package):
    if 'icon_url' in package:
        icon_file = sha256(package['icon_url'])
        if not icon_file in cache:
            try:
                img_data = requests.get(package['icon_url'], timeout=2).content
                cache[icon_file] = img_data
            except:
                return None
        return cache.dir / icon_file
    return None