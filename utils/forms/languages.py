# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
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

"""utils.forms.languages -- form fields for selecting languages."""

from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe

from utils.translation import get_language_choices

class LanguageDropdown(forms.Select):
    """Widget that renders a language dropdown

    Attrs:
        options: space separate string containing language options.  Each one
            of these corresponds to a section on the dropdown.  If present,
            that section will be enabled.  Possible values are "any", "my",
            "popular" and "all".
    """

    def __init__(self, *args, **kwargs):
        super(LanguageDropdown, self).__init__(*args, **kwargs)
        self.options = "any my popular all"

    def render(self, name, value, attrs, choices=()):
        final_attrs = attrs.copy()
        final_attrs['name'] = name
        if 'class' in final_attrs:
            final_attrs['class'] += ' dropdownFilter'
        else:
            final_attrs['class'] = 'dropdownFilter'
        final_attrs['data-language-options'] = self.options
        if value:
            final_attrs['data-initial'] = value
        return mark_safe(u'<select{}></select>'.format(flatatt(final_attrs)))

class LanguageField(forms.ChoiceField):
    widget = LanguageDropdown

    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options', None)
        kwargs['choices'] = get_language_choices()
        super(LanguageField, self).__init__(*args, **kwargs)
        if isinstance(self.widget, LanguageDropdown) and options:
            self.widget.options = options

class MultipleLanguageChoiceField(forms.MultipleChoiceField):
    # TODO: implement a nicer widget for selecting multiple languages
    widget = forms.SelectMultiple

    def __init__(self, *args, **kwargs):
        super(MultipleLanguageChoiceField, self).__init__(*args, **kwargs)
        self._setup_choices()

    def __deepcopy__(self, memo):
        # This is called when we create a new form and bind this field.  We
        # need to reset the choice iter in this case.  This code is copied
        # from ModelChoiceField
        result = super(forms.ChoiceField, self).__deepcopy__(memo)
        result._setup_choices()
        return result

    def _setup_choices(self):
        self._choices = self.widget.choices = self.choice_iter()

    def choice_iter(self):
        for choice in self.calc_language_choices():
            yield choice

    def calc_language_choices(self):
        return get_language_choices()

