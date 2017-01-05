import libtcodpy
import spells
import abilities

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
    'broken' : { #5
        'dmg' : -3,
        'acc' : -3,
        'shred' : -1
    },
    'crude' : { #5
        'dmg' : -2,
        'acc' : -1,
        'break' : 5.0
    },
    '' : { # standard 75
        'dmg' : 0,
        'acc' : 0
    },
    'military' : { #10
        'dmg' : 1,
        'acc' : 1,
    },
    'fine' : { #10
        'dmg' : 2,
        'acc' : 2,
        'break' : -1.0
    },
    'masterwork' : { #10
        'dmg' : 3,
        'acc' : 3,
        'shred' : 1,
        'break' : -10.0
    },
    'artifact' : { #5
        'dmg' : 5,
        'acc' : 5,
        'shred' : 1,
        'peirce' : 1,
        'break' : -1000.0
    },
}

weapon_materials = {
    'wooden' : { # 10
        'dmg' : -2,
        'acc' : 1,
        'break' : 1.0
    },
    'bronze' : { # 15
        'dmg' : 0,
        'acc' : 0,
        'break' : 0.25
    },
    'iron' : { # 65
        'dmg' : 0,
        'acc' : 0,
        'shred' : 1
    },
    'steel' : { # 10
        'dmg' : 1,
        'acc' : 1,
        'shred' : 2
    },
    'crystal' : { # 15
        'dmg' : 3,
        'acc' : -2,
        'pierce' : 1
    },
    'meteor' : { # 10
        'dmg' : 5,
        'acc' : -2,
        'shred' : 1
    },
    'aetherwood' : { # 10
        'dmg' : 2,
        'acc' : 3,
        'shred' : 1
    },
    'blightstone' : { # 10
        'dmg' : 0,
        'acc' : 0,
        'autoshred' : 1
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

    #WEAPONS
    'equipment_longsword': {
        'name'               : 'longsword',
        'category'           : 'weapon',
        'char'               : '/',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'attack_damage_bonus': 10,
        'slot'               :'right hand',
        'description'        : 'A hand-and-a-half cruciform sword',
        'stamina_cost'       : 10,
        'str_requirement'    : 14,
        'shred'              : 1,
        'accuracy'           : 1
    },
    'equipment_dagger': {
        'name'               : 'dagger',
        'category'           : 'weapon',
        'char'               : '-',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'attack_damage_bonus': 3,
        'slot'               :'right hand',
        'description'        : 'A small double-edged knife',
        'stamina_cost'       : 6,
        'str_requirement'    : 10,
        'shred'              : 0,
        'accuracy'           : 5
    },
    'equipment_spear': {
        'name'               : 'spear',
        'category'           : 'weapon',
        'char'               : libtcodpy.CHAR_ARROW_N,
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'attack_damage_bonus': 8,
        'slot'               :'right hand',
        'description'        : 'A light thrusting spear',
        'stamina_cost'       : 10,
        'str_requirement'    : 12,
        'ability'            : 'ability_thrust',
        'pierce'             : 1,
        'shred'              : 0,
        'accuracy'           : 1
    },

    #ARMOR
    'equipment_shield': {
        'name'          : 'Shield',
        'category'      : 'armor',
        'char'          : '[',
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
        'char'          : chr(6),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'slot'          : 'body',
        'description'   : 'A hardened leather coat.',
        'evasion_bonus' : -1
    }
}