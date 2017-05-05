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
import effects
import actions

class Spell:
    def __init__(self, name, function, description, levels, int_requirement = 10, cast_time=0):
        self.name = name
        self.function = function
        self.description = description
        self.levels = levels
        self.int_requirement = int_requirement
        self.max_level = len(levels)

    def max_spell_charges(self,level):
        import game
        base = self.levels[level-1]['charges']
        return int(base + base * game.skill_value('sorcery'))

def is_max_level(spell,level):
    return len(library[spell].levels) == level

charm_shard_of_creation = {
    'life': {
        'name': 'Create grass',
        'description' : 'Create a patch of grass'
    },
    'earth': {
        'name': 'Create stone walls',
        'description' : 'Create a stone wall'
    },
    'water': {
        'name': 'Create pool',
        'description' : 'Create a pool of water'
    },
    'fire': {
        'name': 'Create lava',
        'description' : 'Create a pit of lava'
    },
}

charm_volatile_orb = {
    'fire': {
        'name': 'Fire bomb',
        'description': 'Deal damage and set fires in an area'
    },
    'cold': {
        'name': 'Ice Bomb',
        'description' : 'Deal damage and freeze enemies in an area'
    },
    'arcane': {
        'name': 'Time bomb',
        'description' : 'Create a time bomb, which explodes after a time'
    },
}

charm_farmers_talisman = {
    'life': {
        'name': 'Lifeplant',
        'description' : 'Summon a life plant, which heals all units adjacent to it'
    },
    'earth': {
        'name': 'Dig',
        'description' : 'Dig out a tile'
    },
}

charm_holy_symbol = {
    'life': {
        'name': 'Mass Heal',
        'description' : 'Heal yourself and all nearby allies, and give all targets a regeneration buff'
    },
    'water': {
        'name': 'Mass Cleanse',
        'description' : 'Remove all negative effects from yourself and nearby allies'
    },
    'radiance': {
        'name': 'Mass Reflect',
        'description': 'Protects you and nearby allies from magical harm by returning spells to their casters.'
    }
}

charm_primal_totem = {
    'fire': {
        'name': 'Berserk Self',
        'description': 'You gain attack power for a time but will be exhausted when it ends'
    },
    'air': {
        'name': 'Battle Cry',
        'description': 'Alert all enemies in a wide area, but reduce their defense'
    },
    'death': {
        'name': 'Soul Reaper',
        'description': 'Summon a Soul Reaper weapon for a time, which raises those it slays as zombies'
    },
}

charm_raw_effects = {
    'fire': {
        'name': 'Ignite',
        'description':'Create a fire on a space'
    },
    'earth': {
        'name' : 'Hardness',
        'description':'Instantly repair your armor and gain an armor boost'
    },
    'air': {
        'name' : 'Wind Step',
        'description':'Effortlessly jump to another space'
    },
    'water': {
        'name' : 'Cleanse',
        'description':'Clear yourself of harmfull effects'
    },
    'life': {
        'name' : 'Healing',
        'description':'Heal some of your wounds'
    },
    'cold': {
        'name' : 'Freeze',
        'description': "Freeze a target enemy in ice"
    },
    'arcane': { #todo
        'name' : 'Teleport',
        'description': ""
    },
    'radiance': {
        'name' : 'Invulnerability',
        'description': "Become invulnerable to harm"
    },
    'death': {
        'name' : 'Raise Dead',
        'description': "Raise an adjacent corpse as a zombie"
    },
    'void': { #todo
        'name' : '????',
        'description': "????"
    }
}

charm_resist_effects = {
    'fire' : {
        'name' : 'Resist fire and burning',
        'resists' : ['burning'],
    },
    'water' : {
        'name' : 'Resist piercing and exhaustion',
        'resists' : ['exhaustion'],
    },
    'earth' : {
        'name' : 'Resist crushing and stun',
        'resists' : ['stun'],
    },
    'air' : {
        'name' : 'Resist lightning and immobilization',
        'resists' : ['immobilize'],
    },
    'life' : {
        'name' : 'Resist poison',
        'resists' : ['poison'],
    },
    'cold' : {
        'name' : 'Resist cold and freezing',
        'resists' : ['freeze'],
    },
    'death' : {
        'name' : 'Resist death and rot',
        'resists' : ['rot'],
    },
    'arcane' : {
        'name' : 'Resist silence',
        'resists' : ['silence'],
    },
    'radiance' : {
        'name' : 'Resist radiance and judgement',
        'resists' : ['judgement'],
    },
    'void' : {
        'name' : 'Resist void',
        'resists' : [],
    },
}

library = {
    'spell_heat_ray' : Spell(
        'heat ray',
        actions.heat_ray,
        'Fire a ray of magical heat in a line',
        [
            {'stamina_cost':20,'charges':3},
            {'stamina_cost':15,'charges':4},
            {'stamina_cost':10,'charges':5}
        ],
        10),

    'spell_flame_wall' : Spell(
        'flame wall',
        actions.flame_wall,
        'Create a wall of flames',
        [
            {'stamina_cost':40,'charges':1},
            {'stamina_cost':35,'charges':2}
        ],
        10),

    'spell_fireball' : Spell(
        'fireball',
        actions.fireball,
        'Fling an exploding fireball',
        [
            {'stamina_cost':50,'charges':1},
            {'stamina_cost':45,'charges':2},
            {'stamina_cost':40,'charges':2}
        ],
        10),

    'spell_shatter_item' : Spell(
        'shatter item',
        actions.shatter_item,
        'Overheat items to shatter them',
        [
            {'stamina_cost':50,'charges':2}
            ,{'stamina_cost':40,'charges':3}
        ],
        10),

    'spell_magma_bolt' : Spell(
        'magma bolt',
        actions.magma_bolt,
        'Fire a bolt of boiling magma that melts floors',
        [
            {'stamina_cost':60,'charges':2},
            {'stamina_cost':50,'charges':3},
            {'stamina_cost':40,'charges':4}
        ],
        10),

    'spell_frozen_orb' : Spell(
        'frost orb',
        actions.frozen_orb,
        'Fires an orb of frost that slows struck targets.',
        [
            {'stamina_cost':25,'charges':3},
            {'stamina_cost':20,'charges':4},
            {'stamina_cost':15,'charges':5}
        ],
        10),

    'spell_flash_frost' : Spell(
        'flash frost',
        actions.flash_frost,
        'Attempts to freeze a target solid with a burst of magical ice.',
        [
            {'stamina_cost':40,'charges':1},
            {'stamina_cost':40,'charges':2},
        ],
        11),

    'spell_ice_shards' : Spell(
        'ice shards',
        actions.ice_shards,
        'Blasts an area with razor sharp ice shards',
        [
            {'stamina_cost':40,'charges':2},
            {'stamina_cost':35,'charges':3},
            {'stamina_cost':30,'charges':4}
        ],
        12),

    'spell_snowstorm' : Spell(
        'snowstorm',
        actions.snowstorm,
        'Summons a whirling ice storm, which inhibits movement and sight.',
        [
            {'stamina_cost':45,'charges':1},
            {'stamina_cost':35,'charges':2}
        ],
        14),

    'spell_avalanche' : Spell(
        'avalanche',
        actions.magma_bolt,
        'Summons an avalanche to bury your enemies.',
        [
            {'stamina_cost':70,'charges':1},
            {'stamina_cost':45,'charges':1},
            {'stamina_cost':45,'charges':2}
        ],
        16),

    'spell_hex' : Spell(
        'hex',
        actions.hex,
        'Curse a target, decreasing its armor, spell resist and evasion',
        [
            {'stamina_cost':25,'charges':3},
            {'stamina_cost':20,'charges':4},
            {'stamina_cost':15,'charges':5}
        ],
        8
    ),

    'spell_defile' : Spell(
        'defile',
        actions.defile,
        'Raise a corpse as a zombie, heal undead, or damage the living',
        [
            {'stamina_cost':35,'charges':2},
            {'stamina_cost':30,'charges':3},
            {'stamina_cost':25,'charges':4}
        ],
        10
    ),

    'spell_shackles_of_the_dead' : Spell(
        'shackles of the dead',
        actions.shackles_of_the_dead,
        'Curse a target, decreasing its armor, spell resist and evasion',
        [
            {'stamina_cost':40,'charges':1},
            {'stamina_cost':30,'charges':2},
        ],
        11
    ),

    'spell_sacrifice' : Spell(
        'sacrifice',
        actions.sacrifice,
        "Sacrifice a portion of your remaining hp to deal damage to nearby enemies based on your missing hp",
        [
            {'stamina_cost':25,'charges':2},
            {'stamina_cost':20,'charges':3},
        ],
        12
    ),

    'spell_corpse_dance' : Spell(
        'corpse dance',
        actions.corpse_dance,
        'Raises all corpses in an area as undead and fills them with unholy fury.',
        [
            {'stamina_cost':60,'charges':1},
            {'stamina_cost':40,'charges':1},
            {'stamina_cost':40,'charges':2}
        ],
        13
    ),
}

essence_colors = {
    'normal' : libtcod.gray,
    'life' : libtcod.green,
    'fire' : libtcod.flame,
    'earth' : libtcod.sepia,
    'death' : libtcod.dark_violet,
    'water' : libtcod.azure,
    'air' : libtcod.light_sky,
    'cold' : libtcod.lightest_gray,
    'radiance' : libtcod.lighter_yellow,
    'arcane' : libtcod.fuchsia,
    'void' : libtcod.darker_crimson
}