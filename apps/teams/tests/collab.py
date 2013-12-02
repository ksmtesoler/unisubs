# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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

from __future__ import absolute_import

from django.test import TestCase
from factory import make_factory

from teams.models import (Collaboration, CollaborationLanguage,
                          CollaborationWorkflow)
from teams.permissions_const import (
    ROLE_OWNER, ROLE_ADMIN, ROLE_MANAGER, ROLE_CONTRIBUTOR,
)
from utils.factories import *
from utils.test_utils import reload_model

# make Collaborator.ROLE values global for easier typing
SUBTITLER = Collaborator.SUBTITLER
REVIEWER = Collaborator.REVIEWER
APPROVER = Collaborator.APPROVER

class CollaborationLanguageTestCase(TestCase):
    def setUp(self):
        self.team = CollaborationTeamFactory.create()

    def check_languages(self, correct_languages):
        collab_langs = CollaborationLanguage.objects.for_team(self.team)
        self.assertEquals(set([cl.language_code for cl in collab_langs]),
                          set(correct_languages))
        for cl in collab_langs:
            self.assertEquals(cl.team_id, self.team.id)
            self.assertEquals(cl.project_id, None)

    def check_languages_for_member(self, member, correct_languages):
        self.assertEquals(
            set(CollaborationLanguage.objects.languages_for_member(member)),
            set(correct_languages))

    def update_languages(self, languages):
        CollaborationLanguage.objects.update_for_team(self.team, languages)

    def test_languages_for_team(self):
        self.check_languages([])
        self.update_languages(['en', 'fr', 'de'])
        self.check_languages(['en', 'fr', 'de'])
        self.update_languages(['en', 'pt-br'])
        self.check_languages(['en', 'pt-br'])

    def test_languages_for_user(self):
        user = UserFactory.create(languages=['en', 'fr', 'pt-br'])
        member = TeamMemberFactory.create(team=self.team, user=user)
        # when no languages are defined for the team, languages_for_member()
        # should return all languages for the user
        self.check_languages_for_member(member, ['en', 'fr', 'pt-br'])
        # when languages are defined for the team, languages_for_member()
        # should return the intersection of the team's languages and the
        # user's language
        self.update_languages(['en', 'fr'])
        self.check_languages_for_member(member, ['en', 'fr'])

class CollaborationStateTestCase(TestCase):
    def setUp(self):
        self.team = CollaborationTeamFactory.create()
        self.collaboration = CollaborationFactory.create(
            team=self.team)
        self.subtitler = TeamMemberFactory.create(team=self.team)
        self.reviewer = TeamMemberFactory.create(team=self.team)
        self.approver = TeamMemberFactory.create(team=self.team)

    def set_completion_policy(self, policy):
        self.team.workflow.completion_policy = policy
        self.team.workflow.save()

    def check_state(self, collaboration_state):
        self.assertEquals(self.collaboration.state, collaboration_state)

    def check_complete(self):
        self.assertEquals(self.collaboration.state, Collaboration.COMPLETE)
        for collaborator in self.collaboration.collaborators.all():
            self.assertEquals(collaborator.complete, True)

    def check_not_complete(self):
        self.assertNotEquals(self.collaboration.state, Collaboration.COMPLETE)
        for collaborator in self.collaboration.collaborators.all():
            self.assertEquals(collaborator.complete, False)

    def test_states_before_complete(self):
        self.check_state(Collaboration.NEEDS_SUBTITLER)

        self.collaboration.add_collaborator(self.subtitler, SUBTITLER)
        self.check_state(Collaboration.BEING_SUBTITLED)

        self.collaboration.mark_endorsed(self.subtitler)
        self.check_state(Collaboration.NEEDS_REVIEWER)

        self.collaboration.add_collaborator(self.reviewer, REVIEWER)
        self.check_state(Collaboration.BEING_REVIEWED)

        self.collaboration.mark_endorsed(self.reviewer)
        self.check_state(Collaboration.NEEDS_APPROVER)

        self.collaboration.add_collaborator(self.approver, APPROVER)
        self.check_state(Collaboration.BEING_APPROVED)

    def test_complete_anyone(self):
        self.set_completion_policy(CollaborationWorkflow.COMPLETION_ANYONE)
        self.check_not_complete()
        self.collaboration.add_collaborator(self.subtitler, SUBTITLER)
        self.check_not_complete()
        self.collaboration.mark_endorsed(self.subtitler)
        self.check_complete()

    def test_complete_review(self):
        self.set_completion_policy(CollaborationWorkflow.COMPLETION_REVIEWER)
        self.collaboration.add_collaborator(self.subtitler, SUBTITLER)
        self.check_not_complete()
        self.collaboration.mark_endorsed(self.subtitler)
        self.check_not_complete()
        self.collaboration.add_collaborator(self.reviewer, REVIEWER)
        self.check_not_complete()
        self.collaboration.mark_endorsed(self.reviewer)
        self.check_complete()

    def test_complete_approval(self):
        self.set_completion_policy(CollaborationWorkflow.COMPLETION_APPROVER)
        self.collaboration.add_collaborator(self.subtitler, SUBTITLER)
        self.check_not_complete()
        self.collaboration.mark_endorsed(self.subtitler)
        self.check_not_complete()
        self.collaboration.add_collaborator(self.reviewer, REVIEWER)
        self.check_not_complete()
        self.collaboration.mark_endorsed(self.reviewer)
        self.check_not_complete()
        self.collaboration.add_collaborator(self.approver, APPROVER)
        self.check_not_complete()
        self.collaboration.mark_endorsed(self.approver)
        self.check_complete()

class CollaborationProjectTestCase(TestCase):
    def setUp(self):
        self.team = CollaborationTeamFactory()
        self.project = ProjectFactory(team=self.team)
        self.project2 = ProjectFactory(team=self.team)

    def test_set_project(self):
        tv = TeamVideoFactory.create(team=self.team, project=self.project)
        collaboration = CollaborationFactory(team_video=tv)
        self.assertEquals(collaboration.project, self.project)

    def test_update_project(self):
        tv = TeamVideoFactory.create(team=self.team, project=self.project)
        collaboration = CollaborationFactory(team_video=tv)
        tv.project = self.project2
        tv.save()
        collaboration = reload_model(collaboration)
        self.assertEquals(collaboration.project, self.project2)

class CollaborationTeamTestCase(TestCase):
    # Test the team-related fields of Collaboration.  This is a bit tricky
    # because the team that owns the team video may or may not actually be the
    # team that's working on the collaboration

    def setUp(self):
        self.team = CollaborationTeamFactory.create()
        self.collaboration = CollaborationFactory.create(
            team_video__team=self.team)

    def test_team_is_null_before_collaborators(self):
        self.assertEquals(self.collaboration.team, None)

    def test_owning_team_works_on_collaboration(self):
        member = TeamMemberFactory.create(team=self.team)
        self.collaboration.add_collaborator(member, SUBTITLER)
        self.assertEquals(self.collaboration.team, self.team)

    def test_other_team_works_on_collaboration(self):
        other_team = CollaborationTeamFactory.create()
        member = TeamMemberFactory.create(team=other_team)
        self.collaboration.add_collaborator(member, SUBTITLER)
        self.assertEquals(self.collaboration.team, other_team)

    def test_only_team_members_can_join(self):
        # test that only members of the team working on the collaboration can
        # join it.
        self.team.workflow.only_1_subtitler = False
        self.team.workflow.save()

        member = TeamMemberFactory.create(team=self.team)
        self.collaboration.add_collaborator(member, SUBTITLER)
        self.assertEquals(self.collaboration.team, self.team)

        # if a user from another team tries to join the collaboration, it
        # should fail.
        other_team = CollaborationTeamFactory.create()
        self.assertRaises(ValueError, self.collaboration.add_collaborator,
                          TeamMemberFactory.create(team=other_team),
                          SUBTITLER)

class CollaborationCreationTestCase(TestCase):
    def setUp(self):
        self.team = CollaborationTeamFactory.create()
        self.team_video = TeamVideoFactory.create(team=self.team)

    def check_collaboration_languages(self, team_video, correct_languages):
        collaborations = self.team_video.collaboration_set.all()
        self.assertEquals(set(c.language_code for c in collaborations),
                          set(correct_languages))

    def test_create_on_language_update(self):
        CollaborationLanguage.objects.update_for_team(self.team, ['en', 'es'])
        self.check_collaboration_languages(self.team_video, ['en', 'es'])

    def test_delete_on_language_update(self):
        CollaborationLanguage.objects.update_for_team(self.team, ['en', 'es'])
        self.check_collaboration_languages(self.team_video, ['en', 'es'])
        # when we change the language, we should delete collaborations
        CollaborationLanguage.objects.update_for_team(self.team, ['fr', 'de'])
        self.check_collaboration_languages(self.team_video, ['fr', 'de'])
        # but if collaborators have joined, we shouldn't delete them
        user = TeamMemberFactory.create(team=self.team)
        collaboration = self.team_video.collaboration_set.get(
            language_code='fr')
        collaboration.add_collaborator(user, Collaborator.SUBTITLER)
        CollaborationLanguage.objects.update_for_team(self.team, ['pt-br'])
        self.check_collaboration_languages(self.team_video, ['fr', 'pt-br'])

    def test_create_on_new_teamvideo(self):
        CollaborationLanguage.objects.update_for_team(self.team, ['en', 'es'])
        new_team_video = TeamVideoFactory.create(team=self.team)
        self.check_collaboration_languages(new_team_video, ['en', 'es'])


class CollaborationManagerDashboardTestCase(TestCase):
    def setUp(self):
        self.team = CollaborationTeamFactory()
        self.member = TeamMemberFactory(team=self.team, role=ROLE_MANAGER,
                                        user__languages=['en', 'es', 'fr'])
        self.colleague1 = TeamMemberFactory(team=self.team, role=ROLE_MANAGER)
        self.colleague2 = TeamMemberFactory(team=self.team, role=ROLE_MANAGER)
        self.colleague3 = TeamMemberFactory(team=self.team, role=ROLE_MANAGER)

        # make another team that member.user is also a member of.  We
        # shouldn't return collaborations for this team, even though the user
        # may match.
        self.other_team = CollaborationTeamFactory()
        self.other_team_member = TeamMemberFactory(team=self.other_team,
                                                   user=self.member.user)
        # make a third team that has a project shared with us.  We should
        # return collaborations for this project if they haven't been started
        # yet.
        self.shared_project = ProjectFactory.create(shared_teams=[self.team])

        self.make_collaboration = make_factory(CollaborationFactory,
                                               team_video__team=self.team,
                                               language_code='en')

    def check_joined(self, correct_collaborations):
        collaborations_and_collaborators = [
            (c, c.collaborators.get(user=self.member.user))
            for c in correct_collaborations
        ]
        for_dashboard = Collaboration.objects.for_dashboard(self.member)
        self.assertEquals(set(for_dashboard['joined']),
                          set(collaborations_and_collaborators))

    def check_can_join(self, correct_collaborations):
        for_dashboard = Collaboration.objects.for_dashboard(self.member)
        self.assertEquals(set(for_dashboard['can_join']),
                          set(correct_collaborations))
        self.check_can_join_order(for_dashboard['can_join'])

    def check_can_join_order(self, collaborations):
        if not collaborations:
            return
        # check that the collaborations are ordered by state
        state_order = [
            Collaboration.NEEDS_SUBTITLER,
            Collaboration.BEING_SUBTITLED,
            Collaboration.NEEDS_REVIEWER,
            Collaboration.BEING_REVIEWED,
            Collaboration.NEEDS_APPROVER,
            Collaboration.BEING_APPROVED,
        ]
        last_index = state_order.index(collaborations[0].state)
        for i, collaboration in enumerate(collaborations[1:]):
            if (state_order.index(collaboration.state) < last_index):
                raise AssertionError(
                    "Collabortions out of order (%s followed by %s)" % (
                        collaboration[i-1].get_state_display(),
                        collaboration[i].get_state_display()))

    def test_joined(self):
        # we should return these because member is part of the collaboration
        joined = [
            self.make_collaboration(subtitler=self.member),
            self.make_collaboration(endorsed_subtitler=self.colleague1,
                                    reviewer=self.member),
            self.make_collaboration(endorsed_subtitler=self.colleague1,
                                    endorsed_reviewer=self.colleague2,
                                    approver=self.member)
        ]
        # we shouldn't return these because member is not part of the
        # collaboration
        self.make_collaboration(subtitler=self.colleague1)
        self.make_collaboration(endorsed_subtitler=self.colleague1,
                                endorsed_reviewer=self.colleague2)
        # We shouldn't return this one because the collaboration is complete
        self.make_collaboration(endorsed_subtitler=self.member,
                                endorsed_reviewer=self.colleague1,
                                endorsed_approver=self.colleague2)
        # We shouldn't return this one because it's for another team
        self.make_collaboration(team_video__team=self.other_team,
                                endorsed_subtitler=self.other_team_member)
        self.check_joined(joined)

    def test_can_join(self):
        # Collaborations that the user can start subtitling
        needs_subtitler = [
            self.make_collaboration(),
            self.make_collaboration(language_code='es'),
            self.make_collaboration(language_code='fr'),
            self.make_collaboration(
                team_video__team=self.shared_project.team,
                team_video__project=self.shared_project,
                language_code='en')
        ]
        # Collaborations that the user can join
        needs_reviewer = [
            self.make_collaboration(endorsed_subtitler=self.colleague1),
            self.make_collaboration(language_code='es',
                                    endorsed_subtitler=self.colleague1),
        ]

        needs_approver = [
            self.make_collaboration(endorsed_subtitler=self.colleague1,
                                    endorsed_reviewer=self.colleague2),
            self.make_collaboration(language_code='fr',
                                    endorsed_subtitler=self.colleague1,
                                    endorsed_reviewer=self.colleague2),
        ]
        # Collaborations the user can join depending on the value of the
        # only_1_subtitler/only_1_reviewer/only_1_approver
        can_join_if_not_only_1 = [
            self.make_collaboration(subtitler=self.colleague1),
            self.make_collaboration(endorsed_subtitler=self.colleague1,
                                    reviewer=self.colleague2),
            self.make_collaboration(endorsed_subtitler=self.colleague1,
                                    endorsed_reviewer=self.colleague2,
                                    approver=self.colleague3),
        ]
        # can't join this one because it's owned by a different team
        self.make_collaboration(team_video__team=self.other_team)
        # can't join it's not for a preferred language
        self.make_collaboration(language_code='de')
        self.make_collaboration(language_code='pt-br',
                                endorsed_subtitler=self.colleague1)
        # can't join because member has already joined
        self.make_collaboration(endorsed_subtitler=self.member)
        # can't joint because it's complete
        self.make_collaboration(endorsed_subtitler=self.colleague1,
                                endorsed_reviewer=self.colleague2,
                                endorsed_approver=self.colleague3)
        # okay, let's check the collaborations returned
        self.check_can_join(needs_subtitler + needs_reviewer + needs_approver)
        # non-managers can only join as a reviewer, not an approver
        self.member.role = ROLE_CONTRIBUTOR
        self.member.save()
        self.check_can_join(needs_subtitler + needs_reviewer)
        # test change only_1_subtitler and friends
        self.member.role = ROLE_MANAGER
        self.member.save()
        self.team.workflow.only_1_subtitler = False
        self.team.workflow.only_1_reviewer = False
        self.team.workflow.only_1_approver = False
        self.team.workflow.save()
        self.check_can_join(needs_subtitler + needs_reviewer +
                            needs_approver + can_join_if_not_only_1)

    def test_limits(self):
        for i in xrange(10):
            # make of collaborations that the user can join, these should be
            # limited by the limit we pass to for_dashboard()
            CollaborationFactory(team_video__team=self.team,
                                 language_code='en')
            CollaborationFactory(team_video__team=self.team,
                                 language_code='en',
                                 endorsed_subtitler=self.colleague1)
            CollaborationFactory(team_video__team=self.team,
                                 language_code='en',
                                 endorsed_subtitler=self.colleague1,
                                 endorsed_reviewer=self.colleague2)
            # make collaborations that the user has joined.  We shouldn't
            # limit these
            CollaborationFactory(team_video__team=self.team,
                                 language_code='en',
                                 subtitler=self.member)
        for_dashboard = Collaboration.objects.for_dashboard(
            self.member, can_join_limit=5)
        self.assertEquals(len(for_dashboard['can_join']), 15)
        self.assertEquals(len(for_dashboard['joined']), 10)
