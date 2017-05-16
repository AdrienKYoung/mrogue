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

import libtcodpy as libtcod
import consts
import ai
import pathfinding
import game as main

# Monster Flags
NO_CORPSE = 1
IMMOBILE = 2
EVIL = 4

proto = {
    'monster_zombie_goblin': {
        'name': 'goblin lurker',
        'char': 'g',
        'color': libtcod.desaturated_green,
        'hp': 15,
        'strength_dice' : '3d6',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 2,
        'accuracy': 15,
        'move_speed': 0.6,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'A rotting corpse of a goblin, animated by evil magic. Little has changed from when it was alive.',
        'resistances': [],
        'weaknesses' : ['radiance'],
        'shred': 1,
        'flags' : NO_CORPSE | EVIL,
        'subtype':'zombie',
    },
    'monster_zombie_vermin': {
        'name': 'zombie vermin',
        'char': 'v',
        'color': libtcod.dark_purple,
        'body_type': 'insect',
        'hp': 1,
        'strength_dice' : '1d6',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 19,
        'move_speed': 0.65,
        'attack_speed': 1.0,
        'ai': ai.AI_Default,
        'description': 'A rotting corpse of some vermin, animated by evil magic.',
        'resistances': [],
        'weaknesses' : ['radiance'],
        'shred': 1,
        'flags' : NO_CORPSE | EVIL,
        'subtype':'undead',
    },
    'monster_zombie_insect': {
        'name': 'zombie insect',
        'char': 'z',
        'color': libtcod.dark_purple,
        'body_type': 'insect',
        'hp': 20,
        'strength_dice' : '2d6',
        'attack_bonus' : 1,
        'armor': 0,
        'evasion': 0,
        'accuracy': 15,
        'move_speed': 0.8,
        'attack_speed': 0.8,
        'ai': ai.AI_Default,
        'description': 'Rotting corpse of some insect, animated by evil magic.',
        'resistances': [],
        'shred': 1,
        'subtype':'insect',
        'flags' : NO_CORPSE | EVIL,
    },
    'monster_zombie_beast': {
        'name': 'zombie beast',
        'char': 'b',
        'color': libtcod.dark_purple,
        'hp': 25,
        'strength_dice' : '3d6',
        'attack_bonus' : 1,
        'armor': 0,
        'evasion': 10,
        'accuracy': 20,
        'move_speed': 0.5,
        'attack_speed': 1.0,
        'ai': ai.AI_Default,
        'description': 'A rotting corpose of some beast, animated by evil magic',
        'resistances': [],
        'weaknesses' : ['radiance'],
        'shred': 1,
        'subtype':'zombie',
        'flags' : NO_CORPSE | EVIL,
    },
    'monster_dark_angel': {
        'name': 'dark angel',
        'char': 'A',
        'color': libtcod.dark_purple,
        'hp': 50,
        'strength_dice' : '3d8',
        'attack_bonus' : 2,
        'spell_power': 50,
        'armor': 3,
        'evasion': 12,
        'accuracy': 25,
        'move_speed': 1.1,
        'attack_speed': 1.8,
        'ai': ai.AI_Default,
        'attributes': ['ability_smite'],
        'description': 'A twisted fallen angel, aweful and beautiful',
        'resistances': ['death'],
        'weaknesses' : ['radiance'],
        'shred': 2,
        'subtype':'angel',
        'loot_level':15,
        'equipment': [{'weapon_greatsword':30,'weapon_halberd':30,'weapon_warhammer':30},{'equipment_plate_armor':100}],
        'movement_type': pathfinding.FLYING,
        'flags' : NO_CORPSE | EVIL,
    },
}