import pathlib
import os

path_to_1c = ''
sep = str(os.path.sep)
this_path = str(pathlib.Path().absolute()) + sep
distr_path = this_path + 'distr' + sep


def replace_sep(path):
    return path.replace('/', sep)

def new_docker_command(extra_path=None):
    command = []
    command.append('docker')
    command.append('run')
    command.append('--rm')
    command.append('-v')

    if extra_path != None:
        current_distr_path = this_path + extra_path
        current_distr_path = current_distr_path.replace('/', sep)
    else:
        current_distr_path = distr_path

    command.append(current_distr_path + ':/out_files')
    return command

def add_command_copy_file_from_mnt_to_tmp(commands, container_name, full_path, file_name):

    commands.append('docker')
    commands.append('exec')
    commands.append(container_name)
    commands.append('sh')
    commands.append('-c')
    commands.append('"cp {} /tmp/{}"'.format(full_path, file_name))
    commands.append('&&')

def web_publish_command(host_name, conf_name, internal, descriptor, base_name=''):

    if internal:
        prefix = 'int'
    else:
        prefix = 'a'

    command = []
    command.append('docker')
    command.append('exec')
    command.append('web.' + host_name)
    command.append('{}webinst'.format(path_to_1c))
    command.append('-apache24')
    command.append('-wsdir')
    command.append(prefix + '/' + conf_name)
    command.append('-dir')
    command.append('/var/www/{}/{}'.format(prefix, conf_name))
    command.append('-connstr')

    if base_name != '':
        command.append('"Srvr=srv;Ref={};"'.format(base_name))
    else:
        command.append('"Srvr=srv;Ref={};"'.format(conf_name))
    command.append('-confpath')
    command.append('"/etc/apache2/apache2.conf"')
    command.append('-descriptor')
    command.append('"/mnt/other-files/vrd/{}.vrd"'.format(descriptor))
    return command

def get_out_file_name_command(action, ib_name):
    return '/Out "/mnt/{}_{}.out"'.format(action, ib_name)

def create_ib_command(host_name, ib_name, job_block, action):

    container_name = 'srv.{}'.format(host_name)

    command = []
    command.append('docker')
    command.append('exec')
    command.append('-t')
    command.append(container_name)
    command.append('{}1cv8'.format(path_to_1c))
    command.append('CREATEINFOBASE')
    command.append('"Srvr=srv;Ref={0};DBMS=PostgreSQL;DBSrvr=db;DB={0};DBUID=postgres;LicDstr=Y;Locale=ru_RU;CrSQLDB=Y;SchJobDn={1};"'.format(ib_name, job_block))
    command.append(get_out_file_name_command(action, ib_name))
    return command

def load_cfg_command(host_name, ib_name, file_name, action):

    full_path = '/mnt/{}'.format(file_name)
    container_name = 'srv.{}'.format(host_name)

    command = []
    add_command_copy_file_from_mnt_to_tmp(command, container_name, full_path, file_name)
    command.append('docker')
    command.append('exec')
    command.append('-t')
    command.append(container_name)
    command.append('{}1cv8'.format(path_to_1c))
    command.append('DESIGNER')
    command.append('/S')
    command.append('"srv\\{}"'.format(ib_name))
    command.append('/LoadCfg')
    command.append('/tmp/{}'.format(file_name))
    command.append('/UpdateDBCfg')
    command.append(get_out_file_name_command(action, ib_name))
    return command

def install_control_ext_command(host_name, ib_name, action):

    full_path = '/mnt/other-files/cfe/api_1cfresh.cfe'
    container_name = 'srv.{}'.format(host_name)

    command = []
    add_command_copy_file_from_mnt_to_tmp(command, container_name, full_path, 'api_1cfresh.cfe')
    command.append('docker')
    command.append('exec')
    command.append('-t')
    command.append(container_name)
    command.append('{}1cv8'.format(path_to_1c))
    command.append('DESIGNER')
    command.append('/S')
    command.append('"srv\\{}"'.format(ib_name))
    command.append('/LoadCfg')
    command.append('"/tmp/api_1cfresh.cfe"')
    command.append('-Extension')
    command.append('"api_1cfresh"')
    command.append('/UpdateDBCfg')
    command.append(get_out_file_name_command(action, ib_name))
    return command

def install_sm_ext_command(host_name, ib_name, action):

    full_path = '/mnt/other-files/cfe/УправлениеМС.cfe'
    container_name = 'srv.{}'.format(host_name)

    command = []
    add_command_copy_file_from_mnt_to_tmp(command, container_name, full_path, 'УправлениеМС.cfe')
    command.append('docker')
    command.append('exec')
    command.append('-t')
    command.append(container_name)
    command.append('{}1cv8'.format(path_to_1c))
    command.append('DESIGNER')
    command.append('/S')
    command.append('"srv\\{}"'.format(ib_name))
    command.append('/LoadCfg')
    command.append('"/tmp/УправлениеМС.cfe"')
    command.append('-Extension')
    command.append('"УправлениеМС"')
    command.append('/UpdateDBCfg')
    command.append(get_out_file_name_command(action, ib_name))
    return command

def install_ext_command(host_name, ib_name, action):

    full_path = '/mnt/{}.cfe'.format(ib_name)
    file_name = '{}.cfe'.format(ib_name)
    container_name = 'srv.{}'.format(host_name)

    command = []
    add_command_copy_file_from_mnt_to_tmp(command, container_name, full_path, file_name)
    command.append('docker')
    command.append('exec')
    command.append('-t')
    command.append(container_name)
    command.append('{}1cv8'.format(path_to_1c))
    command.append('DESIGNER')
    command.append('/S')
    command.append('"srv\\{}"'.format(ib_name))
    command.append('/LoadCfg')
    command.append('"/tmp/{}"'.format(file_name))
    command.append('-Extension')
    command.append('"fresh"')
    command.append('/UpdateDBCfg')
    command.append(get_out_file_name_command(action, ib_name))
    return command

def disable_safe_mode(host_name, ib_name, action):

    full_path = '/mnt/other-files/cfe/disable.epf'
    container_name = 'srv.{}'.format(host_name)

    command = []
    add_command_copy_file_from_mnt_to_tmp(command, container_name, full_path, 'disable.epf')
    command.append('docker')
    command.append('exec')
    command.append('-t')
    command.append(container_name)
    command.append('{}1cv8'.format(path_to_1c))
    command.append('ENTERPRISE')
    command.append('/S')
    command.append('"srv\\{}"'.format(ib_name))
    command.append('/Execute')
    command.append('"/tmp/disable.epf"')
    command.append(get_out_file_name_command(action, ib_name))
    return command

def delete_control_extension(ib_name, host_name, user):
    command = []
    command.append('docker')
    command.append('exec')
    command.append('-t')
    command.append('web.{}'.format(host_name))
    command.append('curl')
    if user != None: command.append('--user {}:'.format(user))
    command.append('-X POST')
    command.append('http://localhost/int/{}/hs/api.1cfresh/delete'.format(ib_name))
    return command

def edit_site_settings(host_name, sup_pass):
    command = []
    command.append('docker exec -t web.{}'.format(host_name))
    command.append("curl")
    command.append('-F propertiesMap[\'site.url\']=https://{}'.format(host_name))
    command.append('-F propertiesMap[\'site.locale\']=ru')
    command.append('-F propertiesMap[\'site.media_directory\']=/var/www/content/site_files/')
    command.append('-F propertiesMap[\'search.indexDir\']=/var/www/content/searchIndex/')
    command.append('-F propertiesMap[\'ws.endpoint\']=http://web/int/sm/ws/Subscriber')
    command.append('-F propertiesMap[\'ws.endpoint.rest\']=""')
    command.append('-F propertiesMap[\'ws.endpoint.rest.timeout\']=5000')
    command.append('-F propertiesMap[\'ws.publicUserName\']=Anonymous')
    command.append('-F propertiesMap[\'ws.publicUserPassword\']=')
    command.append('-F propertiesMap[\'ws.protectUserName\']=ProtectedUser')
    command.append('-F propertiesMap[\'ws.protectUserPassword\']=')
    command.append('-F propertiesMap[\'ws.am.endpoint\']=http://web/int/am/ws/Availability')
    command.append('-F propertiesMap[\'ws.am.username\']=Reader')
    command.append('-F propertiesMap[\'ws.am.password\']=' + sup_pass)
    command.append('-F propertiesMap[\'openid.oipEndpointUrl\']=https://{}/a/openid/e1cib/oid2op'.format(host_name))
    command.append('-F propertiesMap[\'viewsProperties.forumUrl\']=https://1cfresh.sample/forum/')
    command.append('-F propertiesMap[\'viewsProperties.adminApplicationUrl\']=https://{}/a/adm/'.format(host_name))
    command.append('-F propertiesMap[\'viewsProperties.mailto\']=info@1cfresh.sample')
    command.append('-F propertiesMap[\'viewsProperties.supportMailto\']=support@1cfresh.sample')
    command.append('-F propertiesMap[\'open.registration.ws.endpoint\']=http://web/int/sm/ws/ExternalRegistration_1_0_0_1')
    command.append('-F propertiesMap[\'open.registration.user\']=ExternalRegistration')
    command.append('-F propertiesMap[\'open.registration.password\']=' + sup_pass)
    command.append('-F propertiesMap[\'open.registration.siteId\']=1')
    command.append('-F propertiesMap[\'open.registration.sourceId\']=1')
    command.append('-F submit=')
    command.append('https://{}/settings/edit_settings'.format(host_name))
    return command

def enable_manual_registration(host_name):
    command = []
    command.append('docker exec -t web.{}'.format(host_name))
    command.append('curl')
    command.append('-F id=25')
    command.append('-F key=ManualRegistration')
    command.append('-F description="Включение регистрации на сайте без выбора партнера (код приглашения высылается автоматически)"')
    command.append('-F enabled=true')
    command.append('-F _enabled=on')
    command.append('https://{}/admin/features/25/edit'.format(host_name))
    return command

def enable_openid(host_name):
    command = []
    command.append('docker exec -t web.{}'.format(host_name))
    command.append('curl')
    command.append('-F id=2')
    command.append('-F key=openid')
    command.append('-F description="Включение работы OpenID на сайте"')
    command.append('-F enabled=true')
    command.append('-F _enabled=on')
    command.append('https://{}/admin/features/2/edit'.format(host_name))
    return command

def add_solution(host_name, brief_desc, full_desc, display_order, id, possibilities, title):
    command = []
    command.append('docker exec -t web.{}'.format(host_name))
    command.append('curl')
    command.append('-F _enableDemo=on')
    command.append('-F _showVideo=on')
    command.append('-F _userVisible=on')
    command.append('-F briefDescription={}'.format(brief_desc))
    command.append('-F displayOrder={}'.format(display_order))
    command.append('-F fullDescription={}'.format(full_desc))
    command.append('-F id={}'.format(id))
    command.append('-F possibilities={}'.format(possibilities))
    command.append('-F screenshotCount=0')
    command.append('-F title={}'.format(title))
    command.append('-F userVisible=true')
    command.append('-F videosPageTitle={}'.format(possibilities))
    command.append('https://{}/admin/solutions/add'.format(host_name))
    return command

def get_host_name(argv):

    if '-h' not in argv:
        print('parameter -р not specified')
        exit(1)
    host_index = argv.index('-h')
    return argv[host_index + 1]


def init(path):
    global path_to_1c
    path_to_1c = path