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

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
import base64, requests, logging

logger = logging.getLogger(__name__)

VIMEO_API_KEY = getattr(settings, 'VIMEO_API_KEY')
VIMEO_API_SECRET = getattr(settings, 'VIMEO_API_SECRET')

VIMEO_API_BASE_URL = "https://api.vimeo.com"


def get_redirect_uri(host):
    return host + reverse("thirdpartyaccounts:vimeo_login_done")

def get_token(code):
    headers = {"Authorization":
               ("basic " + \
                base64.b64encode(VIMEO_API_KEY + ":" + VIMEO_API_SECRET))}
    protocol = getattr(settings, "DEFAULT_PROTOCOL", 'https')
    host = protocol + '://' + Site.objects.get_current().domain
    data = {"grant_type": "authorization_code",
            "code": code,
            "redirect_uri": get_redirect_uri(host)}
    url = "/oauth/access_token"
    response = requests.post(VIMEO_API_BASE_URL + url,
                             data=data,
                             headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        None

def get_video(account, video_id):
    headers = {"Authorization":
               ("Bearer " + account.access_code)}
    url = "/videos/" + video_id
    response = requests.get(VIMEO_API_BASE_URL + url,
                            headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_text_tracks(account, video_id):
    headers = {"Authorization":
               ("Bearer " + account.access_code)}
    url = "/videos/" + video_id + "/texttracks"
    response = requests.get(VIMEO_API_BASE_URL + url,
                            headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_text_track(account, uri):
    headers = {"Authorization":
               ("Bearer " + account.access_code)}
    response = requests.get(VIMEO_API_BASE_URL + uri,
                            headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_values(video_id):
    headers = {"Authorization":
               ("basic " + \
                base64.b64encode(VIMEO_API_KEY + ":" + VIMEO_API_SECRET))}
    data = {"grant_type": "client_credentials"}
    url = "/oauth/authorize/client"
    response = requests.post(VIMEO_API_BASE_URL + url,
                             data=data,
                             headers=headers)
    if response.status_code == 200:
        access_token = response.json()['access_token']
        headers = {"Authorization": "Bearer " + access_token}
        url = "/videos/" + video_id
        response = requests.get(VIMEO_API_BASE_URL + url,
                                headers=headers)
        if response.status_code == 200:
            video_data = response.json()
            small = large = None
            for picture in sorted(video_data['pictures'], key=lambda x: x["width"]):
                if picture['width'] < 120:
                    small = picture['link']
                if picture['width'] < 720:
                    large = picture['link']
            return (video_data["name"],
                    video_data["description"],
                    video_data['duration'],
                    small, large)
    raise Exception("Vimeo API Error")
