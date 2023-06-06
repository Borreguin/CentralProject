"""
This script is a tool to manage subtrees:
A) REMOTE -> LOCAL: From remote to local -> pull
B) LOCAL -> REMOTE: From local to remote -> push

Created by Roberto Sanchez.
Search this: Acts 4:12-19
Version: 1.0
"""
from __future__ import annotations

import argparse
import os
import sys

from sb_util import verify_git_lib_install_if_needed, log_this
if not verify_git_lib_install_if_needed():
    sys.exit()

from GitExecutor import GitExecutor
from sb_constant import git_actions


def parse_args():
    parser = argparse.ArgumentParser(description="Utility to pull/push subtree changes from/to a Remote repository. "
                                                 "\nFind me: Mathew 6:33")
    parser.add_argument("action", help=f"Action to apply", choices=git_actions)
    parser.add_argument("-m", "--message", help=f"Comment for this pull/push", type=str)
    args = parser.parse_args()
    return args


def main():
    inputs = parse_args()
    log_this(f'Start subtree routine --> Path: {os.getcwd()}')
    git_executor = GitExecutor(**inputs.__dict__).execute_action()
    log_this(f'Finish subtree routine --> {git_executor}')


if __name__ == "__main__":
    main()
