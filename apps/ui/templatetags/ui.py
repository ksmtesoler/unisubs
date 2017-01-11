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

from django import template
from django.utils.translation import ungettext
from django.utils.translation import ugettext as _

from utils.dates import now
from utils.text import fmt

register = template.Library()

@register.filter
def date(dt):
    return u'{}/{}/{}'.format(dt.month, dt.day, dt.year)

@register.filter
def elapsed_time(dt, comparison=None):
    """Works like the default timesince filter, but with customized display

    It has a different name to avoid confusion.  Otherwise it would be easy to
    forget to import this templatetag library and use the default timesince.
    """
    if comparison is None:
        comparison = now()
    if comparison <= dt:
        return _('now')

    delta = comparison - dt
    if delta.seconds < 60:
        return _('now')
    elif delta.seconds < 60 * 60:
        minutes = int(round(delta.seconds / 60.0))
        return fmt(ungettext(u'%(count)s minute ago',
                             u'%(count)s minutes ago',
                             minutes),
                   count=minutes)
    elif delta.days < 1:
        hours = int(round(delta.seconds / 60.0 / 60.0))
        return fmt(ungettext(u'%(count)s hours ago',
                             u'%(count)s hours ago',
                             hours),
                   count=hours)
    elif delta.days < 7:
        days = int(round(delta.days + delta.seconds / 60 / 60 / 24))
        return fmt(ungettext('%(count)s day ago',
                             '%(count)s days ago',
                             days), count=days)
    else:
        return date(dt)

@register.filter
def due_date(dt, comparison=None):
    """Works like the default timesince filter, but with customized display

    It has a different name to avoid confusion.  Otherwise it would be easy to
    forget to import this templatetag library and use the default timesince.
    """
    if comparison is None:
        comparison = now()
    if comparison >= dt:
        return _('Due now')

    delta = dt - comparison
    if delta.seconds < 60:
        return _('Due now')
    elif delta.seconds < 60 * 60:
        minutes = int(round(delta.seconds / 60.0))
        return fmt(ungettext(u'Due in %(count)s minute',
                             u'Due in %(count)s minutes',
                             minutes),
                   count=minutes)
    elif delta.days < 1:
        hours = int(round(delta.seconds / 60.0 / 60.0))
        return fmt(ungettext(u'Due in %(count)s hours',
                             u'Due in %(count)s hours',
                             hours),
                   count=hours)
    elif delta.days < 7:
        days = int(round(delta.days + delta.seconds / 60 / 60 / 24))
        return fmt(ungettext('Due in %(count)s day',
                             'Due in %(count)s days',
                             days), count=days)
    else:
        return fmt(_(u'Due %(date)s'), date=date(dt))
