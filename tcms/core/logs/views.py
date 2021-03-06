# -*- coding: utf-8 -*-

from __future__ import absolute_import

import six

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from .models import TCMSLogModel

if six.PY3:
    from django.utils.encoding import smart_text as smart_unicode
else:
    from django.utils.encoding import smart_unicode


class TCMSLog(object):
    """TCMS Log"""

    def __init__(self, model):
        super(TCMSLog, self).__init__()
        self.model = model

    def get_new_log_object(self):
        elements = ['who', 'field', 'original_value', 'new_value']

        for element in elements:
            if not hasattr(self, element):
                raise NotImplementedError(
                    'Log does not have attribute {}'.format(element))

        model = self.get_log_model()
        new = model(**self.get_log_create_data())

        return new

    def get_log_model(self):
        """
        Get the log model to create with this class.
        """
        return TCMSLogModel

    def get_log_create_data(self):
        return dict(
            content_object=self.model,
            site_id=settings.SITE_ID,
            who=self.who,
            field=self.field,
            original_value=self.original_value,
            new_value=self.new_value,
        )

    def make(self, who, new_value, field='', original_value=''):
        """Create new log"""
        self.who = who
        self.field = field
        self.original_value = original_value
        self.new_value = new_value

        model = self.get_new_log_object()
        model.save()

    def lookup_content_type(self):
        return ContentType.objects.get_for_model(self.model)

    def get_query_set(self):
        ctype = self.lookup_content_type()
        model = self.get_log_model()

        qs = model.objects.filter(content_type=ctype,
                                  object_pk=smart_unicode(self.model.pk),
                                  site=settings.SITE_ID)
        qs = qs.select_related('who')
        return qs

    def list(self):
        """List the logs"""
        return self.get_query_set().all()
