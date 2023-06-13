from __future__ import annotations
import os
from git import Repo, Remote, Head
from sb_constant import pull_action, push_action, subtree_name, subtree_path, remote_repository_link, \
    change_log_file, subtree_config_file, create_action, remote_repository_name, remote_branch_name, add_action, \
    command_git_add
from sb_util import get_main_path, stash_project_changes, stash_apply_changes, stash_subtree_changes, \
    get_username_initials, stash_apply_group_changes, log_this, add_message_to_change_log, \
    build_exception_message, stash_count_warning, read_yml_file, check_subtree_config_path, check_path, \
    create_subtree_config_file, copy_file, create_readme_file, check_arguments_by_action, execute_and_remove

script_path = os.path.dirname(os.path.abspath(__file__))


class GitExecutor:
    action: str = None
    projectId: str = None
    workingPath: str = None
    mainProjectPath: str = None
    subtreeName: str = None
    subtreePath: str = None
    subtreeConfFilePath: str = None
    remoteName: str = None
    remoteLink: str = None
    remoteBranchName: str = None
    message: str = None
    success: bool = None
    details: str = None
    # Git objects attributes
    repository: Repo = None
    remoteRepo: Remote = None
    originRepo: Remote = None
    localBranch: Head = None

    def __init__(self, **kwargs):
        # Set init attributes with arguments
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Check arguments by action
        self.success, self.details = check_arguments_by_action(self)
        if not self.success:
            return

        # Check working path
        self.workingPath = os.getcwd()
        self.success, self.details = check_path('Working path', self.workingPath)
        if not self.success:
            return

        # Set required attributes
        self.set_attributes()

    def __str__(self):
        return f'[{self.projectId}, {self.workingPath}] \n--> Success: {self.success} \n--> Details: \n{self.details}'

    def set_attributes(self):
        if self.action == pull_action or self.action == push_action:
            # Set subtree config attributes from subtree.config.yml file
            self.subtreeConfFilePath = os.path.join(self.workingPath, subtree_config_file)
            self.set_subtree_config_attributes(self.subtreeConfFilePath)
            if not self.success:
                return
        elif self.action == create_action:
            # Set create attributes
            self.subtreeName = os.path.basename(self.subtreePath)
            self.message = f'Initial subtree commit'

        # Set main project path and id
        self.mainProjectPath = get_main_path(self.subtreePath, self.workingPath)
        self.projectId = os.path.basename(self.mainProjectPath)

        # Set local repository and branch
        self.repository = Repo.init(self.mainProjectPath)
        origin_repositories = [r for r in self.repository.remotes if r.name == 'origin']
        if not origin_repositories:
            self.success, self.details = False, 'Origin repository not found'
            return
        self.originRepo = origin_repositories[0]
        self.localBranch = self.repository.active_branch

        # Set remote repository
        self.set_remote_repository()

    def set_subtree_config_attributes(self, subtree_config_file_path):
        # Check subtree.config.yml file path
        self.success, self.details = check_path('Subtree.config.yml path', subtree_config_file_path)
        if not self.success:
            return self

        # Read and set attributes from subtree.config.yml
        subtree_config = read_yml_file(subtree_config_file_path)
        self.subtreeName = subtree_config[subtree_name]
        self.subtreePath = subtree_config[subtree_path]
        self.remoteName = subtree_config[remote_repository_name]
        self.remoteLink = subtree_config[remote_repository_link]
        self.remoteBranchName = subtree_config[remote_branch_name]

        # Check subtree config path defined in subtree.config.yml file
        self.success, self.details = check_subtree_config_path(self.subtreePath, self.workingPath)
        if not self.success:
            return self

    def set_remote_repository(self):
        # Find exist remote repository
        remotes = [r for r in self.repository.remotes if r.name == self.remoteName]
        if not remotes:
            # Add remote repository if it does not exist
            self.repository.create_remote(self.remoteName, self.remoteLink)
            log_this(f'Added remote repository {self.remoteName}: link {self.remoteLink}')
            remotes = [r for r in self.repository.remotes if r.name == self.remoteName]
        self.remoteRepo = remotes[0]

    def execute_action(self):
        if self.success:
            if self.action == pull_action and self.remoteRepo is not None:
                return self.pull_from_remote()
            elif self.action == push_action and self.remoteRepo is not None:
                return self.push_to_remote()
            elif self.action == create_action and self.remoteRepo is not None:
                return self.create_subtree()
            elif self.action == add_action and self.remoteRepo is not None:
                return self.add_subtree()

        return self

    def pull_from_remote(self):
        # Check message parameter
        if self.message is None:
            self.success, self.details = False, 'This parameter is missing: \n -m "Your message is required"'
            return

        # Stashed changes count warning
        stash_count_warning(self)

        # Add project changes
        self.repository.active_branch.repo.git.execute(command_git_add.split(' '))
        log_this(f'Git add: {command_git_add}')

        # Check if there are changes
        there_are_changes = False
        if 'No local changes to save' not in f'{stash_project_changes(self)}':
            there_are_changes = True

        # Set git commands
        command_pull = f'git subtree pull --prefix {self.subtreePath} {self.remoteName} {self.remoteBranchName} ' \
                       f'--squash -m'.split(' ')
        command_pull.append(f'[{self.subtreeName}] {self.message}')
        command_stash_apply = f'git stash apply'.split(' ')
        command_restore_staged = f'git restore --staged .'.split(' ')
        commands = [command_pull, command_stash_apply, command_restore_staged]
        try:
            # Pull from subtree
            commands.remove(command_pull)
            self.repository.active_branch.repo.git.execute(command_pull)
            log_this(f'Pull subtree: {" ".join(command_pull)}')

            # Get stashed changes
            if there_are_changes:
                commands.remove(command_stash_apply)
                stash_apply_changes(self)
                log_this(f'Get stashed changes, command: git stash apply ')

            # Restored staged changes
            self.repository.active_branch.repo.git.execute(command_restore_staged)
            commands.remove(command_restore_staged)
            log_this(f'Git restore staged: {" ".join(command_restore_staged)}')

            self.success, self.details = True, f'Code successfully pulled from: ' \
                                               f'{self.remoteName} -> {self.remoteBranchName} \n' \
                                               f'Verify the code before push the changes in [{self.localBranch.name}]' \
                                               f'\n> git push --set-upstream origin {self.localBranch.name}'
        except Exception as e:
            if not there_are_changes:
                commands.remove(command_stash_apply)
                commands.remove(command_restore_staged)
            manual_info = build_exception_message(self, commands, self.localBranch, e)
            self.success, self.details = False, f'Not able to push {self.remoteName} -> {self.remoteBranchName} ' \
                                                f'\n{e} \n\n{manual_info} '
        return self

    def push_to_remote(self):
        # Check message parameter
        if self.message is None:
            self.success, self.details = False, 'This parameter is missing: \n -m "Your message is required"'
            return

        # Stashed changes count warning
        stash_count_warning(self)

        # Add subtree changes
        command = f'git add {self.subtreePath}'
        self.repository.active_branch.repo.git.execute(command.split(' '))
        log_this(f'Git add: {command}')

        # Check subtree changes
        if 'No local changes to save' in f'{stash_subtree_changes(self)}':
            self.success, self.details = False, f'There are not changes in subtree {self.subtreeName}'
            return self
        stashed_changes = ['subtree_changes_stashed']

        # Get temporal branch name
        temp_branch_name = f'{self.remoteBranchName}_temp_{get_username_initials(self)}'

        # Add project changes
        self.repository.active_branch.repo.git.execute(command_git_add.split(' '))
        log_this(f'Git add: {command_git_add}')

        # Stash project changes
        if 'No local changes to save' not in f'{stash_project_changes(self)}':
            stashed_changes.append('project_changes_stashed')

        # Get index to stash apply
        index_to_apply = 1 if len(stashed_changes) == 2 else 0

        # Set git commands
        command_fetch_remote = f'git fetch {self.remoteName}'.split(' ')
        command_checkout_remote = f'git checkout -b {temp_branch_name} {self.remoteName}/{self.remoteBranchName}'\
            .split(' ')
        command_stash_apply_subtree_by_index = f'git stash apply {index_to_apply}'.split(' ')
        # command_git_add
        command_commit_changes = f'git commit -m'.split(' ')
        command_commit_changes.append(f'[{self.projectId}] {self.message}')
        command_push_remote = f'git push {self.remoteName} HEAD:{temp_branch_name}'.split(' ')
        command_checkout_local_branch = f'git checkout {self.localBranch}'.split(' ')
        command_delete_temp_branch = f'git branch -D {temp_branch_name}'.split(' ')
        command_stash_list = f'git stash list'.split(' ')
        command_stash_apply_changes_group = f'git stash apply <#>'.split(' ')
        command_restore_staged = f'git restore --staged .'.split(' ')
        commands = [command_fetch_remote, command_checkout_remote, command_stash_apply_subtree_by_index,
                    command_git_add, command_commit_changes, command_push_remote, command_checkout_local_branch,
                    command_delete_temp_branch, command_stash_list, command_stash_apply_changes_group,
                    command_restore_staged]

        try:
            # Create temporal branch
            self.repository.active_branch.repo.git.execute(command_fetch_remote)
            commands.remove(command_fetch_remote)
            log_this(f'Git fetch remote: {" ".join(command_fetch_remote)}')

            # Checkout to temporal branch
            try:
                self.repository.active_branch.repo.git.execute(command_checkout_remote)
            except Exception as e:
                stash_apply_group_changes(self, stashed_changes)
                if "already exists" in f'{e}':
                    self.success, self.details = False, f'A LOCAL branch named {temp_branch_name} already exists.'
                    return self
            commands.remove(command_checkout_remote)
            log_this(f'Create a temporal branch: {" ".join(command_checkout_remote)}')

            # Get temporal branch
            branches = [b for b in self.repository.branches if b.name == temp_branch_name]
            if len(branches) == 0:
                self.success, self.details = False, f'The temporal branch was not created: [{command_checkout_remote}]'
                return self
            temporal_branch: Head = branches[0]

            # Get stashed changes
            try:
                commands.remove(command_stash_apply_subtree_by_index)
                temporal_branch.repo.git.execute(command_stash_apply_subtree_by_index)
                log_this(f'Get stashed changes: {" ".join(command_stash_apply_subtree_by_index)}')
            except Exception as e:
                if "CONFLICT (file location)" in f'{e}':
                    log_this(f'There are new files in subtree!')

            # Edit changelog.txt file
            change_log_file_path = os.path.join(self.mainProjectPath, change_log_file)
            self.success, self.details = add_message_to_change_log(self, change_log_file_path)
            if not self.success:
                return self
            log_this(f'Changelog.txt file updated!')

            # Add changes
            commands = execute_and_remove(temporal_branch, commands, command_git_add, 'Git add')

            # Commit changes
            commands = execute_and_remove(temporal_branch, commands, command_commit_changes, 'Commit changes')

            # Push changes
            commands = execute_and_remove(temporal_branch, commands, command_push_remote, 'Push changes')

            # Checkout local branch
            commands = execute_and_remove(temporal_branch, commands, command_checkout_local_branch,
                                          'Checkout local branch')

            # Delete temporal branch
            commands = execute_and_remove(temporal_branch, commands, command_delete_temp_branch,
                                          'Delete temporal branch')

            # Get stashed changes
            stash_apply_group_changes(self, stashed_changes)
            commands.remove(command_stash_list)
            commands.remove(command_stash_apply_changes_group)
            log_this(f'Get stashed changes: {" ".join(command_stash_apply_changes_group)}')

            # Restored staged changes
            self.repository.active_branch.repo.git.execute(command_restore_staged)
            commands.remove(command_restore_staged)
            log_this(f'Git restore staged: {" ".join(command_restore_staged)}')

            self.success, self.details = True, f'Code successfully pushed to: ' \
                                               f'{self.remoteName} -> {temp_branch_name}' \
                                               f'\nCheck the changes in [{temp_branch_name}]'

        except Exception as e:
            manual_info = build_exception_message(self, commands, temp_branch_name, e)
            self.success, self.details = False, f'Not able to push {self.remoteName} -> {self.remoteBranchName} ' \
                                                f'\n{e} \n\n{manual_info} '
        return self

    def create_subtree(self):
        # Stashed changes count warning
        stash_count_warning(self)

        # Add project changes
        self.repository.active_branch.repo.git.execute(command_git_add.split(' '))
        log_this(f'Git add: {command_git_add}')

        # Check if there are changes
        there_are_changes = False
        if 'No local changes to save' not in f'{stash_project_changes(self)}':
            there_are_changes = True

        # Set git commands
        command_switch_orphan = f'git switch --orphan {self.remoteBranchName}'.split(' ')
        # command_git_add
        command_commit = f'git commit --allow-empty -m'.split(' ')
        command_commit.append(f'[{self.projectId}] {self.message}')
        command_push = f'git push -u {self.remoteName} {self.remoteBranchName}'.split(' ')
        command_checkout_local_branch = f'git checkout {self.localBranch}'.split(' ')
        command_delete_orphan_branch = f'git branch -D {self.remoteBranchName}'.split(' ')

        try:
            # Create orphan branch
            self.repository.active_branch.repo.git.execute(command_switch_orphan)
            log_this(f'Create orphan branch: {" ".join(command_switch_orphan)}')

            # Create changelog.txt file
            change_log_file_path = os.path.join(self.mainProjectPath, change_log_file)
            self.success, self.details = add_message_to_change_log(self, change_log_file_path)
            if not self.success:
                return self
            log_this(f'Changelog file created!')

            # Create .gitignore file
            origin_path = os.path.join(script_path, 'templates', '.gitignore')
            self.success, self.details = copy_file(origin_path, self.mainProjectPath)
            if not self.success:
                return self
            log_this(f'Git ignore file created!')

            # Create subtree.config.yml file
            subtree_config_file_path = os.path.join(self.mainProjectPath, subtree_config_file)
            self.success, self.details = create_subtree_config_file(self, subtree_config_file_path)
            if not self.success:
                return self
            log_this(f'Subtree config file created!')

            # Create readme.md file
            origin_path = os.path.join(script_path, 'templates', 'readme.md')
            self.success, self.details = create_readme_file(self, origin_path, self.mainProjectPath)
            if not self.success:
                return self
            log_this(f'Readme file created!')

            # Add changes
            self.repository.active_branch.repo.git.execute(command_git_add.split(' '))
            log_this(f'Git add: {command_git_add}')

            # Commit changes
            self.repository.active_branch.repo.git.execute(command_commit)
            log_this(f'Commit: {" ".join(command_commit)}')

            # Push changes
            self.repository.active_branch.repo.git.execute(command_push)
            log_this(f'Push: {" ".join(command_push)}')

            # Checkout local branch
            self.repository.active_branch.repo.git.execute(command_checkout_local_branch)
            log_this(f'Checkout local branch:  {" ".join(command_checkout_local_branch)}')

            # Get stashed changes
            if there_are_changes:
                stash_apply_changes(self)
                log_this(f'Get stashed changes: git stash apply ')

            self.success, self.details = True, f'Successful subtree creation: ' \
                                               f'{self.subtreePath} -> {self.subtreeName}' \
                                               f'\nCheck the changes in [{self.remoteBranchName}]'

        except Exception as e:
            self.repository.active_branch.repo.git.execute(command_checkout_local_branch)
            self.repository.active_branch.repo.git.execute(command_delete_orphan_branch)
            if there_are_changes:
                stash_apply_changes(self)
            self.success, self.details = False, f'Not able to create subtree {self.subtreeName}' \
                                                f'\n{e}'
        return self

    def add_subtree(self):
        # Add project changes
        self.repository.active_branch.repo.git.execute(command_git_add.split(' '))
        log_this(f'Git add: {command_git_add}')

        # Check if there are changes
        there_are_changes = False
        if 'No local changes to save' not in f'{stash_project_changes(self)}':
            there_are_changes = True

        # Set git commands
        command_fetch_remote = f'git fetch {self.remoteName}'.split(' ')
        command_subtree_add = f'git subtree add --prefix {self.subtreePath} ' \
                              f'{self.remoteName} {self.remoteBranchName} --squash'.split(' ')

        try:
            # Git fetch remote
            self.repository.active_branch.repo.git.execute(command_fetch_remote)
            log_this(f'Git fetch remote: {" ".join(command_fetch_remote)}')

            # Subtree add
            self.repository.active_branch.repo.git.execute(command_subtree_add)
            log_this(f'Subtree add:  {" ".join(command_subtree_add)}')

            # Get stashed changes
            if there_are_changes:
                stash_apply_changes(self)
                log_this(f'Get stashed changes: git stash apply ')

            # Create subtree.config.yml file
            subtree_config_file_path = os.path.join(self.mainProjectPath,
                                                    os.path.normpath(self.subtreePath),
                                                    subtree_config_file)
            if not os.path.exists(subtree_config_file_path):
                self.success, self.details = create_subtree_config_file(self, subtree_config_file_path)
                if not self.success:
                    return self
                log_this(f'Subtree config created!')

            self.success, self.details = True, f'Successful subtree addition: ' \
                                               f'{self.subtreePath}'
        except Exception as e:
            if there_are_changes:
                stash_apply_changes(self)
            self.success, self.details = False, f'Not able to add subtree {self.subtreeName}' \
                                                f'\n{e}'
        return self
