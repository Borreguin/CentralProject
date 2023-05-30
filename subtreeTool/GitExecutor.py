from __future__ import annotations

import datetime
import os
import uuid
from typing import List

from git import Repo, Remote, Head

from subtreeTool.InfoTool import InfoTool
from subtreeTool.sb_constant import changeLogName, pull_action, push_action, infoFileName
from subtreeTool.sb_util import to_snake_case, log_this

# global variables to work with
tool_path = os.path.dirname(os.path.abspath(__file__))
tool_info_path = os.path.join(tool_path, infoFileName)
working_path = os.getcwd()
project_id = os.path.basename(working_path)



class GitExecutor:
    path: str = None
    subtreePath: str = None
    action: str = None
    remoteName: str = None
    remoteBranchName: str = None
    message: str = None
    success: bool = None
    details: str = str
    # Git Objects to work with
    repository: Repo
    remoteRepo: Remote
    originRepo: Remote
    localBranch: Head
    sharedCommonBranch: Head
    sharedCommonBranchName: str
    subtreeName: str

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'path':
                self.path = value
                self.subtreePath = os.path.join(working_path, value)
                self.subtreeName = to_snake_case(os.path.basename(value))
            else:
                setattr(self, key, value)
        self.repository = Repo.init(tool_path)
        self.localBranch = self.repository.active_branch
        self.originRepo = [r for r in self.repository.remotes if r.name == 'origin'][0]

    def __str__(self):
        return f'[{project_id}, {self.path}] \n--> Success: {self.success} \n--> Details: \n{self.details}'


    def add_remote(self):
        if os.path.exists(tool_info_path):
            pass
        else:
            info_tool = InfoTool()


    def verify_subtree_path(self):
        self.success = os.path.exists(self.subtreePath)
        self.details = f'Valid path' if self.success else f'This is not a valid path: {self.subtreePath}'
        return self.success

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
            self.sharedCommonBranchName = f'{self.remoteBranchName}_{self.subtreeName}'
            return True
        except Exception as e:
            self.success, self.details = False, f'{e} \n\nThis branch [{self.remoteBranchName}] ' \
                                                f'is not a valid branch in [{self.remoteRepo.name}]' + \
                                         f'\nTo see the available branches: \n> git branch -r'
            return False

    def verify_remote_repo_and_branch(self):
        return self.verify_remote() and self.verify_remote_branch()

    def add_message_to_change_log(self) -> bool:
        if not self.verify_subtree_path():
            return False
        changeLogPath = os.path.join(self.subtreePath, changeLogName)
        mode = 'a' if os.path.exists(changeLogPath) else 'w'
        try:
            with open(changeLogPath, mode) as f:
                f.write(f'\n{datetime.datetime.now()} '
                        f'\t[{self.repository.config_reader().get_value("user", "email")}] '
                        f'\t[{project_id}] {self.message}')
            return True
        except Exception as e:
            self.success, self.details = False, f'Not able to register the message in changelog: \n{e}'
            return False

    def stash_current_changes(self):
        self.repository.active_branch.repo.git.execute('git stash -m "[subtreeTool] save work before any action"')
        return self

    def stash_apply_saved_changes(self):
        self.repository.active_branch.repo.git.execute('git stash apply')
        return self

    def pull_origin(self):
        self.originRepo.repo.git.execute(f'git fetch origin'.split(' '))
        self.originRepo.pull()
        self.success, self.details = True, f'Pull from origin was successful: [{self.originRepo.url}]'
        return self

    def pull_from_remote(self):

        if not self.verify_subtree_path() or not self.verify_remote_repo_and_branch():
            return self

        self.stash_current_changes()

        if self.message is None:
            self.success, self.details = False, 'This parameter is missing: \n -m "Your message is required"'
            return self

        command_checkout = f'git checkout {self.remoteName}/{self.remoteBranchName}'.split(' ')
        command_split = f'git subtree split -P {self.path} -b {self.sharedCommonBranchName}'.split(' ')
        command_push = f'git push origin {self.sharedCommonBranchName}'.split(' ')

        command_checkout_local = f'git checkout {self.localBranch.name}'.split(' ')

        command_pull = f'git subtree pull --prefix {self.path} origin {self.sharedCommonBranchName} --squash -m'.split(
            ' ')
        command_pull.append(f'"[{self.remoteName}] {self.message}"')

        commands: List[List[str]] = [command_checkout, command_split, command_push, command_checkout_local,
                                     command_pull]

        try:
            # checkout to the remote branch, execute subtree split and push this branch
            self.remoteRepo.repo.git.execute(command_checkout)
            commands.remove(command_checkout)

            self.repository.active_branch.repo.git.execute(command_split)
            branches = [b for b in self.repository.branches if b.name == self.sharedCommonBranchName]
            if len(branches) == 0:
                self.success, self.details = False, f'The shared common branch was not created: [{self.sharedCommonBranchName}]'
                return self
            commands.remove(command_split)

            self.sharedCommonBranch = branches[0]
            self.repository.active_branch.repo.git.execute(command_push)
            commands.remove(command_push)

            self.success, self.details = True, f'Shared Common Branch was pushed {self.sharedCommonBranchName}'
            # checkout to current branch, execute subtree pull, commit the message

            self.repository.active_branch.repo.git.execute(command_checkout_local)
            commands.remove(command_checkout_local)
            self.repository.active_branch.repo.git.execute(command_pull)
            self.success, self.details = True, f'Code successfully pulled from: ' \
                                               f'{self.remoteName} -> {self.remoteBranchName} \n' \
                                               f'Verify the code before push the changes in [{self.localBranch.name}]' \
                                               f'\n> git push --set-upstream origin {self.localBranch.name}'
            commands.remove(command_pull)

        except Exception as e:
            manual_info = self.build_exception_message(commands, None, e)
            self.success, self.details = False, f'Not able to pull code from ' \
                                                f'{self.remoteName} -> {self.remoteBranchName}' \
                                                f'\n{e} \n\n{manual_info} '

        return self

    def push_origin(self):
        if not self.verify_subtree_path():
            return self
        # add changes that are inside subtree path
        command = f'git add {self.path}'.split(' ')
        self.localBranch.checkout().repo.git.execute(command)
        diff = self.repository.index.diff(self.localBranch.name)
        if len(diff) == 0:
            self.success, self.details = False, f'No need to commit. There are no changes in [{self.path}]'
            return self
        if not self.add_message_to_change_log():
            return self
        # add changes in ChangeLog file
        self.localBranch.checkout().repo.git.execute(command)
        self.localBranch.repo.index.commit(f'[{project_id}] {self.message}')
        self.success, self.details = True, f'Changes were pushed successfully: {project_id}: -> {self.localBranch.name}'
        return self

    def push_to_remote(self):
        if not self.verify_remote() or not self.verify_remote_branch():
            return self
        self.push_origin()
        # temporal branch to use:
        temporalBranch: Head | None = None
        temp_branch_name = f'{self.remoteName}_temp_{uuid.uuid4()}'

        # commands to execute:
        command_split = f'git subtree split -P {self.path} -b {self.sharedCommonBranchName}'.split(' ')

        command_checkout_remote = f'git checkout {self.remoteName}/{self.remoteBranchName} -b {temp_branch_name}'.split(
            ' ')
        command_pull_remote = f'git pull {self.remoteName} {self.remoteBranchName}'.split(' ')

        command_pull_sub_tree = f'git subtree pull --prefix {self.path} origin {self.sharedCommonBranchName} --squash -m'.split(
            ' ')
        command_pull_sub_tree.append(f'"[{project_id}] {self.message}"')

        command_commit_changes = f'git commit -m'.split(' ')
        command_commit_changes.append(f'"[{project_id}] {self.message}"')

        command_push_remote = f'git push {self.remoteName} HEAD:{self.remoteBranchName}'.split(' ')

        commands = [command_split, command_checkout_remote, command_pull_remote, command_pull_sub_tree,
                    command_commit_changes, command_push_remote]

        try:
            # put last code in shared common branch
            self.localBranch.checkout().repo.git.execute(command_split)
            self.originRepo.push(self.sharedCommonBranchName)
            commands.remove(command_split)
            log_this('Put last code in shared common branch')

            # create a temporal branch:
            self.remoteRepo.repo.git.execute(f'git fetch {self.remoteName}'.split(' '))
            self.remoteRepo.repo.git.execute(command_checkout_remote)
            branches = [b for b in self.repository.branches if b.name == temp_branch_name]
            if len(branches) == 0:
                self.success, self.details = False, f'The temporal branch was not created: [{temp_branch_name}]'
                return self
            temporalBranch: Head = branches[0]
            commands.remove(command_checkout_remote)
            log_this(f'Create a temporal branch {temp_branch_name}')

            # execute split and updated code using the temporal branch
            temporalBranch.repo.git.execute(command_pull_remote)
            commands.remove(command_pull_remote)
            temporalBranch.repo.git.execute(command_pull_sub_tree)
            commands.remove(command_pull_sub_tree)
            log_this(f'Execute split and updated code using the temporal branch')

            # push code in remote repository:
            temporalBranch.repo.git.execute(command_commit_changes)
            commands.remove(command_commit_changes)
            temporalBranch.repo.git.execute(command_push_remote)
            log_this(f'Push code in remote repository: {self.remoteName}')
            # checkout to the active branch and delete the temporal branch
            self.localBranch.checkout()
            temporalBranch.delete(self.repository)
            commands.remove(command_push_remote)
            log_this(f'Checkout to the active branch and delete the temporal branch')
            self.success, self.details = True, f'Code successfully pushed to: ' \
                                               f'{self.remoteName} -> {self.remoteBranchName}' \
                                               f'\nCheck the changes in [{self.sharedCommonBranchName}] ' \
                                               f'\n> git checkout {self.sharedCommonBranchName} '

        except Exception as e:
            if len(commands) == 0 and self.repository.active_branch.name == temp_branch_name:
                self.localBranch.checkout()
                self.repository.delete_head(temporalBranch)
            manual_info = self.build_exception_message(commands, temp_branch_name, e)
            self.success, self.details = False, f'Not able to push {self.remoteName} -> {self.remoteBranchName} ' \
                                                f'\n{e} \n\n{manual_info} '
        return self

    def build_exception_message(self, commands: List, temp_branch_name, e):
        manual_info = str()
        if 'Working tree has modifications' in f'{e}':
            manual_info = f'Your project: [{project_id}] has modifications, you need to commit your changes first'
        else:
            manual_info += f"\nThere are conflicts between {self.remoteName} and {project_id}, run manually:\n"
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

    def execute_action(self):
        if self.action == pull_action and self.remoteName is None:
            return self.pull_origin()
        elif self.action == pull_action and self.remoteName is not None:
            return self.pull_from_remote()
        elif self.action == push_action and self.remoteName is None:
            return self.push_origin()
        elif self.action == push_action and self.remoteName is not None:
            return self.push_to_remote()

        self.success, self.details = False, 'No action was performed'
        return self
