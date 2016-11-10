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

from django import forms
from django.utils.translation import ugettext_lazy as _

from utils.text import fmt

class ManagementForm(forms.Form):
    """
    Management forms are forms that are used on the manage team videos page and
    similar pages.

    Management forms operated inside a paginated list of objects, where each
    object on the current page can be selected.  The team video management
    page is a good example of this.  When the save() method is called, we
    operate on all selected objects.  There is an include all checkbox, which
    if checked, changes this so we operate on all objects on all pages.

    Management forms are intended to be used in the action bar and have a couple
    of attributes to support displaying them as buttons there and opening the
    form via an AJAX call.
    """
    # unique slug to identify the form
    name = NotImplemented
    # human-friendly label
    label = NotImplemented
    # css class for the button
    css_class = 'cta'

    include_all = forms.BooleanField(label='', required=False)
    include_all_label = _("Include all %(count) objects")
    save_queryset_select_related = None

    def __init__(self, queryset, selection, all_selected,
                 *args, **kwargs):
        """Create a ManagementForm

        Args:
            queryset: queryset of all possible objects
            selection: list of ids for selected objects
            all_selected: are all objects on the page selected.
        """
        super(ManagementForm, self).__init__(*args, **kwargs)
        self.queryset = queryset
        self.selection = selection
        self.setup_include_all(queryset, selection, all_selected)
        self.setup_fields()

    def save(self):
        self.perform_save(self.get_save_queryset())

    def single_selection(self):
        return len(self.selection) == 1

    def get_first_object(self):
        return self.queryset.get(id=self.selection[0])

    def get_save_queryset(self):
        """Get a queryset of objects to save.

        This queryset will be passed to perform_save() 
        """
        qs = self.queryset
        if not self.cleaned_data.get('include_all'):
            qs = qs.filter(id__in=self.selection)
        self.count = qs.count()
        if self.save_queryset_select_related:
            qs = qs.select_related(*self.save_queryset_select_related)
        return qs

    def setup_include_all(self, queryset, selection, all_selected):
        if not all_selected:
            del self.fields['include_all']
        else:
            total_objects = queryset.count()
            if total_objects <= len(selection):
                del self.fields['include_all']
            else:
                self.fields['include_all'].label = fmt(
                    self.include_all_label, count=total_objects)

    def setup_fields(self):
        """Override this if you need to dynamically setup the form fields."""
        pass

    def perform_save(self, qs):
        """Does the work for the save() method.

        Args:
            qs -- queryset of objects that should be operated on.
        """
        raise NotImplementedError()

    def message(self):
        """Success message after the form is submitted."""
        raise NotImplementedError()
