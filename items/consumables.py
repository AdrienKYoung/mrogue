import libtcodpy
from actions import item_actions
import spells
import player

table = {
    # Scrolls
    'scroll_forge': {
        'name' : 'Scroll of Forging',
        'category' : 'scroll',
        'char' : '#',
        'color': libtcodpy.yellow,
        'on_use' : item_actions.forge,
        'type' : 'item',
        'description' : 'Upgrades the quality of your held weapon.'
    },

    'glass_key' : {
        'name'          : 'Glass Key',
        'category'      : 'key',
        'char'          : 13,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'A delicate key made from clouded glass. This key can open any lock,'
                          ' but breaks in the process.'
    },

    # Gems
    'gem_lesser_fire': {
        'name'          : 'Rough Ruby',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['fire'],
        'on_use'        : item_actions.potion_essence('fire'), #not a bug, returns a lambda
        'description'   : 'The essence of fire burns within this gemstone. Absorbing it will bestow a single fire essence.'
    },
    'gem_lesser_earth': {
        'name'          : 'Rough Garnet',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['earth'],
        'on_use'        : item_actions.potion_essence('earth'), #not a bug, returns a lambda
        'description'   : 'The essence of earth resonates within this gemstone. Absorbing it will bestow a single earth essence.'
    },
    'gem_lesser_life': {
        'name'          : 'Rough Emerald',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['life'],
        'on_use'        : item_actions.potion_essence('life'), #not a bug, returns a lambda
        'description'   : 'The essence of life emanates from this gemstone. Absorbing it will bestow a single life essence.'
    },
    'gem_lesser_air': {
        'name'          : 'Rough Quartz',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['air'],
        'on_use'        : item_actions.potion_essence('air'), #not a bug, returns a lambda
        'description'   : 'The essence of air swirls in this crystal. Absorbing it will bestow a single air essence.'
    },
    'gem_lesser_water': {
        'name'          : 'Rough Aquamarine',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['water'],
        'on_use'        : item_actions.potion_essence('water'), #not a bug, returns a lambda
        'description'   : 'The essence of water flows through this gemstone. Absorbing it will bestow a single water essence.'
    },
    'gem_lesser_cold': {
        'name'          : 'Rough Zircon',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['cold'],
        'on_use'        : item_actions.potion_essence('cold'), #not a bug, returns a lambda
        'description'   : 'The essence of cold chills the surface of this gemstone. Absorbing it will bestow a single cold essence.'
    },
    'gem_lesser_arcane': {
        'name'          : 'Rough Amethyst',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['arcane'],
        'on_use'        : item_actions.potion_essence('arcane'), #not a bug, returns a lambda
        'description'   : 'The essence of arcana hums within this gemstone. Absorbing it will bestow a single arcane essence.'
    },
    'gem_lesser_radiance': {
        'name'          : 'Rough Diamond',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['radiance'],
        'on_use'        : item_actions.potion_essence('radiance'), #not a bug, returns a lambda
        'description'   : 'The essence of radiance shines through this gemstone. Absorbing it will bestow a single radiance essence.'
    },
    'gem_lesser_death': {
        'name'          : 'Rough Onyx',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['death'],
        'on_use'        : item_actions.potion_essence('death'), #not a bug, returns a lambda
        'description'   : 'The essence of dark envelops this gemstone. Absorbing it will bestow a single dark essence.'
    },

    # Essence
    'essence_fire' : {
        'category' : 'essence',
        'essence_type' : 'fire'
    },
    'essence_water' : {
        'category' : 'essence',
        'essence_type' : 'water'
    },
    'essence_cold' : {
        'category' : 'essence',
        'essence_type' : 'cold'
    },
    'essence_air' : {
        'category' : 'essence',
        'essence_type' : 'air'
    },
    'essence_earth' : {
        'category' : 'essence',
        'essence_type' : 'earth'
    },
    'essence_life' : {
        'category' : 'essence',
        'essence_type' : 'life'
    },
    'essence_death' : {
        'category' : 'essence',
        'essence_type' : 'death'
    },
    'essence_arcane' : {
        'category' : 'essence',
        'essence_type' : 'arcane'
    },
    'essence_radiance' : {
        'category' : 'essence',
        'essence_type' : 'radiance'
    },
    'essence_void' : {
        'category' : 'essence',
        'essence_type' : 'void'
    },

    # Elixirs
    'elixir_con' : {
        'name'          : 'Elixir of Constitution',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : player.gain_con,
        'description'   : 'A small vial of swirling orange liquid. Drinking this elixir will permanently increase your Constitution.'
    },
    'elixir_str' : {
        'name'          : 'Elixir of Strength',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : player.gain_str,
        'description'   : 'A small vial of swirling red liquid. Drinking this elixir will permanently increase your Strength.'
    },
    'elixir_agi' : {
        'name'          : 'Elixir of Agility',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : player.gain_agi,
        'description'   : 'A small vial of swirling green liquid. Drinking this elixir will permanently increase your Agility.'
    },
    'elixir_int' : {
        'name'          : 'Elixir of Intelligence',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : player.gain_int,
        'description'   : 'A small vial of swirling blue liquid. Drinking this elixir will permanently increase your Intelligence.'
    },
    'elixir_wis' : {
        'name'          : 'Elixir of Wisdom',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : player.gain_wis,
        'description'   : 'A small vial of swirling white liquid. Drinking this elixir will permanently increase your Wisdom.'
    },
    'elixir_life' : {
        'name'          : 'Elixir of Life',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : player.full_heal,
        'description'   : 'A small vial of swirling golden liquid. Drinking this elixir will heal you to full health.'
    },

    # Treasure

    'treasure_bejeweled_chalice': {
        'name': 'bejeweled chalice',
        'category': 'treasure',
        'char': '$',
        'color': libtcodpy.yellow,
        'type': 'item',
        'description': 'A golden chalice, encrusted with precious jewels. Mundane, but valuable.'
    },
    'treasure_giant_pearl': {
        'name': 'giant pearl',
        'category': 'treasure',
        'char': '$',
        'color': libtcodpy.yellow,
        'type': 'item',
        'description': 'An enormous pearl the size of a walnut. Mundane, but valuable.'
    },
    'treasure_chest_of_coins': {
        'name': 'chest of coins',
        'category': 'treasure',
        'char': '$',
        'color': libtcodpy.yellow,
        'type': 'item',
        'description': 'A small chest full of ancient coins stamped with the likeness of the Emperor. '
                       'Mundane, but valuable.'
    },
    'treasure_silver_tiara': {
        'name': 'silver tiara',
        'category': 'treasure',
        'char': '$',
        'color': libtcodpy.yellow,
        'type': 'item',
        'description': 'A finely-crafted tiara of shining silver. Mundane, but valuable.'
    },
    'treasure_jade_necklace': {
        'name': 'jade necklace',
        'category': 'treasure',
        'char': '$',
        'color': libtcodpy.yellow,
        'type': 'item',
        'description': 'An elegant piece of jewelry made from many jade stones. Mundane, but valuable.'
    },
    'treasure_burial_mask': {
        'name': 'burial mask',
        'category': 'treasure',
        'char': '$',
        'color': libtcodpy.yellow,
        'type': 'item',
        'description': 'A golden mask with the likeness of a long-dead noble. Mundane, but valuable.'
    },
    'treasure_music_box': {
        'name': 'music box',
        'category': 'treasure',
        'char': '$',
        'color': libtcodpy.yellow,
        'type': 'item',
        'description': 'A finely crafted wooden box inlaid with gold. When wound, it plays a haunting tune. '
                       'Mundane, but valuable.'
    },
}