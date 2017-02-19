import game as main
import libtcodpy as libtcod
import ui
import player

class Ability:
    def __init__(self, name, description, function, cooldown):
        self.name = name
        self.function = function
        self.description = description
        self.cooldown = cooldown
        self.current_cd = 0

    def use(self, actor=None, target=None):
        if self.current_cd < 1:
            result = self.function(actor, target)
            if result != 'didnt-take-turn':
                self.current_cd = self.cooldown
        else:
            if actor is player.instance.instance:
                ui.message('{} is on cooldown'.format(self.name), libtcod.red)
            result = 'didnt-take-turn'
        return result

    def on_tick(self):
        if self.current_cd > 0:
            self.current_cd -= 1

import actions
data = {
    'ability_thrust': {
        'name': 'Thrust',
        'description': 'Thrust at an enemy up to 2 spaces away',
        'function': actions.attack_reach,
        'cooldown': 0
    },

    'ability_berserk': {
        'name': 'Berserk',
        'function': actions.berserk_self,
        'cooldown': 30
    },

    'ability_summon_vermin': {
        'name': 'Summon Vermin',
        'function': actions.spawn_vermin,
        'cooldown': 9
    },

    'ability_grapel': {
        'name': 'Grapel',
        'function': actions.grapel,
        'cooldown': 3
    },

    'ability_cast_arcane_arrow': {
        'name': 'Arcane Arrow',
        'function': actions.arcane_arrow,
        'cooldown': 0
    },

    'ability_raise_zombie': {
        'name': 'Raise Zombie',
        'function' : actions.raise_zombie,
        'cooldown' : 3
    },

    'ability_fireball': {
        'name': 'fireball',
        'function': actions.fireball,
        'cooldown': 20,
        'element':'fire',
        'dice' : 2,
        'base_damage' : '2d6',
        'pierce': 0
    }
}

vermin_summons = [
    {'weight' : 25, 'monster' : 'monster_cockroach', 'count' : 2},
    {'weight' : 25, 'monster' : 'monster_cockroach', 'count' : 3},
    {'weight' : 15, 'monster' : 'monster_cockroach', 'count' : 4},
    {'weight' : 15, 'monster' : 'monster_centipede', 'count' : 1},
    {'weight' : 10, 'monster' : 'monster_bomb_beetle', 'count' : 1},
    {'weight' : 10, 'monster' : 'monster_tunnel_spider', 'count' : 1}
]

default_abilities = {
    'attack' : Ability('Attack','Attack an enemy',actions.attack,0),
    'bash' : Ability('Bash','Knock an enemy back',actions.bash_attack,0),
    'jump' : Ability('Jump','Jump to a tile',player.jump,0)
}
