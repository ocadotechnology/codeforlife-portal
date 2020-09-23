# Tips on using our Wagtail CMS instance

## Adding content in the Wagtail CMS

Our common module provides access to a wagtail cms instance for adding and editing content on the site. Since wagtail uses the same database as the rest of our content, it means we have three different databases (dev, staging, production) + local development databases we want to keep with similar data for non user-generated content.

We have come up with a small process to achieve this as follows:

1. Locally, use the CMS to add the content that you want
2. Run `python example_project/manage.py dumpdata NAME_OF_TABLE_YOU_ADDED_CONTENT_IN >> NAME_OF_TABLE_YOU_ADDED_CONTENT_IN.json`
3. Create a data migration to preload the data in the database
4. Commit these changes and submit a PR so it will eventually propagate through all the servers.

If from step 2, a `NAME_OF_TABLE_YOU_ADDED_CONTENT_IN.json` already exists in the project, create a new data migration for the new content and suffix it with a number (e.g. `NAME_OF_TABLE_YOU_ADDED_CONTENT_IN_2.json`)

## Editing content

Depending on the edit, not doing a data migration and introducing a little inconsistency between the database might be more practical here. Just use the CMS editor at `/cms/` to perform the edits. Please note that you must be an admin to do this.

## Adding images and other media in Wagtail

We don't use the image features/media integration in wagtail. If you want to add something, you can

1. Add the media in the appropriate place in the codeforlife_assets bucket
2. In wagtail, use a CharField and add the path of the media (e.g. for image.png stored in the images folder in codeforlife_assets, add `images/image.png`)
