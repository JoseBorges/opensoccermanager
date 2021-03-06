#!/usr/bin/env python3

#  This file is part of OpenSoccerManager.
#
#  OpenSoccerManager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
#  OpenSoccerManager is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  OpenSoccerManager.  If not, see <http://www.gnu.org/licenses/>.


import random

import data


class Fixtures:
    def __init__(self):
        self.fixtures = {}
        self.fixtureid = 0

        self.events = (16, 8), (23, 8), (30, 8), (13, 9), (20, 9), (27, 9), (4, 10), (18, 10), (25, 10), (1, 11), (8, 11), (22, 11), (29, 11), (2, 12), (6, 12), (13, 12), (20, 12), (26, 12), (28, 12), (1, 1), (10, 1), (17, 1), (31, 1), (7, 2), (10, 2), (21, 2), (28, 2), (3, 3), (14, 3), (21, 3), (4, 4), (11, 4), (18, 4), (25, 4), (2, 5), (9, 5), (16, 5), (24, 5),

    def get_fixtureid(self):
        '''
        Return unique fixture id.
        '''
        self.fixtureid += 1

        return self.fixtureid

    def generate_fixtures(self, league):
        '''
        Generate season fixture list for passed clubs argument.
        '''
        self.league = league
        clubs = league.clubs
        self.clubs = clubs

        random.shuffle(clubs)

        rounds = len(self.clubs) - 1
        matches = int(len(self.clubs) * 0.5)

        for week in range(0, rounds):
            referees = self.get_referee_list()

            for match in range(0, matches):
                home = (week + match) % rounds
                away = (len(self.clubs) - 1 - match + week) % rounds

                if match == 0:
                    away = rounds

                fixture = Fixture()
                fixture.league = self.league
                fixture.week = week
                fixture.referee = data.referees.get_referee_by_id(referees[match])

                if week % 2 == 1:
                    club = data.clubs.get_club_by_id(self.clubs[home])
                    fixture.home.club = club
                    club = data.clubs.get_club_by_id(self.clubs[away])
                    fixture.away.club = club
                else:
                    club = data.clubs.get_club_by_id(self.clubs[away])
                    fixture.home.club = club
                    club = data.clubs.get_club_by_id(self.clubs[home])
                    fixture.away.club = club

                fixture.fixtureid = self.get_fixtureid()
                self.fixtures[fixture.fixtureid] = fixture

        for week in range(0, rounds):
            referees = self.get_referee_list()

            for match in range(0, matches):
                home = ((rounds + week) + match) % rounds
                away = (len(self.clubs) - 1 - match + (rounds + week)) % rounds

                if match == 0:
                    away = rounds

                fixture = Fixture()
                fixture.league = self.league
                fixture.week = rounds + week
                fixture.referee = data.referees.get_referee_by_id(referees[match])

                if (rounds + week) % 2 == 1:
                    club = data.clubs.get_club_by_id(self.clubs[home])
                    fixture.home.club = club
                    club = data.clubs.get_club_by_id(self.clubs[away])
                    fixture.away.club = club
                else:
                    club = data.clubs.get_club_by_id(self.clubs[away])
                    fixture.home.club = club
                    club = data.clubs.get_club_by_id(self.clubs[home])
                    fixture.away.club = club

                fixture.fixtureid = self.get_fixtureid()
                self.fixtures[fixture.fixtureid] = fixture

        self.generate_televised_fixtures()

    def get_referee_list(self):
        '''
        Return randomly ordered list of referees for assignment to fixture.
        '''
        referees = self.league.get_referees()
        random.shuffle(referees)

        return referees

    def get_fixtures(self):
        '''
        Return complete list of fixtures.
        '''
        return self.fixtures

    def get_fixture_by_id(self, fixtureid):
        '''
        Get fixture object for given fixture id.
        '''
        return self.fixtures[fixtureid]

    def get_fixtures_for_week(self, week):
        '''
        Return list of fixtures for passed week value.
        '''
        fixtures = {}

        for fixtureid, fixture in self.fixtures.items():
            if fixture.week == week:
                fixtures[fixtureid] = fixture

        return fixtures

    def get_number_of_rounds(self):
        '''
        Return the number of rounds in the season.
        '''
        return len(self.clubs) * 2 - 2

    def get_initial_fixtures(self):
        '''
        Return name and venue of first three first of the season.
        '''
        fixtures = []
        initial = []

        for fixture in self.fixtures.values():
            if fixture.week in (0, 1, 2):
                if data.user.club in (fixture.home.club, fixture.away.club):
                    fixtures.append([fixture.home.club, fixture.away.club])

        for teams in fixtures:
            for count, team in enumerate(teams):
                if team is not data.user.club:
                    location = ("A", "H")[count]

                    fixture = "%s (%s)" % (team.name, location)
                    initial.append(fixture)

        return initial

    def get_televised_fixtures(self):
        '''
        Return fixtures which have been marked for show on television.
        '''

    def generate_televised_fixtures(self):
        '''
        Choose fixtures which will be shown on television.
        '''
        fixtures = []

        for count in range(0, self.get_number_of_rounds()):
            fixtures = self.get_fixtures_for_week(count)
            fixtures = list(fixtures.values())

            fixture = random.choice(fixtures)
            fixture.televised = True


class Fixture:
    '''
    Fixture object representing match to be played.
    '''
    def __init__(self):
        self.week = 0
        self.played = False
        self.televised = False

        self.home = FixtureTeam()
        self.away = FixtureTeam()
        self.result = None

        self.attendance = 0
        self.referee = None
        self.league = None

    def pay_televised_money(self):
        '''
        Pay money to clubs for game being televised.
        '''
        if self.televised:
            amount = (self.home.club.reputation * 2) * 20000
            self.home.club.accounts.deposit(amount, "television")

            amount = (self.away.club.reputation * 2) * 20000
            self.away.club.accounts.deposit(amount, "television")

            if data.user.club is self.home.club:
                amount = (self.home.club.reputation * 2) * 20000
                amount = data.currency.get_currency(amount, integer=True)
                data.user.club.news.publish("TM01",
                                            team=self.away.club.name,
                                            amount=amount)
            elif data.user.club is self.away.club:
                amount = (self.away.club.reputation * 2) * 20000
                amount = data.currency.get_currency(amount, integer=True)
                data.user.club.news.publish("TM01",
                                            team=self.home.club.name,
                                            amount=amount)

    def store_team_selection(self):
        '''
        Save selected first team and substitutions into fixture object.
        '''
        self.home.team_played[0] = self.home.team_selection[0]
        self.home.increment_player_appearances()
        self.away.team_played[0] = self.away.team_selection[0]
        self.away.increment_player_appearances()


class FixtureTeam:
    '''
    Fixture team object storing squad, events, match statistics, and more.
    '''
    def __init__(self):
        self.club = None

        self.team_selection = [[], []]
        self.team_played = [[], []]

        self.goalscorers = None
        self.assisters = None

        self.formationid = 0

        self.yellow_cards = []
        self.red_cards = []

    def increment_player_appearances(self):
        '''
        Increment appearances for each player in team.
        '''
        for player in self.team_played[0]:
            if player:
                player.appearances += 1

        for player in self.team_played[1]:
            if player:
                player.substitute += 1
