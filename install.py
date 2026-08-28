import subprocess
import sys
import platform
from datetime import datetime

import modules.site as site
import modules.debian as debian
import modules.db as db
import modules.forum as forum
import modules.core as core
import modules.gate as gate
import modules.esb as esb
import modules.cs as cs

class colors:
    GREEN = '\033[92m'
    WHITE = '\033[97m'
    RED = '\033[91m'

def get_docker_image_command():
    if platform.system().lower() == 'windows':
        return ['docker', 'images']
    else:
        return ['docker images']

def image_exist(image_name):
    full_image_name = 'fresh/' + image_name
    result = subprocess.run(get_docker_image_command(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return full_image_name in str(result.stdout)

from components_config import COMPONENTS
for comp in COMPONENTS:
    if comp['nick'] == 'Platform85':
        platform_ver = comp['version']
    if comp['nick'] == 'AddCompPostgre':
        postgre_ver = comp['version'].split('.')[0]
    if comp['nick'] == 'EnterpriseLicenseTools':
        version_parts = comp['version'].split('.')
        if len(version_parts) >= 4:
            license_tools_ver = f"{version_parts[0]}.{version_parts[1]}.{version_parts[2]}{version_parts[3]}"
        else:
            license_tools_ver = '.'.join(version_parts)
    if comp['nick'] == 'Axiom17FullJRE':
        raw = comp['version'].replace('%2b', '+').replace('%2B', '+')
        # "17.0.17+15" -> "17.0.1715"
        if '+' in raw:
            base, suffix = raw.split('+', 1)
            axiom_jre_ver = base + suffix
        else:
            axiom_jre_ver = raw

images = []
images.append(debian.New())
images.append(site.New())
images.append(forum.New())
images.append(core.New())
images.append(db.New())
images.append(gate.New())
images.append(esb.New())
images.append(cs.New())

debug = '-debug' in sys.argv

start_time = datetime.now()
print('{}Build is starting{}'.format(colors.GREEN, colors.WHITE))

if debug:
    stdout = None
    stderr = None
else:
    stdout = subprocess.PIPE
    stderr = subprocess.PIPE

for image in images:

    print('Building', image.name, '...', end='\r')

    for command in image.commands_before:
        if debug: print(command)
        subprocess.call(' '.join(command), shell=True, stdout=stdout, stderr=stderr)

    command_to_run = [
        'docker',
        'build',
        '--platform',
        'linux/amd64',
        '-t',
        'fresh/' + image.name]
    if image.name == 'core':
        command_to_run.append('--build-arg')
        command_to_run.append('DISTR_VERSION=' + platform_ver)
        command_to_run.append('--build-arg')
        command_to_run.append('LICENSE_TOOLS_VERSION=' + license_tools_ver)
        command_to_run.append('--build-arg')
        command_to_run.append('AXIOM_JRE_VERSION=' + axiom_jre_ver)
    if image.name == 'db':
        command_to_run.append('--build-arg')
        command_to_run.append('VERSION=' + postgre_ver)
    command_to_run.append('-f')
    command_to_run.append('images/' + image.name + '/Dockerfile')
    command_to_run.append('.')


    result = subprocess.run(command_to_run, stdout=stdout, stderr=stderr)

    if result.returncode != 0 or not image_exist(image.name):
        print('Building', image.name , '...', '{}error'.format(colors.RED), colors.WHITE)
        exit(1)

    for command in image.commands_after:
        if debug: print(command)
        subprocess.call(' '.join(command), shell=True, stdout=stdout, stderr=stderr)

    print('Building', image.name , '...', '{}done'.format(colors.GREEN), colors.WHITE)

end_time = datetime.now() - start_time
print('{}Build finished{}'.format(colors.GREEN, colors.WHITE), 'Duration:', end_time)
