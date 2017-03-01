# Amara, universalsubtitles.org
#
# Copyright (C) 2017 Participatory Culture Foundation
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

import django.db.transaction
import django.utils.html
import django.template.defaultfilters

from utils.compat import xact
from utils.compat import html as newer_html

def monkeypatch_old_code():
    django.db.transaction.atomic = xact.xact
    django.utils.html.urlize = newer_html.urlize
    django.template.defaultfilters.urlize_impl = newer_html.urlize
