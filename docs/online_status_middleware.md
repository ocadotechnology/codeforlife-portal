# Online status middleware

This middleware keeps track of which users are online, it is entirely cache based so no database/model queries are required.

The basic functionality of the middleware is that it keeps track of all logged in users (that are not anonymous), and stores this list in the cache. users that have been offline or inactive for a fixed amount of time are marked as idle, and after a seperate fixed amount of time they are then removed from the list and considered offline. *This can be seen in the `status.py` file within the `django-online-status` directory*

There are couple of template tags to access this information to help make use of this functionality.

Also, this middleware contains a couple of view/urls by default, the only one that should exist is the `/test` url as one of the others lists every single user currently online for everyone to see which may pose a security risk, and the other is an example which probably shouldn't exist in a production enviroment, if these are present in your project (or are not ignored) please make sure they don't end up in production.

