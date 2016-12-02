import libtcodpy
import spells

item_categories = {
    'weapon' : { 'plural' : 'weapons' },
    'armor' : { 'plural' : 'armor' },
    'spell' : { 'plural' : 'spells' },
    'potion' : { 'plural' : 'potions' }
}

table = {
    'default': ['spell_lightning',None],
    'none': [None]
}

proto = {

    #SPELLS
    'spell_lightning': {
        'name': 'Lightning Bolt',
        'category': 'spell',
        'char': '/',
        'on_use': spells.cast_lightning,
        'color': libtcodpy.yellow,
        'type': 'spell',
        'element': 'lightning',
        'description': 'Strikes the nearest foe with a powerful bolt'
    },

    'spell_fireball': {
        'name': 'Fireball',
        'category': 'spell',
        'char': '#',
        'on_use': spells.cast_fireball,
        'color': libtcodpy.red,
        'type': 'spell',
        'element': 'fire',
        'description': 'Fires a flaming projectile at a target that explodes on impact'
    },

    'spell_confusion': {
        'name': 'Confusion',
        'category': 'spell',
        'char': '#',
        'color': libtcodpy.yellow,
        'on_use': spells.cast_confuse,
        'type': 'spell',
        'description': 'Inflicts confusion on an enemy, causing them to move about erratically.'
    },

    #POTIONS
    'potion_healing': {
        'name': 'Potion of Healing',
        'category': 'potion',
        'char': '!',
        'color': libtcodpy.yellow,
        'on_use': spells.cast_heal,
        'type': 'item',
        'description': 'Potion that heals wounds when consumed'
    },

    'potion_waterbreathing': {
        'name': 'Potion of Waterbreathing',
        'category': 'potion',
        'char': '!',
        'color': libtcodpy.yellow,
        'on_use': spells.cast_waterbreathing,
        'type': 'potion',
        'description': "Drinking this potion causes temporary gills to form on the drinker's throat, allowing him or "
                       "her to breath water like a fish."
    },

    #WEAPONS
    'equipment_longsword': {
        'name': 'Longsword',
        'category': 'weapon',
        'char': '/',
        'color': libtcodpy.yellow,
        'type': 'item',
        'attack_damage_bonus': 10,
        'slot':'right hand',
        'description': 'A hand-and-a-half cruciform sword',
        'stamina_cost': 10,
        'str_requirement': 10
    },
    'equipment_dagger': {
        'name': 'Dagger',
        'category': 'weapon',
        'char': '-',
        'color': libtcodpy.yellow,
        'type': 'item',
        'attack_damage_bonus': 3,
        'slot':'right hand',
        'description': 'A small double-edged knife',
        'stamina_cost': 3,
        'str_requirement': 3
    },

    #ARMOR
    'equipment_shield': {
        'name': 'Shield',
        'category': 'armor',
        'char': '[',
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 5,
        'slot': 'left hand',
        'description': 'An iron kite shield.'
    },

    'equipment_leather_armor': {
        'name': 'Leather Armor',
        'category': 'armor',
        'char': chr(6),
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 5,
        'slot': 'body',
        'description': 'A hardened leather coat.'
    }
}