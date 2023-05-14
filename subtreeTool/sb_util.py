import re
import subprocess as sb


def verify_git_lib_install_if_needed():
    try:
        from git import Repo, Remote, Head
        return True
    except Exception as e:
        log_this(f"gitpython was not found. \n{e} \n"
                 f"I will try to install for you...")

    commands = ['pip3 install gitpython', 'pip install gitpython']
    for command in commands:
        try:
            log_this(f'Try: {command}')
            sb.run(command.split(' '))
            return True
        except Exception as e:
            log_this(f'Error: {e}')
    return False


def log_this(msg: str):
    print(f'[subtree]: {msg}')


def to_snake_case(value):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()
