import game as main
import ai
import libtcodpy as libtcod

proto = {
    'monster_goblin': {
        'name': 'goblin lurker',
        'char': 'g',
        'color': libtcod.desaturated_green,
        'hp': 20,
        'attack_damage': 10,
        'armor': 1,
        'evasion': 9,
        'accuracy': 18,
        'speed': 0.8,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Small vicious humanoid. Dangerous in groups.',
        'resistances': [],
        'shred': 1,
        'modifier_category':'goblin'
    },
    'monster_cockroach': {
        'name': 'cockroach',
        'char': 'r',
        'color': libtcod.dark_red,
        'body_type': 'insect',
        'hp': 1,
        'attack_damage': 6,
        'armor': 0,
        'evasion': 0,
        'accuracy': 19,
        'speed': 1,
        'difficulty': 0,
        'loot': 'none',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'An irritating, crawling insect. Easily defeated, but a nuisance nonetheless.',
        'resistances': [],
        'shred': 1,
    },
    'monster_centipede': {
        'name': 'centipede',
        'char': 'c',
        'color': libtcod.flame,
        'body_type': 'insect',
        'hp': 18,
        'attack_damage': 12,
        'armor': 0,
        'evasion': 6,
        'accuracy': 19,
        'speed': 1,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Many-legged arthropod with a stinging bite that amplifies damage taken.',
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
        'evasion': 9,
        'accuracy': 23,
        'speed': 0.8,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Small vicious humanoid that scavenged some equipment.',
        'resistances': [],
        'equipment': [{'weapon_dagger':50,'weapon_longsword':50},{'none':50,'equipment_shield':50},{'none':50,'equipment_leather_armor':50}],
        'shred': 1,
        'modifier_category':'goblin'
    },
    'monster_goblin_chief': {
        'name': 'goblin chief',
        'char': 'g',
        'color': libtcod.dark_yellow,
        'hp': 30,
        'attack_damage': 15,
        'armor': 3,
        'evasion': 9,
        'accuracy': 23,
        'speed': 0.8,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Slightly larger, much more vicious humanoid that tells other goblins what to do.',
        'resistances': [],
        'equipment': [{'weapon_spear':50,'weapon_longsword':50},{'none':50,'equipment_shield':50},{'equipment_leather_armor':100}],
        'shred': 1,
        'modifier_category':'goblin'
    },
    'monster_bomb_beetle': {
        'name': 'bomb beetle',
        'char': 'b',
        'color': libtcod.light_sepia,
        'body_type': 'insect',
        'hp': 15,
        'attack_damage': 6,
        'armor': 3,
        'evasion': 6,
        'accuracy': 22,
        'speed': 0.9,
        'difficulty': 1,
        'loot': 'default',
        'death_function' : main.bomb_beetle_death,
        'ai': ai.AI_Default,
        'description': 'A round brown beetle. A warm glow emanates from beneath its carapace.',
        'resistances': [],
        'essence': [(50, 'fire')]
    },
    'monster_giant_frog': {
        'name': 'giant frog',
        'char': 'f',
        'color': libtcod.lime,
        'hp': 25,
        'attack_damage': 5,
        'armor': 0,
        'evasion': 10,
        'accuracy': 21,
        'speed': 1.0,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Unusually large amphibian that dwells in lakes and ponds. '
                       'Can grab unwary adventurers with its sticky tongue.',
        'resistances': [],
        'attributes':['ability_grapel'],
        'essence': [(10, 'water'), (10, 'life')]
    },
    'monster_verman': {
        'name': 'verman',
        'char': 'v',
        'color': libtcod.amber,
        'hp': 30,
        'attack_damage': 6,
        'armor': 1,
        'evasion': 13,
        'accuracy': 21,
        'speed': 1.0,
        'difficulty': 2,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': "A filthy rat-faced humanoid clad with ragged scraps of leather. "
                       "The vermin of the dungeon are drawn to his stench.",
        'resistances': [],
        'attributes':['ability_summon_vermin'],
        'shred': 1,
        'essence': [(10, 'earth')]
    },
    'monster_reeker': {
        'name': 'reeker',
        'char': 24,
        'color': libtcod.light_fuchsia,
        'body_type': 'plant',
        'hp': 45,
        'attack_damage': 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 0,
        'speed': 1.0,
        'difficulty': 1,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Reeker,
        'description': 'A short, stocky fungus that emits puffs of foul-smelling gas.',
        'resistances': ['confusion', 'stunned'],
        'essence': [(65, 'life')]
    },
    'monster_blastcap': {
        'name': 'blastcap',
        'char': 5,
        'color': libtcod.gold,
        'body_type': 'plant',
        'hp': 1,
        'attack_damage': 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 0,
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
        'accuracy': 19,
        'speed': 0.5,
        'difficulty': 3,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Large stone golem, animated by magic. Slow but very strong.',
        'resistances': [],
        'shred': 2,
        'essence': [(70, 'earth')]
    },
    'monster_bear': {
        'name': 'cave bear',
        'char': 'B',
        'color': libtcod.sepia,
        'hp': 50,
        'attack_damage': 30,
        'armor': 2,
        'evasion': 6,
        'accuracy': 23,
        'speed': 0.65,
        'difficulty': 3,
        'loot': 'default',
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'A rudely awakened cave bear',
        'resistances': ['ice','freeze'],
        'attributes': ['ability_berserk'],
        'shred': 2
    },
    'monster_tunnel_spider': {
        'name': 'tunnel spider',
        'char': 's',
        'color': libtcod.gray,
        'body_type': 'insect',
        'hp': 20,
        'attack_damage': 6,
        'armor': 0,
        'evasion': 12,
        'accuracy': 22,
        'speed': 1.5,
        'difficulty': 1,
        'loot': 'default',
        'on_create': main.tunnel_spider_spawn_web,
        'ai': ai.AI_TunnelSpider,
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
        'evasion': 15,
        'accuracy': 22,
        'speed': 1,
        'difficulty': 12,
        'loot': 'default',#'boss_undead',
        'on_create': None,
        'ai': ai.AI_Default,
        'attributes': {'perk_flying', 'ability_warp_weapon', 'ability_blink'},
        'description': 'Ancient vampire and servant to a dark god. Fast and dangerous in melee combat.',
        'resistances': [],
        'shred': 3,
        'essence': [(15, 'fire')]
    }
}

modifiers = {
    'brawny' : {
        'hp_bonus' : 1.5
    },
    'wimpy' : {
        'hp_bonus' : 0.5
    },
    'crazed' : {
        'damage_bonus' : 1.5
    },
    'mild' : {
        'damage_bonus' : 0.5
    },
    'nimble' : {
        'evasion_bonus' : 1.5,
        'speed_bonus' : 1.2
    },
    'lethargic' : {
        'evasion_bonus' : 1.5,
        'speed_bonus' : 0.8
    },
    'cursed' : {
        'hp_bonus' : 0.75,
        'evasion_bonus' : 0.75,
        'speed_bonus' : 1.25,
        'damage_bonus' : 1.5
    },
    'chosen of splug' : {
        'damage_bonus' : 1.5,
        'hp_bonus' : 1.75,
        'speed_bonus' : 1.1
    },
    'greased up' : {
        'speed_bonus' : 1.66
    },
    'adventurous' : {
        'hp_bonus': 1.25,
        'resistances' : ['fire','burn','stun']
    }
}

modifier_categories = {
    'default'   : {'brawny':1,'wimpy':1,'crazed':1,'mild':1,'nimble':1,'lethargic':1,'cursed':1},
    'goblin'    : {'brawny':2,'wimpy':3,'crazed':2,'nimble':2,'lethargic':3,'cursed':2,'chosen of splug':1,'greased up':1,'adventurous':2}
}

verman_summons = [
    {'weight' : 25, 'monster' : 'monster_cockroach', 'count' : 2},
    {'weight' : 25, 'monster' : 'monster_cockroach', 'count' : 3},
    {'weight' : 15, 'monster' : 'monster_cockroach', 'count' : 4},
    {'weight' : 15, 'monster' : 'monster_centipede', 'count' : 1},
    {'weight' : 10, 'monster' : 'monster_bomb_beetle', 'count' : 1},
    {'weight' : 10, 'monster' : 'monster_tunnel_spider', 'count' : 1}
]