Changelog
=========


1.0 2017-12-03
--------------

- With no bug reports or pull requests in nearly two months, we're leaving beta.


1.1 (unreleased)
----------------

- Fix CI tests, disable code-analysis tests
- Provide portal object to vocabulary scripts.
  [instification]


1.0 (2017-12-03)
----------------

- Pushing buttons in the editor would cause the field selection to be lost. Fixed.
  [smcmahon]


1.0b4 (2017-10-10)
------------------

- Add tutorial. Elaborate 'Nuts and Bolts'. Add to readthedocs.org.
  [smcmahon]

- Allow RestrictedPython access to datetime.timedelta type.
  [smcmahon]


- Make sure RestrictedPython allows datetime.date and datetime.datetime class types and not just instance types. This is so we can get at date.today() and datetime.now().
  [smcmahon]


1.0b3 (2017-10-03)
------------------

- Added no-cache headers to all AJAX responses.
  [smcmahon]

- Fixed an error in a jQuery selector that would cause an editor error loading content-type information. Bug introduced in b2. Fixed.
  [smcmahon]


1.0b2 (2017-10-02)
------------------

- The editor would sometimes fail to list any content types. Fixed.
  [smcmahon]

- Most operations would not work on sites that didn't have an id of 'Plone'. Fixed.
  Thanks, Wayne Glover.
  [smcmahon]


1.0b1 (2017-09-27)
------------------

- Initial release.
  [smcmahon]
