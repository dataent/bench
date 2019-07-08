import click
import os, sys, logging, json, pwd, subprocess
from bench.utils import is_root, PatchError, drop_privileges, get_env_cmd, get_cmd_output, get_dataent
from bench.app import get_apps
from bench.config.common_site_config import get_config
from bench.commands import bench_command

logger = logging.getLogger('bench')
from_command_line = False

def cli():
	global from_command_line
	from_command_line = True

	check_uid()
	change_dir()
	change_uid()

	if len(sys.argv) > 2 and sys.argv[1] == "dataent":
		return old_dataent_cli()

	elif len(sys.argv) > 1 and sys.argv[1] in get_dataent_commands():
		return dataent_cmd()

	elif len(sys.argv) > 1 and sys.argv[1] in ("--site", "--verbose", "--force", "--profile"):
		return dataent_cmd()

	elif len(sys.argv) > 1 and sys.argv[1]=="--help":
		print(click.Context(bench_command).get_help())
		print()
		print(get_dataent_help())
		return

	elif len(sys.argv) > 1 and sys.argv[1] in get_apps():
		return app_cmd()

	else:
		try:
			# NOTE: this is the main bench command
			bench_command()
		except PatchError:
			sys.exit(1)

def check_uid():
	if cmd_requires_root() and not is_root():
		print('superuser privileges required for this command')
		sys.exit(1)

def cmd_requires_root():
	if len(sys.argv) > 2 and sys.argv[2] in ('production', 'sudoers', 'lets-encrypt', 'fonts',
		'print', 'firewall', 'ssh-port', 'role', 'fail2ban', 'wildcard-ssl'):
		return True
	if len(sys.argv) >= 2 and sys.argv[1] in ('patch', 'renew-lets-encrypt', 'disable-production',
		'install'):
		return True

def change_dir():
	if os.path.exists('config.json') or "init" in sys.argv:
		return
	dir_path_file = '/etc/dataent_bench_dir'
	if os.path.exists(dir_path_file):
		with open(dir_path_file) as f:
			dir_path = f.read().strip()
		if os.path.exists(dir_path):
			os.chdir(dir_path)

def change_uid():
	if is_root() and not cmd_requires_root():
		dataent_user = get_config(".").get('dataent_user')
		if dataent_user:
			drop_privileges(uid_name=dataent_user, gid_name=dataent_user)
			os.environ['HOME'] = pwd.getpwnam(dataent_user).pw_dir
		else:
			print('You should not run this command as root')
			sys.exit(1)

def old_dataent_cli(bench_path='.'):
	f = get_dataent(bench_path=bench_path)
	os.chdir(os.path.join(bench_path, 'sites'))
	os.execv(f, [f] + sys.argv[2:])

def app_cmd(bench_path='.'):
	f = get_env_cmd('python', bench_path=bench_path)
	os.chdir(os.path.join(bench_path, 'sites'))
	os.execv(f, [f] + ['-m', 'dataent.utils.bench_helper'] + sys.argv[1:])

def dataent_cmd(bench_path='.'):
	f = get_env_cmd('python', bench_path=bench_path)
	os.chdir(os.path.join(bench_path, 'sites'))
	os.execv(f, [f] + ['-m', 'dataent.utils.bench_helper', 'dataent'] + sys.argv[1:])

def get_dataent_commands(bench_path='.'):
	python = get_env_cmd('python', bench_path=bench_path)
	sites_path = os.path.join(bench_path, 'sites')
	if not os.path.exists(sites_path):
		return []
	try:
		output = get_cmd_output("{python} -m dataent.utils.bench_helper get-dataent-commands".format(python=python), cwd=sites_path)
		# output = output.decode('utf-8')
		return json.loads(output)
	except subprocess.CalledProcessError as e:
		if hasattr(e, "stderr"):
			print(e.stderr.decode('utf-8'))
		return []

def get_dataent_help(bench_path='.'):
	python = get_env_cmd('python', bench_path=bench_path)
	sites_path = os.path.join(bench_path, 'sites')
	if not os.path.exists(sites_path):
		return []
	try:
		out = get_cmd_output("{python} -m dataent.utils.bench_helper get-dataent-help".format(python=python), cwd=sites_path)
		return "Framework commands:\n" + out.split('Commands:')[1]
	except subprocess.CalledProcessError:
		return ""