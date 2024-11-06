from pathlib import Path
import requests
import hashlib
import shutil

class IconCache:
    def __init__(self, dir):
        self.dir = Path(dir)
        self.dir.mkdir(exist_ok=True)

    def clear(self):
        for file in self.dir.glob('*'):
            file.unlink(file)

    def get_icon(self, package):
        if 'icon_url' in package and package['icon_url'] is not None:
            icon_file = self.md5(package['icon_url'])
            if not (self.dir / icon_file).exists():
                try:
                    img_data = requests.get(package['icon_url'], timeout=2).content
                    with open(self.dir / icon_file, 'wb+') as f:
                        f.write(img_data)
                except:
                    return None
            return self.dir / icon_file
        return None

    def md5(self, data):
        md5 = hashlib.md5()
        md5.update(data.encode('utf-8'))
        return md5.hexdigest()
