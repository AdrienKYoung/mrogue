#part of mrogue, an interactive adventure game
#Copyright (C) 2017 Adrien Young and Tyler Soberanis
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

def conjugate(is_player, conjugations):
    if len(conjugations) <= 1:
        return conjugations[0]
    if is_player:
        return conjugations[0]
    return conjugations[1]

def name(object, possesive=False, proper=False):
    _name = object.name
    if object.fighter and object.fighter.team == 'ally':
        article = 'your '
    else:
        article = 'the '
    if possesive:
        if _name == 'player':
            return 'your'
        if proper:
            if _name[len(_name) - 1] == 's':
                return _name.capitalize() + "'"
            else:
                return _name.capitalize() + "'s"
        else:
            if _name[len(_name) - 1] == 's':
                return article + _name + "'"
            else:
                return article + _name + "'s"
    else:
        if _name == 'player':
            return 'you'
        elif proper:
            return _name.capitalize()
        else:
            return article + _name


def pronoun(_name, possesive=False, objective=False, gender='N'):
    if _name == 'player':
        return name(_name, possesive=possesive)
    if possesive:
        if gender == 'M':
            return 'his'
        elif gender == 'F':
            return 'her'
        else:
            return 'its'
    elif objective:
        if gender == 'M':
            return 'him'
        elif gender == 'F':
            return 'her'
        else:
            return 'it'
    else:
        if gender == 'M':
            return 'he'
        elif gender == 'F':
            return 'she'
        else:
            return 'it'

def relative_adjective(a,b,adjectives):
    if len(adjectives) < 1:
        return ""
    if len(adjectives) < 2:
        return adjectives[0]
    if a < b:
        return adjectives[0]
    elif a > b:
        return adjectives[1]
    else:
        return ""
