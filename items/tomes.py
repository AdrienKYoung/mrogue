import libtcodpy
import spells

table = {
    'book_lesser_fire' : {
        'name'          : 'Book of Embers',
        'category'      : 'book',
        'char'          : '#',
        'color'         : spells.essence_colors['fire'],
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A tome bound in red leather. The faint spell of smoke rises from its singed pages.',
        'essence':'fire',
        'level' : 1,
        'spells': [
            'spell_heat_ray',
            'spell_flame_wall',
            'spell_fireball',
            'spell_shatter_item',
            'spell_magma_bolt'
        ],
        'levels': [
            'spell_heat_ray', 'spell_flame_wall', 'spell_heat_ray', 'spell_fireball', 'spell_shatter_item',
            'spell_fireball', 'spell_magma_bolt', 'spell_heat_ray','spell_flame_wall', 'spell_fireball',
            'spell_magma_bolt', 'spell_shatter_item', 'spell_magma_bolt'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },

    'book_lesser_cold' : {
        'name'          : 'Book of Blizzards',
        'category'      : 'book',
        'char'          : '#',
        'color'         : spells.essence_colors['cold'],
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A book of the magic of winter. Its very pages are cold to the touch.',
        'essence': 'cold',
        'level' : 1,
        'spells': [
            'spell_frozen_orb',
            'spell_flash_frost',
            'spell_ice_shards',
            'spell_snowstorm',
            'spell_avalanche'
        ],
        'levels': [
            'spell_frozen_orb', 'spell_flash_frost', 'spell_frozen_orb', 'spell_ice_shards', 'spell_snowstorm',
            'spell_ice_shards', 'spell_avalanche', 'spell_frozen_orb','spell_flash_frost', 'spell_ice_shards',
            'spell_avalanche', 'spell_snowstorm', 'spell_avalanche'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },

    'book_lesser_death' : {
        'name'          : 'The Dead Walk',
        'category'      : 'book',
        'char'          : '#',
        'color'         : spells.essence_colors['death'],
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A sinister grimoire holding the secrets of Death magic. The seal of the Cult of Eternity is stamped on its cover.',
        'essence': 'death',
        'level' : 1,
        'spells': [
            'spell_hex',
            'spell_defile',
            'spell_shackles_of_the_dead',
            'spell_sacrifice',
            'spell_corpse_dance'
        ],
        'levels': [
            'spell_hex', 'spell_defile', 'spell_hex', 'spell_shackles_of_the_dead', 'spell_defile', 'spell_sacrifice',
            'spell_corpse_dance', 'spell_hex','spell_defile', 'spell_shackles_of_the_dead',
            'spell_corpse_dance', 'spell_sacrifice', 'spell_corpse_dance'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },

    'book_lesser_radiance' : {
        'name'          : 'The Way of the Righteous',
        'category'      : 'book',
        'char'          : '#',
        'color'         : spells.essence_colors['radiance'],
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A book of blessed radiance magic. It is adorned with an icon of The Martyr.',
        'essence': 'radiance',
        'level' : 1,
        'spells': [
            'spell_bless',
            'spell_smite',
            'spell_castigate',
            'spell_blessed_aegis',
            'spell_holy_lance'
        ],
        'levels': [
            'spell_bless', 'spell_smite', 'spell_bless', 'spell_castigate', 'spell_smite', 'spell_blessed_aegis',
            'spell_holy_lance', 'spell_bless','spell_smite', 'spell_castigate',
            'spell_holy_lance', 'spell_blessed_aegis', 'spell_holy_lance'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },

    'book_lesser_life' : {
        'name'          : "The Gardener's Guide",
        'category'      : 'book',
        'char'          : '#',
        'color'         : spells.essence_colors['life'],
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A thin book of Life magic, its vivid green cover stained with soil.',
        'essence': 'life',
        'level' : 1,
        'spells': [
            'spell_green_touch',
            'spell_fungal_growth',
            'spell_dragonseed',
            'spell_bramble',
            'spell_strangleweeds'
        ],
        'levels': [
            'spell_green_touch', 'spell_fungal_growth', 'spell_green_touch', 'spell_dragonseed', 'spell_fungal_growth', 'spell_bramble',
            'spell_strangleweeds', 'spell_green_touch','spell_fungal_growth', 'spell_dragonseed',
            'spell_strangleweeds', 'spell_bramble', 'spell_strangleweeds'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },
    'book_lesser_arcane' : {
        'name'          : "The Sorcerer's Handbook",
        'category'      : 'book',
        'char'          : '#',
        'color'         : spells.essence_colors['arcane'],
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A heavy tome bound in aged leather. It seems to vibrate with an inner power.',
        'essence':'arcane',
        'level' : 1,
        'spells': [
            'spell_arcane_arrow',
            'spell_spatial_exchange',
            'spell_shimmering_swords',
            'spell_time_bomb',
            'spell_arcane_construct'
        ],
        'levels': [
            'spell_arcane_arrow', 'spell_spatial_exchange', 'spell_arcane_arrow', 'spell_shimmering_swords', 'spell_time_bomb',
            'spell_spatial_exchange', 'spell_arcane_construct', 'spell_arcane_arrow','spell_spatial_exchange', 'spell_shimmering_swords',
            'spell_arcane_construct', 'spell_time_bomb', 'spell_arcane_construct', 'spell_shimmering_swords', 'spell_time_bomb'
        ],
        'level_costs': [
            1,1,1,1,2,2,2,3,3,3,3,4,4,4,4
        ]
    },
}