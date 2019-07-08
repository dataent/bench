from jinja2 import Environment, PackageLoader

__version__ = "4.1.0"

env = Environment(loader=PackageLoader('bench.config'))

DATAENT_VERSION = None

def set_dataent_version(bench_path='.'):
	from .app import get_current_dataent_version
	global DATAENT_VERSION
	if not DATAENT_VERSION:
		DATAENT_VERSION = get_current_dataent_version(bench_path=bench_path)