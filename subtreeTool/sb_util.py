import datetime
import os
import platform
import subprocess as sb
import sys
from typing import List


def log_this(msg: str):
    print(f'[subtree]: {msg}')


def verify_git_lib_install_if_needed():
    try:
        from git import Repo, Remote, Head
        import yaml
        return True
    except Exception as e:
        log_this(f"gitpython was not found. \n{e} \n"
                 f"I will try to install for you... \n")

    log_this(f"Your Python version is: {platform.python_version()} | executed on: {os.path.dirname(sys.executable)}")
    commands = ['pip install --upgrade pip', 'pip3 install --upgrade pip',
                'pip install gitpython', 'pip3 install gitpython',
                'pip install pyyaml', 'pip3 install pyyaml']
    was_installed = 0
    for command in commands:
        try:
            log_this(f'Try: {command}')
            sb.run(command.split(' '))
            was_installed += 1
        except Exception as e:
            log_this(f'Error: {e}')
    if was_installed >= 3:
        log_this(f'gitpython was installed successfully... ')
    else:
        log_this(f'gitpython was not installed, check for a solution manually.')
    return was_installed >= 3


def read_yml_file(path):
    import yaml
    with open(path) as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            log_this(f'Subtree yml file did not open, error msg: {exc}')


def check_path(label, path):
    if os.path.exists(path):
        return True, f'{label} valid: {path}'
    return False, f'{label } invalid: {path}'


def check_subtree_config_path(subtree_config_path, subtree_path):
    normalized_subtree_config_path = os.path.normpath(subtree_config_path)
    if normalized_subtree_config_path not in subtree_path:
        return False, f'Invalid subtree path defined in subtree.config.yml: {normalized_subtree_config_path}'
    return True, f'Valid subtree path defined in subtree.config.yml'


def get_main_path(subtree_config_path, subtree_path):
    subtree_path_split = subtree_config_path.split('/')
    subtree_path_split_reverse = subtree_path_split[::-1]
    main_path_processed = subtree_path
    for path_item in subtree_path_split_reverse:
        if path_item in main_path_processed:
            main_path_processed = os.path.abspath(os.path.join(main_path_processed, os.pardir))
    return main_path_processed


def get_username_initials(git_executor):
    reader = git_executor.repository.config_reader()
    username = reader.get_value("user", "name")
    if len(username) == 0:
        return

    initial = ''.join([name[0:2].lower() + "" for name in username.split(' ')])
    return initial


def stash_list(git_executor):
    command_output = git_executor.repository.active_branch.repo.git.execute('git stash list'.split(' '))
    return command_output


def stash_count_warning(git_executor):
    stash_list_command_output = stash_list(git_executor)
    number_stash_changes = len(stash_list_command_output.splitlines())
    if number_stash_changes > 10:
        log_this('WARNING: You have more than 10 stashed changes, you could remove them whit this command: '
                 'git stash clear')
    return number_stash_changes


def stash_project_changes(git_executor):
    command_output = git_executor.repository.active_branch.repo.git.execute('git stash -m "all_changes"'.split(' '))
    return command_output


def stash_subtree_changes(git_executor):
    stash_command = f"git stash push -m {git_executor.remoteBranchName} -- {git_executor.subtreePath}".split(' ')
    command_output = git_executor.repository.active_branch.repo.git.execute(stash_command)
    return command_output


def stash_apply_changes(git_executor):
    git_executor.repository.active_branch.repo.git.execute('git stash apply'.split(' '))


def stash_apply_group_changes(git_executor, stashed_changes):
    for i in range(len(stashed_changes)):
        try:
            stash_command = f'git stash apply {i}'.split(' ')
            git_executor.repository.active_branch.repo.git.execute(stash_command)
        except Exception as e:
            git_executor.success, git_executor.details = False, f'MERGE CONFLICTS EXCEPTION: ' \
                                                f'\n{e} '


def add_message_to_change_log(git_executor, change_log_path):
    mode = 'a' if os.path.exists(change_log_path) else 'w'
    try:
        with open(change_log_path, mode) as f:
            f.write(f'\n{datetime.datetime.now()} '
                    f'\t[{git_executor.repository.config_reader().get_value("user", "email")}] '
                    f'\t[{git_executor.projectId}] {git_executor.message}')
        return True, f'Added message in changelog'
    except Exception as e:
        return False, f'Not able to register in changelog file: \n{e}'


def build_exception_message(git_executor, commands: List, temp_branch_name, e):
    manual_info = str()
    if 'Working tree has modifications' in f'{e}':
        manual_info = f'Your project: [{git_executor.projectId}] has modifications, you need to commit ' \
                      f'your changes first'
    elif 'Merge conflict' in f'{e}':
        manual_info += f"\nThere are conflicts between {git_executor.remoteBranchName} and" \
                       f" {git_executor.projectId}. After resolve merge conflicts, run manually:\n"
        for i, command in enumerate(commands):
            manual_info += f'{i + 1}. {" ".join(command)}\n'

        manual_info += f"\nSolve the conflicts... "
        if temp_branch_name is not None and git_executor.repository.active_branch.name == temp_branch_name:
            manual_info += f'\n==============> NOTE YOU ARE IN BRANCH: {temp_branch_name}' \
                           f"\nDo not forget to delete temporal branch: " \
                           f"\ngit checkout {git_executor.localBranch.name}" \
                           f"\ngit branch --delete {temp_branch_name}\n" \
                           f"\n==============> NOTE YOU ARE IN BRANCH: {temp_branch_name}\n"
    return manual_info
