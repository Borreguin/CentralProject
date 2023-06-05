import datetime
import os
import platform
import re
import subprocess as sb
import sys
from typing import List
from sb_constant import subtreeConfigFile, subtreeName, subtreePath, remoteRepositoryLink, remoteRepositoryCoreName


# -------------------------------------------- Init utils ----------------------------------------

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


def to_snake_case(value):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()


def read_yml_file(path):
    import yaml
    with open(path) as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as exc:
            log_this(f'Subtree yml file did not open, error msg: {exc}')


def check_subtree_parameters(self):
    # Check if subtree.config.yml file doesn't exist
    subtree_config_file_path = os.path.join(self.subtreePath, subtreeConfigFile)
    if not os.path.exists(subtree_config_file_path):
        self.success, self.message = False, "This is not a valid subtree"
        self.details = f"Not able to found: {subtree_config_file_path}"
        return False

    # Set subtree attributes defined in subtree.config.yml
    set_subtree_config_attributes(self, subtree_config_file_path)

    # Check if field subtreePath in subtree.config.yml file is invalid
    normalized_subtree_config_path = os.path.normpath(self.subTreeConfigPath)
    if normalized_subtree_config_path not in self.subtreePath:
        self.success, self.message = False, "Invalid path defined in subtree.config.yml"
        self.details = f"Not able to found: {normalized_subtree_config_path}"
        return False

    return True


def set_subtree_config_attributes(self, subtree_config_file_path):
    subtree_config = read_yml_file(subtree_config_file_path)
    self.subtreeName = subtree_config[subtreeName]
    self.subTreeConfigPath = subtree_config[subtreePath]
    self.remoteLink = subtree_config[remoteRepositoryLink]
    self.remoteName = subtree_config[remoteRepositoryCoreName]


def get_main_path(self):
    subtree_path_split = self.subTreeConfigPath.split('/')
    subtree_path_split_reverse = subtree_path_split[::-1]
    main_path_processed = self.subtreePath
    for path_item in subtree_path_split_reverse:
        if path_item in main_path_processed:
            main_path_processed = os.path.abspath(os.path.join(main_path_processed, os.pardir))
    return main_path_processed


def check_remote_repository(self):
    remotes = [r for r in self.repository.remotes if r.name == self.remoteName]
    if not remotes:
        self.repository.create_remote(self.remoteName, self.remoteLink)
        log_this('Remote repository added')


def get_username_initials(self):
    reader = self.repository.config_reader()
    username = reader.get_value("user", "name")
    if len(username) == 0:
        return

    initial = ''.join([name[0:2].lower() + "" for name in username.split(' ')])
    return initial

# ----------------------------------- Verify utils -------------------------------------


def verify_remote(self):
    remotes = [r for r in self.repository.remotes if r.name == self.remoteName]
    if len(remotes) == 0:
        self.success, self.details = False, f'This is not a valid remote: [{self.remoteName}]' + \
                                            f'\nAvailable repos:\n{self.repository.remotes}'
        return False
    self.success, self.details = True, f'Remote [{self.remoteName}] added'
    self.remoteRepo = remotes[0]
    self.remoteRepo.repo.git.execute(f'git fetch {self.remoteName}'.split(' '))
    return True


def verify_remote_branch(self):
    try:
        self.remoteRepo.repo.git.execute(
            f'git show-branch remotes/{self.remoteRepo}/{self.remoteBranchName}'.split(' '))
        self.success, self.details = True, f'Remote branch [{self.remoteBranchName}] added'
        self.sharedCommonBranchName = f'{self.remoteBranchName}'
        return True
    except Exception as e:
        self.success, self.details = False, f'{e} \n\nThis branch [{self.remoteBranchName}] ' \
                                            f'is not a valid branch in [{self.remoteRepo.name}]' + \
                                            f'\nTo see the available branches: \n> git branch -r'
        return False


def verify_remote_repo_and_branch(self):
    return verify_remote(self) and verify_remote_branch(self)


def verify_subtree_path(self):
    self.success = os.path.exists(self.subtreePath)
    self.details = f'Valid path' if self.success else f'This is not a valid path: {self.subtreePath}'
    return self.success

# ------------------------------------- Stash utils -------------------------------------------


def stash_list(self):
    command_output = self.repository.active_branch.repo.git.execute('git stash list'.split(' '))
    return command_output


def stash_count_warning(self):
    stash_list_command_output = stash_list(self)
    number_stash_changes = len(stash_list_command_output.splitlines())
    if number_stash_changes > 10:
        log_this('You have more than 10 stashed changes, you could remove them whit this command: git stash clear')
    return number_stash_changes


def stash_project_changes(self):
    command_output = self.repository.active_branch.repo.git.execute('git stash -m "all_changes"'.split(' '))
    return command_output


def stash_subtree_changes(self):
    stash_command = f"git stash push -m {self.remoteBranchName} -- {self.subTreeConfigPath}".split(' ')
    command_output = self.repository.active_branch.repo.git.execute(stash_command)
    return command_output


def stash_apply_changes(self):
    self.repository.active_branch.repo.git.execute('git stash apply'.split(' '))


def stash_apply_group_changes(self, stashed_changes):
    for i in range(len(stashed_changes)):
        try:
            stash_command = f'git stash apply {i}'.split(' ')
            self.repository.active_branch.repo.git.execute(stash_command)
        except Exception as e:
            self.success, self.details = False, f'MERGE CONFLICTS EXCEPTION: ' \
                                                f'\n{e} '


# -------------------------------Additional utils----------------------------

def add_message_to_change_log(self, change_log_path) -> bool:
    if not verify_subtree_path(self):
        return False
    mode = 'a' if os.path.exists(change_log_path) else 'w'
    try:
        with open(change_log_path, mode) as f:
            f.write(f'\n{datetime.datetime.now()} '
                    f'\t[{self.repository.config_reader().get_value("user", "email")}] '
                    f'\t[{self.projectId}] {self.message}')
        return True
    except Exception as e:
        self.success, self.details = False, f'Not able to register the message in changelog: \n{e}'
        return False


def build_exception_message(self, commands: List, temp_branch_name, e):
    manual_info = str()
    if 'Working tree has modifications' in f'{e}':
        manual_info = f'Your project: [{self.projectId}] has modifications, you need to commit your changes first'
    elif 'Merge conflict' in f'{e}':
        manual_info += f"\nThere are conflicts between {self.remoteBranchName} and {self.projectId}. After resolve merge conflicts, run manually:\n"
        for i, command in enumerate(commands):
            manual_info += f'{i + 1}. {" ".join(command)}\n'

        manual_info += f"\nSolve the conflicts... "
        if temp_branch_name is not None and self.repository.active_branch.name == temp_branch_name:
            manual_info += f'\n==============> NOTE YOU ARE IN BRANCH: {temp_branch_name}' \
                           f"\nDo not forget to delete temporal branch: " \
                           f"\ngit checkout {self.localBranch.name}" \
                           f"\ngit branch --delete {temp_branch_name}\n" \
                           f"\n==============> NOTE YOU ARE IN BRANCH: {temp_branch_name}\n"
    return manual_info
