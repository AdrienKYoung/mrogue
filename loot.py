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
import log

table = {
    'weapons_0': {
        'weapon_dagger' : 20,
        'weapon_shortsword' : 20,
        'weapon_shortspear' : 20,
        'weapon_hatchet' : 20,
        'weapon_club' : 19,
        'weapons_1' : 1,
    },

    'weapons_1': {
        'weapon_longsword' : 20,
        'weapon_rapier' : 20,
        'weapon_war_axe' : 20,
        'weapon_mace' : 19,
        'weapon_spear' : 19,
        'weapon_boomerang' : 1,
        'weapons_2' : 1,
    },

    'weapons_2' : {
        'weapon_messer' : 15,
        'weapon_greatsword' : 15,
        'weapon_warhammer' : 15,
        'weapon_raider_axe' : 15,
        'weapon_halberd' : 15,
        'weapon_katar' : 15,
        'weapon_boomerang' : 9,
        'weapons_3' : 1
    },

    'weapons_3' : {
        'weapon_assassins_blade' : 20,
        'weapon_scythe' : 20,
        'weapon_scimitar' : 20,
        'weapon_giant_axe' : 20,
        'weapon_blessed_blade' : 5,
        'weapon_black_blade': 5
    },

    'loot_weapons_steel': {
        'weapon_dagger': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_hatchet': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_longsword': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_mace': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_spear': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_messer': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_greatsword': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_warhammer': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_dane_axe': {'weight': 10, 'material': 'steel', 'quality': ''},
        'weapon_halberd': {'weight': 5, 'material': 'steel', 'quality': ''},
        'weapon_katar': {'weight': 5, 'material': 'steel', 'quality': ''},
    },

    'armor_0': {
        'equipment_leather_armor' : 24,
        'equipment_cloth_robes' : 20,
        'equipment_iron_helm' : 20,
        'shield_leather_buckler' : 15,
        'shield_wooden_buckler' : 10,
        'shield_iron_buckler' : 10,
        'armor_1' : 1,
    },

    'armor_1': {
        'equipment_greaves' : 25,
        'equipment_gauntlets' : 25,
        'equipment_mail_armor' : 25,
        'shield_heater_shield' : 12,
        'shield_round_shield' : 12,
        'armor_2' : 1,
    },

    'armor_2' : {
        'equipment_brigandine' : 20,
        'equipment_great_helm' : 20,
        'equipment_boots_of_agility' : 10,
        'equipment_gloves_of_strength' : 10,
        'equipment_crest_of_intelligence' : 10,
        'shield_escutcheon' : 10,
        'shield_kite_shield' : 9,
        'equipment_boots_of_leaping' : 5,
        'equipment_cloak_of_stealth' : 5,
        'armor_3' : 1,
    },

    'armor_3' : {
        'equipment_plate_armor' : 25,
        'equipment_armet_helm' : 20,
        'shield_duelists_buckler' : 20,
        'shield_tower_shield' : 20,
        'equipment_boots_of_levitation' : 5,
        'equipment_longstrider_boots' : 5,
        'equipment_greater_cloak_of_stealth' : 5,
    },

    'consumables_1': {
        'essence_life' : 24,
        'essence_water' : 20,
        'essence_earth' : 15,
        'essence_fire' : 10,
        'essence_air' : 10,
        'essence_cold' : 10,
        'essence_arcane' : 10,
        'consumables_2' : 1,
     },

    'consumables_2': {
        'essence_death' : 40,
        'essence_radiance' : 40,
        'essence_void' : 20,
    },

    'gems_1': {
        'gem_lesser_life' : 24,
        'gem_lesser_water' : 20,
        'gem_lesser_earth' : 15,
        'gem_lesser_fire' : 10,
        'gem_lesser_air' : 10,
        'gem_lesser_cold' : 10,
        'gem_lesser_arcane' : 10,
        'gens_2' : 1,
    },

    'gems_2': {
        'gem_lesser_death' : 40,
        'gem_lesser_radiance' : 40,
        'gem_lesser_void' : 20,
    },

    'tomes_1': {
        'book_lesser_arcane' : 10,
        'book_lesser_fire' : 10,
        'book_lesser_death' : 10,
        'book_lesser_cold' : 10,
        'book_lesser_life' : 10,
        'book_lesser_radiance' : 10,
    },

    'keys_1': {
        'glass_key' : 10
    },

    'charms_1': {
        'charm_farmers_talisman' : 15,
        'charm_primal_totem' : 15,
        'charm_holy_symbol' : 15,
        'charm_shard_of_creation' : 15,
        'charm_volatile_orb' : 15,
        'charm_prayer_beads' : 14,
        'charm_alchemists_flask' : 10,
        'charms_2': 1,
    },

    'charms_2': {
        'charm_elementalists_lens' : 100,
    },

    'rings_1': {
        'equipment_ring_of_stamina' : 8,
        'equipment_ring_of_evasion' : 7,
        'equipment_ring_of_accuracy' : 7,
        'equipment_ring_of_vengeance' : 7,
        'equipment_ring_of_rage' : 7,
        'equipment_ring_of_fortitude' : 7,
        'equipment_ring_of_tenacity' : 7,
        'equipment_ring_of_mending' : 7,
        'equipment_ring_of_breath' : 7,
        'equipment_ring_of_burdens' : 7,
        'equipment_ring_of_alchemy' : 7,
        'equipment_ring_of_poison_immunity' : 7,
        'equipment_ring_of_freedom' : 7,
        'equipment_ring_of_blessings' : 7,
        'rings_2' : 1
    },

    'rings_2': {
        'equipment_ring_of_vampirism' : 50,
        'equipment_ring_of_salvation' : 50,
    },

    'elixirs_0': {
        'elixir_con' : 20,
        'elixir_str' : 20,
        'elixir_agi' : 20,
        'elixir_int' : 20,
        'elixir_wis' : 20,
    },

    'chest_0': {
        'elixirs_0' : 10,
        'elixir_life' : 10,
        'rings_1' : 10,
        'charms_1' : 10,
        'keys_1' : 10,
        'tomes_1' : 10,
        'armor_2' : 10,
        'weapons_2' : 10,
        'scroll_forge' : 10,
        'treasure_0' : 10
    },

    'treasure_0': {
        'treasure_bejeweled_chalice' : 10,
        'treasure_burial_mask' : 10,
        'treasure_chest_of_coins' : 10,
        'treasure_giant_pearl' : 10,
        'treasure_jade_necklace' : 10,
        'treasure_silver_tiara' : 10,
        'treasure_music_box' : 10,
    },

}

def item_from_table(branch,loot_table=None):
    if loot_table is None:
        loot_table = choose_loot_table(branch)

    if loot_table is None:
        return None

    # fall back to lower level table if higher level isn't available (TODO: Removeme)
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
    item_id = main.random_choice(table[loot_table])

    if item_id in table.keys():
        return item_from_table(branch, loot_table=item_id)

    material = None
    quality = ''
    if category == 'weapon':
        material = choose_weapon_material(loot_level)
        quality = choose_quality(loot_level)
    if category == 'armor':
        quality = choose_quality(loot_level)
        material = choose_armor_material(loot_level)

    return main.create_item(item_id, material, quality)

def item_from_table_ex(loot_table, loot_level=1):
    if loot_table is None or loot_table not in table:
        log.warn("loot", "Couldn't find loot table {}", loot_table)
        return None

    loot_table = table[loot_table]
    chances = { k:v.get('weight',10) for k,v in loot_table.items() }
    item_id = main.random_choice(chances)
    choice = loot_table[item_id]

    import items
    prototype = items.table()[item_id]
    material = choice.get('material', None)
    quality = choice.get('quality', None)
    if prototype['category'] == 'weapon':
        if material is None:
            material = choice.get('material', choose_weapon_material(loot_level))
        if quality is None:
            quality = choice.get('quality', choose_quality(loot_level))
    if prototype['category'] == 'armor':
        if material is None:
            material = choice.get('material', choose_armor_material(loot_level))
        if quality is None:
            quality = choice.get('quality', choose_quality(loot_level))
    if quality is None:
        quality = ''

    return main.create_item(item_id, material, quality)


def choose_loot_table(branch):
    import dungeon
    b = dungeon.branches[branch]
    if b.get('loot') is None:
        return None
    else:
        return main.random_choice(b['loot'])

def choose_weapon_material(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 25 * loot_level, 150))
    if roll < 5:
        return choose_weapon_material(loot_level + 1)
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
    roll = libtcodpy.random_get_int(0, 0, min(100 + 30 * loot_level, 150))
    if roll > 100:
        ops = armor_materials.keys()
        return ops[libtcodpy.random_get_int(0,0,len(ops)-1)]
    else:
        return ''


def choose_quality(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 20 * loot_level, 130))
    if roll < 5:
        return choose_quality(loot_level + 1)
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

elixir_life_ticker = 0
elixir_stat_ticker = 0
scroll_forge_ticker = 0

def check_special_drop():
    global elixir_life_ticker, elixir_stat_ticker, scroll_forge_ticker
    elixir_stat_ticker += 1
    scroll_forge_ticker += 1
    elixir_life_ticker += 1
    if main.roll_dice('1d850') <= elixir_life_ticker:
        elixir_life_ticker = 0
        return 'elixir_life'
    elif main.roll_dice('1d300') <= elixir_stat_ticker:
        elixir_stat_ticker = 0
        return main.random_choice(table['elixirs_0'])
    elif main.roll_dice('1d200') <= scroll_forge_ticker:
        scroll_forge_ticker = 0
        return 'scroll_forge'
    else:
        return None

item_categories = {
    'weapon' : { 'plural' : 'weapons' },
    'armor' : { 'plural' : 'armor' },
    'scroll' : { 'plural' : 'scrolls' },
    'potion' : { 'plural' : 'potions' },
    'book' : { 'plural' : 'books' },
    'charm' : { 'plural' : 'charms'},
    'gem' : { 'plural' : 'gems'},
    'key' : { 'plural' : 'keys'},
    'treasure' : { 'plural' : 'treasure' },
    'accessory' : {'plural': 'accessories'},
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
            'weight_bonus' : 0,
            'sh_max_bonus' : 0,
            'sh_recovery_bonus' : 5,
            'sh_raise_cost_bonus' : 10,
        }
    },
    'crude' : {
        'color' : libtcodpy.dark_sepia,
        'weapon': {
            'strength_dice_bonus' : -2,
            'accuracy_bonus' : -1,
        },
        'armor': {
            'evasion_bonus' : -1,
            'armor_bonus' : 0,
            'weight_bonus' : 1,
            'sh_max_bonus' : 0,
            'sh_recovery_bonus' : 2,
            'sh_raise_cost_bonus' : 5,
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
            'weight_bonus' : 0,
            'sh_max_bonus' : 0,
            'sh_recovery_bonus' : 0,
            'sh_raise_cost_bonus' : 0,
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
            'weight_bonus' : -1,
            'sh_max_bonus' : 1,
            'sh_recovery_bonus' : 0,
            'sh_raise_cost_bonus' : -1,
        }
    },
    'fine' : {
        'color' : libtcodpy.sea,
        'weapon':{
            'strength_dice_bonus' : 2,
            'accuracy_bonus' : 2,
        },
        'armor': {
            'evasion_bonus' : 1,
            'armor_bonus' : 0,
            'weight_bonus' : -2,
            'sh_max_bonus' : 3,
            'sh_recovery_bonus' : -1,
            'sh_raise_cost_bonus' : -2,
        }
    },
    'masterwork' : {
        'color' : libtcodpy.green,
        'weapon':{
            'strength_dice_bonus' : 3,
            'accuracy_bonus' : 3,
            'shred_bonus' : 1,
        },
        'armor':{
            'evasion_bonus' : 1,
            'armor_bonus' : 0,
            'weight_bonus' : -3,
            'sh_max_bonus' : 6,
            'sh_recovery_bonus' : -2,
            'sh_raise_cost_bonus' : -3,
        }
    },
    'artifact' : {
        'color' : libtcodpy.purple,
        'weapon':{
            'strength_dice_bonus' : 5,
            'accuracy_bonus' : 5,
            'shred_bonus' : 1,
            'peirce_bonus' : 1,
        },
        'armor':{
            'evasion_bonus' : 2,
            'armor_bonus' : 1,
            'weight_bonus' : -5,
            'sh_max_bonus' : 10,
            'sh_recovery_bonus' : -3,
            'sh_raise_cost_bonus' : -5,
        }
    },
}

weapon_materials = {
    'wooden' : {
        'strength_dice_bonus' : -2,
        'accuracy_bonus' : 1,
    },
    'bronze' : {
        'strength_dice_bonus' : 0,
        'accuracy_bonus' : 0,
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
    },
    'crystal' : {
        'strength_dice_bonus' : 3,
        'accuracy_bonus' : -2,
        'pierce_bonus' : 1,
    },
    'meteor' : {
        'strength_dice_bonus' : 5,
        'accuracy_bonus' : -2,
        'shred_bonus' : 1,
    },
    'aetherwood' : {
        'strength_dice_bonus' : 2,
        'accuracy_bonus' : 3,
        'shred_bonus' : 1,
    },
    'blightstone' : {
        'strength_dice_bonus' : 0,
        'accuracy_bonus' : 0,
        'guaranteed_shred_bonus' : 1,
    },
    '' : {
        'strength_dice_bonus' : 0,
        'accuracy_bonus' : 0,
        'shred_bonus' : 0
    },
}

armor_materials = {
    ''              :   {},
    'heavy'         :   {'armor_bonus': 1, 'weight_bonus' : 3},
    'fire-proof'    :   {'resistance': ('fire', 1)},
    'insulated'     :   {'resistance': ('lightning', 1)},
    'fur-lined'     :   {'resistance': ('cold', 1)},
    'blessed'       :   {'resistance': ('death', 1)},
    'infernal'      :   {'resistance': ('radiance', 1)},
    'enchanted'     :   {'will_bonus': 1}
}