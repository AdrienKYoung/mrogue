import libtcodpy
import spells
import game as main
import abilities

def item_from_table(loot_level=0, category=None):
    if category is None:
        category = choose_category()

    item_id = ''
    material = None
    quality = None
    if category == 'consumable':
        item_id = choose_consumable(loot_level)
    elif category == 'weapon':
        item_id = choose_weapon(loot_level)
        material = choose_material(loot_level)
        quality = choose_quality(loot_level)
    elif category == 'armor':
        item_id = choose_armor(loot_level)
    elif category == 'book':
        item_id = choose_book(loot_level)

    return main.create_item(item_id, material, quality)

def choose_category():
    return main.random_choice({'consumable' : 45, 'weapon' : 25, 'armor' : 20, 'book': 10})


def choose_weapon(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(50 + loot_level, 70))
    if roll < 5:
        return choose_weapon(loot_level + 5)
    elif roll < 20:
        return 'equipment_dagger'
    elif roll < 30:
        return 'equipment_spear'
    elif roll < 40:
        return 'equipment_hatchet'
    elif roll < 50:
        return 'equipment_longsword'
    else:
        return 'equipment_pickaxe'


def choose_armor(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(50 + loot_level, 70))
    if roll < 5:
        return choose_armor(loot_level + 5)
    elif roll < 35:
        return 'equipment_leather_armor'
    else:
        return 'equipment_shield'


def choose_book(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(50 + loot_level, 70))
    if roll < 5:
        return choose_book(loot_level + 5)
    elif roll < 25:
        return 'tome_manabolt'
    elif roll < 40:
        return 'tome_mend'
    else:
        return 'tome_ignite'


def choose_consumable(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(50 + loot_level, 65))
    if roll < 5:
        return choose_consumable(loot_level + 5)
    elif roll < 20:
        return 'potion_healing'
    elif roll < 30:
        return 'potion_waterbreathing'
    elif roll < 35:
        return 'potion_shielding'
    elif roll < 40:
        return 'scroll_lightning'
    elif roll < 45:
        return 'scroll_fireball'
    elif roll < 50:
        return 'scroll_confusion'
    else:
        return 'scroll_forge'


def choose_material(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 2 * loot_level, 150))
    if roll < 5:
        return choose_material(loot_level + 5)
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


def choose_quality(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 2 * loot_level, 130))
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
    'book' : { 'plural' : 'books' }
}

table = {
    'default': [None],
    'none': [None]
}

weapon_qualities = {
    'broken' : {
        'dmg' : -3,
        'acc' : -3,
        'shred' : -1,
        'color' : libtcodpy.desaturated_red
    },
    'crude' : {
        'dmg' : -2,
        'acc' : -1,
        'break' : 5.0,
        'color' : libtcodpy.dark_sepia
    },
    '' : { # standard
        'dmg' : 0,
        'acc' : 0,
        'color' : libtcodpy.light_gray
    },
    'military' : {
        'dmg' : 1,
        'acc' : 1,
        'color' : libtcodpy.dark_orange
    },
    'fine' : {
        'dmg' : 2,
        'acc' : 2,
        'break' : -1.5,
        'color' : libtcodpy.sea
    },
    'masterwork' : {
        'dmg' : 3,
        'acc' : 3,
        'shred' : 1,
        'break' : -10.0,
        'color' : libtcodpy.green
    },
    'artifact' : {
        'dmg' : 5,
        'acc' : 5,
        'shred' : 1,
        'peirce' : 1,
        'break' : -1000.0,
        'color' : libtcodpy.yellow
    },
}

weapon_materials = {
    'wooden' : {
        'dmg' : -2,
        'acc' : 1,
        'break' : 5.0
    },
    'bronze' : {
        'dmg' : 0,
        'acc' : 0,
        'break' : 1.5
    },
    'iron' : {
        'dmg' : 0,
        'acc' : 0,
        'shred' : 1
    },
    'steel' : {
        'dmg' : 1,
        'acc' : 1,
        'shred' : 2,
        'break' : -5.0
    },
    'crystal' : {
        'dmg' : 3,
        'acc' : -2,
        'pierce' : 1,
        'break' : -1000.0
    },
    'meteor' : {
        'dmg' : 5,
        'acc' : -2,
        'shred' : 1,
        'break' : -5.0
    },
    'aetherwood' : {
        'dmg' : 2,
        'acc' : 3,
        'shred' : 1,
        'break' : -15.0
    },
    'blightstone' : {
        'dmg' : 0,
        'acc' : 0,
        'autoshred' : 1,
        'break' : -5.0
    },
}

proto = {

    #SCROLLS
    'scroll_lightning': {
        'name'          : 'Scroll of Lightning Bolt',
        'category'      : 'scroll',
        'char'          : '#',
        'on_use'        : spells.cast_lightning,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'Strikes the nearest foe with a powerful bolt'
    },

    'scroll_fireball': {
        'name'          : 'Scroll of Fireball',
        'category'      : 'scroll',
        'char'          : '#',
        'on_use'        : spells.cast_fireball,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'Fires a flaming projectile at a target that explodes on impact'
    },

    'scroll_confusion': {
        'name'          : 'Scroll of Confusion',
        'category'      : 'scroll',
        'char'          : '#',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_confuse,
        'type'          : 'item',
        'description'   : 'Inflicts confusion on an enemy, causing them to move about erratically.'
    },

    'scroll_forge': {
        'name' : 'Scroll of Forging',
        'category' : 'scroll',
        'char' : '#',
        'color': libtcodpy.yellow,
        'on_use' : spells.cast_forge,
        'type' : 'item',
        'description' : 'Upgrades the quality of your held weapon.'
    },

    #POTIONS
    'potion_healing': {
        'name'          : 'Potion of Healing',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_heal,
        'type'          : 'item',
        'description'   : 'Potion that heals wounds when consumed'
    },

    'potion_waterbreathing': {
        'name'          : 'Potion of Waterbreathing',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_waterbreathing,
        'type'          : 'item',
        'description'   : "Drinking this potion causes temporary gills to form on the drinker's throat, allowing him or "
                          "her to breath water like a fish."
    },

    'potion_shielding': {
        'name'          : 'Potion of Shielding',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_shielding,
        'type'          : 'item',
        'description'   : 'This oily metallic potion bolsters the defenses of anyone who drinks it, repairing shreded'
                          ' armor and temporarily enhancing its effectiveness'
    },

    #TOMES
    'tome_manabolt': {
        'name'          : 'Tome of Manabolt',
        'category'      : 'book',
        'char'          : '=',
        'color'         : libtcodpy.yellow,
        'learn_spell'   : 'manabolt',
        'type'          : 'item',
        'description'   : "A weathered book that holds the secrets of Manabolt."
    },

    'tome_mend': {
        'name'          : 'Tome of Mend',
        'category'      : 'book',
        'char'          : '=',
        'color'         : libtcodpy.yellow,
        'learn_spell'   : 'mend',
        'type'          : 'item',
        'description'   : "A weathered book that holds the secrets of Mend."
    },

    'tome_ignite': {
        'name'          : 'Tome of Ignite',
        'category'      : 'book',
        'char'          : '=',
        'color'         : libtcodpy.yellow,
        'learn_spell'   : 'ignite',
        'type'          : 'item',
        'description'   : "A weathered book that holds the secrets of Ignite."
    },

    #WEAPONS
    'equipment_longsword': {
        'name'               : 'longsword',
        'category'           : 'weapon',
        'char'               : '/',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'attack_damage_bonus': 0, #10
        'slot'               :'right hand',
        'description'        : 'A hand-and-a-half cruciform sword',
        'stamina_cost'       : 10,
        'str_requirement'    : 12,
        'shred'              : 1,
        'accuracy'           : 1,
        'weapon_dice'        : '2d6',
        'str_dice'           : 2
    },
    'equipment_dagger': {
        'name'               : 'dagger',
        'category'           : 'weapon',
        'char'               : '-',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'attack_damage_bonus': 0, #3
        'slot'               :'right hand',
        'description'        : 'A small double-edged knife. Deals triple damage to incapacitated targets',
        'stamina_cost'       : 6,
        'str_requirement'    : 10,
        'shred'              : 0,
        'accuracy'           : 5,
        'weapon_dice'        : '2d4',
        'str_dice'           : 1
    },
    'equipment_spear': {
        'name'               : 'spear',
        'category'           : 'weapon',
        'char'               : libtcodpy.CHAR_ARROW_N,
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'attack_damage_bonus': 0, #6
        'slot'               :'right hand',
        'description'        : 'A light thrusting spear',
        'stamina_cost'       : 10,
        'str_requirement'    : 12,
        'ability'            : 'ability_thrust',
        'pierce'             : 1,
        'shred'              : 0,
        'accuracy'           : 1,
        'ctrl_attack'        : main.player_reach_attack,
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction. Deals 50% more '
                               'damage to enemies exactly 2 spaces away.',
        'weapon_dice'        : '2d5',
        'str_dice'           : 1
    },
    'equipment_pickaxe': {
        'name'               : 'pickaxe',
        'category'           : 'weapon',
        'char'               : 'T',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'attack_damage_bonus': 0, #5
        'slot'               :'right hand',
        'description'        : 'A heavy digging implement used by miners. Can be used to dig through the walls '
                               'of the dungeon',
        'stamina_cost'       : 18,
        'str_requirement'    : 14,
        'pierce'             : 1,
        'shred'              : 1,
        'accuracy'           : -3,
        'ctrl_attack'        : main.player_dig,
        'ctrl_attack_desc'   : 'Dig - dig through walls in this direction.',
        'break'              : 5.0,
        'weapon_dice'        : '1d4',
        'str_dice'           : 3
    },
    'equipment_hatchet': {
        'name'               : 'hatchet',
        'category'           : 'weapon',
        'char'               : 'p',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'attack_damage_bonus': 0, #7
        'slot'               : 'right hand',
        'description'        : 'A one-handed axe made for cutting wood.',
        'stamina_cost'       : 9,
        'str_requirement'    : 10,
        'shred'              : 1,
        'accuracy'           : 3,
        'ctrl_attack'        : main.player_cleave_attack,
        'ctrl_attack_desc'   : 'Cleave - attack all adjacent enemies. Costs 2x stamina.',
        'weapon_dice'        : '1d6',
        'str_dice'           : 2
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
        'evasion_bonus' : -2

    },

    'equipment_leather_armor': {
        'name'          : 'Leather Armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'slot'          : 'body',
        'description'   : 'A hardened leather vest.',
        'evasion_bonus' : -1
    },

    'equipment_mail_armor': {
        'name'          : 'Mail Armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.gray,
        'type'          : 'item',
        'armor_bonus'   : 3,
        'evasion_bonus' : -3,
        'slot'          : 'body',
        'description'   : 'A coat of mail made of interlocking iron rings'
    },

    'equipment_brigandine': {
        'name'          : 'Brigandine',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.red,
        'type'          : 'item',
        'armor_bonus'   : 5,
        'evasion_bonus' : -5,
        'slot'          : 'body',
        'description'   : 'A vest of articulated steel plates'
    },

    'equipment_plate_armor': {
        'name'          : 'Plate armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.light_blue,
        'type'          : 'item',
        'armor_bonus'   : 7,
        'evasion_bonus' : -7,
        'slot'          : 'body',
        'description'   : 'A hardened steel breastplate'
    },

    'equipment_boob_plate': {
        'name'          : 'Boob Plate',
        'category'      : 'armor',
        'char'          : chr(235), #infinity
        'color'         : libtcodpy.gray,
        'type'          : 'item',
        'armor_bonus'   : 6,
        'evasion_bonus' : -4,
        'slot'          : 'body',
        'description'   : 'A steel bra that deflects harm from the entire torso by an unknown mechanism'
    },

    'equipment_iron_helm': {
        'name'          : 'Iron Helm',
        'category'      : 'armor',
        'char'          : chr(67),
        'color'         : libtcodpy.gray,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'evasion_bonus' : -1,
        'slot'          : 'head',
        'description'   : 'A conical iron helm with a nose guard'
    },

    'equipment_great_helm': {
        'name'          : 'Great Helm',
        'category'      : 'armor',
        'char'          : chr(67),
        'color'         : libtcodpy.red,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -3,
        'slot'          : 'head',
        'description'   : 'A large cylindrical steel helm. Very heavy and cumbersome'
    },

    'equipment_armet_helm': {
        'name'          : 'Armet Helm',
        'category'      : 'armor',
        'char'          : chr(67),
        'color'         : libtcodpy.light_blue,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -1,
        'slot'          : 'head',
        'description'   : 'A crested steel helm with visor and bevor.'
    },
}