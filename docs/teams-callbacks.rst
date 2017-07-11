========================
HTTP Callbacks for Teams
========================

Enterprise customers can register an http callback so that activity on their
teams will fire an HTTP POST request.

To register your Team to receive HTTP notfications get in contact with us,
this process is done manually, there is no UI for this over the website at the
moment. You can also contact us to inquire about any custom notifications.

Pick a URL where you'd like to get notified. Each team can have their own
URL, or a URL can be used amongst serveral teams (for example in a public /
private team setup) We recomend the URL uses https for safer communication.

Notification Details
====================

We can send notifications for various events, depending on what your team is interested in.
Currently, we send the following notifications:

Video notifications
-------------------

Video notifications always include the following data::

    event, amara_video_id, youtube_video_id, team, project

They can also include primary_team if the video being worked on belongs to another team.

    on_video_added
        Sent when a video is added to your team, or moved to your team from another team.

        Additional data: old_team (if video is added to a new team)
    on_video_removed
        Sent when a video is removed from your team, or moved to another team.

        Additional data: new_team (if moved from another team)
    on_video_url_made_primary
        Sent when one of the URLs for a video on your team is set as the primary URL.

        Additional data: url
    on_video_moved_project
        Sent when a video on your team is moved to a new project.

        Additional data: old_project
    on_subtitles_published
        Sent when a new subtitle version for a video on your team is published.

        Additional data: language_code, amara_version
    on_subtitles_deleted
        Sent when subtitles are deleted for a video on your team.

        Additional data: language_code

User notifications
------------------

User notifications always include the following data::

    event, username, team

They can also include primary_team if the video being worked on belongs to another team.

    on_user_added
        Sent when a user is added to your team.
    on_user_removed
        Sent when a user is removed from your team.
    on_user_info_updated
        Sent when a team member's profile information is changed.


For each event we can customize the data that is sent with the notification.
This includes anything available via the API.

Also, each notification will include a number in the POST data.  This is an
integer that increments by 1 for each notification we send you.  You can use
the number field to check if you missed any notifications.

To view previously sent notifications use the :ref:`Team Notifications API <api_notifications>`.
