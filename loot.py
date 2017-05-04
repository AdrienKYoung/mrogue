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
        'weapon_hatchet',
        'weapon_longsword',
        'weapon_mace',
        'weapon_spear',
        'weapon_pickaxe',
    ],

    'armor_0': [
        'equipment_shield',
        'equipment_leather_armor',
        'equipment_iron_helm',
        'equipment_gauntlets'
    ],

    'armor_1': [
        'equipment_shield',
        'equipment_leather_armor',
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
        'potion_healing',
        'potion_healing',
        'potion_healing',
        'potion_waterbreathing',
        'potion_shielding',
        'potion_shielding',
        'scroll_fireball',
        'scroll_confusion',
        'scroll_forge',
    ],

    'tomes_1': [
        'book_lesser_fire'
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
    'hardened'      :   {'resistance':'piercing'},
    'padded'        :   {'resistance':'bludgeoning'},
    'fire-proof'    :   {'resistance':'fire'},
    'insulated'     :   {'resistance':'lightning'},
    'fur-lined'     :   {'resistance':'cold'},
    'blessed'       :   {'resistance':'death'},
    'infernal'      :   {'resistance':'radiant'},
    'enchanted'     :   {'resistance':'spell'}
    #TODO: heavy - increased weight and +1 armor
}

proto = {

    #SCROLLS
    'scroll_fireball': {
        'name'          : 'Scroll of Fireball',
        'category'      : 'scroll',
        'char'          : '#',
        'on_use'        : actions.fireball,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'Fires a flaming projectile at a target that explodes on impact'
    },

    'scroll_confusion': {
        'name'          : 'Scroll of Confusion',
        'category'      : 'scroll',
        'char'          : '#',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.confuse,
        'type'          : 'item',
        'description'   : 'Inflicts confusion on an enemy, causing them to move about erratically.'
    },

    'scroll_forge': {
        'name' : 'Scroll of Forging',
        'category' : 'scroll',
        'char' : '#',
        'color': libtcodpy.yellow,
        'on_use' : actions.forge,
        'type' : 'item',
        'description' : 'Upgrades the quality of your held weapon.'
    },

    #POTIONS
    'potion_healing': {
        'name'          : 'Potion of Healing',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.heal,
        'type'          : 'item',
        'description'   : 'Potion that heals wounds when consumed'
    },

    'potion_waterbreathing': {
        'name'          : 'Potion of Waterbreathing',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.waterbreathing,
        'type'          : 'item',
        'description'   : "Drinking this potion causes temporary gills to form on the drinker's throat, allowing him or "
                          "her to breath water like a fish."
    },

    'potion_shielding': {
        'name'          : 'Potion of Shielding',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.shielding,
        'type'          : 'item',
        'description'   : 'This oily metallic potion bolsters the defenses of anyone who drinks it, repairing shreded'
                          ' armor and temporarily enhancing its effectiveness'
    },

    # GEMS
    'gem_lesser_fire': {
        'name'          : 'Rough Ruby',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['fire'],
        'on_use'        : actions.potion_essence('fire'), #not a bug, returns a lambda
        'description'   : 'The essence of fire burns within this gemstone. Absorbing it will bestow a single fire essence.'
    },
    'gem_lesser_earth': {
        'name'          : 'Rough Garnet',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['earth'],
        'on_use'        : actions.potion_essence('earth'), #not a bug, returns a lambda
        'description'   : 'The essence of earth resonates within this gemstone. Absorbing it will bestow a single earth essence.'
    },
    'gem_lesser_life': {
        'name'          : 'Rough Emerald',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['life'],
        'on_use'        : actions.potion_essence('life'), #not a bug, returns a lambda
        'description'   : 'The essence of life emanates from this gemstone. Absorbing it will bestow a single life essence.'
    },
    'gem_lesser_air': {
        'name'          : 'Rough Quartz',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['air'],
        'on_use'        : actions.potion_essence('air'), #not a bug, returns a lambda
        'description'   : 'The essence of air swirls in this crystal. Absorbing it will bestow a single air essence.'
    },
    'gem_lesser_water': {
        'name'          : 'Rough Aquamarine',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['water'],
        'on_use'        : actions.potion_essence('water'), #not a bug, returns a lambda
        'description'   : 'The essence of water flows through this gemstone. Absorbing it will bestow a single water essence.'
    },
    'gem_lesser_cold': {
        'name'          : 'Rough Zircon',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['cold'],
        'on_use'        : actions.potion_essence('cold'), #not a bug, returns a lambda
        'description'   : 'The essence of cold chills the surface of this gemstone. Absorbing it will bestow a single cold essence.'
    },
    'gem_lesser_arcane': {
        'name'          : 'Rough Amethyst',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['arcane'],
        'on_use'        : actions.potion_essence('arcane'), #not a bug, returns a lambda
        'description'   : 'The essence of arcana hums within this gemstone. Absorbing it will bestow a single arcane essence.'
    },
    'gem_lesser_radiance': {
        'name'          : 'Rough Diamond',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['radiant'],
        'on_use'        : actions.potion_essence('radiant'), #not a bug, returns a lambda
        'description'   : 'The essence of radiance shines through this gemstone. Absorbing it will bestow a single radiant essence.'
    },
    'gem_lesser_death': {
        'name'          : 'Rough Onyx',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['death'],
        'on_use'        : actions.potion_essence('death'), #not a bug, returns a lambda
        'description'   : 'The essence of dark envelops this gemstone. Absorbing it will bestow a single dark essence.'
    },

    #WEAPONS
    'weapon_longsword': {
        'name'               : 'longsword',
        'category'           : 'weapon',
        'subtype'            : 'sword',
        'damage_type'        : 'slashing',
        'char'               : '/',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A hand-and-a-half cruciform sword',
        'stamina_cost'       : 10,
        'str_requirement'    : 12,
        'shred'              : 1,
        'accuracy'           : 1,
        'weapon_dice'        : '2d6',
        'str_dice'           : 2,
        'attack_delay'       : 14,
        'crit_bonus'         : 1.5
    },
    'weapon_greatsword': { #called a spadone or montante in historical circles, but no one will recognize that
        'name'               : 'greatsword',
        'category'           : 'weapon',
        'subtype'            : 'sword',
        'damage_type'        : 'slashing',
        'char'               : '/',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A huge greatsword, made for fighting many foes at once.',
        'stamina_cost'       : 12,
        'str_requirement'    : 16,
        'shred'              : 2,
        'accuracy'           : 1,
        'weapon_dice'        : '3d6',
        'str_dice'           : 3,
        'attack_delay'       : 14,
        'crit_bonus'         : 1.5
    },
    'weapon_dagger': {
        'name'               : 'dagger',
        'category'           : 'weapon',
        'subtype'            : 'dagger',
        'damage_type'        : 'stabbing',
        'char'               : '-',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A small double-edged knife. Deals triple damage to incapacitated targets',
        'stamina_cost'       : 6,
        'str_requirement'    : 6,
        'shred'              : 0,
        'accuracy'           : 5,
        'weapon_dice'        : '2d4',
        'str_dice'           : 1,
        'attack_delay'       : 12,
        'crit_bonus'         : 3.0
    },
    'weapon_messer': { #lit. german: 'knife'. no english period term
        'name'               : 'messer',
        'category'           : 'weapon',
        'damage_type'        : 'slashing',
        'subtype'            : 'dagger',
        'char'               : '-',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A long knife, made for dueling',
        'stamina_cost'       : 8,
        'str_requirement'    : 8,
        'shred'              : 0,
        'accuracy'           : 5,
        'weapon_dice'        : '2d4',
        'str_dice'           : 2,
        'attack_delay'       : 12,
        'crit_bonus'         : 2
    },
    'weapon_katar': {
        'name'               : 'katar',
        'category'           : 'weapon',
        'damage_type'        : 'stabbing',
        'subtype'            : 'dagger',
        'char'               : chr(19),
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A pair of exotic hooded punching daggers.',
        'stamina_cost'       : 6,
        'str_requirement'    : 10,
        'shred'              : 1,
        'accuracy'           : 5,
        'weapon_dice'        : '2d8',
        'str_dice'           : 2,
        'attack_delay'       : 10,
        'crit_bonus'         : 3.5
    },
    'weapon_spear': {
        'name'               : 'spear',
        'category'           : 'weapon',
        'subtype'            : 'polearm',
        'damage_type'        : 'stabbing',
        'char'               : libtcodpy.CHAR_ARROW_N,
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A light thrusting spear',
        'stamina_cost'       : 10,
        'str_requirement'    : 12,
        'ability'            : 'ability_thrust',
        'pierce'             : 1,
        'shred'              : 0,
        'accuracy'           : 1,
        'ctrl_attack'        : player.reach_attack,
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction.',
        'weapon_dice'        : '2d10',
        'str_dice'           : 1,
        'attack_delay'       : 14,
        'crit_bonus'         : 1.5
    },
    'weapon_halberd': {
        'name'               : 'halberd',
        'category'           : 'weapon',
        'subtype'            : 'polearm',
        'damage_type'        : 'slashing',
        'char'               : libtcodpy.CHAR_ARROW_N,
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A superior two-handed polearm with a spike, axe and hook on its head.',
        'stamina_cost'       : 12,
        'str_requirement'    : 16,
        'pierce'             : 1,
        'shred'              : 0,
        'accuracy'           : 2,
        'ctrl_attack'        : player.reach_attack, #could use a special reach attack that cleaves
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction.',
        'weapon_dice'        : '3d6',
        'str_dice'           : 3,
        'attack_delay'       : 14,
        'crit_bonus'         : 1.5
    },
    'weapon_pickaxe': {
        'name'               : 'pickaxe',
        'category'           : 'weapon',
        'subtype'            : 'axe',
        'damage_type'        : 'stabbing',
        'char'               : 'T',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A heavy digging implement used by miners. Can be used to dig through the walls '
                               'of the dungeon',
        'stamina_cost'       : 18,
        'str_requirement'    : 14,
        'pierce'             : 1,
        'shred'              : 1,
        'accuracy'           : -3,
        'ctrl_attack'        : actions.dig,
        'ctrl_attack_desc'   : 'Dig - dig through walls in this direction.',
        'break'              : 5.0,
        'weapon_dice'        : '1d4',
        'str_dice'           : 3,
        'attack_delay'       : 28,
        'crit_bonus'         : 1.5
    },
    'weapon_hatchet': {
        'name'               : 'hatchet',
        'category'           : 'weapon',
        'subtype'            : 'axe',
        'damage_type'        : 'slashing',
        'char'               : 'p',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A one-handed axe made for cutting wood.',
        'stamina_cost'       : 9,
        'str_requirement'    : 10,
        'shred'              : 1,
        'accuracy'           : 3,
        'ctrl_attack'        : player.cleave_attack,
        'ctrl_attack_desc'   : 'Cleave - attack all adjacent enemies. Costs 2x stamina.',
        'weapon_dice'        : '1d6',
        'str_dice'           : 2,
        'attack_delay'       : 16,
        'crit_bonus'         : 1.5
    },
    'weapon_dane_axe': {
        'name'               : 'dane axe',
        'category'           : 'weapon',
        'subtype'            : 'axe',
        'damage_type'        : 'slashing',
        'char'               : 'P',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'both hands',
        'description'        : 'A massive, two handed axe made for smashing shields and armor.',
        'stamina_cost'       : 12,
        'str_requirement'    : 18,
        'shred'              : 3,
        'accuracy'           : 3,
        'ctrl_attack'        : player.cleave_attack,
        'ctrl_attack_desc'   : 'Cleave - attack all adjacent enemies. Costs 2x stamina.',
        'weapon_dice'        : '2d10',
        'str_dice'           : 3,
        'attack_delay'       : 16,
        'crit_bonus'         : 1.5
    },
    'weapon_mace': {
        'name'               : 'mace',
        'category'           : 'weapon',
        'subtype'            : 'mace',
        'damage_type'        : 'bludgeoning',
        'char'               : chr(157),
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A one-handed flanged mace. Good against armored enemies',
        'stamina_cost'       : 10,
        'str_requirement'    : 13,
        'shred'              : 2,
        'accuracy'           : 2,
        'weapon_dice'        : '1d6',
        'str_dice'           : 2,
        'on_hit'             : [actions.mace_stun],
        'attack_delay'       : 18,
        'crit_bonus'         : 1.5
    },
    'weapon_warhammer': {
        'name'               : 'warhammer',
        'category'           : 'weapon',
        'subtype'            : 'mace',
        'damage_type'        : 'bludgeoning',
        'char'               : chr(157),
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'both hands',
        'description'        : 'A heavy hammer head mounted to a haft. Made for slaying armored foes outright.',
        'stamina_cost'       : 15,
        'str_requirement'    : 20,
        'shred'              : 2,
        'pierce'             : 3,
        'accuracy'           : 1,
        'weapon_dice'        : '1d8',
        'str_dice'           : 4,
        'on_hit'             : [actions.mace_stun],
        'attack_delay'       : 20,
        'crit_bonus'         : 1.5
    },
    'weapon_coal_mace': {
        'name'               : 'coal-brazer mace',
        'category'           : 'weapon',
        'damage_type'        : 'fire',
        'subtype'            : 'mace',
        'char'               : chr(157),
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A one-handed mace, fitted with a grate for burning coals.',
        'stamina_cost'       : 10,
        'str_requirement'    : 13,
        'shred'              : 2,
        'accuracy'           : 2,
        'weapon_dice'        : '1d6',
        'str_dice'           : 2,
        'on_hit'             : [actions.mace_stun],
        'attack_delay'       : 22,
        'crit_bonus'         : 1.5
    },

    'weapon_battleaxe_of_pure_fire': {
        'name'               : 'battleaxe of pure fire',
        'category'           : 'weapon',
        'damage_type'        : 'fire',
        'subtype'            : 'axe',
        'char'               : 'P',
        'color'              : libtcodpy.flame,
        'type'               : 'item',
        'slot'               : 'both hands',
        'description'        : 'A battleaxe of pure flame, cleaving and burning all in its path.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'shred'              : 3,
        'accuracy'           : 3,
        'ctrl_attack'        : player.cleave_attack,
        'ctrl_attack_desc'   : 'Cleave - attack all adjacent enemies. Costs 2x stamina.',
        'weapon_dice'        : '2d12',
        'str_dice'           : 3,
        'on_hit'             : [combat.on_hit_burn],
        'attack_delay'       : 16,
        'crit_bonus'         : 1.5
    },
    'weapon_diamond_warhammer': {
        'name'               : 'diamond warhammer',
        'category'           : 'weapon',
        'subtype'            : 'mace',
        'damage_type'        : 'bludgeoning',
        'char'               : chr(157),
        'color'              : libtcodpy.sepia,
        'type'               : 'item',
        'slot'               : 'both hands',
        'description'        : 'A diamond warhammer, crushing its foes when wielded with strength.',
        'stamina_cost'       : 15,
        'str_requirement'    : 1,
        'shred'              : 2,
        'pierce'             : 3,
        'accuracy'           : 1,
        'weapon_dice'        : '1d8',
        'str_dice'           : 5,
        'on_hit'             : [actions.mace_stun],
        'attack_delay'       : 22,
        'crit_bonus'         : 1.5
    },
    'weapon_storm_mace': {
        'name'               : 'storm mace',
        'category'           : 'weapon',
        'damage_type'        : 'lightning',
        'subtype'            : 'mace',
        'char'               : chr(157),
        'color'              : libtcodpy.light_sky,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A storm mace, booming with thunder as chain-lightning arcs through its victims.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'shred'              : 2,
        'accuracy'           : 2,
        'weapon_dice'        : '3d6',
        'str_dice'           : 2,
        'on_hit'             : [combat.on_hit_chain_lightning],
        'attack_delay'       : 22,
        'crit_bonus'         : 1.5
    },
    'weapon_trident_of_raging_water': {
        'name'               : 'trident of raging water',
        'category'           : 'weapon',
        'subtype'            : 'polearm',
        'damage_type'        : 'stabbing',
        'char'               : libtcodpy.CHAR_ARROW_N,
        'color'              : libtcodpy.azure,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A trident of raging water, threatening foes from a distance and hindering their movements.',
        'stamina_cost'       : 12,
        'str_requirement'    : 1,
        'pierce'             : 2,
        'shred'              : 1,
        'accuracy'           : 2,
        'ctrl_attack'        : player.reach_attack, #could use a special reach attack that cleaves
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction.',
        'weapon_dice'        : '3d6',
        'str_dice'           : 3,
        'on_hit'             : [combat.on_hit_slow, combat.on_hit_sluggish],
        'attack_delay'       : 14,
        'crit_bonus'         : 1.5
    },
    'weapon_lifedrinker_dagger': { #lit. german: 'knife'. no english period term
        'name'               : 'lifedrinker dagger',
        'category'           : 'weapon',
        'damage_type'        : 'stabbing',
        'subtype'            : 'dagger',
        'char'               : '-',
        'color'              : libtcodpy.green,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : "A lifedrinker dagger, sustaining the life of it's wielder with the suffering of others",
        'stamina_cost'       : 8,
        'str_requirement'    : 1,
        'shred'              : 0,
        'accuracy'           : 5,
        'weapon_dice'        : '2d4',
        'str_dice'           : 1,
        'on_hit'             : [combat.on_hit_lifesteal],
        'attack_delay'       : 12,
        'crit_bonus'         : 3
    },
    'weapon_frozen_blade': {
        'name'               : 'frozen blade',
        'category'           : 'weapon',
        'subtype'            : 'sword',
        'damage_type'        : 'cold',
        'char'               : '/',
        'color'              : libtcodpy.lightest_azure,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A frozen blade, inflicting merciless wounds on individual targets.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'shred'              : 2,
        'accuracy'           : 4,
        'weapon_dice'        : '2d10',
        'str_dice'           : 2,
        'on_hit'             : [combat.on_hit_freeze],
        'attack_delay'       : 10,
        'crit_bonus'         : 2.5
    },
    'weapon_staff_of_force': {
        'name'               : 'staff of force',
        'category'           : 'weapon',
        'subtype'            : 'staff',
        'damage_type'        : 'bludgeoning',
        'char'               : '|',
        'color'              : libtcodpy.fuchsia,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A staff of force, humming with arcane energy that sends its targets flying.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'shred'              : 1,
        'accuracy'           : 3,
        'weapon_dice'        : '1d10',
        'str_dice'           : 1,
        'on_hit'             : [combat.on_hit_knockback],
        'attack_delay'       : 10,
        'crit_bonus'         : 1.5
    },
    'weapon_soul_reaper': {
        'name'               : 'soul reaper',
        'category'           : 'weapon',
        'subtype'            : 'polearm',
        'damage_type'        : 'slashing',
        'char'               : ')',
        'color'              : libtcodpy.dark_violet,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A soul reaper, a grim scythe that raises those it kills as zombies.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'pierce'             : 1,
        'shred'              : 2,
        'accuracy'           : 2,
        'ctrl_attack'        : player.reach_attack, #could use a special reach attack that cleaves
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction.',
        'weapon_dice'        : '3d10',
        'str_dice'           : 2,
        'on_hit'             : [combat.on_hit_reanimate],
        'attack_delay'       : 18,
        'crit_bonus'         : 1.5
    },

    #ARMOR
    'equipment_shield': {
        'name'          : 'Shield',
        'category'      : 'armor',
        'char'          : chr(233), #theta
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'slot'          : 'left hand',
        'description'   : 'An iron kite shield.',
        'ability'       : 'block', #not implemented
        'evasion_bonus' : -2,
        'weight'        : 3
    },

    'equipment_cloth_robes': {
        'name'          : 'Cloth Robes',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'slot'          : 'body',
        'description'   : 'Heavy cloth robes. Provide some degree of protection against attacks.',
        'evasion_bonus' : 0,
        'weight'        : 2
    },

    'equipment_leather_armor': {
        'name'          : 'Leather Armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'slot'          : 'body',
        'description'   : 'A hardened leather vest.',
        'evasion_bonus' : -1,
        'weight'        : 5
    },

    'equipment_mail_armor': {
        'name'          : 'Mail Armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 3,
        'evasion_bonus' : -3,
        'slot'          : 'body',
        'description'   : 'A coat of mail made of interlocking iron rings',
        'weight'        : 10
    },

    'equipment_brigandine': {
        'name'          : 'Brigandine',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 5,
        'evasion_bonus' : -5,
        'slot'          : 'body',
        'description'   : 'A vest of articulated steel plates',
        'weight'        : 20
    },

    'equipment_plate_armor': {
        'name'          : 'Plate armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 7,
        'evasion_bonus' : -7,
        'slot'          : 'body',
        'description'   : 'A hardened steel breastplate',
        'weight'        : 30
    },

    'equipment_boob_plate': {
        'name'          : 'Boob Plate',
        'category'      : 'armor',
        'char'          : chr(235), #infinity
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 6,
        'evasion_bonus' : -4,
        'slot'          : 'body',
        'description'   : 'A steel bra that deflects harm from the entire torso by an unknown mechanism',
        'weight'        : 10
    },

    'equipment_iron_helm': {
        'name'          : 'Iron Helm',
        'category'      : 'armor',
        'char'          : chr(167),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'evasion_bonus' : -1,
        'slot'          : 'head',
        'description'   : 'A conical iron helm with a nose guard',
        'weight'        : 3
    },

    'equipment_great_helm': {
        'name'          : 'Great Helm',
        'category'      : 'armor',
        'char'          : chr(167),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -3,
        'slot'          : 'head',
        'description'   : 'A large cylindrical steel helm. Very heavy and cumbersome',
        'weight'        : 7
    },

    'equipment_armet_helm': {
        'name'          : 'Armet Helm',
        'category'      : 'armor',
        'char'          : chr(167),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -1,
        'slot'          : 'head',
        'description'   : 'A crested steel helm with visor and bevor.',
        'weight'        : 6
    },

    'equipment_witch_hat': {
        'name'          : 'Witch Hat',
        'category'      : 'armor',
        'char'          : '^',
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 0,
        'evasion_bonus' : 0,
        'slot'          : 'head',
        'description'   : 'A black pointed hat, suitable for the fashionable culdron stirrer.',
        'resistances'   : ['fire','burning'],
        'weight'        : 1
    },

    'equipment_gauntlets' : {
        'name'          : 'Gauntlets',
        'category'      : 'armor',
        'char'          : chr(34),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'evasion_bonus' : 0,
        'slot'          : 'hands',
        'description'   : 'An armored pair of gloves',
        'weight'        : 3
    },

    'equipment_greaves' : {
        'name'          : 'Greaves',
        'category'      : 'armor',
        'char'          : chr(239),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'evasion_bonus' : -1,
        'slot'          : 'feet',
        'description'   : 'Steel plates that protect the shins',
        'weight'        : 3
    },

    #Charms
    'charm_resistance' : {
        'name'          : 'Charm of Resistance',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : charms.charm_resist,
        'description'   : 'When infused with essence, this charm grants resistance to that type of essence.'
    },
    'charm_raw' : {
        'name'          : 'Essence Crystal',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : charms.charm_raw,
        'description'   : 'This charm will turn any type of essence into a basic spell.'
    },
    'charm_shard_of_creation' : {
        'name'          : 'Shard of Creation',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : charms.shard_of_creation,
        'description'   : 'A tiny mote of magical creation. Can be used to temporarily modify terrain.'
    },
    'charm_holy_symbol' : {
        'name'          : 'Holy Symbol',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : charms.holy_symbol,
        'description'   : 'A sacred symbol. While the knowledge of the devotion is lost, its magic is still potent.'
    },
    'charm_farmers_talisman' : {
        'name'          : "Farmer's Talisman",
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : charms.farmers_talisman,
        'description'   : 'A simple good luck charm given by wife to husband.'
    },
    'charm_primal_totem' : {
        'name'          : 'Primal Totem',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : charms.primal_totem,
        'description'   : 'A charm made from charred bone. It is said these battle charms were soaked in sacrificial blood.'
    },

    #Books

    'book_lesser_fire' : {
        'name'          : 'Lesser Book of Fire',
        'category'      : 'book',
        'char'          : '#',
        'color'         : libtcodpy.flame,
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A basic book of fire magic',
        'essence':'fire',
        'level' : 1,
        'spells': [
            'spell_heat_ray',
            'spell_flame_wall',
            'spell_fireball',
            'spell_shatter_item',
            'spell_magma_bolt'
        ],
        'levels': [
            'spell_heat_ray', 'spell_flame_wall', 'spell_heat_ray', 'spell_fireball', 'spell_shatter_item',
            'spell_fireball', 'spell_magma_bolt', 'spell_heat_ray','spell_flame_wall', 'spell_fireball',
            'spell_magma_bolt', 'spell_shatter_item', 'spell_magma_bolt'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },

    'book_lesser_cold' : {
        'name'          : 'Book of Blizzards',
        'category'      : 'book',
        'char'          : '#',
        'color'         : libtcodpy.lightest_azure,
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A basic book of ice magic',
        'essence': 'cold',
        'level' : 1,
        'spells': [
            'spell_frozen_orb',
            'spell_flash_frost',
            'spell_ice_shards',
            'spell_snowstorm',
            'spell_avalanche'
        ],
        'levels': [
            'spell_frozen_orb', 'spell_flash_frost', 'spell_frozen_orb', 'spell_ice_shards', 'spell_snowstorm',
            'spell_ice_shards', 'spell_avalanche', 'spell_frozen_orb','spell_flash_frost', 'spell_ice_shards',
            'spell_avalanche', 'spell_snowstorm', 'spell_avalanche'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },

    'book_lesser_death' : {
        'name'          : 'The Dead Walk',
        'category'      : 'book',
        'char'          : '#',
        'color'         : libtcodpy.dark_violet,
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A basic book of death magic',
        'essence': 'death',
        'level' : 1,
        'spells': [
            'spell_hex',
            'spell_defile',
            'spell_shackles_of_the_dead',
            'spell_sacrifice',
            'spell_corpse_dance'
        ],
        'levels': [
            'spell_hex', 'spell_defile', 'spell_hex', 'spell_shackles_of_the_dead', 'spell_defile', 'spell_sacrifice',
            'spell_corpse_dance', 'spell_hex','spell_defile', 'spell_shackles_of_the_dead',
            'spell_corpse_dance', 'spell_sacrifice', 'spell_corpse_dance'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },

    #Misc

    'glass_key' : {
        'name'          : 'Glass Key',
        'category'      : 'key',
        'char'          : 13,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'A delicate key made from clouded glass. This key can open any lock,'
                          ' but breaks in the process.'
    },

    'treasure_bejeweled_chalice': {
        'name'          : 'bejeweled chalice',
        'category'      : 'treasure',
        'char'          : '$',
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'A golden chalice, encrusted with precious jewels. Mundane, but valuable.'
    }
}