import appdirs
from pathlib import Path

app_name = 'omnipkg'
app_author = 'Nathaniel Markham'
data_dir = Path(appdirs.user_data_dir(app_name, app_author))
config_dir = Path(appdirs.user_config_dir(app_name, app_author))
cache_dir = Path(appdirs.user_cache_dir(app_name, app_author))
installed_dir = Path(__file__).parent
pm_defs_dir = config_dir / 'pm-defs'
pkg_cache_dir = cache_dir / 'index'
icon_cache_dir = cache_dir / 'icons'
