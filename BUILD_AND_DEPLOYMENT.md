## Current build / deployment process:

The build/deployment process takes place on Jenkins which is accessed here: build.codeforlife.education.

1. Changes pushed to the ocargo, codeforlife-portal and codeforlife-deploy github repositories trigger the Publish Ocargo Files, Publish Portal Files and Publish Deploy Files builds on Jenkins respectively.
1. Each of "Publish X files" builds publishes all of the files of its repository and triggers Create Distribution.
1. Create Distribution puts the the three projects into the distribution package structure 
(deploy as the root directory, ocargo and portal directories copied as directories in submodules directory), 
collects static files and compresses them. The resulting artifact is distribution.tar.gz. 
This is used by all subsequent builds (tests and deploy), so we can be sure that what we deploy is what we tested.
1. Create Distribution triggers Run Portal Tests and Run Ocargo Tests and when they complete successfuly, Deploy to Dev is triggered.
1. Deploy to Staging and Deploy to Prod can be manually triggered:
    1. Select Deploy to Staging or Deploy to Prod
    1. Select Build with parameters on the left hand side
    1. Select 'Specific Build' from the drop down menu
    1. Provide the latest 'Create Distribution' build number

## Making ad-hoc changes to production:

Occasionally changes need to be deployed quickly. Going through the usual deployment process requires testing of all changes that various team members have made and therefore can be slow. The ad-hoc deployment process has been put in place to bypass these usual obstacles. 

1. For each repository do the following:

  1. Create branch:
  
    Every Create Distribution and “Deploy to X” (Dev, Staging, Prod) build publishes commit.txt on Jenkins which contains a commit ID for each project/respository which looks like this '24b0852d52c5a35a280be01d6ee420a120fd1318'. This ID specifies the state of the corresponding git hub repository which was used to build the deployed distribution artifact.

    Use the commit ID to create a new branch for the corresponding repository:
      1. Navigate to the local repository (codeforlife-deploy, codeforlife-portal or ocargo)
      1. Use the commit ID to navigate to the relevant state of that repository: $ git checkout [commit ID]
      1. Create a new branch (the name of the branch is not important but the name of the new branches on each repository must be the same): $ git checkout -b <new-branch-name>
      1. Push the new branch to the remote repository: $ git push
        
    1. Commit and push the adhoc changes to created branch.        
        
  1. To ensure these changes are not lost with subsequent deployments via the usual process we need to integrate the adhoc changes back to the master:
    1. Navigate to the master state: $ git checkout master
    1. Copy the relevant commit ID from the log: $ git log
    1. Cherry pick the adhoc change back into master: $ git cherry-pick [commit ID]

1. Manually trigger  "Ad-hoc distribution" build with the branch name as the parameter:
    1. On Jenkins select "Ad-hoc distribution"
    1. Click 'Build with parameters' on the left-hand side
    1. Input the name of the branch newly created

  This will kick off all three "Publish X files" off the branch and "Create Distribution" will follow using the published files.

1. Deploy the created distribution and Test on Dev or Staging.

1. Deploy to prod.

