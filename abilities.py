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
            if result != 'didnt-take-turn' or result != 'cancelled':
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

    'ability_crush': {
        'name': 'Crush',
        'description': "Make an attack that gains damage and shred"
                         "for each point of your target's armor",
        'require_weapon':'mace',
        'function': weapon_attack('ability_crush'),
        'cooldown': 5,
        'stamina_multiplier': 1.5,
        'damage_multiplier': actions.crush_calc_damage_bonus,
        'shred_bonus': actions.crush_calc_shred_bonus
    },

    'ability_essence_fist': {
        'name': 'Essence Fist',
        'description': 'Consume an essence to deal high elemental damage',
        'require_weapon':'unarmed',
        'function': actions.essence_fist,
        'stamina_cost': 50,
        'cooldown':0,
        'damage_multiplier': 4,
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

    'ability_dragonweed_pull': {
        'name': 'Dragonweed Pull',
        'function': actions.dragonweed_pull,
        'cooldown': 1
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

    'ability_flame_breath': {
        'name': 'Flame Breath',
        'function' : actions.flame_breath,
        'element':'fire',
        'cooldown' : 6,
        'range': 4,
        'damage': '2d8',
    },

    'ability_great_dive': {
        'name': 'Great Dive',
        'function' : actions.great_dive,
        'cooldown' : 10,
        'range': 10,
        'cast_time': 1,
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

    'ability_flame_wall': {
        'name': 'heat ray',
        'function': actions.flame_wall,
        'cooldown': 10,
        'element':'fire',
        'dice' : 0,
        'base_damage' : '0d0',
        'range':10
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
        'element':'radiance',
        'dice' : 2,
        'base_damage' : '3d6',
        'pierce': 3,
        'shred' : 2,
        'range':10
    },

    'ability_frozen_orb': {
        'name': 'frozen orb',
        'function': actions.frozen_orb,
        'cooldown': 10,
        'element':'cold',
        'dice' : 2,
        'base_damage' : '3d4',
        'range':4
    },

    'ability_flash_frost': {
        'name': 'flash frost',
        'function': actions.flash_frost,
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
        'base_damage' : '1d8',
        'range': 5,
        'radius': 1
    },

    'ability_snowstorm': {
        'name': 'snowstorm',
        'function': actions.magma_bolt,
        'cooldown': 10,
        'element':'cold',
        'dice' : 1,
        'base_damage' : '1d4',
        'range':10,
        'radius':4
    },

    'ability_avalanche': {
        'name': 'avalanche',
        'function': actions.avalanche,
        'cooldown': 20,
        'element':'cold',
        'dice' : 2,
        'base_damage' : '3d8',
        'range':10
    },

    'ability_hex': {
        'name': 'hex',
        'function': actions.hex,
        'cooldown': 20,
        'element':'death',
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'range':6
    },

    'ability_defile': {
        'name': 'defile',
        'function': actions.defile,
        'cooldown': 10,
        'element':'death',
        'dice' : 1,
        'base_damage' : '2d8',
        'pierce': 0,
        'range':6
    },

    'ability_shackles_of_the_dead': {
        'name': 'shackles of the dead',
        'function': actions.shackles_of_the_dead,
        'cooldown': 20,
        'element':'death',
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'range':6,
        'radius':1
    },

    'ability_sacrifice': {
        'name': 'profane',
        'function': actions.sacrifice,
        'cooldown': 10,
        'element':'death',
        'dice' : 2,
        'base_damage' : '3d8',
        'pierce': 2,
        'radius':2
    },

    'ability_corpse_dance': {
        'name': 'corpse dance',
        'function': actions.corpse_dance,
        'cooldown': 40,
        'element':'death',
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'range':6,
        'radius':3,
        'cast_time':3,
        'buff_duration':50
    },

    'ability_green_touch': {
        'name': 'green touch',
        'function': actions.green_touch,
        'cooldown': 5,
        'element':'life',
        'range':8,
        'radius':3,
    },

    'ability_fungal_growth': {
        'name': 'fungal growth',
        'function': actions.fungal_growth,
        'cooldown': 10,
        'element':'life',
        'range':4,
    },

    'ability_summon_dragonweed': {
        'name': 'summon dragonweed',
        'function': actions.summon_dragonweed,
        'cooldown': 5,
        'element':'life',
        'range':2,
    },

    'ability_off_hand_shoot': {
        'name': 'Off Hand Shot',
        'function': actions.offhand_shot,
        'cooldown': 20,
        'range': 10
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
    'jump' : Ability('Jump','Jump to a tile',player.jump,0),
    'raise shield' : Ability('Raise Shield', 'Spend stamina to recover your shield after it has been knocked aside.', actions.recover_shield, 0)
}
