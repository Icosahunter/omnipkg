
class SerObj(dict):

    def __init__(self, data: dict = {}, template: dict = {}, compress: bool = True, strict: bool = True, callable_defaults = True):
        super().__init__()
        super().update(data)
        self.template = template
        self.compress = compress
        self.strict = strict
        self.callable_defaults = callable_defaults
        
    def __getattr__(self, key):
        if self.__contains__(key):
            return self.__getitem__(key)
        else:
            self.__getattribute__(key)
    
    def __setattr__(self, key, value):
        if not key == 'template' and self.__contains__(key):
            if not (self.compress and value == self.template[key]):
                self.__setitem__(key, value)
        else:
            super().__setattr__(key, value)
    
    def __getitem__(self, key):
        if super().__contains__(key):
            return super().__getitem__(key)
        elif key in self.template:
            if self.callable_defaults and callable(self.template[key]):
                return self.template[key]()
            else:
                return self.template[key]
        else:
            raise KeyError(f"'{key}'")
    
    def __setitem__(self, key, value):
        if key in self.template or not self.strict:
            super().__setitem__(key, value)
        else:
            raise KeyError(f"'{key}'")
    
    def __contains__(self, key):
        return super().__contains__(key) or key in self.template
    
    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
    
    def update(self, dictionary):
        if self.strict:
            super().update({k:v for k,v in dictionary.items() if k in self.template})
        else:
            super().update(dictionary)
    
    def keys(self):
        if self.compress:
            superobj = super()
            return [k for k in superobj.keys() if superobj.__getitem__(k) != self.template[k]]
        else:
            return self.template.keys()
    
    def values(self):
        superobj = super()
        if self.compress:
            return [superobj.__getitem__(k) for k in superobj.keys() if superobj.__getitem__(k) != self.template[k]]
        else:
            return [superobj.__getitem__(k) for k in self.template.keys()]
    
    def items(self):
        return zip(self.keys(), self.values())