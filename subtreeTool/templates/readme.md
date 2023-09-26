# General notes:
Subtree: `#subtree_path`

This subtree allows you to keep the code referring to this `#subtree_name`, the following explains how the
code should be updated from the local project to the shared common code (#remote_repository_name) and vice versa.
This tool is available in the following link: https://github.com/Borreguin/CentralProject

**IMPORTANT:**

- `<subtree_name>` is the subtree name
- `<subtree_path>` is the subtree path
- `<subtree_branch>` is the REMOTE branch that the subtree will use
- `<remote_repository_name>` is the REMOTE repository name
- `<remote_repository_link>` is the REMOTE repository link

## A. Update from Remote / Central Project to your local project (Pull)
Run the Python script (subtree.py) at the subtree path

1. `subtree pull -m "put your comment"`

**Note**: If the Python script fails, follow manually the steps shown by the script to resolve the issue

## B. Update from local project to Remote / Central Project (Push)
Run the Python script (subtree.py) at the subtree path

1. `subtree push -m "put your comment"`
2. `Create a merge request in the web page`

**Note**: If the Python script fails, follow manually the steps shown by the script to resolve the issue

## C. Create subtree
NO NEED TO RUN THIS ANYMORE THIS WAS DONE, but it is included as a reference, it was executed at the beginning:
IMPORTANT: The creation of the subtree should be done in your local project not in the Core/Central Project.
Run the Python script (subtree.py) in the **root** of the project:

1. `subtree create -p "<subtree_path>" -b "<subtree_branch>" -rn "<remote_repository_name>" -rl "<remote_repository_link>"`

**Note**: If the Python script fails, follow the steps shown by the script to resolve the issue

**Note**: Don't forget protect the created branch


## D. Add subtree
NO NEED TO RUN THIS ANYMORE THIS WAS DONE, but it is included as a reference, it was executed at the beginning.
Run the Python script (subtree.py) in the **root** of the project:

1. `subtree add -p "#subtree_path" -b "#subtree_branch" -rn "#remote_repository_name" -rl "#remote_repository_link"`

**Note**: If the Python script fails, follow the steps shown by the script to resolve the issue

## How to make this script executable:
### Windows:
1. Create new folder `Shared` in local disk `C:`
2. Copy `subtreeTool` folder in `C:\Shared`
3. Open "Edit the system environment variables" section and edit Environment Variables
4. Edit _PATH_ environment variable from "User variables for admin" section
5. Add the following path `C:\Shared\subtreeTool` and save changes
6. Edit _PATHEXT_ environment variable from "System variables" section
7. Add the following extension `.PY` and save changes

### Linux:
1. Create new folder in `/usr/Shared`:
   - `sudo mkdir /usr/Shared`
2. Copy `subtreeTool` folder in `/usr/Shared`:
   - `sudo mv subtreeTool /usr/Shared`
3. Open and check the Python execution path in 
file: [subtree.py](https://github.com/Borreguin/CentralProject/blob/b93d0c0fe7b13d0f885656d9dcc6d579f3be9ceb/subtreeTool/subtree.py) (line 1). 
To know the versions of Python that you have to use, please execute: `whereis python`, `whereis python3` 
   - `#!/usr/bin/python` (this is the usual path for python executor - changed it if you need)
4. Go to the path `/usr/Shared/subtreeTool` and rename the file _subtree.py_ to _subtree_:
   - `cd /usr/Shared/subtreeTool`
   - `sudo mv subtree.py subtree`
5. Give file permissions:
   - `sudo chmod +x subtree`
6. Edit (`.bashrc`) file to configure environment variables:
   - `sudo nano ~/.bashrc` 
7. Include the following lines:
   - `export SHARED=/usr/Shared`
   - `export PATH=$PATH:$SHARED/subtreeTool`
8. Update (`.bashrc`) file configurations:
   - `source ~/.bashrc`
9. Run the script in new terminal:
   - `subtree -h`

**Note**: If the script execution fails and the "Bad interpreter" error is displayed, execute these commands:
   - `sudo apt-get install dos2unix`
   - `cd /usr/Shared/subtreeTool`
   - `sudo dos2unix subtree`


### Mac:
1. Create new folder in `/usr/Shared`:
   - `sudo mkdir /usr/Shared`
2. Copy `subtreeTool` folder in `/usr/Shared`:
   - `sudo mv subtreeTool /usr/Shared`
3. Open and check the Python execution path in 
file: [subtree.py](https://github.com/Borreguin/CentralProject/blob/b93d0c0fe7b13d0f885656d9dcc6d579f3be9ceb/subtreeTool/subtree.py) (line 1). 
To know the versions of Python that you have to use, please execute: `where python`, `where python3`
   - `#!/usr/bin/python` (this is the usual path for python executor - changed it if you need)
4. Go to the path `/usr/Shared/subtreeTool` and rename the file _subtree.py_ to _subtree_:
   - `cd /usr/Shared/subtreeTool`
   - `sudo mv subtree.py subtree`
5. Give file permissions:
   - `sudo chmod +x subtree`
6. Edit the path environment variable file (`/etc/paths`) by including the following path `/Users/Shared/subtreeTool` at the end of this file:
   - `sudo nano /etc/paths` 
7. Run the script in new terminal:
   - `subtree -h`

**Note**: If the script execution fails and the "Bad interpreter" error is displayed, execute these commands:
   - `brew install dos2unix`
   - `cd /usr/Shared/subtreeTool`
   - `sudo dos2unix subtree`