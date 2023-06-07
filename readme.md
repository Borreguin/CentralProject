# General notes:
Subtree: `testName`

This subtree allows you to keep the code referring to this `testName`, the following explains how the
code should be updated from the local project to the shared common code (CORE-MOBILE) and vice versa.
This tool is available in the following link: https://github.com/Borreguin/CentralProject

**IMPORTANT:**

- `<subtree_name>` is the subtree name
- `<subtree_path>` is the subtree path
- `<subtree_branch>` is the REMOTE branch that the subtree will use
- `<remote_repository_name>` is the REMOTE repository name
- `<remote_repository_link>` is the REMOTE repository link

## A. Update from Remote / Central Project to your local project (Pull)
Run the Python script (subtree.py) at the subtree path

1. `subtree pull -m "put your commet"`

**Note**: If the Python script fails, follow manually the steps shown by the script to resolve the issue

## B. Update from local project to Remote / Central Project (Push)
Run the Python script (subtree.py) at the subtree path

1. `subtree push -m "put your commet"`
2. `Create a merge request in the web page`

**Note**: If the Python script fails, follow manually the steps shown by the script to resolve the issue

## C. Create subtree
NO NEED TO RUN THIS ANYMORE THIS WAS DONE, but it is included as a reference, it was executed at the beginning:
IMPORTANT: The creation of the subtree should be done in your local project not in the Core/Central Project.
Run the Python script (subtree.py)

1. `subtree create -n "<subtree_name>" -p "<subtree_path>" -b "<subtree_branch>" -rn "<remote_repository_name>" -rl "<remote_repository_link>"`

**Note**: If the Python script fails, follow the steps shown by the script to resolve the issue

**Note**: Don't forget protect the created branch




