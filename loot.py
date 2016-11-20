import libtcodpy
import spells

table = {
    'default': ['spell_lightning',None]
}

proto = {

    #SPELLS
    'spell_lightning': {
        'name': 'Lightning Bolt',
        'char': '/',
        'on_use': spells.cast_lightning,
        'color': libtcodpy.yellow,
        'type': 'spell',
        'element': 'lightning',
        'description': 'Strikes the nearest foe with a powerful bolt'
    },

    'spell_fireball': {
        'name': 'Fireball',
        'char': '#',
        'on_use': spells.cast_fireball,
        'color': libtcodpy.red,
        'type': 'spell',
        'element': 'fire',
        'description': 'Fires a flaming projectile at a target that explodes on impact'
    },

    'spell_confusion': {
        'name': 'Confusion',
        'char': '#',
        'color': libtcodpy.yellow,
        'on_use': spells.cast_confuse,
        'type': 'spell',
        'description': 'Inflicts confusion on an enemy, causing them to move about erratically.'
    },

    #POTIONS
    'potion_healing': {
        'name': 'Potion of Healing',
        'char': '!',
        'color': libtcodpy.yellow,
        'on_use': spells.cast_heal,
        'type': 'potion',
        'description': 'Potions that heals wounds when consumed'
    },

    #WEAPONS
    'equipment_longsword': {
        'name': 'Longsword',
        'char': '/',
        'color': libtcodpy.yellow,
        'type': 'equipment',
        'attack_damage_bonus': 10,
        'slot':'right hand',
        'description': 'A hand-and-a-half cruciform sword',
        'stamina_cost': 10,
        'str_requirement': 10
    },

    #ARMOR
    'equipment_shield': {
        'name': 'Shield',
        'char': '[',
        'color': libtcodpy.yellow,
        'type': 'equipment',
        'armor_bonus': 5,
        'slot': 'left hand',
        'description': 'An iron kite shield.'
    },
}