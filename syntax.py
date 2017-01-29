def conjugate(is_player, conjugations):
    if len(conjugations) <= 1:
        return conjugations[0]
    if is_player:
        return conjugations[0]
    return conjugations[1]


def name(name, possesive=False, proper=False):
    if possesive:
        if name == 'player':
            return 'your'
        elif proper:
            if name[len(name) - 1] == 's':
                return name.capitalize() + "'"
            else:
                return name.capitalize() + "'s"
        else:
            if name[len(name) - 1] == 's':
                return 'the ' + name + "'"
            else:
                return 'the ' + name + "'s"
    else:
        if name == 'player':
            return 'you'
        elif proper:
            return name.capitalize()
        else:
            return 'the ' + name


def pronoun(name, possesive=False, objective=False, gender='N'):
    if name == 'player':
        return name(name, possesive=possesive)
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
