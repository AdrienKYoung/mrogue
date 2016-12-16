import game as main
import libtcodpy as libtcod

proto = {
    'monster_goblin': {
        'name': 'goblin lurker',
        'char': 'g',
        'color': libtcod.desaturated_green,
        'hp': 20,
        'attack_damage': 10,
        'armor': 1,
        'evasion': 15,
        'accuracy': 0.65,
        'speed': 0.8,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': main.AI_Default,
        'description': 'Small vicious humanoid. Dangerous in groups.',
        'resistances': [],
        'shred': 1
    },
    'monster_cockroach': {
        'name': 'cockroach',
        'char': 'r',
        'color': libtcod.dark_red,
        'hp': 1,
        'attack_damage': 3,
        'armor': 0,
        'evasion': 0,
        'accuracy': 0.85,
        'speed': 1,
        'difficulty': 0,
        'loot': 'none',
        'on_create': None,
        'ai': main.AI_Default,
        'description': 'An irritating, crawling insect. Easily defeated, but a nuisance nonetheless.',
        'resistances': [],
        'shred': 1
    },
    'monster_centipede': {
        'name': 'centipede',
        'char': 'c',
        'color': libtcod.flame,
        'hp': 15,
        'attack_damage': 12,
        'armor': 0,
        'evasion': 5,
        'accuracy': 0.55,
        'speed': 1,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': main.AI_Default,
        'description': 'Many-legged arthropod with a stinging bite that amplifies damage.',
        'resistances': [],
        'on_hit': main.centipede_on_hit,
        'shred': 2
    },
    'monster_goblin_warrior': {
        'name': 'goblin warrior',
        'char': 'g',
        'color': libtcod.gray,
        'hp': 20,
        'attack_damage': 10,
        'armor': 2,
        'evasion': 5,
        'accuracy': 0.65,
        'speed': 0.8,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': main.AI_Default,
        'description': 'Small vicious humanoid that scavenged some equipment.',
        'resistances': [],
        'equipment': [{'equipment_dagger':50,'equipment_longsword':50},{'none':50,'equipment_shield':50},{'none':50,'equipment_leather_armor':50}],
        'shred': 1
    },
    'monster_bomb_beetle': {
        'name': 'bomb beetle',
        'char': 'b',
        'color': libtcod.light_sepia,
        'hp': 15,
        'attack_damage': 4,
        'armor': 3,
        'evasion': 8,
        'accuracy': 0.75,
        'speed': 0.9,
        'difficulty': 1,
        'loot': 'default',
        'death_function' : main.bomb_beetle_death,
        'ai': main.AI_Default,
        'description': 'A round brown beetle. A warm glow emanates from beneath its carapace.',
        'resistances': []
    },
    'monster_giant_frog': {
        'name': 'giant frog',
        'char': 'f',
        'color': libtcod.lime,
        'hp': 25,
        'attack_damage': 4,
        'armor': 0,
        'evasion': 20,
        'accuracy': 0.55,
        'speed': 1.0,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': main.AI_GiantFrog,
        'description': 'Unusually large amphibian that dwells in lakes and ponds. '
                       'Can grab unwary adventurers with its sticky tongue.',
        'resistances': []
    },
    'monster_verman': {
        'name': 'verman',
        'char': 'v',
        'color': libtcod.amber,
        'hp': 35,
        'attack_damage': 6,
        'armor': 1,
        'evasion': 20,
        'accuracy': 0.55,
        'speed': 1.0,
        'difficulty': 2,
        'loot': 'default',
        'on_create': None,
        'ai': main.AI_Verman,
        'description': "A filthy rat-faced humanoid clad with ragged scraps of leather. "
                       "The vermin of the dungeon are drawn to his stench.",
        'resistances': [],
        'shred': 1
    },
    'monster_reeker': {
        'name': 'reeker',
        'char': 24,
        'color': libtcod.light_fuchsia,
        'hp': 45,
        'attack_damage': 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 0.0,
        'speed': 1.0,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': main.AI_Reeker,
        'description': 'A short, stocky fungus that emits puffs of foul-smelling gas.',
        'resistances': ['confusion', 'stunned']
    },
    'monster_blastcap': {
        'name': 'blastcap',
        'char': 5,
        'color': libtcod.gold,
        'hp': 1,
        'attack_damage': 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 0.0,
        'speed': 1.0,
        'difficulty': 0,
        'loot': 'none',
        'on_create': None,
        'description': 'a volatile yellow fungus covered in softly glowing nodules. If disrupted, it bursts in a '
                       'deafening crack, stunning anything adjacent for several turns.',
        'resistances': ['confusion', 'stunned'],
        'death_function': main.blastcap_explode
    },
    'monster_golem': {
        'name': 'golem',
        'char': 'G',
        'color': libtcod.sepia,
        'hp': 100,
        'attack_damage': 30,
        'armor': 7,
        'evasion': 5,
        'accuracy': 0.5,
        'speed': 0.5,
        'difficulty': 3,
        'loot': 'default',
        'on_create': None,
        'ai': main.AI_Default,
        'description': 'Large stone golem, animated by magic. Slow but very strong.',
        'resistances': [],
        'shred': 2
    },
    'monster_tunnel_spider': {
        'name': 'tunnel spider',
        'char': 's',
        'color': libtcod.gray,
        'hp': 16,
        'attack_damage': 6,
        'armor': 0,
        'evasion': 25,
        'accuracy': 0.75,
        'speed': 1.5,
        'difficulty': 1,
        'loot': 'default',
        'on_create': main.tunnel_spider_spawn_web,
        'ai': main.AI_TunnelSpider,
        'description': 'An arachnid who hunts by trapping hapless prey in its webs. Fast, but fragile.',
        'resistances': [],
        'shred': 1
    },
    'monster_nosferatu': {
        'name': 'Nosferatu',
        'char': 'N',
        'color': libtcod.purple,
        'hp': 100,
        'attack_damage': 65,
        'armor': 10,
        'evasion': 50,
        'accuracy': 0.70,
        'speed': 1,
        'difficulty': 12,
        'loot': 'default',#'boss_undead',
        'on_create': None,
        'ai': main.AI_Default,
        'attributes': {'flying': 'always', 'spell_warp_weapon': 20, 'spell_blink': 10},
        'description': 'Ancient vampire and servant to a dark god. Fast and dangerous in melee combat.',
        'resistances': [],
        'shred': 3
    }
}

verman_summons = [
    {'weight' : 25, 'monster' : 'monster_cockroach', 'count' : 2},
    {'weight' : 25, 'monster' : 'monster_cockroach', 'count' : 3},
    {'weight' : 15, 'monster' : 'monster_cockroach', 'count' : 4},
    {'weight' : 15, 'monster' : 'monster_centipede', 'count' : 1},
    {'weight' : 10, 'monster' : 'monster_bomb_beetle', 'count' : 1},
    {'weight' : 10, 'monster' : 'monster_tunnel_spider', 'count' : 1}
]