import libtcodpy as libtcod

table = {
    'dungeon_1': {
        'loot_profile':'early',
        'versions':[
            { 'weight': 50,  'spawns': {'monster_goblin': [6,8], 'encounter_goblin_pack': [1,1]}},
            { 'weight': 50,  'spawns': {'monster_goblin': [6,8]}}
        ]
    },
    'dungeon_2': {
        'loot_profile':'early',
        'versions': [
            { 'weight': 75,  'spawns': {'monster_goblin': [6,8], 'encounter_goblin_pack': [2,2]}},
            { 'weight': 25,  'spawns': {'monster_goblin': [4,6], 'monster_golem': [1,1]}}
        ]
    },
    'dungeon_3': {
        'loot_profile':'early',
        'versions': [
            { 'weight': 34,  'spawns': {'encounter_goblin_pack': [3,5]}},
            { 'weight': 33,  'spawns': {'monster_goblin': [6,8], 'monster_golem': [1,2]}},
            { 'weight': 33,  'spawns': {'encounter_goblin_pack': [2,3], 'monster_golem': [1,2]}}
        ]
    },
}

bosses = {
    'monster_nosferatu': { 'dungeon_2':10, 'dungeon_3':15, 'dungeon_4':15, 'dungeon_5':20 }
}