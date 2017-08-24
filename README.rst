==============================================================================
collective.ambidexterity
==============================================================================

This is currently a set of explorations of the idea of doing Dexterity validators, vocabularies and defaults TTW via scripts in portal_resources.
It's at proof-of-concept stage.
If it works, we can build a plone.app.theming style UI to edit the portal_resources/ambidexterity space.

The general idea is that we will be able to use Dexterity XML to specify a schema like::

    <schema>
      <field name="test_integer_field" type="zope.schema.Int">
        <description/>
        <required>False</required>
        <defaultFactory>collective.ambidexterity.default</defaultFactory>
        <title>Test Integer Field</title>
      </field>
      <field name="test_string_field"
        type="zope.schema.TextLine"
        form:validator="collective.ambidexterity.validate"
      >
        <description/>
        <required>False</required>
        <defaultFactory>collective.ambidexterity.default</defaultFactory>
        <title>Test String Field</title>
      </field>
      <field name="test_choice_field" type="zope.schema.Choice">
        <description/>
        <required>False</required>
        <title>Test Choice Field</title>
        <source>collective.ambidexterity.vocabulary</source>
      </field>
    </schema>

for the Dexterity type "my_simple_type" and we would get::

    portal_resources/ambidexterity/my_simple_type/test_integer_field/default
    portal_resources/ambidexterity/my_simple_type/test_string_field/default
    portal_resources/ambidexterity/my_simple_type/test_string_field/validate
    portal_resources/ambidexterity/my_simple_type/test_choice_field/vocabulary

automatically called as appropriate.

Contribute
----------

- Issue Tracker: https://github.com/collective/collective.ambidexterity/issues
- Source Code: https://github.com/collective/collective.ambidexterity


Support
-------

None!


License
-------

The project is licensed under the GPLv2.
