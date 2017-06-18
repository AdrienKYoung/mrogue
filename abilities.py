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
import ai

class Ability:
    def __init__(self, ability_id, name, description, function, cooldown, stamina_cost=0, intent='aggressive'):
        self.ability_id = ability_id
        self.name = name
        self.function = function
        self.description = description
        self.cooldown = cooldown
        self.current_cd = 0
        self.stamina_cost = stamina_cost
        self.intent = intent

    def use(self, actor=None, target=None):
        if self.current_cd < 1:
            result = self.function(actor, target)
            if result != 'didnt-take-turn' and result != 'cancelled':
                self.current_cd = self.cooldown
            else:
                result = 'didnt-take-turn'
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
        'cooldown': 0,
        'intent': 'aggressive',
    },

    'ability_cleave': {
        'name': 'Cleave',
        'description': 'Make an attack against all adjacent enemies',
        'function': actions.cleave_attack,
        'cooldown': 0,
        'intent': 'aggressive',
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
        'on_hit': actions.on_hit_tx(actions.exhaust_self,'ability_pommel_strike'),
        'intent': 'aggressive',
    },

    'ability_blade_dance': {
        'name': 'Blade Dance',
        'description': 'Attack and swap places with a target',
        'require_weapon':'sword',
        'function': weapon_attack('ability_blade_dance'),
        'cooldown': 2,
        'stamina_multiplier': 1.2,
        'damage_multiplier': 1,
        'on_hit':actions.swap,
        'intent': 'aggressive',
    },

    'ability_skullsplitter': {
        'name': 'Skull Splitter',
        'description': 'Attack a single target for massive bonus damage that increases the '
                         'closer the target is to death',
        'require_weapon':'axe',
        'function': weapon_attack('ability_skullsplitter'),
        'cooldown': 10,
        'stamina_multiplier': 1.5,
        'damage_multiplier': actions.skullsplitter_calc_damage_bonus,
        'intent': 'aggressive',
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
        'shred_bonus': actions.crush_calc_shred_bonus,
        'intent': 'aggressive',
    },

    'ability_essence_fist': {
        'name': 'Essence Fist',
        'description': 'Consume an essence to deal high elemental damage',
        'require_weapon':'unarmed',
        'function': actions.essence_fist,
        'stamina_cost': 50,
        'cooldown':0,
        'damage_multiplier': 4,
        'intent': 'aggressive',
    },

    'ability_sweep': {
        'name': 'Sweep',
        'description': 'Attack all enemies at a range of exactly 2',
        'require_weapon':'polearm',
        'function': actions.sweep_attack,
        'cooldown': 5,
        'stamina_multiplier': 3,
        'damage_multiplier': 1.5,
        'intent': 'aggressive',
    },

    'ability_berserk': {
        'name': 'Berserk',
        'function': actions.berserk_self,
        'cooldown': 30,
        'intent': 'supportive',
    },

    'ability_summon_vermin': {
        'name': 'Summon Vermin',
        'function': actions.spawn_vermin,
        'cooldown': 9,
        'intent': 'aggressive',
    },

    'ability_grapel': {
        'name': 'Grapel',
        'function': actions.frog_tongue,
        'cooldown': 3,
        'intent': 'aggressive',
    },

    'ability_dragonweed_pull': {
        'name': 'Dragonweed Pull',
        'function': actions.dragonweed_pull,
        'cooldown': 1,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_silence': {
        'name': 'Silence',
        'function': actions.silence,
        'range':5,
        'cooldown': 15,
        'intent': 'aggressive',
    },

    'ability_raise_zombie': {
        'name': 'Raise Zombie',
        'function' : actions.raise_zombie,
        'cooldown' : 3,
        'intent': 'neutral',
    },

    'ability_flame_breath': {
        'name': 'Flame Breath',
        'function' : actions.flame_breath,
        'element':['fire'],
        'cooldown' : 6,
        'range': 4,
        'damage': '2d8',
        'intent': 'aggressive',
    },

    'ability_reeker_breath': {
        'name': 'Reeker Breath',
        'function' : actions.reeker_breath,
        'element':['life'],
        'cooldown' : 5,
        'range': 4,
        'damage': '1d8',
        'intent': 'aggressive',
    },

    'ability_great_dive': {
        'name': 'Great Dive',
        'function' : actions.great_dive,
        'cooldown' : 10,
        'range': 10,
        'cast_time': 1,
        'intent': 'aggressive',
    },

    'ability_fireball': {
        'name': 'fireball',
        'function': actions.fireball,
        'cooldown': 20,
        'element':['fire'],
        'dice' : 2,
        'base_damage' : '2d6',
        'pierce': 1,
        'cast_time':2,
        'range':8,
        'radius':2,
        'intent': 'aggressive',
    },

    'ability_heat_ray': {
        'name': 'heat ray',
        'function': actions.heat_ray,
        'cooldown': 2,
        'element':['fire'],
        'dice' : 1,
        'base_damage' : '3d4',
        'pierce': 0,
        'range':3,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_flame_wall': {
        'name': 'heat ray',
        'function': actions.flame_wall,
        'cooldown': 10,
        'element':['fire'],
        'dice' : 0,
        'base_damage' : '0d0',
        'range':10,
        'intent': 'aggressive',
    },

    'ability_magma_bolt': {
        'name': 'heat ray',
        'function': actions.magma_bolt,
        'cooldown': 10,
        'element':['fire'],
        'dice' : 3,
        'base_damage' : '3d6',
        'pierce': 1,
        'range':10,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_arcane_arrow': {
        'name': 'arcane arrow',
        'function': actions.arcane_arrow,
        'cooldown': 2,
        'element':['lightning'],
        'dice' : 1,
        'base_damage' : '3d6',
        'pierce': 0,
        'range':5,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_smite': {
        'name': 'smite',
        'function': actions.smite,
        'cooldown': 10,
        'element':['radiance'],
        'dice' : 2,
        'base_damage' : '3d6',
        'pierce': 3,
        'shred' : 2,
        'range':10,
        'intent': 'aggressive',
    },

    'ability_frozen_orb': {
        'name': 'frozen orb',
        'function': actions.frozen_orb,
        'cooldown': 3,
        'element':['cold'],
        'dice' : 2,
        'base_damage' : '3d4',
        'range':4,
        'intent': 'aggressive',
    },

    'ability_flash_frost': {
        'name': 'flash frost',
        'function': actions.flash_frost,
        'cooldown': 10,
        'element':['cold'],
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'range':6,
        'intent': 'aggressive',
    },

    'ability_ice_shards': {
        'name': 'ice shards',
        'function': actions.ice_shards,
        'cooldown': 4,
        'element':['cold'],
        'dice' : 1,
        'base_damage' : '1d8',
        'range': 5,
        'radius': 1,
        'intent': 'aggressive',
    },

    'ability_snowstorm': {
        'name': 'snowstorm',
        'function': actions.snowstorm,
        'cooldown': 10,
        'element':['cold'],
        'dice' : 1,
        'base_damage' : '1d4',
        'range':10,
        'radius':4,
        'intent': 'aggressive',
    },

    'ability_avalanche': {
        'name': 'avalanche',
        'function': actions.avalanche,
        'cooldown': 20,
        'element':['cold'],
        'dice' : 2,
        'base_damage' : '3d8',
        'range':10,
        'intent': 'aggressive',
    },

    'ability_hex': {
        'name': 'hex',
        'function': actions.hex,
        'cooldown': 20,
        'element':['death'],
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'range':6,
        'intent': 'aggressive',
    },

    'ability_defile': {
        'name': 'defile',
        'function': actions.defile,
        'cooldown': 5,
        'element':['death'],
        'dice' : 1,
        'base_damage' : '2d8',
        'pierce': 0,
        'range':6,
        'intent': 'neutral',
    },

    'ability_shackles_of_the_dead': {
        'name': 'shackles of the dead',
        'function': actions.shackles_of_the_dead,
        'cooldown': 20,
        'element':['death'],
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'range':6,
        'radius':1,
        'intent': 'aggressive',
    },

    'ability_sacrifice': {
        'name': 'profane',
        'function': actions.sacrifice,
        'cooldown': 10,
        'element':['death'],
        'dice' : 2,
        'base_damage' : '3d8',
        'pierce': 2,
        'radius':2,
        'intent': 'aggressive',
    },

    'ability_corpse_dance': {
        'name': 'corpse dance',
        'function': actions.corpse_dance,
        'cooldown': 40,
        'element':['death'],
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'range':6,
        'radius':3,
        'cast_time':3,
        'buff_duration':50,
        'intent': 'supportive',
    },

    'ability_green_touch': {
        'name': 'green touch',
        'function': actions.green_touch,
        'cooldown': 5,
        'element':['life'],
        'range':8,
        'radius':3,
        'intent': 'neutral',
    },

    'ability_fungal_growth': {
        'name': 'fungal growth',
        'function': actions.fungal_growth,
        'cooldown': 10,
        'element':['life'],
        'range':4,
        'intent': 'neutral',
    },

    'ability_summon_dragonweed': {
        'name': 'summon dragonweed',
        'function': actions.summon_dragonweed,
        'cooldown': 5,
        'element':['life'],
        'range':2,
        'intent': 'aggressive',
    },

    'ability_bramble': {
        'name': 'bramble',
        'function': actions.bramble,
        'cooldown': 5,
        'element':['life'],
        'range':4,
        'intent': 'aggressive',
        'damage': '3d6',
        'duration_base': 20,
        'duration_variance': '1d10',
        'bleed_duration': 5
    },

    'ability_strangleweeds': {
        'name': 'strangleweeds',
        'function': actions.bramble,
        'cooldown': 5,
        'element':['life'],
        'intent': 'aggressive',
        'tick_damage': '3d10',
        'duration': 10,
    },

    'ability_bless': {
        'name': 'bless',
        'function': actions.bless,
        'cooldown': 30,
        'element':['radiance'],
        'intent': 'supportive',
    },

    'ability_castigate': {
        'name': 'castigate',
        'function': actions.castigate,
        'cooldown': 10,
        'element':['radiance'],
        'intent': 'aggressive',
    },

    'ability_holy_lance': {
        'name': 'bless',
        'function': actions.bless,
        'cooldown': 30,
        'element':['radiance'],
        'dice' : 2,
        'base_damage' : '2d8',
        'radius':2,
        'range':8,
        'intent': 'aggressive',
    },

    'ability_holy_lance_tick': {
        'name': 'bless',
        'function': actions.bless,
        'cooldown': 1,
        'dice' : 1,
        'base_damage' : '1d8',
        'element':['radiance'],
        'intent': 'aggressive',
    },

    'ability_off_hand_shoot': {
        'name': 'Off Hand Shot',
        'function': actions.offhand_shot,
        'cooldown': 5,
        'range': 10,
        'description': 'Fire your weapon at an enemy you can see.',
        'intent': 'aggressive',
    },

    'ability_focus': {
        'name' : 'Focus',
        'function': actions.focus,
        'cooldown': 0,
        'range': 10,
        'stamina_cost' : 5,
        'description' : 'Focus on hitting your target, increasing your accuracy for a turn.',
        'intent': 'aggressive',
    },

    'ability_summon_spiders': {
        'name': 'Summon Spiders',
        'function': actions.spawn_spiders,
        'cooldown': 8,
        'max_summons': 4,
        'summons_per_cast': '1d2',
        'intent': 'aggressive',
    },

    'ability_web_bomb': {
        'name': 'Web Bomb',
        'function': actions.web_bomb,
        'cooldown': 6,
        'intent': 'aggressive',
    },

    'ability_heal_other': {
        'name': 'Heal Other',
        'function': actions.heal_other,
        'cooldown': 1,
        'intent': 'support',
        'target_function': ai.target_damaged_ally,
    },

    'ability_throw_net': {
        'name': 'Throw Net',
        'function': actions.throw_net,
        'range' : 4,
        'accuracy' : 25,
        'cooldown': 30,
        'duration': 5,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_haste': {
        'name': 'Haste',
        'function': actions.haste,
        'cooldown': 15,
        'intent': 'support',
        'range': 8,
        'duration': 10,
    },

    'ability_teleportal': {
        'name': 'Teleportal',
        'function': actions.create_teleportal,
        'cooldown': 8,
        'intent': 'aggressive',
        'range': 3,
    },

    'ability_time_bomb': {
        'name': 'Time Bomb',
        'function': actions.timebomb,
        'cooldown': 6,
        'intent': 'aggressive',
        'range': 6,
    },

    'ability_summon_demon': {
        'name' : 'Summon Demon',
        'cooldown': 20,
        'cast_time': 10,
        'summons':{'monster_servant_of_oblivion':20},
        'function': actions.summon_demon
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
    'attack' : Ability('ability_attack', 'Attack','Attack an enemy',actions.attack,0),
    'bash' : Ability('ability_bash', 'Bash','Knock an enemy back',actions.bash_attack,0, stamina_cost=20),
    'jump' : Ability('ability_jump', 'Jump','Jump to a tile',player.jump,0, stamina_cost=50),
    'raise shield' : Ability('ability_raise_shield', 'Raise Shield',
                             'Spend stamina to recover your shield after it has been knocked aside.',
                             actions.recover_shield, cooldown=10)
}
