import json
import pickle
from pathlib import Path
import omnipkg.ini as ini
import tomllib

class SerDir:

    formats = [
        {'ext': ['.json'], '.load': json.load, 'dump': json.dump, 'binary': False},
        {'ext': ['.pickle', '.pkl'], 'load': pickle.load, 'dump': pickle.dump, 'binary': True},
        {'ext': ['.ini', '.conf', ''], 'load': ini.load, 'dump': ini.dump, 'binary': False},
        {'ext': ['.toml'], '.load': tomllib.load, 'dump': tomllib.dump, 'binary': False}
    ]
    
    def __init__(self, dir):
        self.dir = Path(dir)
        self.dir.mkdir(exist_ok=True)
    
    def get_format(path):
        f = [x for x in formats if Path(path).suffix in x['ext']]
        if len(f) > 0:
            return f[0]

    def split_key(key):
        path_part = self.dir / key
        while not path_part.exists():
            path_part = path_part.parent
        if path_part.isdir():
            return None
        key_part = (self.dir / key).relative_to(path_part)
        return (str(path_part.absolute()), str(key_part))
 
    def __getitem__(self, key):
        sk = split_key(key)
        if sk is None:
            raise KeyError(key)
        fmt = get_format(sk[0])
        mode = 'rb' if fmt['binary'] else 'r'
        val = None
        with open(sk[0], mode) as f:
            val = _get_val(fmt['load'](f), key)
        return val

    def _get_val(obj, key):
        val = obj
        for k in key.split('/'):
            val = val[k]
        return val
    
    def __setitem__(self, key, value):
        sk = split_key(key)
        if sk is None:
            raise KeyError(key)
        fmt = get_format(sk[0])
        m = 'b' if fmt['binary'] else ''
        obj = {}
        with open(sk[0], 'r'+m) as f:
            obj = fmt['load'](f)
        _set_val(obj, key, value)
        with open(sk[0], 'w'+m) as f:
            fmt['dump'](obj, f)
        return val

    def _set_val(obj, key, value):
        obj2 = obj
        splitkey = key.split('/')
        for k in splitkey[0:-1]:
            obj2 = obj[k]
        obj2[splitkey[-1]] = value