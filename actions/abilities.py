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
    def __init__(self, ability_id, name, description, cooldown=0, stamina_cost=0, intent='aggressive'):
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
            result = actions.invoke_ability(self.ability_id, actor, target,
                                            spell_context={'stamina_cost': self.stamina_cost})
            if result != 'didnt-take-turn' and result != 'cancelled':
                self.current_cd = self.cooldown
                if self.stamina_cost != 0 and actor is player.instance:
                    actor.fighter.adjust_stamina(-self.stamina_cost)
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
        'targeting': 'beam_interrupt',
        'range': 1
    },

    'ability_thrust_and_cleave': {
        'name': 'Thrust/Cleave',
        'description': 'Attack an enemy up to 2 spaces away and all enemies adjacent to it.',
        'function': common.reach_and_cleave_attack,
        'cooldown': 0,
        'intent': 'aggressive',
        'targeting': 'beam_interrupt',
        'range': 1
    },

    'ability_raise_shield': {
        'name': 'raise shield',
        'description': 'restore your shield points to maximum',
        'function': lambda a,t,_: a.fighter.get_equipped_shield().sh_raise(),
        'targeting': 'self',
        'intent': 'supportive',
        'cooldown': 10
    },

    'ability_bash': {
        'name': 'Bash',
        'description': 'Knock an enemy back',
        'targeting': 'override',
        'function': lambda a,t,_: common.bash_attack(a),
        'intent': 'aggressive',
    },

    'ability_cleave': {
        'name': 'Cleave',
        'description': 'Make an attack against all adjacent enemies',
        'targeting': 'override',
        'function': common.cleave_attack,
        'cooldown': 0,
        'intent': 'aggressive',
    },

    'ability_jump': {
        'name': 'Jump',
        'targeting': 'self',
        'function': lambda a,t,_: player.jump(a,2)
    },

    'ability_attack': {
        'name': 'Attack',
        'targeting': 'override',
        'description': 'Attack an enemy with your held weapon',
        'function': lambda a,t,_: common.attack(),
        'cooldown': 0,
        'intent': 'aggressive',
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
        'targeting': 'self'
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
        'targeting': 'beam_interrupt',
        'cooldown': 3,
        'intent': 'aggressive',
        'range': 4,
        'target_function' : ai.target_clear_line_of_fire,
    },

    'ability_dragonweed_pull': {
        'name': 'Dragonweed Pull',
        'function': monster_actions.dragonweed_pull,
        'targeting': 'beam_interrupt',
        'cooldown': 1,
        'intent': 'aggressive',
        'target_function' : ai.target_clear_line_of_fire,
        'save_dc': 15,
    },

    'ability_silence': {
        'name': 'Silence',
        'function': monster_actions.silence,
        'range':5,
        'cooldown': 15,
        'intent': 'aggressive',
        'base_dc': 20,
        'duration': 15
    },

    'ability_raise_zombie': {
        'name': 'Raise Zombie',
        'function' : monster_actions.raise_zombie,
        'cooldown' : 3,
        'intent': 'neutral',
        'targeting': 'self',
        'target_ground': True,
        'burst':1
    },

    'ability_flame_breath': {
        'name': 'Flame Breath',
        'function' : monster_actions.flame_breath,
        'element':['fire'],
        'defense_types': [],
        'cooldown' : 6,
        'range': 4,
        'base_damage': '2d8',
        'intent': 'aggressive',
        'targeting': 'cone',
        'target_ground': True,
        'save_dc': 20
    },

    'ability_reeker_breath': {
        'name': 'Reeker Breath',
        'function' : monster_actions.reeker_breath,
        'element':['life'],
        'damage_types':['fume'],
        'defense_types': ['fortitude'],
        'accuracy': 25,
        'cooldown' : 5,
        'range': 4,
        'base_damage': '1d8',
        'intent': 'aggressive',
    },

    'ability_great_dive': {
        'name': 'Great Dive',
        'function' : monster_actions.great_dive,
        'cooldown' : 10,
        'range': 10,
        'cast_time': 1,
        'target_ground': True,
        'pre_cast': monster_actions.great_dive_channel,
        'burst': 1,
        'intent': 'aggressive',
        'warning': True
    },

    'ability_heat_ray': {
        'name': 'heat ray',
        'function': spell_actions.heat_ray,
        'target_ground': True,
        'targeting': 'beam',
        'cooldown': 2,
        'element':['fire'],
        'defense_types': [],
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
        'range': 3,
        'intent': 'aggressive',
    },

    'ability_fireball': {
        'name': 'fireball',
        'function': spell_actions.fireball,
        'cooldown': 20,
        'element': ['fire'],
        'defense_types': [],
        'dice': 2,
        'base_damage': '2d6',
        'cast_time': 2,
        'range': 8,
        'targeting': 'beam_interrupt',
        'burst': 1,
        'hits_friendlies': True,
        'intent': 'aggressive',
    },

    'ability_shatter_item': {
        'name': 'shatter item',
        'function': spell_actions.shatter_item,
        'targeting': 'override',  # invented override targeting for this ability
        'range':10,
        'burst': 1,
        'cooldown': 20,
        'damage_types':['slashing'],
        'element': ['fire'],
        'defense_types': [],
        'shred': 3,
        'pierce': 1,
        'dice' : 2,
        'base_damage' : '2d4',
        'blockable': True,
        'save_dc': 8,
        'intent': 'aggressive',
    },

    'ability_magma_bolt': {
        'name': 'heat ray',
        'function': spell_actions.magma_bolt,
        'cooldown': 10,
        'element':['fire'],
        'dice' : 3,
        'base_damage' : '3d6',
        'defense_types' : ['evasion'],
        'target_ground': True,
        'range': 5,
        'shred': 3,
        'intent': 'aggressive',
        'targeting' : 'beam',
        'target_function' : ai.target_clear_line_of_fire,
        'lava_duration': '3d4'
    },

    'ability_arcane_arrow': {
        'name': 'arcane arrow',
        'function': spell_actions.arcane_arrow,
        'targeting': 'beam_interrupt',
        'target_function' : ai.target_clear_line_of_fire,
        'range':7,
        'cooldown': 2,
        'element':['arcane'],
        'damage_types':['lightning'],
        'defense_types' : ['evasion'],
        'accuracy': 14,
        'dice' : 1,
        'base_damage' : '2d6',
        'blockable': True,
        'intent': 'aggressive',
    },

    'ability_spatial_exchange': {
        'name': 'spatial exchange',
        'function': spell_actions.spatial_exchange,
        'range': 5,
        'cooldown': 10,
        'element': ['arcane'],
        'damage_types': ['bludgeoning'],
        'defense_types': ['will'],
        'accuracy': 10,
        'dice': 0,
        'base_damage': '0d0',
        'intent': 'aggressive'
    },

    'data_ability_spatial_exchange': {
        'name': 'spatial exchange',
        'element': ['arcane'],
        'damage_types': ['bludgeoning'],
        'defense_types': None,
        'dice': 1,
        'base_damage': '1d6',
        'intent': 'aggressive'
    },

    'ability_shimmering_swords': {
        'function': spell_actions.shimmering_swords,
        'targeting': 'self',
        'cooldown': 30,
        'element': ['arcane'],
        'duration_base': 3,
        'intent': 'aggressive',
        'sword_count': 4
    },

    'ability_frozen_orb': {
        'name': 'frozen orb',
        'function': spell_actions.frozen_orb,
        'targeting': 'beam_interrupt',
        'target_function' : ai.target_clear_line_of_fire,
        'range':4,
        'cooldown': 3,
        'element':['cold'],
        'defense_types' : ['evasion'],
        'base_acc': 25,
        'dice' : 1,
        'base_damage' : '3d4',
        'save_dc': 10,
        'blockable': True,
        'intent': 'aggressive',
    },

    'ability_flash_frost': {
        'name': 'flash frost',
        'function': spell_actions.flash_frost,
        'cooldown': 10,
        'element':['cold'],
        'save_dc':12,
        'range':3,
        'intent': 'aggressive',
    },

    'ability_ice_shards': {
        'name': 'ice shards',
        'function': spell_actions.ice_shards,
        'targeting': 'cone',
        'target_ground': True,
        'range': 5,
        'cooldown': 4,
        'element':['cold'],
        'damage_types':['cold', 'piercing'],
        'defense_types': [],
        'pierce': 1,
        'shred': 2,
        'dice' : 1,
        'base_damage' : '1d8',
        'blockable': True,
        'save_dc': 10,
        'intent': 'aggressive',
    },

    'ability_snowstorm': {
        'name': 'snowstorm',
        'function': spell_actions.snowstorm,
        'target_ground': True,
        'cooldown': 10,
        'element':['cold'],
        'defense_types' : ['fortitude'],
        'accuracy' : 20,
        'dice' : 1,
        'base_damage' : '1d4',
        'range':10,
        'intent': 'aggressive',
    },

    'ability_snowstorm_tick': {
        'name': 'snowstorm tick',
        'function': spell_actions.snowstorm_tick,
        'targeting': 'self',
        'burst': 4,
        'element':['cold'],
        'defense_types' : ['fortitude'],
        'accuracy' : 20,
        'dice' : 1,
        'base_damage' : '1d4',
        'save_dc':10,
    },

    'ability_avalanche': {
        'name': 'avalanche',
        'function': spell_actions.avalanche,
        'targeting':'beam_wide',
        'target_ground': True,
        'cooldown': 20,
        'element':['cold'],
        'defense_types':['fortitude'],
        'accuracy': 40,
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
        'save_dc':10,
        'range':6,
        'intent': 'aggressive',
    },

    'ability_defile': {
        'name': 'defile',
        'function': spell_actions.defile,
        'target_ground': True,
        'cooldown': 5,
        'element':['death'],
        'defense_types':['will'],
        'accuracy':20,
        'dice' : 1,
        'base_damage' : '2d8',
        'range':6,
        'intent': 'neutral',
    },

    'ability_shackles_of_the_dead': {
        'name': 'shackles of the dead',
        'function': spell_actions.shackles_of_the_dead,
        'burst':1,
        'cooldown': 20,
        'element':['death'],
        'save_dc': 15,
        'range':5,
        'intent': 'aggressive',
        'duration': 5,
    },

    'ability_sacrifice': {
        'name': 'profane',
        'function': spell_actions.sacrifice,
        'targeting': 'self',
        'burst': 1,
        'cooldown': 10,
        'element':['death'],
        'defense_types':['will'],
        'accuracy': 35,
        'dice' : 1,
        'base_damage' : '1d24',
        'intent': 'aggressive',
    },

    'ability_corpse_dance': {
        'name': 'corpse dance',
        'function': spell_actions.corpse_dance,
        'target_ground': True,
        'targeting':'self',
        'radius':3,
        'cooldown': 40,
        'element':['death'],
        'cast_time':1,
        'buff_duration':50,
        'intent': 'supportive',
    },

    'ability_green_touch': {
        'name': 'green touch',
        'function': spell_actions.green_touch,
        'target_ground': True,
        'cooldown': 5,
        'element':['life'],
        'range':8,
        'intent': 'neutral',
    },

    'ability_fungal_growth': {
        'name': 'fungal growth',
        'function': spell_actions.fungal_growth,
        'target_ground': True,
        'cooldown': 10,
        'element':['life'],
        'range':4,
        'intent': 'neutral',
    },

    'ability_summon_dragonweed': {
        'name': 'summon dragonweed',
        'function': spell_actions.summon_dragonweed,
        'targeting': 'summon',
        'cooldown': 5,
        'element':['life'],
        'range':2,
        'intent': 'aggressive',
    },

    'ability_bramble': {
        'name': 'bramble',
        'function': spell_actions.bramble,
        'targeting': 'cone',
        'target_ground': True,
        'cooldown': 5,
        'element':['life'],
        'damage_types':['slashing'],
        'defense_types': ['fortitude'],
        'accuracy': 35,
        'shred': 3,
        'range':4,
        'base_damage': '3d6',
        'dice':1,
        'duration_base': 20,
        'duration_variance': '1d10',
        'bleed_dc_base': 12,
        'bleed_duration': 5,
        'intent': 'aggressive',
    },

    'ability_strangleweeds': {
        'name': 'strangleweeds',
        'function': spell_actions.strangleweeds,
        'targeting': 'self',
        'range': 10,
        'cooldown': 5,
        'element':['life'],
        'tick_damage': '3d10',
        'duration': 10,
        'intent': 'aggressive',
    },

    'ability_bless': {
        'name': 'bless',
        'function': spell_actions.bless,
        'targeting': 'self',
        'cooldown': 30,
        'element':['radiance'],
        'intent': 'supportive',
    },

    'ability_blessed_aegis': {
        'name': 'blessed aegis',
        'function': charm_actions.summon_weapon,
        'targeting': 'self',
        'item': 'shield_blessed_aegis',
        'element': ['radiance'],
        'intent': 'supportive',
    },

    'ability_smite': {
        'name': 'smite',
        'function': spell_actions.smite,
        'range': 10,
        'cooldown': 10,
        'element': ['radiance'],
        'defense_types':['will'],
        'accuracy': 40,
        'dice': 2,
        'base_damage': '3d6',
        'defense': 'will',
        'save_dc': 15,
        'intent': 'aggressive',
    },

    'ability_castigate': {
        'name': 'castigate',
        'function': spell_actions.castigate,
        'targeting': 'self',
        'burst': 1,
        'cooldown': 10,
        'element':['radiance'],
        'intent': 'aggressive',
        'save_dc': 15,
    },

    'ability_holy_lance': {
        'name': 'holy lance',
        'function': spell_actions.holy_lance,
        'target_ground' : True,
        'burst': 2,
        'range':7,
        'cooldown': 30,
        'element':['radiance'],
        'defense_types':['evasion'],
        'accuracy':30,
        'dice' : 2,
        'base_damage' : '2d8',
        'blockable': True,
        'intent': 'aggressive',
    },

    'ability_holy_lance_tick': {
        'name': 'holy lance tick',
        'function': spell_actions.holy_lance_tick,
        'targeting': 'self',
        'burst': 2,
        'dice': 1,
        'base_damage': '1d8',
        'element': ['radiance'],
        'defense_types': ['will'],
        'accuracy': 25,
        'intent': 'aggressive',
    },

    'ability_bow_shot': {
        'name': 'Bow Shot',
        'function': item_actions.bow_shot,
        'range': 20,
        'cooldown': 0,
        'cast_time': 1,
        'description': 'Fire your weapon at an enemy you can see.',
        'intent': 'aggressive',
    },

    'ability_off_hand_shot': {
        'name': 'Off-Hand Shot',
        'function': item_actions.offhand_shot,
        'range': 10,
        'cooldown': 5,
        'description': 'Fire your weapon at an enemy you can see.',
        'intent': 'aggressive',
    },

    'ability_focus': {
        'name' : 'Focus',
        'function': perk_actions.focus,
        'targeting':'self',
        'cooldown': 0,
        'stamina_cost' : 5,
        'description' : 'Focus on hitting your target, increasing your accuracy for a turn.',
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
        'target_function': ai.target_damaged_ally,
        'cooldown': 1,
        'intent': 'support',
    },

    'ability_throw_net': {
        'name': 'Throw Net',
        'function': monster_actions.throw_net,
        'target_function' : ai.target_clear_line_of_fire,
        'range' : 4,
        'save_dc' : 25,
        'cooldown': 30,
        'duration': 5,
        'intent': 'aggressive',
    },

    'ability_haste': {
        'name': 'Haste',
        'function': monster_actions.haste,
        'target_function': ai.target_damaged_ally,
        'range': 8,
        'cooldown': 15,
        'intent': 'support',
        'duration': 10,
    },

    'ability_teleportal': {
        'name': 'Teleportal',
        'function': charm_actions.create_teleportal,
        'target_ground': True,
        'range': 3,
        'cooldown': 8,
        'intent': 'aggressive',
    },

    'ability_fire_bomb': {
        'name': 'Time Bomb',
        'function': charm_actions.firebomb,
        'targeting': 'beam_interrupt',
        'burst': 1,
        'range': 5,
        'cooldown': 6,
        'elements': ['fire'],
        'defense_types': [],
        'base_damage': '4d10',
        'dice': 0,
        'hits_friendlies': True,
        'intent': 'aggressive',
    },

    'ability_ice_bomb': {
        'name': 'Time Bomb',
        'function': charm_actions.icebomb,
        'targeting': 'beam_interrupt',
        'burst': 1,
        'range': 5,
        'cooldown': 6,
        'elements': ['cold'],
        'defense_types': [],
        'base_damage': '3d10',
        'dice': 0,
        'hits_friendlies': True,
        'freeze_duration': 6,
        'intent': 'aggressive',
    },

    'ability_time_bomb': {
        'name': 'Time Bomb',
        'function': charm_actions.timebomb,
        'target_ground': True,
        'target_function': ai.target_open_space_near_target,
        'range': 5,
        'cooldown': 6,
        'delay': 3,
        'intent': 'aggressive',
    },

    'data_time_bomb_explosion': {  # Data only - not invokable
        'name': 'time bomb explosion',
        'base_damage': '6d10',
        'dice': 0,
        'elements': ['arcane'],
        'damage_types': ['lightning'],
        'defense_types': [],
        'hits_friendlies': True,
    },

    'ability_summon_demon': {
        'name' : 'Summon Demon',
        'cooldown': 20,
        'cast_time': 10,
        'summons':{'monster_servant_of_oblivion':20},
        'function': monster_actions.summon_demon
    },

    'ability_mass_heal': {
        'name': 'mass heal',
        'function': charm_actions.mass_heal,
        'targeting': 'self',
        'burst' : 10,
        'intent' : 'support',
        'allies_only': True
    },

    'ability_mass_cleanse': {
        'name': 'mass cleanse',
        'function': charm_actions.mass_cleanse,
        'targeting': 'self',
        'burst' : 10,
        'intent' : 'support',
        'allies_only': True
    },

    'ability_mass_reflect': {
        'name': 'mass reflect',
        'function': charm_actions.mass_reflect,
        'targeting': 'self',
        'burst' : 10,
        'intent' : 'support',
        'allies_only': True
    },

    'ability_holy_water': {
        'name': 'holy water',
        'function': charm_actions.holy_water,
        'targeting': 'beam_interrupt',
        'range':2,
        'cooldown': 2,
        'element':['water'],
        'damage_types':['radiance'],
        'defense_types':['evasion', 'fortitude'],
        'accuracy': 50,
        'dice' : 0,
        'base_damage' : '8d10',
        'intent': 'aggressive',
    },

    'ability_summon_guardian_angel': {
        'targeting': 'summon'
    },

    'ability_healing_trance': {
        'targeting': 'self',
        'intent': 'support',
        'function': charm_actions.healing_trance,
    },

    'ability_summon_fire_elemental': {
        'targeting': 'self',
        'intent': 'aggressive',
        'function': charm_actions.summon_elemental,
        'summon': 'monster_fire_elemental',
        'duration_base': 15,
        'duration_variance': '1d10',
    },

    'ability_summon_earth_elemental': {
        'targeting': 'self',
        'intent': 'aggressive',
        'function': charm_actions.summon_elemental,
        'summon': 'monster_earth_elemental',
        'duration_base': 50,
        'duration_variance': '1d10',
    },

    'ability_summon_water_elemental': {
        'targeting': 'self',
        'intent': 'aggressive',
        'function': charm_actions.summon_elemental,
        'summon': 'monster_water_elemental',
        'duration_base': 30,
        'duration_variance': '1d10',
    },

    'ability_summon_air_elemental': {
        'targeting': 'self',
        'intent': 'aggressive',
        'function': charm_actions.summon_elemental,
        'summon': 'monster_air_elemental',
        'duration_base': 30,
        'duration_variance': '1d10',
    },

    'ability_summon_arcane_construct': {
        'targeting': 'self',
        'intent': 'aggressive',
        'function': spell_actions.summon_arcane_construct,
        'summon': 'monster_air_elemental',
        'duration_base': 20,
        'element': ['arcane'],
    },

    'ability_summon_lifeplant': {
        'targeting': 'self',
        'intent': 'support',
        'function': charm_actions.summon_lifeplant,
        'duration_base': 15,
        'duration_variance': '1d10',
    },

    'ability_dig': {
        'target_ground': True,
        'range': 1,
        'min_depth': 3,
        'depth_variance': '1d4',
        'function': charm_actions.farmers_talisman_dig,
    },

    'ability_create_terrain_wall': {
        'target_ground': True,
        'range': 5,
        'terrain_type': 'wall',
        'function': charm_actions.create_terrain,
    },
    'ability_create_terrain_grass': {
        'target_ground': True,
        'range': 5,
        'terrain_type': 'grass floor',
        'function': charm_actions.create_terrain,
    },
    'ability_create_terrain_water': {
        'target_ground': True,
        'range': 5,
        'terrain_type': 'shallow water',
        'function': charm_actions.create_terrain,
    },
    'ability_create_terrain_lava': {
        'target_ground': True,
        'range': 5,
        'terrain_type': 'lava',
        'function': charm_actions.create_terrain,
    },
    'ability_summon_soul_reaper': {
        'targeting': 'self',
        'intent': 'aggressive',
        'function': charm_actions.summon_weapon,
        'item': 'weapon_soul_reaper',
    },
    'ability_wild_growth': {
        'intent': 'aggressive',
        'range': 7,
        'cooldown': 4,
        'function': monster_actions.wild_growth,
        'root_duration': '1d5',
        'damage_per_tick': '1d10',
        'save_dc': 15
    },
    'ability_acid_flask': {
        'name': 'acid flask',
        'function': charm_actions.acid_flask,
        'targeting': 'beam_interrupt',
        'range': 5,
        'burst': 1,
        'cooldown': 6,
        'base_damage': '5d4',
        'dice': 0,
        'element': [],
        'damage_types': ['acid'],
        'defense_types': [],
        'shred': 10,
        'intent': 'aggressive',
    },
    'ability_frostfire': {
        'name': 'frostfire',
        'function': charm_actions.frostfire,
        'cooldown': 10,
        'element':['cold'],
        'target_ground': True,
        'range': 3,
        'intent': 'aggressive',
    },
    'ability_vitality_potion': {
        'name': 'vitality potion',
        'targeting': 'self',
        'intent': 'support',
        'function': charm_actions.vitality_potion,
    },
    'ability_longstride': {
        'name': 'Longstride',
        'description': 'instantly teleport to a space you can see.',
        'range': consts.TORCH_RADIUS,
        'target_ground': True,
        'function': item_actions.longstride,
        'cooldown': 100,
    },
    'ability_boomerang': {
        'name': 'Throw Boomerang',
        'description': 'throw your boomerang at an enemy and attempt to catch it upon return.',
        'range': 7,
        'function': common.boomerang,
        'intent': 'aggressive'
    }
}

default_abilities = {
    'attack' : Ability('ability_attack', 'Attack','Attack an enemy'),
    'bash' : Ability('ability_bash', 'Bash','Knock an enemy back'),
    'jump' : Ability('ability_jump', 'Jump','Jump to a tile'),
    'raise shield' : Ability('ability_raise_shield', 'Raise Shield', 'Spend stamina to fully recover your shield.',
                             cooldown=10)
}
