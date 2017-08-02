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

from itertools import chain

from django.forms import widgets
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class AmaraLanguageSelectMixin(object):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = ''
        if attrs is None:
            attrs = {}
        if isinstance(value, basestring):
            # single-select
            attrs['data-initial'] = value
        else:
            # multi-select
            attrs['data-initial'] = ':'.join(value)
        return super(AmaraLanguageSelectMixin, self).render(
            name, value, attrs, choices)

    def render_options(self, choices, selected_choices):
        # The JS code populates the options
        return ''

class AmaraLanguageSelect(AmaraLanguageSelectMixin, widgets.Select):
    pass

class AmaraLanguageSelectMultiple(AmaraLanguageSelectMixin,
                                  widgets.SelectMultiple):
    pass

class AmaraRadioSelect(widgets.RadioSelect):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = ''
        choices = list(chain(self.choices, choices))
        output = [u'<ul>']
        for i, choice in enumerate(choices):
            input_id = '{}_{}'.format(attrs['id'], i)
            output.extend([
                u'<li><div class="radio">',
                self.render_input(name, value, choice, input_id),
                self.render_label(name, value, choice, input_id),
                u'</div></li>',
            ])
        output.append(u'</ul>')
        return mark_safe(u''.join(output))

    def render_input(self, name, value, choice, input_id):
        attrs = {
            'id': input_id,
            'type': 'radio',
            'name': name,
            'value': force_unicode(choice[0]),
        }
        if choice[0] == value:
            attrs['checked'] = 'checked'
        return u'<input{}>'.format(flatatt(attrs))

    def render_label(self, name, value, choice, input_id):
        return u'<label for="{}"><span></span>{}</label>'.format(
            input_id, force_unicode(choice[1]))

class SearchBar(widgets.TextInput):
    def render(self, name, value, attrs=None):
        input = super(SearchBar, self).render(name, value, attrs)
        return mark_safe(u'<div class="searchbar">'
                         '<label class="sr-only">Search</label>'
                         '{}'
                         '</div>'.format(input))

__all__ = [
    'AmaraRadioSelect', 'SearchBar',
]
