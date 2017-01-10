# Amara, universalsubtitles.org
#
# Copyright (C) 2016 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""utils.frontend -- frontend-related classes

This module contains a few utility classes that's used by the views code.
"""

from __future__ import absolute_import

from collections import namedtuple
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from utils.text import fmt

class Link(object):
    def __init__(self, label, view_name, *args, **kwargs):
        self.label = label
        if '/' in view_name:
            # URL path passed in, don't try to reverse it
            self.url = view_name
        else:
            self.url = reverse(view_name, args=args, kwargs=kwargs)

    def __unicode__(self):
        return mark_safe(u'<a href="{}">{}</a>'.format(self.url, self.label))

    def __eq__(self, other):
        return (isinstance(other, Link) and
                self.label == other.label and
                self.url == other.url)

class CTA(Link):
    def __init__(self, label, icon, view_name, *args, **kwargs):
        super(CTA, self).__init__(label, view_name, *args, **kwargs)
        self.icon = icon

    def __unicode__(self):
        return mark_safe(u'<a href="{}" class="button cta">'
                         u'<i class="icon {}"></i> {}</a>'.format(
                             self.url, self.icon, self.label))

    def __eq__(self, other):
        return (isinstance(other, Link) and
                self.label == other.label and
                self.icon == other.icon and
                self.url == other.url)

class Tab(Link):
    def __init__(self, name, label, view_name, *args, **kwargs):
        self.name = name
        super(Tab, self).__init__(label, view_name, *args, **kwargs)

    def __eq__(self, other):
        return (isinstance(other, Tab) and
                self.name == other.name and
                self.label == other.label and
                self.url == other.url)

class SectionWithCount(list):
    """Section that contains a list of things with a count in the header
    """
    header_template = _('%(header)s <span class="count">(%(count)s)</span>')
    def __init__(self, header_text):
        self.header_text = header_text

    def header(self):
        return mark_safe(fmt(self.header_template, header=self.header_text,
                             count=len(self)))

__all__ = [
    'Link', 'Tab', 'SectionWithCount',
]
