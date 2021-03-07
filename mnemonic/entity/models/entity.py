import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from mnemonic.core.models import BaseModel
from .base import EntityBase
from .twitter import TwitterMixin

_LOG = logging.getLogger(__name__)


class OrganizationType(EntityBase):
    pass


class Organization(TwitterMixin):
    type = models.ForeignKey(OrganizationType, on_delete=models.CASCADE)

    def __str__(self):
        return '%s:%s' % (self.type, self.name)


class Person(TwitterMixin):
    pass


class RelationshipType(EntityBase):
    pass


class Relationship(BaseModel):
    from_entity_content_type = models.ForeignKey(ContentType,
                                                 on_delete=models.CASCADE,
                                                 related_name='from_entity_content_type')
    from_entity_object_id = models.PositiveIntegerField()
    from_entity = GenericForeignKey('from_entity_content_type', 'from_entity_object_id')

    to_entity_content_type = models.ForeignKey(ContentType,
                                               on_delete=models.CASCADE,
                                               related_name='to_entity_content_type')
    to_entity_object_id = models.PositiveIntegerField()
    to_entity = GenericForeignKey('to_entity_content_type', 'to_entity_object_id')

    type = models.ForeignKey(RelationshipType, on_delete=models.CASCADE)

    def __str__(self):
        return '[%s]-(%s)->[%s]' % (self.from_entity, self.type, self.to_entity)
