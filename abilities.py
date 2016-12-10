import game as main
import consts
import libtcodpy as libtcod

class Ability:
    def __init__(self, name, description, function, cooldown):
        self.name = name
        self.function = function
        self.description = description
        self.cooldown = cooldown
        self.current_cd = 0

    def use(self):
        if self.current_cd < 1:
            result = self.function()
            self.current_cd = self.cooldown
        else:
            main.message('{} is on cooldown'.format(self.name), libtcod.red)
        return result

    def on_tick(self):
        if self.current_cd > 0:
            self.current_cd -= 1


def ability_attack():
    x,y = main.target_tile(max_range=1)
    target = None
    for object in main.objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
    if target is not None:
        result = main.player.fighter.attack(target)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def ability_attack_reach():
    x, y = main.target_tile(max_range=2)
    target = None
    for object in main.objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
    if target is not None:
        result = main.player.fighter.attack(target)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def ability_bash_attack():
    x,y = main.target_tile(max_range=1)
    target = None
    for object in main.objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
    if target is not None:
        result = main.player_bash_attack(target)
        if result != 'failed':
            return result
    return 'didnt-take-turn'


#data = {
#    'thrust':Ability('Thrust','Thrust at an enemy up to 2 spaces away',ability_attack_reach,0)
#}

data = {
    'thrust' : {
        'name' : 'Thrust',
        'description' : 'Thrust at an enemy up to 2 spaces away',
        'function' : ability_attack_reach,
        'cooldown' : 0
    }
}

default_abilities = [
    Ability('Attack','Attack an enemy',ability_attack,0),
    Ability('Bash','Knock an enemy back',ability_bash_attack,0),
    Ability('Jump','Jump to a tile',main.jump,0)
]