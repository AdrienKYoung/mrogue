def conjugate(is_player, conjugations):
    if len(conjugations) <= 1:
        return conjugations[0]
    if is_player:
        return conjugations[0]
    return conjugations[1]


def name(_name, possesive=False, proper=False):
    if possesive:
        if _name == 'player':
            return 'your'
        elif proper:
            if _name[len(_name) - 1] == 's':
                return _name.capitalize() + "'"
            else:
                return _name.capitalize() + "'s"
        else:
            if _name[len(_name) - 1] == 's':
                return 'the ' + _name + "'"
            else:
                return 'the ' + _name + "'s"
    else:
        if _name == 'player':
            return 'you'
        elif proper:
            return _name.capitalize()
        else:
            return 'the ' + _name


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
