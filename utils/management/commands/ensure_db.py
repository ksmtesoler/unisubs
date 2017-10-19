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


from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = u'Ensure the database is up-to-date'

    def handle(self, *args, **kwargs):
        if self.is_db_created():
            self.migrate_existing_db()
        else:
            self.initialize_new_db()

    def is_db_created(self):
        cursor = connection.cursor()
        table_count = cursor.execute("SHOW TABLES")
        return table_count > 0

    def migrate_existing_db(self):
        print('migrating existing database')
        call_command('migrate')

    def initialize_new_db(self):
        print('initializing new database')
        # South overrides syncdb and that makes the commandline flags fail.
        # So we have to pass them as named options.  Note: Need to make sure
        # the options match the internal argparse name.  It's not the same
        # string as the command line option
        call_command('syncdb', migrate_all=True, interactive=False)
        call_command('migrate', fake=True)
        call_command('setup_indexes')
