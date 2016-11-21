import game as main
import libtcodpy as libtcod

proto = {
    'monster_goblin': {
        'name': 'Goblin Lurker',
        'char': 'g',
        'color': libtcod.desaturated_green,
        'hp': 20,
        'attack_damage': 10,
        'armor': 5,
        'evasion': 15,
        'accuracy': 0.65,
        'speed': 0.8,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai' : main.AI_Default,
        'description': 'Small vicious humanoid. Dangerous in groups.'
    },
    'monster_golem': {
        'name': 'Golem',
        'char': 'G',
        'color': libtcod.sepia,
        'hp': 100,
        'attack_damage': 30,
        'armor': 50,
        'evasion': 5,
        'accuracy': 0.5,
        'speed': 0.5,
        'difficulty': 3,
        'loot': 'default',
        'on_create': None,
        'ai' : main.AI_Default,
        'description': 'Large stone golem, animated by magic. Slow but very strong.'
    },
    'monster_tunnel_spider': {
        'name': 'Tunnel Spider',
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
        'on_create': main.make_spiderweb,
        'ai' : main.AI_TunnelSpider,
        'description': 'An arachnid who hunts by trapping hapless prey in its webs. Fast, but fragile.'
    },
    'monster_nosferatu': {
        'name': 'Nosferatu',
        'char': 'N',
        'color': libtcod.purple,
        'hp': 100,
        'attack_damage': 65,
        'armor': 40,
        'evasion': 50,
        'accuracy': 0.70,
        'speed': 1,
        'difficulty': 12,
        'loot': 'default',#'boss_undead',
        'on_create': None,
        'ai' : main.AI_Default,
        'attributes': {'flying': 'always', 'spell_warp_weapon': 20, 'spell_blink': 10},
        'description': 'Ancient vampire and servant to a dark god. Fast and dangerous in melee combat.'
    }
}