import json
from pathlib import Path
import glob
import os

class ObjectCache:
    def __init__(self, file):
        self.file = Path(file)
        self.cache = {}
        if not self.file.exists():
            self.save()
        else:
            with open(self.file, 'r') as f:
                self.cache = json.load(f)
    
    def clear(self):
        self.cache = {}
        self.save()
        print('cleared!')
        
    def save(self):
        with open(self.file, 'w+') as f:
            json.dump(self.cache, f, indent=4, default=str)

    def __getitem__(self, key):
        data = None
        if key in self.cache:
            return self.cache[key]
        return data
    
    def __setitem__(self, key, value):
        self.cache[key] = value
        self.save()
    
    def __contains__(self, key):
        return key in self.cache

class FileCache:
    def __init__(self, dir, binary=False):
        self.dir = Path(dir)
        self.dir.mkdir(exist_ok=True)
        self.binary = binary
    
    def clear():
        for file in glob.glob(self.dir / '*'):
            os.remove(file)
    
    def __getitem__(self, key):
        file = self.dir / key
        if file.exists():
            return file
        else:
            return None
    
    def __setitem__(self, key, value):
        mode = 'wb+' if self.binary else 'w+'
        with open(self.dir / key, mode) as f:
            f.write(value)
    
    def __contains__(self, key):
        return (self.dir / key).exists()