==============================================================================
collective.ambidexterity
==============================================================================

collective.ambidexterity provides through-the-web editing of views, defaults, validators and vocabularies for Dexterity content types.

Documentation: http://collectiveambidexterity.readthedocs.io

Status of the package
---------------------

The package currently only works in Plone 5.

Installation
------------

Add `collective.ambidexterity` to the `eggs` list in your Plone 5 buildout.
Run buildout.

Use the add/remove addons option in site setup to activate the package for a particular Plone site.

Quick operation
---------------

Look for the `Ambidexterity` option near the end of site setup.
This will open the Ambidexterity editor.

You should be able to add view templates for all Dexterity content types.
View templates are standard Plone page templates using TAL for dynamic content.

Default, validator and vocabulary scripts may be added for all Dexterity content types that you have created through-the-web.
You may not add default, validator or vocabulary scripts for content types that have been set up via Python packages.
(Exception: if the content-type's fields are definedd in a `model source` attribute of the FTI, you may add Ambidexterity scripts.)

Default, validator and vocabulary scripts are much like the Scripts (Python) that may be added via the Zope Management Interface.
They will execute in a Restricted Python environment with the privileges of the logged-in user.
Limited imports are available.

Restricted Python provides a safety net for programmers who don't know the details of the Zope/Plone security model.
If you are running up against the limitations of Restricted Python, you should consider migrating your Ambidexterity code to a Python package.
It is important that you understand that the safety net is not perfect: it is not adequate to protect your site from coding by an untrusted user.
Only highly trusted users should be allowed to use the Ambidexterity editor.
It is by default restricted to site managers.

Cautions
--------

This package marks the `re`, `datetime` and `time` modules as safe for use in RestrictedPython.
That will affect all PythonScripts.

To do
-----

Test coverage: pretty good for the nuts and bolts.
The user interface is currently completely untested.
If you're up-to-date on robot testing, your assistance would be appreciated.

i18n: Undeveloped.

Accessibility: Undeveloped.

Contribute
----------

- Issue Tracker: https://github.com/collective/collective.ambidexterity/issues
- Source Code: https://github.com/collective/collective.ambidexterity

Support
-------

Plone community forums: https://community.plone.org/


License
-------

The project is licensed under the GPLv2.
