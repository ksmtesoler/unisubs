# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
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

"""externalsites.subfetch -- Fetch subtitles from external services
"""

import logging

import unilangs

from externalsites import google
from externalsites.models import YouTubeAccount
from subtitles.models import ORIGIN_IMPORTED
from subtitles import pipeline
from subtitles.signals import subtitles_imported
from videos.models import VIDEO_TYPE_YOUTUBE

logger = logging.getLogger('externalsites.subfetch')

def convert_language_code(lc):
    """
    Convert from a YouTube language code to an Amara one
    """
    try:
        return unilangs.LanguageCode(lc, 'youtube_with_mapping').encode('internal')
    except KeyError:
        # Error looking up the youtube language code.  Return none and we'll
        # skip importing the subtitles.
        return None

def should_fetch_subs(video_url):
    return video_url.type == VIDEO_TYPE_YOUTUBE

def fetch_subs(video_url, user=None, team=None):
    if video_url.type == VIDEO_TYPE_YOUTUBE:
        fetch_subs_youtube(video_url, user, team)
    else:
        logger.warn("fetch_subs() bad video type: %s" % video_url.type)

def fetch_subs_youtube(video_url, user, team):
    video_id = video_url.videoid
    channel_id = video_url.owner_username
    possible_accounts = set()
    if team is not None and user is not None:
        for account in YouTubeAccount.objects.get_accounts_for_user_and_team(user, team):
            if account.fetch_initial_subtitles:
                possible_accounts.add(account)
    if channel_id:
        try:
            account = YouTubeAccount.objects.get(channel_id=channel_id)
            if account.fetch_initial_subtitles:
                possible_accounts.add(account)
        except:
            pass
    account = find_youtube_account(video_id, possible_accounts)
    if account is None:
        logger.warn("fetch_subs() no available credentials.")
        return
    existing_langs = set(
        l.language_code for l in
        video_url.video.newsubtitlelanguage_set.having_versions()
    )
    access_token = google.get_new_access_token(account.oauth_refresh_token)
    captions_list = google.captions_list(access_token, video_id)
    versions = []
    for caption_id, language_code, caption_name in captions_list:
        language_code = convert_language_code(language_code)
        if language_code and language_code not in existing_langs:
            dfxp = google.captions_download(access_token, caption_id)
            try:
                version = pipeline.add_subtitles(video_url.video, language_code, dfxp,
                                                 note="From youtube", complete=True,
                                                 origin=ORIGIN_IMPORTED)
                versions.append(version)
            except Exception, e:
                logger.error("Exception while importing subtitles " + str(e))
    if len(versions) > 0:
        subtitles_imported.send(sender=versions[0].subtitle_language, versions=versions)

def find_youtube_account(video_id, possible_accounts):
    video_info = google.get_video_info(video_id, possible_accounts)
    for account in possible_accounts:
        if account.channel_id == video_info.channel_id:
            return account
    return None
