import libtcodpy as libtcod
import mapgen

branches = {
    'beach': {
        'name'          : 'the shore',
        'default_wall'  : 'sea cliff',
        'default_floor' : 'sand',
        'default_ramp'  : 'stone ramp',
        'scaling'       : 0,
        'loot'          : None,
        'monsters'      : None,
        'generate'      : mapgen.make_map_beach,
        'connect'       : ['marsh', 'badlands']
    },
    'badlands': {
        'name'          : 'the badlands',
        'default_wall'  : 'dark shale wall',
        'default_floor' : 'shale',
        'default_ramp'  : 'shale slope',
        'scaling'       : 0,
        'loot_level':0,
        'loot':{
            'armor_1':25,
            'weapons_1':20,
            'consumables_1':40,
            'tomes_1':10
        },
        'loot_dice':'1d4',
        'encounter_dice':'1d4+5',
        'xp_amount':7,
        'encounter_range':6,
        'monsters':[
            {'encounter':['monster_cockroach'], 'party':'2d2+2'},
            {'encounter':['monster_goblin']},
            {'encounter':['monster_centipede']},
            {'encounter':['monster_tunnel_spider']},
            {'encounter':['monster_golem']},
            {'encounter':['monster_cockroach'], 'party':'3d2'},
            {'encounter':['monster_goblin','monster_goblin_warrior'],'party':'2d3'},
            {'encounter':['monster_golem'], 'party':'1d3'},
        ],
        'generate'      : mapgen.make_map_badlands,
        'connect'       : ['beach', 'forest', 'goblin']
    },
    'marsh': {
        'name'          : 'the marshes',
        'default_wall'  : 'mossy stone wall',
        'default_floor' : 'damp soil',
        'default_ramp'  : 'stone ramp',
        'scaling'       : 0,
        'loot_level':0,
        'loot':{
            'armor_1':25,
            'weapons_1':20,
            'consumables_1':40,
            'tomes_1':10
        },
        'loot_dice':'1d4',
        'encounter_dice':'1d4+5',
        'xp_amount':7,
        'encounter_range':6,
        'monsters':[
            {'encounter':['monster_cockroach'], 'party':'2d2+2'},
            {'encounter':['monster_centipede']},
            {'encounter':['monster_reeker'],'party':'1d2'},
            {'encounter':['monster_tunnel_spider']},
            {'encounter':['monster_bomb_beetle'],'party':'1d2'},
            {'encounter':['monster_cockroach'], 'party':'3d2'},
            {'encounter':['monster_giant_frog']},
            {'encounter':['monster_bear']},
            {'encounter':['monster_verman']},
            {'encounter':['monster_cockroach','monster_centipede','monster_bomb_beetle'],'party':'2d3'},
        ],
        'generate':mapgen.make_map_marsh,
        'connect':['beach', 'garden', 'goblin']
    }
}