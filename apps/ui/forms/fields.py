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

import json

from django.utils.translation import ugettext_lazy as _
from django import forms

from utils import translation
from ui.forms import widgets

class AmaraChoiceFieldMixin(object):
    def __init__(self, allow_search=True, border=False, *args, **kwargs):
        super(AmaraChoiceFieldMixin, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'select'
        self.border = border
        if not allow_search:
            self.widget.attrs['nosearchbox'] = 1

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        self._choices = list(value)
        self._setup_widget_choices(value)

    choices = property(_get_choices, _set_choices)

    def _setup_widget_choices(self, choices):
        placeholder = None
        widget_choices = []
        for choice in choices:
            if choice[0]:
                widget_choices.append(choice)
            else:
                placeholder = choice[1]
        self.widget.choices = choices
        if placeholder:
            self.widget.attrs['placeholder'] = placeholder
            self.widget.attrs['data-allow-clear'] = 1
        else:
            self.widget.attrs.pop('placeholder', None)
            self.widget.attrs.pop('data-allow-clear', None)

class AmaraChoiceField(AmaraChoiceFieldMixin, forms.ChoiceField):
    pass

class AmaraMultipleChoiceField(AmaraChoiceFieldMixin,
                               forms.MultipleChoiceField):
    def __init__(self, max_choices=None, *args, **kwargs):
        super(AmaraMultipleChoiceField, self).__init__(*arg, **kwargs)
        if max_choices is not None:
            self.widget.attrs['max-allowed-choices'] = max_choices

class LanguageFieldMixin(AmaraChoiceFieldMixin):
    def __init__(self, options="null my popular all",
                 placeholder=_("Select language"), *args, **kwargs):
        kwargs['choices'] = translation.get_language_choices()
        super(LanguageFieldMixin, self).__init__(*args, **kwargs)
        self.widget.attrs['data-language-options'] = options
        if 'null' in options:
            self.widget.attrs['placeholder'] = placeholder
            self.widget.attrs['data-allow-clear'] = 1

    def exclude(self, languages):
        self.widget.attrs['data-exclude'] = json.dumps(languages)
        self.choices = [
            c for c in self.choices if c[0] not in languages
        ]

    def limit_to(self, languages):
        self.widget.attrs['data-limit-to'] = json.dumps(languages)
        self.choices = [
            c for c in self.choices if c[0] in languages
        ]

    def _setup_widget_choices(self, choices):
        pass

class LanguageField(LanguageFieldMixin, forms.ChoiceField):
    pass

class MultipleLanguageField(LanguageFieldMixin, forms.MultipleChoiceField):
    pass

class SearchField(forms.CharField):
    widget = widgets.SearchBar

    def __init__(self, **kwargs):
        label = kwargs.pop('label')
        kwargs['label'] = ''
        super(SearchField, self).__init__(**kwargs)
        if label:
            self.widget.attrs['placeholder'] = label

__all__ = [
    'AmaraChoiceField', 'AmaraMultipleChoiceField', 'LanguageField',
    'MultipleLanguageField', 'SearchField',
]
