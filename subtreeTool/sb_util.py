from __future__ import annotations

import datetime
import os
import platform
import re
import shutil
import subprocess as sb
import sys
from pathlib import Path
from typing import List
from sb_constant import readme_file, pull_action, push_action, create_action, add_action


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


def check_arguments_by_action(git_executor):
    if git_executor.action == pull_action or git_executor.action == push_action:
        return check_pull_push_arguments(git_executor.message)
    elif git_executor.action == create_action or git_executor.action == add_action:
        return check_create_add_arguments(git_executor.subtreePath,
                                          git_executor.remoteBranchName,
                                          git_executor.remoteName,
                                          git_executor.remoteLink)


def check_pull_push_arguments(message):
    if message is None:
        return False, f'Parameter message is required'
    return True, f'Complete pull/push parameters'


def check_create_add_arguments(subtree_path, subtree_branch, remote_name, remote_link):
    if subtree_path is None:
        return False, f'Parameter subtree path is required'
    elif subtree_branch is None:
        return False, f'Parameter subtree branch is required'
    elif remote_name is None:
        return False, f'Parameter remote repository name is required'
    elif remote_link is None:
        return False, f'Parameter remote repository link is required'
    return True, f'Complete create parameters'


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
    return False, f'{label} invalid: {path}'


def check_subtree_config_path(subtree_config_path, subtree_path):
    normalized_subtree_config_path = os.path.normpath(subtree_config_path)
    if normalized_subtree_config_path not in subtree_path:
        return False, f'Invalid subtree path defined in subtree.config.yml: {normalized_subtree_config_path}'
    return True, f'Valid subtree path defined in subtree.config.yml'


def get_main_path(subtree_config_path, subtree_path):
    subtree_config_path_split = subtree_config_path.split('/')
    subtree_config_path_split_reverse = subtree_config_path_split[::-1]
    subtree_path_split = Path(subtree_path).parts
    subtree_path_split_reverse = subtree_path_split[::-1]
    main_path_processed = subtree_path
    for index, path_item in enumerate(subtree_config_path_split_reverse):
        if path_item == subtree_path_split_reverse[index]:
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
        log_this('WARNING: You have more than 10 stashed changes, you could remove them with this command: '
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
    init_line_break = '\n' if mode == 'a' else ''
    try:
        with open(change_log_path, mode) as f:
            f.write(f'{init_line_break}{datetime.datetime.now()} '
                    f'\t[{git_executor.repository.config_reader().get_value("user", "email")}] '
                    f'\t[{git_executor.projectId}] {git_executor.message}')
        return True, f'Added message in changelog'
    except Exception as e:
        return False, f'Not able to register in changelog file: \n{e}'


def copy_file(origin_path, destiny_path):
    try:
        shutil.copy(origin_path, destiny_path)
        return True, f'File has been copied!'
    except Exception as e:
        return False, f'Not able to copy file: \n{e}'


def create_subtree_config_file(git_executor, subtree_config_path):
    # Create subtree.config.yml file
    mode = 'a' if os.path.exists(subtree_config_path) else 'w'
    try:
        with open(subtree_config_path, mode) as f:
            f.write(f'subtreeName: "{git_executor.subtreeName}"\n'
                    f'subtreePath: "{git_executor.subtreePath}"\n'
                    f'remoteRepositoryName: "{git_executor.remoteName}"\n'
                    f'remoteRepositoryLink: "{git_executor.remoteLink}"\n'
                    f'remoteBranchName: "{git_executor.remoteBranchName}"')
        return True, f'Subtree.config.yml file created'
    except Exception as e:
        return False, f'Not able to create Subtree.config.yml file: \n{e}'


def create_readme_file(git_executor, origin_path, destiny_path):
    # Copy readme template file
    success, detail = copy_file(origin_path, destiny_path)
    if not success:
        return

    readme_file_path = os.path.join(destiny_path, readme_file)
    try:
        # Create and read readme file
        with open(readme_file_path, 'r') as file:
            filedata = file.read()

        # Replace values
        filedata = filedata.replace('#subtree_name', git_executor.subtreeName)
        filedata = filedata.replace('#subtree_path', git_executor.subtreePath)
        filedata = filedata.replace('#subtree_branch', git_executor.remoteBranchName)
        filedata = filedata.replace('#remote_repository_name', git_executor.remoteName)
        filedata = filedata.replace('#remote_repository_link', git_executor.remoteLink)

        # Write new readme file
        with open(readme_file_path, 'w') as file:
            file.write(filedata)

        return True, f'Readme file created'
    except Exception as e:
        return True, f'Not able to create readme file: \n{e}'


def build_exception_message(git_executor, commands: List, temp_branch_name, e):
    manual_info = str()
    if 'Working tree has modifications' in f'{e}':
        manual_info = f'Your project: [{git_executor.projectId}] has modifications, you need to commit ' \
                      f'your changes first'
    elif 'Merge conflict' in f'{e}':
        manual_info += f"\nThere are conflicts between {git_executor.remoteBranchName} and" \
                       f" {git_executor.projectId}. After resolve merge conflicts, run manually:\n"

    for i, command in enumerate(commands):
        if isinstance(command, str):
            manual_info += f'{i + 1}. {command}\n'
        else:
            manual_info += f'{i + 1}. {" ".join(command)}\n'

    manual_info += f"\nSolve the conflicts... "
    if temp_branch_name is not None and git_executor.repository.active_branch.name == temp_branch_name:
        manual_info += f'\n==============> NOTE YOU ARE IN BRANCH: {temp_branch_name}' \
                       f"\nDo not forget to delete temporal branch: " \
                       f"\ngit checkout {git_executor.localBranch.name}" \
                       f"\ngit branch --delete {temp_branch_name}\n" \
                       f"\n==============> NOTE YOU ARE IN BRANCH: {temp_branch_name}\n"
    return manual_info


def execute_and_remove(branch, commands: List[str | List[str]], command_to_execute: str | List[str], msg: str):
    to_execute = command_to_execute
    if isinstance(command_to_execute, str):
        to_execute = command_to_execute.split(' ')
    branch.repo.git.execute(to_execute)
    commands.remove(command_to_execute)
    to_log = msg if isinstance(msg, str) else " ".join(command_to_execute)
    log_this(f'{msg}: {to_log}')
    return commands


def search_path_in_error_message(error):
    possible_errors_pattern = ['renamed to (.*) in Updated upstream', '->"(.*)" in branch']
    for pattern in possible_errors_pattern:
        file_path = re.search(pattern, error)
        if file_path:
            return file_path.group(1)
    return None


def log_this(msg: str):
    print(f'[subtree]: {msg}')
