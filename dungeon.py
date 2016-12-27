import libtcodpy as libtcod

table = {
    'dungeon_1': {
        'loot_profile':'early',
        'versions':[
            { 'weight': 30, 'spawns': {'monster_goblin': [0,1]}},
            { 'weight': 10, 'spawns': {'monster_cockroach': [4,7]}},
            { 'weight': 20, 'spawns': {'monster_tunnel_spider': [1,1]}},
            { 'weight': 30, 'spawns': {'monster_reeker': [1,1]}},
            { 'weight': 15, 'spawns': {'monster_giant_frog': [1,1]}},
            { 'weight': 15, 'spawns': {'monster_centipede': [1,1]}},
            { 'weight': 30, 'spawns': {'monster_goblin_warrior': [1,1]}},
            { 'weight': 5, 'spawns': {'monster_goblin': [2,3]}},
            { 'weight': 5, 'spawns': {'monster_bomb_beetle': [1,1]}},
            { 'weight': 10, 'spawns': {'monster_bear':[1,1]} },
        ]
    },
    'dungeon_2': {
        'loot_profile':'early',
        'versions': [
            { 'weight': 55, 'spawns': {'monster_goblin': [0,2]}},
            { 'weight': 15, 'spawns': {'monster_goblin': [3,5]}},
            { 'weight': 10, 'spawns': {'monster_golem': [1,1]}},
            { 'weight': 25, 'spawns': {'monster_verman': [1,1]}},
            { 'weight': 10, 'spawns': {'monster_bear':[1,1]} }
        ]
    },
    'dungeon_3': {
        'loot_profile':'early',
        'versions': [
            {'weight': 55, 'spawns': {'monster_goblin': [0, 2]}},
            {'weight': 15, 'spawns': {'monster_goblin': [3, 5]}},
            {'weight': 10, 'spawns': {'monster_golem': [1, 1], 'monster_goblin': [0, 3]}},
            { 'weight': 25, 'spawns': {'monster_verman': [1,1]}}
        ]
    },
}

bosses = {
    'monster_nosferatu': { 'dungeon_2':15, 'dungeon_3':15, 'dungeon_4':15, 'dungeon_5':20 }
}