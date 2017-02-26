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
            if actor is player.instance:
                ui.message('{} is on cooldown'.format(self.name), libtcod.red)
            result = 'didnt-take-turn'
        return result

    def on_tick(self):
        if self.current_cd > 0:
            self.current_cd -= 1

def weapon_attack(ability_name):
    return lambda actor,target:actions.weapon_attack_ex(ability_name,actor,target)

import actions
data = {
    'ability_thrust': {
        'name': 'Thrust',
        'description': 'Thrust at an enemy up to 2 spaces away',
        'function': actions.attack_reach,
        'cooldown': 0
    },

    'ability_pommel_strike': {
        'name': 'Pommel Strike',
        'description': 'Smash your opponent with your sword pommel for extra damage and shred at the expense of'
                       ' greater stamina usage and exhaustion.',
        'require_weapon':'sword',
        'function': weapon_attack('ability_pommel_strike'),
        'cooldown': 2,
        'stamina_multiplier': 2,
        'damage_multiplier': 1.8,
        'guaranteed_shred_bonus': 2,
        'exhaustion_duration': 3,
        'verb': ('smash','smashes'),
        'on_hit': actions.on_hit_tx(actions.exhaust_self,'ability_pommel_strike')
    },

    'ability_blade_dance': {
        'name': 'Blade Dance',
        'description': 'Attack and swap places with a target',
        'require_weapon':'sword',
        'function': weapon_attack('ability_blade_dance'),
        'cooldown': 2,
        'stamina_multiplier': 1.2,
        'damage_multiplier': 1,
        'on_hit':actions.swap
    },

    'ability_skullsplitter': {
        'name': 'Skull Splitter',
        'description': 'Attack a single target for massive bonus damage that increases the '
                         'closer the target is to death',
        'require_weapon':'axe',
        'function': weapon_attack('ability_skullsplitter'),
        'cooldown': 10,
        'stamina_multiplier': 1.5,
        'damage_multiplier': actions.skullsplitter_calc_damage_bonus
    },

    'ability_sweep': {
        'name': 'Sweep',
        'description': 'Attack all enemies at a range of exactly 2',
        'require_weapon':'polearm',
        'function': actions.sweep_attack,
        'cooldown': 5,
        'stamina_multiplier': 3,
        'damage_multiplier': 1.5
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
        'function': actions.frog_tongue,
        'cooldown': 3
    },

    'ability_silence': {
        'name': 'Silence',
        'function': actions.silence,
        'range':5,
        'cooldown': 15
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
        'pierce': 1,
        'cast_time':2,
        'range':8,
        'radius':2
    },

    'ability_heat_ray': {
        'name': 'heat ray',
        'function': actions.heat_ray,
        'cooldown': 5,
        'element':'fire',
        'dice' : 1,
        'base_damage' : '3d4',
        'pierce': 0,
        'range':3
    },

    'ability_magma_bolt': {
        'name': 'heat ray',
        'function': actions.magma_bolt,
        'cooldown': 10,
        'element':'fire',
        'dice' : 3,
        'base_damage' : '3d6',
        'pierce': 1,
        'range':10
    },

    'ability_arcane_arrow': {
        'name': 'arcane arrow',
        'function': actions.arcane_arrow,
        'cooldown': 0,
        'element':'lightning',
        'dice' : 1,
        'base_damage' : '3d6',
        'pierce': 0,
        'range':5
    },

    'ability_smite': {
        'name': 'smite',
        'function': actions.smite,
        'cooldown': 10,
        'element':'radiant',
        'dice' : 2,
        'base_damage' : '3d6',
        'pierce': 3,
        'shred' : 2,
        'range':10
    },

    'ability_frozen_orb': {
        'name': 'frozen orb',
        'function': actions.magma_bolt,
        'cooldown': 10,
        'element':'cold',
        'dice' : 2,
        'base_damage' : '3d4',
        'range':4
    },

    'ability_flash_frost': {
        'name': 'flash frost',
        'function': actions.magma_bolt,
        'cooldown': 10,
        'element':'cold',
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'range':6
    },

    'ability_ice_shards': {
        'name': 'ice shards',
        'function': actions.magma_bolt,
        'cooldown': 10,
        'element':'cold',
        'dice' : 1,
        'base_damage' : '3d6',
        'range':3
    },

    'ability_snowstorm': {
        'name': 'snowstorm',
        'function': actions.magma_bolt,
        'cooldown': 10,
        'element':'cold',
        'dice' : 1,
        'base_damage' : '1d6',
        'range':10
    },

    'ability_avalanche': {
        'name': 'avalanche',
        'function': actions.magma_bolt,
        'cooldown': 20,
        'element':'cold',
        'dice' : 2,
        'base_damage' : '3d8',
        'range':10
    },
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
