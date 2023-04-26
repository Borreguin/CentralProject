
# General notes:
Subtree: `sharedCode`

This subtree allows you to keep the code referring to this `subtree core`, the following explains how the
code should be updated from the mobile application (App) to the shared common code (CORE-MOBILE) and vice versa.

Make sure you have included the following REMOTE repository:
* git remote add CORE-MOBILE https://github.com/Borreguin/CentralProject

Note: App refers the LOCAL mobile application that you are working on (i.e. Make and Pack)

**IMPORTANT:**

- `sc_shared_code` is the REMOTE branch that has the common shared code between App and Core Mobile
- `<working_branch>` is the LOCAL branch for the App where you want to pull/push the changes in your LOCAL App
- `commonFeatures` is the REMOTE branch from where you want to pull/push the changes in Core Mobile

## A. Update from Core Mobile to App (Pull)

1. `git checkout <working_branch>`
2. `git subtree pull --prefix sharedCode CORE-MOBILE sc_shared_code --squash -m "[CoreMobile] put your comment"`

## B. Update from App to Core Mobile (Push)
If you have a maintainer role:
1. `git subtree push --prefix sharedCode CORE-MOBILE sc_shared_code`

If you have a developer role:
1. `git checkout -b sc_shared_code_temp CORE-MOBILE/sc_shared_code`
2. `git push CORE-MOBILE HEAD:sc_shared_code_temp`
3. `git checkout <working_branch>`
4. `git subtree push --prefix sharedCode CORE-MOBILE sc_shared_code_temp`
5. Create a pull request in the web page: https://git.formos.com/formos/perfect-core-mobile/-/compare/

## ONLY FIRST TIME: When the subtree is created only for reference - NO RUN THIS: (Create)
NO NEED TO RUN THIS ANYMORE THIS WAS DONE but it is included as a reference, it was executed at the beginning:

1. `git subtree split -P sharedCode -b sc_shared_code_temp`
2. `git fetch CORE-MOBILE`
3. `git checkout CORE-MOBILE/commonFeatures`
4. `git subtree add --prefix sharedCode sc_shared_code_temp --squash`
5. `git push CORE-MOBILE HEAD:commonFeatures`
6. `git checkout sc_shared_code_temp`
7. `git push CORE-MOBILE HEAD:sc_shared_code`
8. `git checkout <working_branch>`
9. `git branch -D sc_shared_code_temp`
10. Remove the folder that you want to share with Core Mobile
* `git rm -r sharedCode`
* `git commit -m "Remove before to use sub-tree"`
11. Bring the shared code from the shared common branch
* `git subtree add --prefix sharedCode CORE-MOBILE sc_shared_code --squash`
12. Push the shared code in the REMOTE
* `git push`

## ONLY FIRST TIME: When the subtree is added only for reference - NO RUN THIS: (ADD)
NO NEED TO RUN THIS ANYMORE THIS WAS DONE but it is included as a reference, it was executed at the beginning:

1. `git fetch CORE-MOBILE`
2. Bring the shared code from the shared common branch
* `git subtree add --prefix sharedCode CORE-MOBILE sc_shared_code --squash`
3. Push the shared code in the REMOTE
* `git push --set-upstream origin <working_branch>`
