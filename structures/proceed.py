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


import data
import structures.advertising
import uigtk.match
import uigtk.squaderror


class ContinueGame:
    '''
    Class handling proceeding with the game to the next event.
    '''
    def __init__(self):
        self.continue_to_match = ContinueToMatch()
        self.continue_allowed = 0

    def on_continue_game(self):
        '''
        Determine whether game will continue, or handle if there is a match.
        '''
        if self.continue_allowed == 0:
            if not data.calendar.get_fixture():
                data.date.increment_date()
                data.window.screen.refresh_visible_screen()

            if data.calendar.get_fixture():
                data.calendar.get_user_fixture()
                self.continue_allowed = 1

        if self.continue_allowed == 1:
            self.continue_allowed = 2
        elif self.continue_allowed == 2:
            opposition = data.calendar.get_user_opposition()

            if self.on_continue_to_match(opposition):
                self.continue_allowed = 3
        elif self.continue_allowed == 3:
            data.window.screen.change_visible_screen("squad")
            data.calendar.increment_event()
            self.continue_allowed = 0

    def on_continue_to_match(self, club):
        '''
        Determine whether match can continue or display error.
        '''
        if self.continue_to_match.get_valid_squad():
            dialog = uigtk.match.ProceedToMatch(club.name)

            if dialog.show():
                if self.continue_to_match.get_selected_substitutes():
                    return True
                else:
                    return False
        else:
            return False


class ContinueToMatch:
    '''
    Class to verify whether next match is able to be played.
    '''
    def get_valid_squad(self):
        '''
        Verify eleven selected players are eligible.
        '''
        count = data.user.club.squad.teamselection.get_team_count()

        state = count == 11

        if not state:
            uigtk.match.NotEnoughPlayers(count)
        else:
            state = len(data.user.club.squad.teamselection.get_injured_players()) == 0 and len(data.user.club.squad.teamselection.get_suspended_players()) == 0

            if not state:
                dialog = uigtk.squaderror.SquadError()
                dialog.show()

        return state

    def get_selected_substitutes(self):
        '''
        Check whether the user has selected all substitutes.
        '''
        count = data.user.club.squad.teamselection.get_subs_count()

        state = True

        if not data.preferences.hide_warnings:
            if count < 5:
                dialog = uigtk.match.NotEnoughSubs(count)
                state = dialog.show()

            if state:
                state = self.get_selected_responsibilities()

        if state:
            fixture = data.calendar.get_user_fixture()

            self.match_preparations(fixture)

            data.window.screen.change_visible_screen("match")
            data.window.screen.active.update_match_details(fixture)

        return state

    def get_selected_responsibilities(self):
        '''
        Check whether the user has selected team responsibilities.
        '''
        state = True

        if None in (data.user.club.tactics.captain,
                    data.user.club.tactics.corner_taker,
                    data.user.club.tactics.penalty_taker,
                    data.user.club.tactics.free_kick_taker):
            dialog = uigtk.match.UnsetResponsibilities()
            state = dialog.show()

        return state

    def match_preparations(self, fixture):
        '''
        Generate squad for computer-run club.
        '''
        if fixture.home.club is data.user.club:
            fixture.away.club.squad.generate_squad()
        elif fixture.away.club is data.user.club:
            fixture.home.club.squad.generate_squad()
