import libtcodpy

table = {
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
        'weight'        : 8
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
        'weight'        : 15
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
        'weight'        : 25
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
        'weight'        : 35
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
        'weight'        : 12
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
        'weight'        : 6
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
        'weight'        : 10
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
        'weight'        : 9
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
        'weight'        : 3
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
        'weight'        : 6
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
        'weight'        : 6
    },

    'shield_leather_buckler': {
        'name': 'Leather Buckler',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 0,
        'slot': 'left hand',
        'description': 'A small round shield made from stiff boiled leather. It is lightweight and easy to lift,'
                       ' but easily knocked away.',
        'evasion_bonus': 0,
        'weight': 6,
        'sh_max': 1,
        'sh_raise_cost': 25,
        'sh_recovery': 15,
    },

    'shield_wooden_buckler': {
        'name': 'Wooden Buckler',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 0,
        'slot': 'left hand',
        'description': 'A small round shield made from wooden planks bound in an iron ring. It is lightweight and easy'
                       ' to lift, but easily knocked away.',
        'evasion_bonus': 0,
        'weight': 8,
        'sh_max': 5,
        'sh_raise_cost': 30,
        'sh_recovery': 18,
    },

    'shield_iron_buckler': {
        'name': 'Iron Buckler',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 0,
        'slot': 'left hand',
        'description': 'A small round shield made of roughly hammered iron. It is lightweight and easy to lift,'
                       ' but easily knocked away.',
        'evasion_bonus': -1,
        'weight': 8,
        'sh_max': 8,
        'sh_raise_cost': 35,
        'sh_recovery': 20,
    },

    'shield_duelists_buckler': {
        'name': "Duelist's Buckler",
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 0,
        'slot': 'left hand',
        'description': 'A small, bronze shield emblazoned with a red serpent. It is the sigil of the Taguinnes, a family'
                       ' who left no slight to their honor unpaid in blood.',
        'evasion_bonus': 2,
        'weight': 4,
        'sh_max': 3,
        'sh_raise_cost': 20,
        'sh_recovery': 12,
    },

    'shield_heater_shield': {
        'name': 'Heater Shield',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 1,
        'slot': 'left hand',
        'description': 'A simple, sturdy shield carried by footsoldiers.',
        'evasion_bonus': -2,
        'weight': 12,
        'sh_max': 12,
        'sh_raise_cost': 50,
        'sh_recovery': 20,
    },

    'shield_blessed_aegis': { #note - not a valid item, summoned by spell "Holy Aegis"
        'name': 'Blessed Aegis',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 0,
        'slot': 'floating shield',
        'description': 'A mote of radiance that intercepts attacks',
        'evasion_bonus': 0,
        'weight': 0,
        'sh_max': 12,
        'sh_raise_cost': 50,
        'sh_recovery': 20,
    },

    'shield_escutcheon': {
        'name': 'Escutcheon',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 1,
        'slot': 'left hand',
        'description': 'A decorative shield bearing the faded heraldry of some long-forgotten knight.',
        'evasion_bonus': -2,
        'weight': 14,
        'sh_max': 15,
        'sh_raise_cost': 50,
        'sh_recovery': 18,
    },

    'shield_round_shield': {
        'name': 'Round Shield',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 1,
        'slot': 'left hand',
        'description': 'A large round shield made of wood and flecked with colored paint. Shields like these were '
                       'carried by raiders from the Stormy Seas.',
        'evasion_bonus': -1,
        'weight': 13,
        'sh_max': 10,
        'sh_raise_cost': 35,
        'sh_recovery': 20,
    },

    'shield_kite_shield': {
        'name': 'Kite Shield',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 2,
        'slot': 'left hand',
        'description': 'A long shield with a rounded top and a pointed tip.',
        'evasion_bonus': -4,
        'weight': 18,
        'sh_max': 20,
        'sh_raise_cost': 60,
        'sh_recovery': 26,
    },

    'shield_tower_shield': {
        'name': 'Tower Shield',
        'category': 'armor',
        'char': chr(233),  # theta
        'color': libtcodpy.yellow,
        'type': 'item',
        'armor_bonus': 3,
        'slot': 'left hand',
        'description': 'A massive iron shield offering complete protection - for those that can heft its weight.',
        'evasion_bonus': -6,
        'weight': 28,
        'sh_max': 35,
        'sh_raise_cost': 85,
        'sh_recovery': 33,
    },
}