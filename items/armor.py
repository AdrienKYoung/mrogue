import libtcodpy

table = {
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
}