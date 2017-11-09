#!/usr/bin/env python
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

from optparse import make_option
import multiprocessing
import signal
import sys
import time

from django.core.management.base import BaseCommand
from django.db import connection

from videos.models import VideoFeed

# Time we aim to update all feeds (in seconds)
PASS_DURATION = 3600

class Command(BaseCommand):
    """
    Long-running process that updates our video feeds
    """

    option_list = BaseCommand.option_list + (
        make_option('-w', '--workers', default=4,
                    type=int),
    )
    def handle(self, *args, **options):
        self.quitting = False
        self.pool = multiprocessing.Pool(options['workers'], init_worker)
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)
        self.loop()

    def loop(self):
        while not self.quitting:
            feed_ids = VideoFeed.objects.values_list('id', flat=True)
            seconds_per_feed = float(PASS_DURATION) / len(feed_ids)
            for feed_id in feed_ids:
                if self.quitting:
                    break
                self.pool.apply_async(update_feed, args=(feed_id,))
                time.sleep(seconds_per_feed)

    def terminate(self, signum, frame):
        print '\nterminating'
        sys.stdout.flush()
        self.quitting = True
        self.pool.close()
        self.pool.join()

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def update_feed(feed_id):
    try:
        video_feed = VideoFeed.objects.get(pk=feed_id)
        video_feed.update()
    except VideoFeed.DoesNotExist:
        print('update_video_feed: VideoFeed does not exist. ID: %s'.format(
            feed_id))
    else:
        print('Updated {}'.format(video_feed))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
