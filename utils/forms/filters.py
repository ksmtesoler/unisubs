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

class FiltersForm(forms.Form):
    """Form to handle the filters on a page

    These forms are intended to be used with GET params, rather than POST
    data.  This means we need some special code to avoid them thinking they're
    bound when there is another GET param that doesn't have to do with the
    form (e.g. page).
    """
    def __init__(self, get_data=None, **kwargs):
        super(FiltersForm, self).__init__(data=self.calc_data(get_data),
                                          **kwargs)

    def calc_data(self, get_data):
        if get_data is None:
            return None
        data = {
            name: get_data[name]
            for name in self.base_fields.keys()
            if name in get_data
        }
        return data if data else None
