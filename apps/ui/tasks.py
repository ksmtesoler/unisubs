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

import logging

from celery import current_task
from celery.task import task

logger = logging.getLogger(__name__)

@task(queue='priority')
def process_management_form(FormClass, pickle_state):
    def progress_callback(current, total):
        current_task.update_state(state='PROGRESS', meta={
            'current': current,
            'total': total,
        })
    try:
        form = FormClass.restore_from_pickle_state(pickle_state)
        if not form.is_valid():
            current_task.update_state(state='FAILURE', meta={
                'error_messages': [
                    unicode(e) for e in form.errors
                ]
            })
            return
        form.submit(progress_callback)
        current_task.update_state(state='SUCCESS', meta={
            'message': form.message(),
            'error_messages': form.error_messages(),
        })
    except:
        logger.warn("Error processing form", exc_info=True)
        current_task.update_state(state='FAILURE')
