#part of mrogue, an interactive adventure game
#Copyright (C) 2017 Adrien Young and Tyler Soberanis
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        'map_color'     : libtcod.Color(0, 95, 191),
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
            'consumables_1':35,
            'gems_1':10,
            'tomes_1':4,
            'keys_1':1,
            'charms_1':5
        },
        'loot_dice':'1d4',
        'encounter_dice':'1d4+5',
        'xp_amount':7,
        'encounter_range':7,
        'monsters':[
            {'encounter':['monster_cockroach'], 'party':'2d2+1'},
            {'encounter':['monster_rotting_zombie'], 'party':'1d3'},
            {'encounter':['monster_goblin']},
            {'encounter':['monster_centipede']},
            {'encounter':['monster_tunnel_spider']},
            {'encounter':['monster_cockroach'], 'party':'3d2'},
            {'encounter':['monster_rotting_zombie'], 'party':'1d3+2'},
            {'encounter':['monster_goblin','monster_goblin_warrior'],'party':'2d3'},
            {'encounter':['monster_golem']},
            {'encounter':['monster_snow_kite']},
            {'encounter':['monster_necroling']},
            {'encounter':['monster_witch']},
            {'encounter':['monster_necroling', 'monster_goblin'], 'party':'1d3+3'},
            {'encounter':['monster_infested_treant']},
        ],
        'generate'      : mapgen.make_map_badlands,
        'map_color'     : libtcod.Color(96, 96, 96),
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
            'consumables_1':35,
            'gems_1':10,
            'tomes_1':4,
            'keys_1':1,
            'charms_1':5
        },
        'loot_dice':'1d4',
        'encounter_dice':'1d4+5',
        'xp_amount':7,
        'encounter_range':7,
        'monsters':[
            {'encounter':['monster_cockroach'], 'party':'2d2+2'},
            {'encounter':['monster_centipede']},
            {'encounter':['monster_reeker'],'party':'1d2'},
            {'encounter':['monster_tunnel_spider']},
            {'encounter':['monster_bomb_beetle'],'party':'1d2'},
            {'encounter':['monster_marsh_hunter']},
            {'encounter':['monster_cockroach'], 'party':'3d2'},
            {'encounter':['monster_giant_frog']},
            {'encounter':['monster_alligator']},
            {'encounter':['monster_verman']},
            {'encounter':['monster_cockroach','monster_centipede','monster_bomb_beetle'],'party':'2d3'},
            {'encounter':['monster_infested_treant']},
        ],
        'generate':mapgen.make_map_marsh,
        'map_color'     : libtcod.Color(255, 191, 0),
    },
    'gtunnels': {
        'name'          : 'the goblin tunnels',
        'default_wall'  : 'tunnel wall',
        'default_floor' : 'tunnel floor',
        'default_ramp'  : 'tunnel ramp',
        'terrain_types' : ['tunnel floor','tunnel floor','shallow water','mud'],
        'scaling'       : 0,
        'generate'      : mapgen.make_map_gtunnels,
        'map_color'     : libtcod.dark_orange,
        'encounter_dice':'1d4+5',
        'xp_amount':7,
        'loot_level':1,
        'loot':{
            'armor_2':25,
            'weapons_2':20,
            'consumables_1':35,
            'gems_1':10,
            'tomes_1':4,
            'keys_1':1,
            'charms_1':5
        },
        'loot_dice':'2d3',
        'encounter_range':3,
        'monsters':[
            {'encounter':['monster_goblin'], 'party':'1d2+1'},
            {'encounter':['monster_goblin_warrior'],},
            {'encounter':['monster_tunnel_spider']},
            {'encounter':['monster_bear']},
            {'encounter':['monster_goblin','monster_goblin_warrior'],'party':'2d3'},
        ],
    },
    'forest': {
        'name'          :"the frozen forest",
        'default_wall'  : 'pine tree',
        'default_floor' : 'snowy ground',
        'default_ramp'  : 'snowy slope',
        'scaling'       : 0,
        'loot':{
            'armor_1':25,
            'weapons_1':20,
            'consumables_1':35,
            'gems_1':10,
            'tomes_1':4,
            'keys_1':1
        },
        'loot_level':2,
        'loot_dice':'1d4',
        'encounter_dice':'1d4+5',
        'xp_amount':7,
        'encounter_range':4,
        'monsters':[
            {'encounter':['monster_wolf']},
            {'encounter':['monster_wolf'], 'party':'1d2+2'},
            {'encounter':['monster_silencer']},
            {'encounter':['monster_witch']},
            {'encounter':['monster_nosferatu']},
        ],
        'generate':mapgen.make_map_forest,
        'map_color'     : libtcod.darkest_sky,
    },
    'garden': {
        'name'          :"the gardens",
        'default_wall'  : 'stone wall',
        'default_floor' : 'stone floor',
        'default_ramp'  : 'stone ramp',
        'scaling'       : 0,
        'loot':{},
        'loot_level':0,
        'loot_dice':'1d4',
        'encounter_dice':'1d4+5',
        'xp_amount':7,
        'encounter_range':6,
        'monsters':[

        ],
        'generate':mapgen.make_map_garden,
        'map_color'     : libtcod.darker_green,
    },
    'grotto': {
        'name'          :"pilgrim's grotto",
        'default_wall'  : 'sea cliff',
        'default_floor' : 'sand',
        'default_ramp'  : 'shale slope',
        'scaling'       : 0,
        'loot'          : None,
        'monsters'      : None,
        'generate'      : mapgen.make_map_grotto,
        'map_color'     : libtcod.dark_sea,
    }
}