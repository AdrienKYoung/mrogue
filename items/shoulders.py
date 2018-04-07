import libtcodpy

table = {
    'equipment_cloak_of_stealth': {
        'name'          : 'Cloak of Stealth',
        'category'      : 'armor',
        'char'          : chr(168), #upside down question mark
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'shoulders',
        'description'   : "A heavy cloak woven from rough, dark cloth. "
                          "It helps its wearer blend into the shadows and avoid detection",
        'weight'        : 2,
        'stealth'       : 7
    },
    'equipment_greater_cloak_of_stealth': {
        'name'          : 'Greater Cloak of Stealth',
        'category'      : 'armor',
        'char'          : chr(168), #upside down question mark
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'shoulders',
        'description'   : 'A shimmering cloak that you can almost see through',
        'weight'        : 3,
        'stealth'       : 4
    },
    'equipment_quiver_of_blood': {
        'name'          : 'Quiver of Blood',
        'category'      : 'quiver',
        'char'          : '%',
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'slot'          : 'quiver',
        'description'   : "A dark red leather quiver embroidered with an image of Gyllados, the god of the hunt. One can"
                          " use one's own life force to draw an arrow from this quiver even when it is empty.",
        'weight'        : 2,
        'max_ammo'      : 25,
        'attributes'    : ['draw_blood']
    },
}