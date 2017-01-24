import libtcodpy as libtcod
import mapgen

branches = {
    'beach': {
        'name':'Rocky Coast',
        'loot':None,
        'monsters':None,
        'generate':mapgen.make_map_beach,
        'connect':['marsh','badlands']
    },
    'marsh': {
        'name':'Fetid Bog',
        'loot_level':0,
        'loot':{
            'armor_1':25,
            'weapons_1':20,
            'consumables_1':40,
            'tomes_1':10
        },
        'loot_dice':'1d4',
        'encounter_dice':'1d4+5',
        'encounter_range':6,
        'monsters':[
            {'encounter':['monster_cockroach'], 'party':'2d2+2'},
            {'encounter':['monster_centipede']},
            {'encounter':['monster_reeker'],'party':'1d2'},
            {'encounter':['monster_tunnel_spider']},
            {'encounter':['monster_bomb_beetle'],'party':'1d2'},
            {'encounter':['monster_giant_frog']},
            {'encounter':['monster_bear']},
            {'encounter':['monster_verman']},
            {'encounter':['monster_cockroach','monster_centipede','monster_bomb_beetle'],'party':'2d3'},
        ],
        'generate':mapgen.make_map_marsh,
        'connect':['beach','garden','goblin']
    }
}