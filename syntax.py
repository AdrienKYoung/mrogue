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

def name(object, possesive=False, reflexive=None):
    _name = object.name
    proper = False
    gender = 'neutral'
    if hasattr(object, 'syntax_data'):
        proper = object.syntax_data.get('proper', False)
        gender = object.syntax_data.get('gender', 'neutral')
    if reflexive == object:
        if _name == 'player':
            return 'yourself'
        else:
            if get_gender(gender) == 'M':
                return 'himself'
            elif get_gender(gender) == 'F':
                return 'herself'
            else:
                return 'itself'
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


def pronoun(object, possesive=False, objective=False):
    _name = object.name
    gender = 'neutral'
    if hasattr(object, 'syntax_data'):
        gender = object.syntax_data.get('gender', 'neutral')
    if _name == 'player':
        if possesive:
            return 'your'
        else:
            return 'you'
    if possesive:
        if get_gender(gender) == 'M':
            return 'his'
        elif get_gender(gender) == 'F':
            return 'her'
        else:
            return 'its'
    elif objective:
        if get_gender(gender) == 'M':
            return 'him'
        elif get_gender(gender) == 'F':
            return 'her'
        else:
            return 'it'
    else:
        if get_gender(gender) == 'M':
            return 'he'
        elif get_gender(gender) == 'F':
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

def get_gender(g):
    if g == 'male' or g == 'Male' or g == 'm' or g == 'M':
        return 'M'
    elif g == 'female' or g == 'Female' or g == 'f' or g == 'F':
        return 'F'
    return 'N'