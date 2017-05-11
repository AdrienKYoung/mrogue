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

import libtcodpy
import game as main
import player
import combat
import dungeon
import spells
import actions
import charms

table = {
    'weapons_0': [
        'weapon_dagger',
        'weapon_hatchet',
        'weapon_longsword',
        'weapon_mace',
        'weapon_spear',
    ],

     'weapons_1': [
        'weapon_dagger',
        'weapon_hatchet',
        'weapon_longsword',
        'weapon_mace',
        'weapon_spear',
        'weapon_pickaxe',
    ],

    'weapons_2' : [
        'weapon_dagger',
        'weapon_messer',
        'weapon_hatchet',
        'weapon_longsword',
        'weapon_greatsword',
        'weapon_mace',
        'weapon_warhammer',
        'weapon_dane_axe',
        'weapon_spear',
        'weapon_halberd',
        'weapon_pickaxe',
        'weapon_katar',
    ],

    'armor_0': [
        'equipment_shield',
        'equipment_leather_armor',
        'equipment_cloth_robes',
        'equipment_iron_helm',
        'equipment_gauntlets'
    ],

    'armor_1': [
        'equipment_shield',
        'equipment_leather_armor',
        'equipment_cloth_robes',
        'equipment_iron_helm',
        'equipment_greaves',
        'equipment_gauntlets',
        'equipment_mail_armor'
    ],

    'armor_2' : [
        'equipment_iron_helm',
        'equipment_greaves',
        'equipment_gauntlets',
        'equipment_mail_armor',
        'equipment_brigandine',
        'equipment_great_helm',
        'equipment_greaves'
    ],

    'armor_3' : [
        'equipment_brigandine',
        'equipment_great_helm',
        'equipment_greaves',
        'equipment_gauntlets',
        'equipment_armet_helm',
        'equipment_plate_armor',
    ],

     'consumables_1': [
        'essence_life',
        'essence_life',
        'essence_life',
        'essence_earth',
        'essence_earth',
        'essence_water',
        'essence_water',
        'essence_fire',
        'essence_air',
        'essence_cold',
        'essence_arcane',
    ],

     'consumables_2': [
        'essence_life',
        'essence_life',
        'essence_life',
        'essence_earth',
        'essence_water',
        'essence_fire',
        'essence_air',
        'essence_cold',
        'essence_arcane',
        'essence_death',
        'essence_radiant',
        'scroll_forge',
    ],

    'tomes_1': [
        'book_lesser_fire',
        'book_lesser_death',
        'book_lesser_cold',
    ],

    'gems_1': [
        'gem_lesser_fire',
        'gem_lesser_water',
        'gem_lesser_earth',
        'gem_lesser_air',
        'gem_lesser_cold',
        'gem_lesser_life',
        'gem_lesser_arcane',
    ],

    'gems_2': [
        'gem_lesser_fire',
        'gem_lesser_water',
        'gem_lesser_earth',
        'gem_lesser_air',
        'gem_lesser_cold',
        'gem_lesser_life',
        'gem_lesser_arcane',
        'gem_lesser_death',
        'gem_lesser_radiance',
    ],

    'keys_1': [
        'glass_key'
    ],

    'charms_1': [
        'charm_farmers_talisman',
        'charm_primal_totem',
        'charm_holy_symbol',
        'charm_shard_of_creation'
    ]
}

def item_from_table(branch,loot_table=None):
    if loot_table is None:
        loot_table = choose_loot_table(branch)

    if loot_table is None:
        return None

    if not loot_table in table:
        split = loot_table.split('_')
        i = int(split[1]) - 1
        while i >= 0:
            lower = split[0]+'_'+str(i)
            if lower in table:
                loot_table = lower
                break
            i -= 1
        if loot_table not in table:
            return None

    loot_level=int(loot_table.split('_')[1])
    category=loot_table.split('_')[0]

    while main.roll_dice('1d20') == 20:
        loot_level += 1 #oh lawdy
        tmp = category+'_'+str(loot_level)
        if not tmp in table.keys():
            loot_level-=1
            break

    loot_table = category+'_'+str(loot_level)

    item_id = table[loot_table][libtcodpy.random_get_int(0,0,len(table[loot_table]))-1]
    material = None
    quality = ''
    if category == 'weapon':
        material = choose_weapon_material(loot_level)
        quality = choose_quality(loot_level)
    if category == 'armor':
        quality = choose_quality(loot_level)
        material = choose_armor_material(loot_level)

    return main.create_item(item_id, material, quality)

def choose_loot_table(branch):
    b = dungeon.branches[branch]
    if b.get('loot') is None:
        return None
    else:
        return main.random_choice(b['loot'])

def choose_weapon_material(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 20 * loot_level, 150))
    if roll < 5:
        return choose_weapon_material(loot_level + 5)
    elif roll < 15:
        return 'wooden'
    elif roll < 30:
        return 'bronze'
    elif roll < 95:
        return 'iron'
    elif roll < 105:
        return 'steel'
    elif roll < 120:
        return 'crystal'
    elif roll < 130:
        return 'meteor'
    elif roll < 140:
        return 'aetherwood'
    else:
        return 'blightstone'

def choose_armor_material(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 20 * loot_level, 150))
    if roll > 100:
        ops = armor_materials.keys()
        return ops[libtcodpy.random_get_int(0,0,len(ops)-1)]
    else:
        return ''


def choose_quality(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 20 * loot_level, 130))
    if roll < 5:
        return choose_quality(loot_level + 5)
    elif roll < 10:
        return 'broken'
    elif roll < 20:
        return 'crude'
    elif roll < 90:
        return '' # standard
    elif roll < 100:
        return 'military'
    elif roll < 110:
        return 'fine'
    elif roll < 120:
        return 'masterwork'
    else:
        return 'artifact'

item_categories = {
    'weapon' : { 'plural' : 'weapons' },
    'armor' : { 'plural' : 'armor' },
    'scroll' : { 'plural' : 'scrolls' },
    'potion' : { 'plural' : 'potions' },
    'book' : { 'plural' : 'books' },
    'charm' : { 'plural' : 'charms'},
    'gem' : { 'plural' : 'gems'},
    'key' : { 'plural' : 'keys'},
    'treasure' : { 'plural' : 'treasure' }
}

quality_progression = [
    'broken',
    'crude',
    '',
    'military',
    'fine',
    'masterwork',
    'artifact'
]

qualities = {
    'broken' : {
        'color' : libtcodpy.desaturated_red,
        'weapon': {
            'strength_dice_bonus' : -3,
            'accuracy_bonus' : -3,
            'shred_bonus' : -1,
        },
        'armor': {
            'evasion_bonus' : -5,
            'armor_bonus' : -1,
            'weight_bonus' : 0
        }
    },
    'crude' : {
        'color' : libtcodpy.dark_sepia,
        'weapon': {
            'strength_dice_bonus' : -2,
            'accuracy_bonus' : -1,
            'break_chance_bonus' : 5.0,
        },
        'armor': {
            'evasion_bonus' : -1,
            'armor_bonus' : 0,
            'weight_bonus' : 1
        }
    },
    '' : { # standard
        'color' : libtcodpy.light_gray,
        'weapon': {
            'strength_dice_bonus' : 0,
            'accuracy_bonus' : 0,
        },
        'armor': {
            'evasion_bonus' : 0,
            'armor_bonus' : 0,
            'weight_bonus' : 0
        }
    },
    'military' : {
        'color' : libtcodpy.dark_orange,
        'weapon': {
            'strength_dice_bonus' : 1,
            'accuracy_bonus' : 1,
        },
        'armor': {
            'evasion_bonus' : 0,
            'armor_bonus' : 0,
            'weight_bonus' : -1
        }
    },
    'fine' : {
        'color' : libtcodpy.sea,
        'weapon':{
            'strength_dice_bonus' : 2,
            'accuracy_bonus' : 2,
            'break_chance_bonus' : -1.5,
        },
        'armor': {
            'evasion_bonus' : 1,
            'armor_bonus' : 0,
            'weight_bonus' : -2
        }
    },
    'masterwork' : {
        'color' : libtcodpy.green,
        'weapon':{
            'strength_dice_bonus' : 3,
            'accuracy_bonus' : 3,
            'shred_bonus' : 1,
            'break_chance_bonus' : -10.0,
        },
        'armor':{
            'evasion_bonus' : 2,
            'armor_bonus' : 0,
            'weight_bonus' : -3
        }
    },
    'artifact' : {
        'color' : libtcodpy.purple,
        'weapon':{
            'strength_dice_bonus' : 5,
            'accuracy_bonus' : 5,
            'shred_bonus' : 1,
            'peirce_bonus' : 1,
            'break_chance_bonus' : -1000.0,
        },
        'armor':{
            'evasion_bonus' : 3,
            'armor_bonus' : 1,
            'weight' : -5
        }
    },
}

weapon_materials = {
    'wooden' : {
        'strength_dice_bonus' : -2,
        'accuracy_bonus' : 1,
        'break_chance_bonus' : 5.0
    },
    'bronze' : {
        'strength_dice_bonus' : 0,
        'accuracy_bonus' : 0,
        'break_chance_bonus' : 1.5
    },
    'iron' : {
        'strength_dice_bonus' : 0,
        'accuracy_bonus' : 0,
        'shred_bonus' : 1
    },
    'steel' : {
        'strength_dice_bonus' : 1,
        'accuracy_bonus' : 1,
        'shred_bonus' : 2,
        'break_chance_bonus' : -5.0
    },
    'crystal' : {
        'strength_dice_bonus' : 3,
        'accuracy_bonus' : -2,
        'pierce_bonus' : 1,
        'break_chance_bonus' : -1000.0
    },
    'meteor' : {
        'strength_dice_bonus' : 5,
        'accuracy_bonus' : -2,
        'shred_bonus' : 1,
        'break_chance_bonus' : -5.0
    },
    'aetherwood' : {
        'strength_dice_bonus' : 2,
        'accuracy_bonus' : 3,
        'shred_bonus' : 1,
        'break_chance_bonus' : -15.0
    },
    'blightstone' : {
        'strength_dice_bonus' : 0,
        'accuracy_bonus' : 0,
        'guaranteed_shred_bonus' : 1,
        'break_chance_bonus' : -5.0
    },
    '' : {
        'strength_dice_bonus' : 0,
        'accuracy_bonus' : 0,
        'shred_bonus' : 0
    },
}

armor_materials = {
    ''              :   {},
    'reinforced'    :   {'resistance':'slashing'},
    'hardened'      :   {'resistance':'stabbing'},
    'padded'        :   {'resistance':'bludgeoning'},
    'fire-proof'    :   {'resistance':'fire'},
    'insulated'     :   {'resistance':'lightning'},
    'fur-lined'     :   {'resistance':'cold'},
    'blessed'       :   {'resistance':'death'},
    'infernal'      :   {'resistance':'radiance'},
    'enchanted'     :   {'resistance':'spell'}
    #TODO: heavy - increased weight and +1 armor
}