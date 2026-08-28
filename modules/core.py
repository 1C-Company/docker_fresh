import modules.helper as helper

def delete_core_distr_files():
    command = helper.new_docker_command('images/core/distr/')
    command.append('alpine')
    command.append('sh -c "rm -rf /out_files/*.deb /out_files/*.run"')
    return command

def delete_license_tools_files():
    command = helper.new_docker_command('images/core/distr/')
    command.append('alpine')
    command.append('sh -c "rm -rf /out_files/license-tools"')
    return command

def add_all_after_commands():
    commands = []
    commands.append(delete_core_distr_files())
    commands.append(delete_license_tools_files())
    return commands

class New():

    name = ''
    commands_before = []
    commands_after = []

    def __init__(self):
        self.name = 'core'
        self.commands_before = []
        self.commands_after = add_all_after_commands() #after-команды больше не должны быть нужны. Проверить, что и без них временные файлы не остаются.