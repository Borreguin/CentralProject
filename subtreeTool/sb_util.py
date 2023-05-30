import os
import platform
import re
import subprocess as sb
import sys


def verify_git_lib_install_if_needed():
    try:
        from git import Repo, Remote, Head
        return True
    except Exception as e:
        log_this(f"gitpython was not found. \n{e} \n"
                 f"I will try to install for you... \n")

    log_this(f"Your Python version is: {platform.python_version()} | executed on: {os.path.dirname(sys.executable)}")
    commands = ['pip install --upgrade pip', 'pip3 install --upgrade pip',
                'pip install gitpython', 'pip3 install gitpython']
    was_installed = 0
    for command in commands:
        try:
            log_this(f'Try: {command}')
            sb.run(command.split(' '))
            was_installed += 1
        except Exception as e:
            log_this(f'Error: {e}')
    if was_installed >= 2:
        log_this(f'gitpython was installed successfully... ')
    else:
        log_this(f'gitpython was not installed, check for a solution manually.')
    return was_installed >= 2


def log_this(msg: str):
    print(f'[subtree]: {msg}')


def to_snake_case(value):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()
