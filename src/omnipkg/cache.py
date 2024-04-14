import json
from pathlib import Path

class ObjectCache:
    def __init__(self, file):
        self.file = Path(file)
        self.cache = {}
        print(self.file)
        if not self.file.exists():
            print('hello!')
            with open(self.file, 'w+') as f:
                json.dump(self.cache, f, indent=4)
        else:
            with open(self.file, 'r') as f:
                self.cache = json.load(f)
    
    def __getitem__(self, key):
        data = None
        if key in self.cache:
            return self.cache[key]
        return data
    
    def __setitem__(self, key, value):
        self.cache[key] = value
        with open(self.file, 'w+') as f:
            json.dump(self.cache, f, indent=4)
    
    def __contains__(self, key):
        return key in self.cache

class FileCache:
    def __init__(self, dir, binary=False):
        self.dir = Path(dir)
        self.dir.mkdir(exist_ok=True)
        self.binary = binary
    
    def __getitem__(self, key):
        file = self.dir / key
        if file.exists():
            return file
        else:
            return None
    
    def __setitem__(self, key):
        mode = 'wb+' if self.binary else 'w+'
        with open(self.dir / key, mode) as f:
            f.write(data)
    
    def __contains__(self, key):
        return (self.dir / key).exists()