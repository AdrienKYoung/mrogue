import libtcodpy
import charms

table = {
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
}