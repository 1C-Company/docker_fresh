import subprocess
import sys
import os


class colors:
    GREEN = '\033[92m'
    WHITE = '\033[97m'
    RED = '\033[91m'


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))


def print_usage():
    print('Использование: python deploy.py -h <имя_хоста> [-new] [-debug] [--skip-download] [--skip-install]')
    print()
    print('  -h <имя_хоста>     обязательный, передаётся в start.py')
    print('  -new               передаётся в start.py (разворачивание нового стенда)')
    print('  -debug             передаётся в install.py и start.py')
    print('  --skip-download    пропустить шаг скачивания дистрибутивов (download_releases.py)')
    print('  --skip-install     пропустить шаг сборки docker-образов (install.py)')


def run_step(description, cmd):
    print('{}=== {} ==={}'.format(colors.GREEN, description, colors.WHITE))
    result = subprocess.call(cmd, cwd=REPO_ROOT)
    if result != 0:
        print('{}Шаг "{}" завершился с ошибкой (код {}). Останавливаюсь.{}'.format(colors.RED, description, result, colors.WHITE))
        sys.exit(1)
    print('{}=== {} завершено успешно ==={}\n'.format(colors.GREEN, description, colors.WHITE))


if __name__ == '__main__':
    if '-help' in sys.argv or '--help' in sys.argv:
        print_usage()
        sys.exit(0)

    host_name = None
    if '-h' in sys.argv:
        idx = sys.argv.index('-h')
        if idx + 1 < len(sys.argv):
            host_name = sys.argv[idx + 1]

    new_server = '-new' in sys.argv
    debug = '-debug' in sys.argv
    skip_download = '--skip-download' in sys.argv
    skip_install = '--skip-install' in sys.argv

    if host_name is None:
        print('Не указано имя хоста.')
        print_usage()
        sys.exit(1)

    # Скачивание дистрибутивов 1С
    if not skip_download:
        run_step('Скачивание дистрибутивов 1С', [sys.executable, 'download_releases.py'])
    else:
        print('Шаг скачивания дистрибутивов пропущен (--skip-download)\n')

    # Сборка docker-образов
    if not skip_install:
        install_cmd = [sys.executable, 'install.py']
        if debug:
            install_cmd.append('-debug')
        run_step('Сборка docker-образов', install_cmd)
    else:
        print('Шаг сборки docker-образов пропущен (--skip-install)\n')

    # Развёртывание стенда
    start_cmd = [sys.executable, 'start.py', '-h', host_name]
    if new_server:
        start_cmd.append('-new')
    if debug:
        start_cmd.append('-debug')
    run_step('Развёртывание стенда', start_cmd)

    print('{}Все шаги успешно выполнены.{}'.format(colors.GREEN, colors.WHITE))
