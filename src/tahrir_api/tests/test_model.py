#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import raises
from hamcrest import calling
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import has_property

import fudge

from tahrir_api.model import generate_default_id

from tahrir_api.tests import BaseTahrirTest


class TestModel(BaseTahrirTest):

    def test_issuer(self):
        issuer = self.api.get_issuer('xyz')
        assert_that(issuer, is_(none()))

        issuer_id = self.api.add_issuer(
            "http://bleach.org",
            "aizen",
            "Bleach",
            "aizen@bleach.org"
        )
        issuer = self.api.get_issuer(issuer_id)
        repr(issuer)

        assert_that(str(issuer), is_('aizen'))
        assert_that(issuer.__json__(),
                    has_entries('origin', 'http://bleach.org',
                                'org', 'Bleach',
                                'created_on', is_(float),
                                'contact', 'aizen@bleach.org',
                                'name', u'aizen'))

    def test_generate_default_id(self):
        params = {'name': 'my id'}
        context = fudge.Fake().has_attr(current_parameters=params)
        assert_that(generate_default_id(context),
                    is_('my-id'))

    def test_badge(self):
        issuer_id = self.api.add_issuer(
            "http://bleach.org",
            "aizen",
            "Bleach",
            "aizen@bleach.org"
        )
        badge = self.api.get_badge('kido')
        assert_that(badge, is_(none()))

        badge_id = self.api.add_badge(
            "kido",
            "kido",
            "A test badge for doing kido",
            "kido-expert",
            issuer_id,
        )
        badge = self.api.get_badge(badge_id)
        repr(badge)

        assert_that(str(badge), is_('kido'))

        assert_that(badge.__json__(),
                    has_entries('name', 'kido',
                                'tags', is_(none()),
                                'image', '/pngs/kido',
                                'description', 'A test badge for doing kido',
                                'created_on', is_(float),
                                'version', '0.5.0',
                                'criteria', 'kido-expert',
                                'issuer', is_(dict)))

        self.api.add_person('hinamori@bleach.org', 'hinamori',
                            "http://bleach.org", 'lieutenant of the 5th Division')

        self.api.add_authorization(badge_id, 'hinamori@bleach.org')

        # get badge due to autocommit
        badge = self.api.get_badge(badge_id)
        assert_that(badge.authorized('izuru@bleach.org'),
                    is_(False))
        person = self.api.get_person('hinamori@bleach.org')
        assert_that(badge.authorized(person),
                    is_(True))

        assert_that(list(self.api.get_all_badges()),
                    has_length(1))

    def test_team_series_milestone(self):
        assert_that(self.api.get_team('bankai'), is_(none()))
        team_id = self.api.create_team('bankai')
        team = self.api.get_team(team_id)
        assert_that(team, is_not(none()))
        repr(team)

        assert_that(str(team), is_('bankai'))
        assert_that(team.__json__(),
                    has_entries('id', team_id,
                                'name', 'bankai',
                                'created_on', is_not(none())))

        assert_that(self.api.get_series('bleach'), is_(none()))
        series_id = self.api.create_series('bleach', 'anime',
                                           team_id, 'japan')
        series = self.api.get_series(series_id)
        assert_that(series, is_not(none()))
        repr(series)

        assert_that(str(series), is_('bleach'))
        assert_that(series.__json__(),
                    has_entries('id', series_id,
                                'name', 'bleach',
                                'created_on', is_not(none()),
                                'last_updated', is_not(none()),
                                'team', is_(dict)))

        assert_that(self.api.get_series_from_team('bleach'),
                    is_(none()))

        assert_that(self.api.get_series_from_team('bankai'),
                    is_not(none()))

        issuer_id = self.api.add_issuer(
            "http://bleach.org",
            "aizen",
            "Bleach",
            "aizen@bleach.org"
        )
        badge = self.api.get_badge('materialize')
        assert_that(badge, is_(none()))

        badge_id = self.api.add_badge(
            "materialize",
            "materialize",
            "subjugate zanpakuto",
            "summon the zanpakuto's spirit into the physical world.",
            issuer_id,
        )
        assert_that(self.api.milestone_exists('10years'), is_(False))
        assert_that(self.api.get_milestone('10years'), is_(none()))

        mil_id = self.api.create_milestone(1, badge_id, series_id)
        milestone = self.api.get_milestone(mil_id)
        repr(milestone)

        assert_that(milestone.__json__(),
                    has_entries('position', 1,
                                'series_id', series_id,
                                'badge', is_(dict)))

        assert_that(self.api.get_all_milestones(series_id),
                    has_length(1))

        assert_that(self.api.milestone_exists_for_badge_series(badge_id, series_id),
                    is_(True))

        assert_that(self.api.get_milestone_from_badge_series(badge_id, series_id),
                    is_not(none()))

        assert_that(list(self.api.get_milestone_from_series_ids((series_id,))),
                    has_length(1))

        assert_that(self.api.get_badges_from_team('000'),
                    is_(none()))

        assert_that(list(self.api.get_badges_from_team(team_id)),
                    has_length(1))

    def test_person(self):
        self.api.add_person("aizen@bleach.org", "aizen")
        person = self.api.get_person("aizen@bleach.org")
        assert_that(person, is_not(none()))
        repr(person)
        assert_that(str(person), is_('aizen@bleach.org'))
        person_id = person.id
        assert_that(person.__json__(),
                    has_entries('id', person_id,
                                'bio', is_(none()),
                                'rank', is_(none()),
                                'nickname', 'aizen',
                                'website', is_(none()),
                                'email', "aizen@bleach.org"))

        assert_that(self.api.get_person_email(person_id),
                    is_('aizen@bleach.org'))

        assert_that(person.gravatar_link,
                    is_('https://www.gravatar.com/avatar/e6ec20e4670cb11aa5759fed7974757b?s=24&d=mm'))

    def test_invitation(self):
        issuer_id = self.api.add_issuer(
            "http://bleach.org",
            "aizen",
            "Bleach",
            "aizen@bleach.org"
        )

        badge_id = self.api.add_badge(
            "kido",
            "kido",
            "A test badge for doing kido",
            "kido-expert",
            issuer_id,
        )
        inv_id = self.api.add_invitation(badge_id)
        invitation = self.api.get_invitation(inv_id)
        assert_that(invitation, is_not(none()))

        assert_that(invitation.expired, is_(False))
        assert_that(invitation.expires_on_relative,
                    is_('in an hour'))

        assert_that(calling(self.api.add_invitation).with_args('000'),
                    raises(ValueError))

        self.api.add_person("ichigo@bleach.org", "ichigo")
        person = self.api.get_person("ichigo@bleach.org")
        person_id = person.id

        inv_id = self.api.add_invitation(badge_id,
                                         created_by_email="ichigo@bleach.org")
        invitation = self.api.get_invitation(inv_id)
        assert_that(invitation,
                    has_property('created_by', is_(person.id)))

        assert_that(list(self.api.get_all_invitations()),
                    has_length(2))

        assert_that(self.api.get_invitation('xxxx'),
                    is_(none()))

        assert_that(list(self.api.get_invitations(person_id)),
                    has_length(2))

    def test_authorization(self):
        issuer_id = self.api.add_issuer(
            "http://bleach.org",
            "aizen",
            "Bleach",
            "aizen@bleach.org"
        )

        badge_id = self.api.add_badge(
            "kido",
            "kido",
            "A test badge for doing kido",
            "kido-expert",
            issuer_id,
        )
        assert_that(self.api.add_authorization(badge_id, 'hinamori@bleach.org'),
                    is_(False))

        self.api.add_person("hinamori@bleach.org", "hinamori")
        assert_that(self.api.add_authorization(badge_id, 'hinamori@bleach.org'),
                    is_(('hinamori@bleach.org', badge_id)))

        assert_that(self.api.authorization_exists(badge_id, 'hinamori@bleach.org'),
                    is_(True))

        assert_that(self.api.authorization_exists(badge_id, 'ichigo@bleach.org'),
                    is_(False))

        auth = self.api.get_authorization(badge_id, 'ichigo@bleach.org')
        assert_that(auth, is_(none()))

        auth = self.api.get_authorization(badge_id, 'hinamori@bleach.org')
        assert_that(auth, is_not(none()))
        repr(auth)
