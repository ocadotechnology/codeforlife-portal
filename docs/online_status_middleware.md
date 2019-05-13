# Online status middleware

This middleware keeps track of which users are online, it is entirely cache based so no database/model queries are required.

The basic functionality of the middleware is that it keeps track of all logged in users (that are not anonymous), and stores this list in the cache. Users that don't perform an action after a fixed amount of time are removed from the list of online users and thus considered offline. *This can be seen in the `status.py` file within the `django-online-status` directory*

