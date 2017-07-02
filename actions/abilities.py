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
import consts

import item_actions
import monster_actions
import perk_actions
import charm_actions
import spell_actions
import common
import actions

class Ability:
    def __init__(self, ability_id, name, description, cooldown, stamina_cost=0, intent='aggressive'):
        self.ability_id = ability_id
        self.name = name
        self.description = description
        self.cooldown = cooldown
        self.current_cd = 0
        self.stamina_cost = stamina_cost
        self.intent = intent

    def use(self, actor=None, target=None):
        if self.current_cd < 1:
            info = data[self.ability_id]
            result = actions.invoke_ability(self.ability_id, actor, target)
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

data = {
    'ability_thrust': {
        'name': 'Thrust',
        'description': 'Thrust at an enemy up to 2 spaces away',
        'function': common.attack_reach,
        'cooldown': 0,
        'intent': 'aggressive',
        'targeting': 'beam interrupt',
        'range': 1
    },

    'ability_cleave': {
        'name': 'Cleave',
        'description': 'Make an attack against all adjacent enemies',
        'function': common.cleave_attack,
        'cooldown': 0,
        'intent': 'aggressive',
    },

    'ability_jump': {
        'name': 'Jump',
        'function': lambda(a,t,_): player.jump(a,t)
    },

    'ability_pommel_strike': {
        'name': 'Pommel Strike',
        'description': 'Smash your opponent with your sword pommel for extra damage and shred at the expense of'
                       ' greater stamina usage and exhaustion.',
        'require_weapon':'sword',
        'function': perk_actions.pommel_strike,
        'cooldown': 2,
        'stamina_multiplier': 2,
        'damage_multiplier': 1.8,
        'guaranteed_shred_bonus': 2,
        'exhaustion_duration': 3,
        'verb': ('smash','smashes'),
        'intent': 'aggressive',
    },

    'ability_blade_dance': {
        'name': 'Blade Dance',
        'description': 'Attack and swap places with a target',
        'require_weapon':'sword',
        'function': perk_actions.blade_dance,
        'cooldown': 2,
        'stamina_multiplier': 1.2,
        'damage_multiplier': 1,
        'intent': 'aggressive',
    },

    'ability_skullsplitter': {
        'name': 'Skull Splitter',
        'description': 'Attack a single target for massive bonus damage that increases the '
                         'closer the target is to death',
        'require_weapon':'axe',
        'function': perk_actions.skullsplitter,
        'cooldown': 10,
        'stamina_multiplier': 1.5,
        'intent': 'aggressive',
    },

    'ability_crush': {
        'name': 'Crush',
        'description': "Make an attack that gains damage and shred"
                         "for each point of your target's armor",
        'require_weapon':'mace',
        'function': perk_actions.crush,
        'cooldown': 5,
        'stamina_multiplier': 1.5,
        'intent': 'aggressive',
    },

    'ability_essence_fist': {
        'name': 'Essence Fist',
        'description': 'Consume an essence to deal high elemental damage',
        'require_weapon':'unarmed',
        'function': perk_actions.essence_fist,
        'stamina_cost': 50,
        'cooldown':0,
        'damage_multiplier': 4,
        'intent': 'aggressive',
        'range': 1
    },

    'ability_sweep': {
        'name': 'Sweep',
        'description': 'Attack all enemies at a range of exactly 2',
        'require_weapon':'polearm',
        'function': perk_actions.sweep_attack,
        'cooldown': 5,
        'stamina_multiplier': 3,
        'damage_multiplier': 1.5,
        'intent': 'aggressive',
        'range': 1,
    },

    'ability_berserk': {
        'name': 'Berserk',
        'function': monster_actions.berserk_self,
        'cooldown': 30,
        'intent': 'supportive',
    },

    'ability_summon_vermin': {
        'name': 'Summon Vermin',
        'function': monster_actions.spawn_vermin,
        'cooldown': 9,
        'intent': 'aggressive',
        'max_summons':8,
        'summons': [
            {'weight' : 25, 'monster' : 'monster_cockroach', 'count' : 2},
            {'weight' : 25, 'monster' : 'monster_cockroach', 'count' : 3},
            {'weight' : 15, 'monster' : 'monster_cockroach', 'count' : 4},
            {'weight' : 15, 'monster' : 'monster_centipede', 'count' : 1},
            {'weight' : 10, 'monster' : 'monster_bomb_beetle', 'count' : 1},
            {'weight' : 10, 'monster' : 'monster_tunnel_spider', 'count' : 1}
        ]
    },

    'ability_grapel': {
        'name': 'Grapel',
        'function': monster_actions.frog_tongue,
        'targeting': 'beam interrupt',
        'cooldown': 3,
        'intent': 'aggressive',
    },

    'ability_dragonweed_pull': {
        'name': 'Dragonweed Pull',
        'function': monster_actions.dragonweed_pull,
        'targeting': 'beam interrupt',
        'cooldown': 1,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_silence': {
        'name': 'Silence',
        'function': monster_actions.silence,
        'range':5,
        'cooldown': 15,
        'intent': 'aggressive',
    },

    'ability_raise_zombie': {
        'name': 'Raise Zombie',
        'function' : monster_actions.raise_zombie,
        'cooldown' : 3,
        'intent': 'neutral',
        'targeting': 'burst',
        'target_ground': True,
        'radius':1
    },

    'ability_flame_breath': {
        'name': 'Flame Breath',
        'function' : monster_actions.flame_breath,
        'element':['fire'],
        'cooldown' : 6,
        'range': 4,
        'damage': '2d8',
        'intent': 'aggressive',
        'targeting': 'cone',
        'target_ground': True,
        'save_dc': 20
    },

    'ability_reeker_breath': {
        'name': 'Reeker Breath',
        'function' : monster_actions.reeker_breath,
        'element':['life'],
        'cooldown' : 5,
        'range': 4,
        'damage': '1d8',
        'intent': 'aggressive',
    },

    'ability_great_dive': {
        'name': 'Great Dive',
        'function' : monster_actions.great_dive,
        'cooldown' : 10,
        'range': 10,
        'radius': 1,
        'cast_time': 1,
        'target_ground': True,
        'pre_cast': monster_actions.great_dive_channel,
        'targeting': 'ranged burst',
        'intent': 'aggressive',
    },

    'ability_heat_ray': {
        'name': 'heat ray',
        'function': spell_actions.heat_ray,
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
        'function': spell_actions.flame_wall,
        'cooldown': 10,
        'element':['fire'],
        'dice' : 0,
        'target_ground': True,
        'base_damage' : '0d0',
        'range':10,
        'intent': 'aggressive',
    },

    'ability_fireball': {
        'name': 'fireball',
        'function': spell_actions.fireball,
        'cooldown': 20,
        'element': ['fire'],
        'dice': 2,
        'base_damage': '2d6',
        'targeting': 'beam',
        'target_ground': True,
        'pierce': 1,
        'cast_time': 2,
        'range': 8,
        'radius': 2,
        'intent': 'aggressive',
    },

    'ability_magma_bolt': {
        'name': 'heat ray',
        'function': spell_actions.magma_bolt,
        'cooldown': 10,
        'element':['fire'],
        'dice' : 3,
        'base_damage' : '3d6',
        'target_ground': True,
        'pierce': 1,
        'range':10,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_arcane_arrow': {
        'name': 'arcane arrow',
        'function': spell_actions.arcane_arrow,
        'cooldown': 2,
        'element':['lightning'],
        'dice' : 1,
        'base_damage' : '3d6',
        'pierce': 0,
        'range':5,
        'intent': 'aggressive',
        'targeting': 'beam_interrupt',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_frozen_orb': {
        'name': 'frozen orb',
        'function': spell_actions.frozen_orb,
        'cooldown': 3,
        'element':['cold'],
        'dice' : 2,
        'base_damage' : '3d4',
        'save_dc': 10,
        'targeting': 'beam-interrupt',
        'range':4,
        'intent': 'aggressive',
    },

    'ability_flash_frost': {
        'name': 'flash frost',
        'function': spell_actions.flash_frost,
        'cooldown': 10,
        'element':['cold'],
        'dice' : 0,
        'base_damage' : '0d0',
        'save_dc':12,
        'range':6,
        'intent': 'aggressive',
    },

    'ability_ice_shards': {
        'name': 'ice shards',
        'function': spell_actions.ice_shards,
        'cooldown': 4,
        'element':['cold'],
        'dice' : 1,
        'base_damage' : '1d8',
        'targeting': 'cone',
        'target_ground': True,
        'save_dc': 10,
        'range': 5,
        'radius': 1,
        'intent': 'aggressive',
    },

    'ability_snowstorm': {
        'name': 'snowstorm',
        'function': spell_actions.snowstorm,
        'cooldown': 10,
        'element':['cold'],
        'dice' : 1,
        'save_dc':10,
        'base_damage' : '1d4',
        'range':10,
        'radius':4,
        'intent': 'aggressive',
    },

    'ability_avalanche': {
        'name': 'avalanche',
        'function': spell_actions.avalanche,
        'cooldown': 20,
        'element':['cold'],
        'targeting':'beam_wide',
        'target_ground': True,
        'save_dc':10,
        'dice' : 2,
        'base_damage' : '3d8',
        'range':10,
        'intent': 'aggressive',
    },

    'ability_hex': {
        'name': 'hex',
        'function': spell_actions.hex,
        'cooldown': 20,
        'element':['death'],
        'dice' : 0,
        'base_damage' : '0d0',
        'pierce': 0,
        'save_dc':10,
        'range':6,
        'intent': 'aggressive',
    },

    'ability_defile': {
        'name': 'defile',
        'function': spell_actions.defile,
        'cooldown': 5,
        'element':['death'],
        'dice' : 1,
        'base_damage' : '2d8',
        'target_ground': True,
        'pierce': 0,
        'range':6,
        'intent': 'neutral',
    },

    'ability_shackles_of_the_dead': {
        'name': 'shackles of the dead',
        'function': spell_actions.shackles_of_the_dead,
        'cooldown': 20,
        'element':['death'],
        'dice' : 0,
        'base_damage' : '0d0',
        'target_ground': True,
        'save_dc': 15,
        'pierce': 0,
        'range':6,
        'radius':1,
        'intent': 'aggressive',
    },

    'ability_sacrifice': {
        'name': 'profane',
        'function': spell_actions.sacrifice,
        'cooldown': 10,
        'element':['death'],
        'dice' : 2,
        'base_damage' : '3d8',
        'targeting': 'burst',
        'pierce': 2,
        'radius': 2,
        'intent': 'aggressive',
    },

    'ability_corpse_dance': {
        'name': 'corpse dance',
        'function': spell_actions.corpse_dance,
        'cooldown': 40,
        'element':['death'],
        'dice' : 0,
        'base_damage' : '0d0',
        'target_ground': True,
        'range':6,
        'radius':3,
        'cast_time':3,
        'buff_duration':50,
        'intent': 'supportive',
    },

    'ability_green_touch': {
        'name': 'green touch',
        'function': spell_actions.green_touch,
        'cooldown': 5,
        'element':['life'],
        'range':8,
        'radius':3,
        'intent': 'neutral',
        'target_ground': True,
    },

    'ability_fungal_growth': {
        'name': 'fungal growth',
        'function': spell_actions.fungal_growth,
        'cooldown': 10,
        'element':['life'],
        'range':4,
        'intent': 'neutral',
        'target_ground': True,
    },

    'ability_summon_dragonweed': {
        'name': 'summon dragonweed',
        'function': spell_actions.summon_dragonweed,
        'cooldown': 5,
        'element':['life'],
        'range':2,
        'intent': 'aggressive',
        'targeting': 'summon',
    },

    'ability_bramble': {
        'name': 'bramble',
        'function': spell_actions.bramble,
        'cooldown': 5,
        'element':['life'],
        'range':4,
        'intent': 'aggressive',
        'damage': '3d6',
        'duration_base': 20,
        'duration_variance': '1d10',
        'bleed_duration': 5,
        'targeting': 'cone',
        'target_ground': True
    },

    'ability_strangleweeds': {
        'name': 'strangleweeds',
        'function': spell_actions.bramble,
        'cooldown': 5,
        'element':['life'],
        'intent': 'aggressive',
        'tick_damage': '3d10',
        'duration': 10,
        'range': 10
    },

    'ability_bless': {
        'name': 'bless',
        'function': spell_actions.bless,
        'cooldown': 30,
        'element':['radiance'],
        'intent': 'supportive',
    },

    'ability_smite': {
        'name': 'smite',
        'function': spell_actions.smite,
        'cooldown': 10,
        'element': ['radiance'],
        'dice': 2,
        'base_damage': '3d6',
        'defense': 'will',
        'save_dc': 15,
        'pierce': 3,
        'shred': 2,
        'range': 10,
        'intent': 'aggressive',
    },

    'ability_castigate': {
        'name': 'castigate',
        'function': spell_actions.castigate,
        'cooldown': 10,
        'element':['radiance'],
        'intent': 'aggressive',
    },

    'ability_holy_lance': {
        'name': 'holy lance',
        'function': spell_actions.holy_lance,
        'cooldown': 30,
        'element':['radiance'],
        'dice' : 2,
        'base_damage' : '2d8',
        'target_ground' : True,
        'radius':2,
        'range':8,
        'intent': 'aggressive',
        'tick': {
            'cooldown': 1,
            'dice' : 1,
            'base_damage' : '1d8',
            'element':['radiance'],
            'intent': 'aggressive',
        },
    },

    'ability_off_hand_shoot': {
        'name': 'Off Hand Shot',
        'function': item_actions.offhand_shot,
        'cooldown': 5,
        'range': 10,
        'description': 'Fire your weapon at an enemy you can see.',
        'intent': 'aggressive',
    },

    'ability_focus': {
        'name' : 'Focus',
        'function': perk_actions.focus,
        'cooldown': 0,
        'range': 10,
        'stamina_cost' : 5,
        'description' : 'Focus on hitting your target, increasing your accuracy for a turn.',
        'targeting':'self',
        'intent': 'aggressive',
    },

    'ability_summon_spiders': {
        'name': 'Summon Spiders',
        'function': monster_actions.spawn_spiders,
        'cooldown': 8,
        'max_summons': 4,
        'summons_per_cast': '1d2',
        'intent': 'aggressive',
    },

    'ability_web_bomb': {
        'name': 'Web Bomb',
        'function': monster_actions.web_bomb,
        'cooldown': 6,
        'intent': 'aggressive',
    },

    'ability_heal_other': {
        'name': 'Heal Other',
        'function': monster_actions.heal_other,
        'cooldown': 1,
        'intent': 'support',
        'target_function': ai.target_damaged_ally,
    },

    'ability_throw_net': {
        'name': 'Throw Net',
        'function': monster_actions.throw_net,
        'range' : 4,
        'save_dc' : 25,
        'cooldown': 30,
        'duration': 5,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_haste': {
        'name': 'Haste',
        'function': monster_actions.haste,
        'cooldown': 15,
        'intent': 'support',
        'range': 8,
        'duration': 10,
        'target_function': ai.target_damaged_ally,
    },

    'ability_teleportal': {
        'name': 'Teleportal',
        'function': charm_actions.create_teleportal,
        'cooldown': 8,
        'intent': 'aggressive',
        'range': 3,
    },

    'ability_fire_bomb': {
        'name': 'Time Bomb',
        'function': charm_actions.timebomb,
        'cooldown': 6,
        'intent': 'aggressive',
        'targeting': 'ranged burst',
        'radius': 1,
        'range': 6,
    },

    'ability_ice_bomb': {
        'name': 'Time Bomb',
        'function': charm_actions.timebomb,
        'cooldown': 6,
        'intent': 'aggressive',
        'targeting': 'ranged burst',
        'radius': 1,
        'range': 6,
    },

    'ability_time_bomb': {
        'name': 'Time Bomb',
        'function': charm_actions.timebomb,
        'cooldown': 6,
        'intent': 'aggressive',
        'range': 6,
        'delay': 3,
    },

    'ability_summon_demon': {
        'name' : 'Summon Demon',
        'cooldown': 20,
        'cast_time': 10,
        'summons':{'monster_servant_of_oblivion':20},
        'function': monster_actions.summon_demon
    },

    'ability_mass_heal': {
        'name': 'Mass Heal',
        'function': None,
        'targeting': 'allies'
    },

    'ability_mass_cleanse': {
        'name': 'Mass Heal',
        'function': None,
        'targeting': 'allies'
    },

    'ability_mass_reflect': {
        'name': 'Mass Heal',
        'function': None,
        'targeting': 'allies'
    },

    'ability_holy_water': {
        'name': 'holy water',
        'function': charm_actions.holy_water,
        'cooldown': 2,
        'element':['radiance'],
        'dice' : 0,
        'base_damage' : '8d10',
        'pierce': 3,
        'range':2,
        'intent': 'aggressive',
        'targeting': 'beam_interrupt'
    },

    'summon_guardian_angel': {
        'targeting': 'summon'
    },
}

default_abilities = {
    'attack' : Ability('ability_attack', 'Attack','Attack an enemy',0),
    'bash' : Ability('ability_bash', 'Bash','Knock an enemy back',0, stamina_cost=20),
    'jump' : Ability('ability_jump', 'Jump','Jump to a tile',0, stamina_cost=50),
    'raise shield' : Ability('ability_raise_shield', 'Raise Shield',
                             'Spend stamina to recover your shield after it has been knocked aside.',
                              cooldown=10)
}
