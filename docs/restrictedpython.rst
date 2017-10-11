About RestrictedPython
======================

All of our scripts are a Python with some special limitations defined by `RestrictedPython <http://restrictedpython.readthedocs.io/en/latest/#contents>`_.

*RestrictedPython* is meant to provide a safety net for programmers that are not familiar with the Plone/Zope security model.
It limits built-in classes, modules and functions.
It also controls object-database access, limiting access to items that are available to the current user.
The `current user` is not you; if you're using the Ambidexterity editor, you have great powers (and great responsibility).
Rather, the `current user` will be the contributor adding or editing the content item.

RestrictedPython is what you're using when you add *Scripts (Python)* in the Zope Management Interface.
It's also used by some add-on packages like *PloneFormGen* which allow limited scripting.

Import restrictions
-------------------

Python's standard library is rich.
The packages installed with Zope and Plone add much, much more.
You **really, truly** don't want access to most of that functionality when you're scripting something like a validator, dynamic default or vocabulary.
Much of that extra functionality can't be used without some knowledge of the Zope/Plone security model and of the way web requests are handled.

A quick example: you might want to use ``urllib`` or ``urllib2`` to use an external resource via http/s to get information for a script.
If you do, the network I/O for that request will block execution of the thread processing your request.
Request-processing threads are precious on a Plone server; block a few of them and your site is at-least temporarily down.

Want to read something on the file system?
Are you prepared to do all the checking to make sure it can't access other information available to the Plone server?
Like the salt-hashed passwords of your users?

And, do you trust every possible person that can script on your site to not make those mistakes?
Or leave a vulnerability that might allow someone else to edit a script?

We can't vet the whole Python or Zope/Plone libraries for safety.
So, we mark a few modules as safe-for-importing in RestrictedPython.
The rest are unavailable.

RestrictedPython marks the following modules as safe-for-importing:

    * math
    * random
    * string

Ambidexterity adds two more because they're so obviously useful for defaults and validation:

    * datetime
    * re

Adding to the safe list
.......................

You may add other modules to the safe-for-importing list via add-on package.
See `collective.localfunctions <https://github.com/collective/collective.localfunctions>`_ for an example.

Be cautious. Your changes will affect all functions using RestrictedPython on the Zope instance where you add your modules and types.

Permissions
-----------

Ambidexterity scripts allow you access to a ``context`` variable that represents the current object.
When an item is being added, the context is the folder.
When it's being edited, it's the object itself.

With the right permissions, a knowledgeable programmer can work from *context* get access to nearly everything in your object database or request.
RestrictedPython controls access to object properties by checking user permissions.
In this case, the *user* is the one adding or editing the content object.
If a protected attribute or object is read without the right permissions, an *Unauthorized* error is raised, resulting a an HTTP ``Forbidden`` response and a redirect to the login form.

When you add Ambidexterity scripts, you're working as a very powerful user.
Your content contributors should have much less power.
So, you're not done with your Ambidexterity scripts until you log in as a less-powerful user to check for authorization errors.

Just a safety net
-----------------

RestrictedPython is a safety net.
It is not a replacement for caution.
The proper use for a safety net is to exercise all caution to avoid falling and only depend on the safety net as a last resort.
You should make sure that you do not extend any role that allows Ambidexterity editing to untrusted or uncautious users.
(These are the same roles as those that allow creation of Dexterity content types.)
