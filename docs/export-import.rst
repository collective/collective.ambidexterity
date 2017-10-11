
Export/Import
=============

Ambidexterity includes limited facilities for exporting and importing your content-type views and scripts.
The goal is to allow you to elaborate a content type's functionality TTW, then copy those elaborations to a matching content type on another Plone site.

Background
----------

The views and scripts you add via the Ambidexterity editor have two parts that reside in different parts of the object database of a Plone site. You may examine each via the Zope Management Interface.

**The scripts and views themselves** reside in ``portal_resources`` in a folder named ``ambidexterity`` that has subfolder for each content type and within each content-type folder for fields.

**Ambidexterity also changes a content type's Type Profile**. You may see those changes by examining your TTW Dexterity types in ``portal_types``. You may also see the script-enabling code by viewing the XML for a content type in the Dexterity field editor.

Exporting a Type Profile
------------------------

This capacity is built into Dexterity. Visit the Dexterity control panel, check the box to the left of a content type listing, and press the ``Export Type Profiles`` button.
This will generate a zip archive; unpack it if you want to examing it but make sure to keep around the zip file.

Exporting Ambidexterity resources
---------------------------------

Visit the Ambidexterity control panel and select a content type. Press the ``Export`` button and a zip archive will be downloaded.
As with the *Type Profile* zip, you may unpack it to examine it, but keep the zip file.

Import strategy
---------------

I suggest importing an Ambidexterity elaborated content type in four steps:

    1. Activate Ambidexterity on the target site;
    2. Visit the Dexterity control panel and import your type profile;
    3. Visit the Ambidexterity control panel and auto-synchronize when a problem is discovered;
    4. In the Ambidexterity editor, choose your imported content type and press the ``Import`` button to import your Ambidexterity resources.

Step 3 is required by the fact that you have imported a content type that uses Ambidexterity views, classes and functions, but does not yet have any portal resources to match.
The auto-synchronization will remove those references from the portal type. Between step 2 and step 3, the content type is broken.
Step 3 fixes it, but leaves it with no Ambidexterity support.

Step 4 will automatically re-synchronize the imported Ambidexterity resources with the portal-type information.
Everything should work again.

Caution, caution, caution
-------------------------

Using Ambidexterity should be a quick (and a bit dirty) solution to ad-hoc problems.
So, why would you want to transfer Ambidexterity resources from one Plone site to another?

If you have used Dexterity and Ambidexterity to develop a solution you wish to use on multiple Plone sites, you should strongly consider transferring your content-type definition to a Python add-on package.
Add-on packages can be version-controlled and tracked; they allow for sophisticated debugging and lack the limitations of RestrictedPython.

