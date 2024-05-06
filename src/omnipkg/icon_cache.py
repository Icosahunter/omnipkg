from pathlib import Path
import requests
import hashlib

class IconCache:
    def __init__(self, dir):
        self.dir = Path(dir)
        self.dir.mkdir(exist_ok=True)
    
    def clear(self):
        for file in glob.glob(str(self.dir) + '/*'):
            os.remove(file)
    
    def get_icon(self, package):
        if 'icon_url' in package:
            icon_file = self.sha1(package['icon_url'])
            if not (self.dir / icon_file).exists():
                try:
                    img_data = requests.get(package['icon_url'], timeout=2).content
                    with open(self.dir / icon_file, 'wb+') as f:
                        f.write(img_data)
                except:
                    return None
            return self.dir / icon_file
        return None

    def sha1(self, data):
        sha1 = hashlib.sha1()
        sha1.update(data.encode('ascii'))
        return sha1.hexdigest()