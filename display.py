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


import operator
import statistics

import game
import constants
import calculator


def name(player, mode=0):
    '''
    Return the player name in the requested format depending on whether
    it should be displayed as first/second or second/first name.
    '''
    if not player.common_name:
        player.common_name = ""

    if player.common_name is not "":
        name = player.common_name
    else:
        if mode == 0:
            name = "%s, %s" % (player.second_name, player.first_name)
        elif mode == 1:
            name = "%s %s" % (player.first_name, player.second_name)

    return name


def format_position(value):
    '''
    Format position with ordinal for display to player.

    * Will clearly cause problems if league table is longer than 20
    teams, e.g. 21th, 32th. Needs to be fixed.
    '''
    if value == 1:
        output = "%ist" % (value)
    elif value == 2:
        output = "%ind" % (value)
    elif value == 3:
        output = "%ird" % (value)
    elif value >= 4:
        output = "%ith" % (value)

    return output


def sorted_standings():
    standings = []

    for clubid, details in game.standings.items():
        details = (clubid,
                   game.clubs[clubid].name,
                   details.played,
                   details.wins,
                   details.draws,
                   details.losses,
                   details.goals_for,
                   details.goals_against,
                   details.goal_difference,
                   details.points
                  )
        standings.append(details)

    if game.eventindex > 0:
        standings = sorted(standings,
                           key=operator.itemgetter(9, 8, 6, 7),
                           reverse=True)
    else:
        standings = sorted(standings,
                           key=operator.itemgetter(1))

    return standings


def find_champion():
    '''
    Returns clubid of the team at the top of the league.
    '''
    standings = sorted_standings()
    champion = standings[0][0]

    return champion


def find_position(teamid, ordinal=True):
    '''
    Returns the position in standings of specified club.
    '''
    standings = sorted_standings()

    position = 0

    for count, item in enumerate(standings, start=1):
        if item[0] == teamid:
            position = count

    if ordinal:
        position = format_position(position)

    return position


def top_scorer():
    top = [0, 0]

    for playerid, player in game.players.items():
        if player.goals > top[1]:
            top[0] = playerid
            top[1] = player.goals

    return top


def top_assister():
    top = [0, 0]

    for playerid, player in game.players.items():
        if player.assists > top[1]:
            top[0] = playerid
            top[1] = player.assists

    return top


def player_of_the_season():
    '''
    Find player with the highest performance ratings for the season, and return
    as the 'Player of the Year'.
    '''
    top = [0, 0]

    for playerid, player in game.players.items():
        if player.man_of_the_match > top[1]:
            if len(player.rating) > 0:
                top[0] = playerid
                top[1] = statistics.mean(player.rating)

    return top


def player_morale(value):
    '''
    Return the string indicating the players morale value.
    '''
    status = ""

    if value >= 85:
        status = constants.morale[8]
    elif value >= 70:
        status = constants.morale[7]
    elif value >= 45:
        status = constants.morale[6]
    elif value >= 20:
        status = constants.morale[5]
    elif value >= 0:
        status = constants.morale[4]
    elif value >= -25:
        status = constants.morale[3]
    elif value >= -50:
        status = constants.morale[2]
    elif value >= -75:
        status = constants.morale[1]
    elif value >= -100:
        status = constants.morale[0]

    return status


def value(value):
    value = calculator.value_rounder(value)
    currency, exchange = constants.currency[game.currency]

    if value >= 1000000:
        amount = (value / 1000000) * exchange
        value = "%s%.1fM" % (currency, amount)
    elif value >= 1000:
        amount = (value / 1000) * exchange
        value = "%s%iK" % (currency, amount)

    return value


def wage(wage):
    wage = calculator.wage_rounder(wage)
    currency, exchange = constants.currency[game.currency]

    if wage >= 1000:
        amount = (wage / 1000) * exchange
        wage = "%s%.1fK" % (currency, amount)
    elif wage >= 100:
        amount = wage * exchange
        wage = "%s%i" % (currency, amount)

    return wage


def currency(amount, mode=0):
    '''
    Format the amount into the selected currency and convert to appropriate
    exchange rate.
    '''
    currency = constants.currency[game.currency][0]
    amount *= constants.currency[game.currency][1]

    if mode == 0:
        amount = "%s%i" % (currency, amount)
    elif mode == 1:
        amount = "%s%.2f" % (currency, amount)

    return amount


def contract(period):
    '''
    Format the number of weeks on the contract remaining.
    '''
    if period > 1:
        text = "%i Weeks" % (period)
    elif period == 1:
        text = "%i Week" % (period)
    elif period == 0:
        text = "Out of Contract"

    return text


def club(clubid):
    '''
    Return club name for the specified id or nothing when player is unattached.
    '''
    if clubid == 0:
        text = ""
    else:
        text = game.clubs[clubid].name

    return text


def injury(value):
    if value == 1:
        text = "%i Week" % (value)
    else:
        text = "%i Weeks" % (value)

    return text


def suspension(value):
    if value == 1:
        text = "%i Match" % (value)
    else:
        text = "%i Matches" % (value)

    return text


def rating(player):
    '''
    Display the average player rating.
    '''
    if player.rating != []:
        rating = "%.1f" % (statistics.mean(player.rating))
    else:
        rating = "0.0"

    return rating


def season():
    '''
    Return the season in yyyy/yyyy format.
    '''
    season = "%i/%i" % (game.year, game.year + 1)

    return season
