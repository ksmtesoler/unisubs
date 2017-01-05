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
        self.url = reverse(view_name, args=args, kwargs=kwargs)

class Tab(Link):
    def __init__(self, name, label, view_name, *args, **kwargs):
        self.name = name
        super(Tab, self).__init__(label, view_name, *args, **kwargs)

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
