# -*- coding: utf-8 -*-

# Dexterity's schema editor deletes field attributes and elements that it doesn't
# know how to handle. This means that nearly any use of it will destroy
# synchronization between the FTI and the ambidexterity resources.
# Fortunately, the schema editor publishes an ISchemaModifiedEvent event
# whenever it finishes changing an FTI. Let's watch it and do some automatic
# resynchronization.


from audit import resynchronize_content_type
from utilities import logger


def resync_if_necessary(event):
    logger.info(
        "Schema for %s has been modified. Checking Ambidexterity synchronization.",
        event.object.getId(),
    )
    resynchronize_content_type(event.object.getId())
