import libtcodpy
import actions
import spells

table = {
    #Scrolls
    'scroll_forge': {
        'name' : 'Scroll of Forging',
        'category' : 'scroll',
        'char' : '#',
        'color': libtcodpy.yellow,
        'on_use' : actions.forge,
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

    'treasure_bejeweled_chalice': {
        'name'          : 'bejeweled chalice',
        'category'      : 'treasure',
        'char'          : '$',
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'A golden chalice, encrusted with precious jewels. Mundane, but valuable.'
    },

# GEMS
    'gem_lesser_fire': {
        'name'          : 'Rough Ruby',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['fire'],
        'on_use'        : actions.potion_essence('fire'), #not a bug, returns a lambda
        'description'   : 'The essence of fire burns within this gemstone. Absorbing it will bestow a single fire essence.'
    },
    'gem_lesser_earth': {
        'name'          : 'Rough Garnet',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['earth'],
        'on_use'        : actions.potion_essence('earth'), #not a bug, returns a lambda
        'description'   : 'The essence of earth resonates within this gemstone. Absorbing it will bestow a single earth essence.'
    },
    'gem_lesser_life': {
        'name'          : 'Rough Emerald',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['life'],
        'on_use'        : actions.potion_essence('life'), #not a bug, returns a lambda
        'description'   : 'The essence of life emanates from this gemstone. Absorbing it will bestow a single life essence.'
    },
    'gem_lesser_air': {
        'name'          : 'Rough Quartz',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['air'],
        'on_use'        : actions.potion_essence('air'), #not a bug, returns a lambda
        'description'   : 'The essence of air swirls in this crystal. Absorbing it will bestow a single air essence.'
    },
    'gem_lesser_water': {
        'name'          : 'Rough Aquamarine',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['water'],
        'on_use'        : actions.potion_essence('water'), #not a bug, returns a lambda
        'description'   : 'The essence of water flows through this gemstone. Absorbing it will bestow a single water essence.'
    },
    'gem_lesser_cold': {
        'name'          : 'Rough Zircon',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['cold'],
        'on_use'        : actions.potion_essence('cold'), #not a bug, returns a lambda
        'description'   : 'The essence of cold chills the surface of this gemstone. Absorbing it will bestow a single cold essence.'
    },
    'gem_lesser_arcane': {
        'name'          : 'Rough Amethyst',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['arcane'],
        'on_use'        : actions.potion_essence('arcane'), #not a bug, returns a lambda
        'description'   : 'The essence of arcana hums within this gemstone. Absorbing it will bestow a single arcane essence.'
    },
    'gem_lesser_radiance': {
        'name'          : 'Rough Diamond',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['radiance'],
        'on_use'        : actions.potion_essence('radiance'), #not a bug, returns a lambda
        'description'   : 'The essence of radiance shines through this gemstone. Absorbing it will bestow a single radiance essence.'
    },
    'gem_lesser_death': {
        'name'          : 'Rough Onyx',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['death'],
        'on_use'        : actions.potion_essence('death'), #not a bug, returns a lambda
        'description'   : 'The essence of dark envelops this gemstone. Absorbing it will bestow a single dark essence.'
    },

#Essence
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

'scroll_fireball': {
        'name'          : 'Scroll of Fireball',
        'category'      : 'scroll',
        'char'          : '#',
        'on_use'        : actions.fireball,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'Fires a flaming projectile at a target that explodes on impact'
    },

    'scroll_confusion': {
        'name'          : 'Scroll of Confusion',
        'category'      : 'scroll',
        'char'          : '#',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.confuse,
        'type'          : 'item',
        'description'   : 'Inflicts confusion on an enemy, causing them to move about erratically.'
    },
}