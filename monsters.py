import game as main
import ai
import libtcodpy as libtcod
import pathfinding
import combat
import actions

# Monster Flags
NO_CORPSE = 1

proto = {
    'monster_goblin': {
        'name': 'goblin lurker',
        'char': 'g',
        'color': libtcod.desaturated_green,
        'hp': 20,
        'strength_dice' : '3d6',
        'attack_bonus' : 0,
        'armor': 1,
        'evasion': 9,
        'accuracy': 18,
        'move_speed': 0.8,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Small vicious humanoid. Dangerous in groups.',
        'resistances': [],
        'shred': 1,
        'modifier_category':'goblin',
        'subtype':'goblin',
    },
    'monster_cockroach': {
        'name': 'cockroach',
        'char': 'r',
        'color': libtcod.dark_red,
        'body_type': 'insect',
        'hp': 1,
        'strength_dice' : '2d6',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 19,
        'move_speed': 1.0,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'An irritating, crawling insect. Easily defeated, but a nuisance nonetheless.',
        'resistances': [],
        'shred': 1,
        'subtype':'insect',
    },
    'monster_centipede': {
        'name': 'centipede',
        'char': 'c',
        'color': libtcod.flame,
        'body_type': 'insect',
        'hp': 25,
        'strength_dice' : '2d6',
        'attack_bonus' : 2,
        'armor': 0,
        'evasion': 6,
        'accuracy': 19,
        'move_speed': 1.0,
        'attack_speed': 1.0,
        'difficulty': 1,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Many-legged arthropod with a stinging bite that amplifies damage taken.',
        'resistances': [],
        'on_hit': main.centipede_on_hit,
        'shred': 2,
        'subtype':'insect',
    },
    'monster_rotting_zombie': {
        'name': 'rotting zombie',
        'char': 'z',
        'color': libtcod.dark_chartreuse,
        'hp': 45,
        'strength_dice' : '2d8',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 4,
        'accuracy': 19,
        'move_speed': 0.5,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'A rotting corpse animated by some evil magic. It shambles slowly, but once it reaches its prey it latches on tight.',
        'resistances': [],
        'weaknesses' : ['radiant'],
        'on_hit': main.zombie_on_hit,
        'shred': 1,
        'flags' : NO_CORPSE,
        'modifier_category':'default',
        'subtype':'undead',
    },
    'monster_goblin_warrior': {
        'name': 'goblin warrior',
        'char': 'g',
        'color': libtcod.gray,
        'hp': 20,
        'strength_dice' : '3d6',
        'attack_bonus' : 0,
        'armor': 1,
        'evasion': 9,
        'accuracy': 23,
        'move_speed': 0.8,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Small vicious humanoid that scavenged some equipment.',
        'resistances': [],
        'equipment': [{'weapon_dagger':50,'weapon_longsword':50},{'none':50,'equipment_shield':50},{'none':50,'equipment_leather_armor':50}],
        'shred': 1,
        'modifier_category':'goblin',
        'subtype':'goblin',
    },
    'monster_snow_kite': {
        'name': 'snow kite',
        'char': 'k',
        'color': libtcod.lightest_azure,
        'hp': 36,
        'strength_dice' : '3d8',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 12,
        'accuracy': 24,
        'move_speed': 1.25,
        'attack_speed': 1.0,
        'ai': ai.AI_Default,
        'body_type': 'avian',
        'description': 'A predatory bird with white plumage flecked with gray. It glides with grace on chill winds, '
                       'searching for prey with its keen avian eyes.',
        'resistances': [],
        'essence': [(50, 'cold')],
        'shred': 1,
        'subtype':'beast',
        'movement_type': pathfinding.FLYING
    },
    'monster_goblin_chief': {
        'name': 'goblin chief',
        'char': 'g',
        'color': libtcod.dark_yellow,
        'hp': 30,
        'strength_dice' : '3d6',
        'attack_bonus' : 10,
        'armor': 2,
        'evasion': 9,
        'accuracy': 23,
        'move_speed': 0.9,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Slightly larger, much more vicious humanoid that tells other goblins what to do.',
        'resistances': [],
        'equipment': [{'weapon_spear':50,'weapon_longsword':50},{'none':50,'equipment_shield':50},{'equipment_leather_armor':100}],
        'shred': 1,
        'modifier_category':'goblin',
        'subtype':'goblin',
    },
    'monster_bomb_beetle': {
        'name': 'bomb beetle',
        'char': 'b',
        'color': libtcod.light_sepia,
        'body_type': 'insect',
        'hp': 15,
        'strength_dice' : '2d6',
        'attack_bonus' : 0,
        'armor': 3,
        'evasion': 6,
        'accuracy': 22,
        'move_speed': 0.9,
        'attack_speed': 1.5,
        'death_function' : main.bomb_beetle_death,
        'ai': ai.AI_Default,
        'description': 'A round brown beetle. A warm glow emanates from beneath its carapace.',
        'resistances': [],
        'essence': [(50, 'fire')],
        'subtype':'insect',
    },
    'monster_giant_frog': {
        'name': 'giant frog',
        'char': 'f',
        'color': libtcod.lime,
        'hp': 35,
        'strength_dice' : '2d4',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 10,
        'accuracy': 21,
        'move_speed': 1.0,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Unusually large amphibian that dwells in lakes and ponds. '
                       'Can grab unwary adventurers with its sticky tongue.',
        'resistances': [],
        'attributes':['ability_grapel'],
        'essence': [(10, 'water'), (10, 'life')],
        'subtype':'beast',
        'movement_type': pathfinding.NORMAL | pathfinding.AQUATIC
    },
    'monster_necroling': {
        'name': 'necroling',
        'char': 'n',
        'color': libtcod.dark_violet,
        'hp': 35,
        'strength_dice' : '3d8',
        'attack_bonus' : 10,
        'armor': 2,
        'evasion': 12,
        'accuracy': 19,
        'move_speed': 0.9,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': "A giant segmented worm covered in bony scales and reeking of death. It is drawn to fresh "
                       "corpses, animating them by means of some dark magic.",
        'resistances': [],
        'attributes':['ability_raise_zombie'],
        'essence': [(15, 'dark')],
        'flags' : NO_CORPSE,
        'subtype':'undead',
    },
    'monster_verman': {
        'name': 'verman',
        'char': 'v',
        'color': libtcod.amber,
        'hp': 30,
        'strength_dice' : '1d8',
        'attack_bonus' : 4,
        'armor': 1,
        'evasion': 13,
        'accuracy': 21,
        'move_speed': 0.5,
        'attack_speed': 1.8,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': "A filthy rat-faced humanoid clad with ragged scraps of leather. "
                       "The vermin of the dungeon are drawn to his stench.",
        'resistances': [],
        'attributes':['ability_summon_vermin'],
        'shred': 1,
        'essence': [(10, 'earth')],
        'subtype':'beast',
    },
    'monster_reeker': {
        'name': 'reeker',
        'char': 24,
        'color': libtcod.light_fuchsia,
        'body_type': 'plant',
        'hp': 45,
        'strength_dice' : '0d0',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 0,
        'on_create': None,
        'ai': ai.AI_Reeker,
        'description': 'A short, stocky fungus that emits puffs of foul-smelling gas.',
        'weaknesses' : ['fire'],
        'resistances': ['confusion', 'stunned'],
        'essence': [(65, 'life')],
        'flags' : NO_CORPSE,
        'subtype':'plant',
    },
    'monster_blastcap': {
        'name': 'blastcap',
        'char': 5,
        'color': libtcod.gold,
        'body_type': 'plant',
        'hp': 1,
        'strength_dice' : '0d0',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 0,
        'on_create': None,
        'description': 'A volatile yellow fungus covered in softly glowing nodules. If disrupted, it bursts in a '
                       'deafening crack, stunning anything adjacent (but not diagonally) for several turns.',
        'resistances': ['confusion', 'stunned'],
        'death_function': main.blastcap_explode,
        'subtype':'plant',
        'team' : 'neutral'
    },
    'monster_golem': {
        'name': 'golem',
        'char': 'G',
        'color': libtcod.sepia,
        'hp': 100,
        'strength_dice' : '1d20',
        'attack_bonus' : 20,
        'armor': 7,
        'evasion': 5,
        'accuracy': 19,
        'move_speed': 0.5,
        'attack_speed': 0.5,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'Large stone golem, animated by magic. Slow but very strong.',
        'resistances': ['stun','fire','burn'],
        'shred': 2,
        'essence': [(70, 'earth')],
        'flags' : NO_CORPSE,
        'subtype':'construct',
    },
    'monster_alligator': {
        'name': 'alligator',
        'char': 'A',
        'color': libtcod.dark_green,
        'hp': 40,
        'strength_dice' : '1d12',
        'attack_bonus' : 5,
        'armor': 2,
        'evasion': 2,
        'accuracy': 10,
        'move_speed': 0.85,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'A hunting alligator. Moves swiftly in the water. Its rending teath are especially dangerous for '
                       'unarmored adventurers.',
        'weaknesses': ['ice','freeze'],
        'attributes': ['attribute_fast_swimmer','attribute_rend'],
        'shred': 1,
        'subtype':'beast',
        'body_type':'beast'
    },
    'monster_bear': {
        'name': 'cave bear',
        'char': 'B',
        'color': libtcod.sepia,
        'hp': 50,
        'strength_dice' : '2d20',
        'attack_bonus' : 0,
        'armor': 2,
        'evasion': 6,
        'accuracy': 15,
        'move_speed': 0.85,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'A rudely awakened cave bear',
        'resistances': ['ice','freeze'],
        'attributes': ['ability_berserk'],
        'body_type':'beast',
        'shred': 2,
        'subtype':'beast',
    },
    'monster_tunnel_spider': {
        'name': 'tunnel spider',
        'char': 's',
        'color': libtcod.gray,
        'body_type': 'insect',
        'hp': 28,
        'strength_dice' : '2d6',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 12,
        'accuracy': 22,
        'move_speed': 1.6,
        'attack_speed': 1.0,
        'on_create': main.tunnel_spider_spawn_web,
        'ai': ai.AI_TunnelSpider,
        'description': 'An arachnid who hunts by trapping hapless prey in its webs. Fast, but fragile.',
        'resistances': [],
        'shred': 1,
        'subtype':'insect',
    },
    'monster_witch': {
        'name': 'witch',
        'char': 'w',
        'color': libtcod.dark_purple,
        'hp': 20,
        'strength_dice' : '2d4',
        'attack_bonus' : 0,
        'spell_power' : 10,
        'armor': 1,
        'evasion': 10,
        'accuracy': 50,
        'move_speed': 0.8,
        'attack_speed': 1.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'description': 'A servant of dark magic',
        'resistances': ['dark','madness'],
        'attributes': ['ability_fireball'],
        'essence': [(15, 'fire'),(10, 'arcane')],
        'shred': 0,
        'equipment': [{'none':30,'weapon_dagger':30,'weapon_messer':30},{'none':90,'book_lesser_fire':10},{'equipment_witch_hat':100}],
        'subtype':'human',
    },
    'monster_wolf': {
        'name': 'tundra wolf',
        'char': 'w',
        'color': libtcod.gray,
        'hp': 35,
        'strength_dice' : '3d6',
        'attack_bonus' : 2,
        'armor': 1,
        'evasion': 10,
        'accuracy': 20,
        'move_speed': 1.1,
        'attack_speed': 1.0,
        'ai': ai.AI_Default,
        'description': 'A great gray wolf. Hunts in packs.',
        'resistances': [],
        'shred': 1,
        'modifier_category':'beast',
        'subtype':'beast',
    },
    'monster_silencer': {
        'name': 'corvid silencer',
        'char': 'c',
        'color': libtcod.darkest_grey,
        'hp': 40,
        'strength_dice' : '3d6',
        'attack_bonus' : 0,
        'armor': 1,
        'evasion': 20,
        'accuracy': 25,
        'move_speed': 1.0,
        'attack_speed': 1.5,
        'ai': ai.AI_Default,
        'body_type': 'avian',
        'description': 'A small raven-headed humanoid. '
                       'Silencers hunt rogue wizards, and can hide themselves from sight with magic.',
        'resistances': [],
        'loot_level':3,
        'equipment': [{'weapon_katar':10,'weapon_dagger':30,'weapon_messer':30},{'equipment_leather_armor':50,'equipment_cloth_robes':50}],
        'attributes': ['ability_silence'],
        'shred': 1,
        'stealth':4,
        'modifier_category':None,
        'subtype':'humanoid',
    },
    'monster_nosferatu': {
        'name': 'Nosferatu',
        'char': 'N',
        'color': libtcod.purple,
        'hp': 150,
        'strength_dice' : '2d10',
        'attack_bonus' : 20,
        'armor': 5,
        'evasion': 15,
        'accuracy': 22,
        'move_speed': 1.0,
        'attack_speed': 2.0,
        'on_create': None,
        'ai': ai.AI_Default,
        'attributes': {'perk_flying', 'ability_warp_weapon', 'ability_blink'},
        'description': 'Ancient vampire and servant to a dark god. Fast and dangerous in melee combat.',
        'resistances': [],
        'shred': 3,
        'essence': [(15, 'fire')],
        'subtype':'undead',
    },
    'monster_fire_elemental': {
        'name': 'fire elemental',
        'char': 'E',
        'color': libtcod.flame,
        'hp': 32,
        'strength_dice' : '3d8',
        'attack_bonus' : 0,
        'armor': 1,
        'evasion': 12,
        'accuracy': 22,
        'move_speed': 1.0,
        'attack_speed': 1.8,
        'ai': ai.AI_Default,
        'description': 'A roaring vortex of living flame. '
                       'It fights with searing fury, leaving its victims charred and burned',
        'resistances': ['fire'],
        'shred': 3,
        'subtype':'elemental',
        'on_hit': combat.on_hit_burn
    },
    'monster_earth_elemental': {
        'name': 'earth elemental',
        'char': 'E',
        'color': libtcod.sepia,
        'hp': 80,
        'strength_dice' : '2d12',
        'attack_bonus' : 0,
        'armor': 5,
        'evasion': 8,
        'accuracy': 20,
        'move_speed': 0.5,
        'attack_speed': 0.5,
        'ai': ai.AI_Default,
        'description': 'A form of stone, sand, and soil given life. '
                       'Attacks hardly phase it as it lumbers steadily forward.',
        'resistances': ['earth'],
        'shred': 2,
        'subtype':'elemental',
    },
    'monster_air_elemental': {
        'name': 'air elemental',
        'char': 'E',
        'color': libtcod.light_sky,
        'hp': 36,
        'strength_dice' : '2d8',
        'attack_bonus' : 0,
        'armor': 1,
        'evasion': 18,
        'accuracy': 24,
        'move_speed': 2.2,
        'attack_speed': 1.2,
        'ai': ai.AI_Default,
        'description': 'A playful spirit made of whirling gusts of wind. '
                       'It moves swiftly, leaving swirling dust and leaves in its wake.',
        'resistances': ['air'],
        'shred': 1,
        'subtype':'elemental',
        'movement_type' : pathfinding.FLYING
    },
    'monster_water_elemental': {
        'name': 'water elemental',
        'char': 'E',
        'color': libtcod.azure,
        'hp': 55,
        'strength_dice' : '3d4',
        'attack_bonus' : 0,
        'armor': 2,
        'evasion': 12,
        'accuracy': 16,
        'move_speed': 1.0,
        'attack_speed': 1.0,
        'ai': ai.AI_Default,
        'description': 'An amorphous being of pure water. '
                       'Anything caught in its flows will struggle to move or evade attacks.',
        'resistances': ['water'],
        'shred': 2,
        'subtype':'elemental',
        'movement_type' : pathfinding.AQUATIC | pathfinding.NORMAL,
        'on_tick' : main.water_elemental_tick
    },
    'monster_ice_elemental': {
        'name': 'ice elemental',
        'char': 'E',
        'color': libtcod.lightest_azure,
        'hp': 20,
        'strength_dice' : '3d8',
        'attack_bonus' : 10,
        'armor': 3,
        'evasion': 12,
        'accuracy': 18,
        'move_speed': 1.0,
        'attack_speed': 1.0,
        'ai': ai.AI_Default,
        'description': 'A frigid creature made of blue glacial ice. '
                       'Heat drains away in its presence, leaving an aura of winter in its absence.',
        'resistances': ['cold'],
        'shred': 2,
        'pierce': 1,
        'subtype':'elemental',
    },
    'monster_lifeplant': {
        'name': 'lifeplant',
        'char': chr(5),
        'color': libtcod.green,
        'hp': 60,
        'body_type': 'plant',
        'strength_dice' : '0d0',
        'attack_bonus' : 0,
        'armor': 0,
        'evasion': 0,
        'accuracy': 0,
        'move_speed': 1.0,
        'attack_speed': 1.0,
        'ai': ai.AI_Lifeplant,
        'description': 'A twisting, climbing vine adorned with golden flowers. '
                       'It glows with a soft warmth - those close enough to touch'
                       ' it can feel that warmth flow through them, healing their wounds.',
        'resistances': [],
        'shred': 3,
        'subtype':'plant',
    },
    'monster_arcane_construct': {
        'name': 'arcane construct',
        'char': 'A',
        'color': libtcod.fuchsia,
        'hp': 20,
        'strength_dice' : '0d0',
        'attack_bonus' : 0,
        'spell_power' : 8,
        'armor': 1,
        'evasion': 16,
        'accuracy': 26,
        'move_speed': 1.0,
        'attack_speed': 0.4,
        'ai': ai.AI_Default,
        'attributes': ['ability_arcane_arrow'],
        'description': 'An artificial construct of glowing geometric shapes and symbols of power, '
                       'vibrating with arcane energy. '
                       'It bombards its enemies with magical energy from a distance.',
        'resistances': ['cold'],
        'shred': 0,
        'subtype':'elemental',
        'movement_type' : pathfinding.FLYING
    },
    'monster_guardian_angel': {
        'name': 'guardian angel',
        'char': 'A',
        'color': libtcod.light_yellow,
        'hp': 50,
        'strength_dice' : '3d8',
        'attack_bonus' : 0,
        'spell_power': 50,
        'armor': 3,
        'evasion': 12,
        'accuracy': 25,
        'move_speed': 1.0,
        'attack_speed': 1.8,
        'ai': ai.AI_Default,
        'attributes': ['ability_smite'],
        'description': 'A mighty warrior angel in radiant golden armor.',
        'resistances': ['radiant','dark'],
        'shred': 2,
        'subtype':'angel',
        'loot_level':15,
        'equipment': [{'weapon_greatsword':30,'weapon_halberd':30,'weapon_warhammer':30},{'equipment_plate_armor':100}],
        'movement_type': pathfinding.FLYING
    },
    'monster_infested_treant': {
        'name': 'infested treant',
        'char': 'T',
        'color': libtcod.dark_magenta,
        'hp': 180,
        'strength_dice' : '4d10',
        'attack_bonus' : 0,
        'armor': 4,
        'evasion': 4,
        'accuracy': 22,
        'move_speed': 1.0,
        'attack_speed': 0.6,
        'ai': ai.AI_Default,
        'description': 'A walking hulk of rotting wood, crawling with roaches.',
        'resistances': [],
        'weaknesses' : ['fire'],
        'on_get_hit' : actions.summon_roaches,
        'shred': 1,
        'flags' : NO_CORPSE,
        'subtype' : 'treant',
    },
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
    },
    'alpha' : {
        'hp_bonus':1.25,
        'damage_bonus':1.25
    },
    'starved' : {
        'hp_bonus':0.8,
        'evasion_bonus':0.5
    },
    'lithe' : {
        'speed_bonus':1.25,
        'evasion_bonus':0.5
    },
    'scarred' : {
        'hp_bonus':1.5
    },
    'dire' : {
        'hp_bonus':1.5,
        'damage_bonus':1.5,
        'shred_bonus':1
    }
}

modifier_categories = {
    'default'   : {'brawny':1,'wimpy':1,'crazed':1,'mild':1,'nimble':1,'lethargic':1,'cursed':1},
    'goblin'    : {'brawny':2,'wimpy':3,'crazed':2,'nimble':2,'lethargic':3,'cursed':2,'chosen of splug':1,'greased up':1,'adventurous':2},
    'beast'     : {'brawny':1,'wimpy':1,'alpha':1,'starved':1,'lithe':1,'scarred':1,'dire':1},
}