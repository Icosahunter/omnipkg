from pathlib import Path
import json
import shutil

class PackageCache:
    def __init__(self, dir):
        self.dir = Path(dir)
        self.dir.mkdir(exist_ok=True)

    def __contains__(self, omnipkg_id):
        return (self.dir / (omnipkg_id + '.json')).exists()

    def load_package(self, omnipkg_id):
        if (self.dir / (omnipkg_id + '.json')).exists():
            with open(self.dir / (omnipkg_id + '.json'), 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_package(self, omnipkg_id, data):
        (self.dir / (omnipkg_id + '.json')).parent.mkdir(exist_ok=True)
        with open(self.dir / (omnipkg_id + '.json'), 'w+') as f:
            json.dump(data, f, default=str, indent=4)

    def clear(self):
        shutil.rmtree(self.dir)
        self.dir.mkdir(exist_ok=True)
