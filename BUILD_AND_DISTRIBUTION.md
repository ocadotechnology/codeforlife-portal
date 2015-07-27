## Current build / deployment process:

1. Changes pushed to ocargo, codeforlife-portal and codeforlife-deploy trigger Publish Ocargo Files, Publish Portal Files and Publish Deploy Files respectively.
1. Each of "Publish <X> files" builds publishes all of the files of its repository and triggers Create Distribution.
1. Create Distribution puts the the three projects into the distribution package structure 
(deploy as the root directory, ocargo and portal directories copied as directories in submodules directory), 
collects static files and compresses them. The resulting artifact is distribution.tar.gz. 
This is used by all subsequent builds (tests and deploy), so we can be sure that what we deploy is what we tested.
1. Create Distribution triggers Run Portal Tests and Run Ocargo Tests and when they complete successfuly, Deploy to Dev is triggered.
1. Deploy to Staging and Deploy to Prod are manually triggered and take the number of the distribution build that gets deployed (defaults to last successful).

## Making ad-hoc changes to production:

1. Create a branch of production code:

    Every Create Distribution and “Deploy to <X>” (Dev, Staging, Prod) build publishes commit.txt on Jenkins.
    For each project / repository it contains hash of the commit that was used to build the deployed distribution artifact.
    Use that tp branch or tag the appropriate commits in all three repos. The important part is that branches and tags on all repos have the same name.

1. Push changes to created branches.

1. Manually trigger  "Ad-hoc distribution" build with the branch / tag name as the parameter.
This will kick off all three "Publish <X> files" off the branch / tag and "Create Distribution" will follow using the published files.

1. Deploy the created distribution and Test on Dev or Staging.

1. Deploy to prod.