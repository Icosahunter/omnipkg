import json
import pickle
from pathlib import Path
import omnipkg.ini as ini
import tomllib
import tomli_w
import shutil

class SerDir:

    formats = [
        {'ext': ['.json'], 'load': json.load, 'dump': lambda o,f: json.dump(o, f, default=str, indent=4), 'binary': False},
        #{'ext': ['.pickle', '.pkl'], 'load': pickle.load, 'dump': pickle.dump, 'binary': True},
        {'ext': ['.ini', '.conf', ''], 'load': ini.load, 'dump': ini.dump, 'binary': False},
        {'ext': ['.toml'], 'load': tomllib.load, 'dump': tomli_w.dump, 'binary': True}
    ]
    
    def __init__(self, dir, default_ext=None):
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.default_ext = default_ext
    
    def create_file(self, path):
        path = self.dir / Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fmt = self.get_format(path)
        m = 'wb+' if fmt['binary'] else 'w+'
        with open(path, m) as f:
            fmt['dump']({}, f)

    @staticmethod
    def supported_extensions():
        supext = []
        for x in (x['ext'] for x in SerDir.formats):
            supext.extend(x)
        return supext
    
    def get_format(self, path):
        f = [x for x in self.formats if Path(path).suffix in x['ext']]
        if len(f) > 0:
            return f[0]

    def split_key(self, key):
        path_part = self.dir / key
        while not path_part.is_dir():
            path_part = path_part.parent
        
        relpath = (self.dir / key).relative_to(path_part)
        filename = ''

        if len(relpath.parts) == 1:
            filename = relpath.name
        else:
            filename = relpath.parents[-2].name

        if not (path_part / filename).is_file():
            files = [x for x in path_part.iterdir() if x.stem == filename]

            if len(files) > 0:
                filename = files[0].name
            else:
                filename = None
        
        if filename:
            path_part = (path_part / filename)

        print(str(self.dir / key))
        print(str(path_part.parent / path_part.stem))

        key_part = str((self.dir / key).relative_to(path_part.parent / path_part.stem))

        return (path_part, key_part)

    def __getitem__(self, key):
        sk = self.split_key(key)
        if sk[1] == '.' and sk[0].is_dir():
            return SerDir(sk[0])
        else:
            fmt = self.get_format(sk[0])
            mode = 'rb' if fmt['binary'] else 'r'
            val = None
            with open(sk[0], mode) as f:
                val = self._get_val(fmt['load'](f), sk[1])
            return val

    def _get_val(self, obj, key):
        if key == '.':
            return obj
        val = obj
        for k in key.split('/'):
            val = val[k]
        return val
    
    def __setitem__(self, key, value):
        sk = self.split_key(key)
        if sk is None:
            if self.default_ext is None:
                raise KeyError(key + '; No config file in key path.')
            else:
                self.create_file(key + self.default_ext)
                sk = self.split_key(key)
        fmt = self.get_format(sk[0])
        m = 'b' if fmt['binary'] else ''
        obj = {}
        with open(sk[0], 'r'+m) as f:
            obj = fmt['load'](f)
        
        self._set_val(obj, sk[1], value)
        with open(sk[0], 'w'+m) as f:
            fmt['dump'](obj, f)

    def _set_val(self, obj, key, value):
        obj2 = obj
        if key == '.':
            obj.clear()
            obj.update(value)
        else:
            splitkey = key.split('/')
            for k in splitkey[0:-1]:
                obj2 = obj[k]
            obj2[splitkey[-1]] = value
    
    def __contains__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            return False
    
    def keys(self):
        return (x.stem for x in self.dir.glob('*') if x.is_dir() or x.suffix in SerDir.supported_extensions())
    
    def values(self):
        return (self[x] for x in self.keys())
    
    def items(self):
        return zip(self.keys(), self.values())

    def __iter__(self):
        return (x.stem for x in self.dir.glob('*') if x.is_dir() or x.suffix in SerDir.supported_extensions()).__iter__()
    
    def clear(self):
        shutil.rmtree(self.dir)
        self.dir.mkdir(exist_ok=True)