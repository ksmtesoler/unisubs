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

from base import VideoType
from externalsites import google
from utils.memoize import memoize

logger = logging.getLogger(__file__)

class GoogleDriveVideoType(VideoType):

    abbreviation = 'I'
    name = 'Google Drive'
    site = 'drive.google.com'

    def __init__(self, url):
        self.url = url
        self.file_id = self._get_file_id()

    @property
    def video_id(self):
        return self.file_id

    def player_url(self):
        try:
            return self.get_drive_file_info().embed_url
        except google.APIError():
            return None

    def _get_file_id(self):
        return google.get_drive_file_id(self.url)

    def convert_to_video_url(self):
        # Drive files have a lot of URLs associated with them.  It's not clear
        # which one we should use.  The most logical is the API endpoint,
        # however even that changes when google updates the version.  So we
        # create our own custom URI
        return 'drive:///{}'.format(self.file_id)

    @classmethod
    def matches_video_url(cls, url):
        return google.matches_drive_url(url)

    @memoize
    def get_drive_file_info(self):
        try:
            return google.get_drive_file_info(self.file_id)
        except google.APIError:
            logger.warn("Error getting drive file info {}".format(
                self.file_id))
            raise

    def set_values(self, video, user, team, video_url):
        try:
            video_info = self.get_drive_file_info()
        except google.APIError:
            return
        if not video_info.mime_type.startswith('video/'):
            logger.warn("{} is not a video file".format(self.file_id))
            return
        if video_info.title is not None:
            video.title = video_info.title
        if video_info.description is not None:
            video.description = video_info.description
        if video_info.duration is not None:
            video.duration = video_info.duration
        if video_info.thumbnail_url is not None:
            video.thumbnail = video_info.thumbnail_url
