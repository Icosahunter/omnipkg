from configparser import ConfigParser

def load(file):
    parser = ConfigParser()
    parser.read_file(file)
    obj = {}
    obj = _create_sections(obj, [x.split('.') for x in parser.keys()])
    for section in parser.keys():
        for key in parser[section].keys():
            _set_value(obj, section, key, parser[section][key])
    return obj

def dump(obj, file):
    parser = ConfigParser()
    parser.read_dict(_flatten_dict(obj))
    parser.write(file)

def _flatten_dict(obj):
    subdict_keys = [x for x in obj.keys() if isinstance(obj[x], dict)]
    val_keys = [x for x in obj.keys() if x not in subdict_keys]
    flat = {'DEFAULT': {}}
    for key in val_keys:
        flat['DEFAULT'][key] = obj[key]
    for key in subdict_keys:
        flatsub = _flatten_dict(obj[key])
        flat[key] = flatsub['DEFAULT']
        for subkey in flatsub.keys():
            if subkey != 'DEFAULT':
                flat[key + '.' + subkey] = flatsub[subkey]
    return flat

def _set_value(obj, section, key, value):
    o = obj
    for s in section.split('.'):
        o = o[s]
    o[key] = _cast_data(value)

def _create_sections(obj, keys):
    first_level_keys = list(set([x[0] for x in keys]))
    for key in first_level_keys:
        second_level_keys = [x[1:] for x in keys if x[0]==key and len(x) > 1]
        if len(second_level_keys) > 0:
            obj[key] = _create_sections({}, second_level_keys)
        else:
            obj[key] = {}
    return obj

def _cast_data(data):
    if data.lower() in ['true', 'yes', '1']:
        return True
    if data.lower() in ['false', 'no', '0']:
        return False
    try:
        return int(data)
    except:
        pass
    try:
        return float(data)
    except:
        pass
    return data