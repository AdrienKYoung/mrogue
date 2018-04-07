import libtcodpy
import effects

table = {
    'equipment_boots_of_levitation': {
        'name': 'Boots of Levitation',
        'category': 'armor',
        'char' : chr(28),
        'color': libtcodpy.yellow,
        'type': 'item',
        'slot': 'feet',
        'weight': 2,
        'description': 'An enchanted pair of boots that allows its wearer to '
                       'permanently hover a few feet above the ground.',
        'status_effect': effects.levitating,
    },
    'equipment_boots_of_agility': {
        'name': 'Boots of Agility',
        'category': 'armor',
        'char' : chr(28),
        'color': libtcodpy.yellow,
        'type': 'item',
        'slot': 'feet',
        'weight': 2,
        'description': 'A coveted treasure from the arid lands of Sko Kall, these boots magically enhance the agility '
                       'and reflexes of whoever wears them.',
        'agi_bonus': 5,
    },
    'equipment_boots_of_leaping': {
        'name': 'Boots of Leaping',
        'category': 'armor',
        'char' : chr(28),
        'color': libtcodpy.yellow,
        'type': 'item',
        'slot': 'feet',
        'weight': 2,
        'description': "Rabbit hide boots woven with spells that enhance their wearer's ability to jump long distances",
        'attributes': ['jump_distance'],
    },
    'equipment_longstrider_boots': {
        'name': 'Longstrider Boots',
        'category': 'armor',
        'char' : chr(28),
        'color': libtcodpy.yellow,
        'type': 'item',
        'slot': 'feet',
        'weight': 2,
        'description': "A pair of black and silver boots that appear to flicker in and out of existence. "
                       "Wearing them allows the wearer to step through space itself.",
        'ability': 'ability_longstride',
    },
}