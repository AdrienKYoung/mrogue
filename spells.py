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

charm_blessing_effects = {
    'fire': {
        'buff':effects.berserk,
        'description':'Drive yourself berserk for a bonus to melee damage'
    },
    'earth': {
        'buff':effects.stoneskin,
        'description':'Turn your skin to stone for a bonus to armor'
    },
    'air': {
        'buff':effects.swiftness,
        'description':'Turn your skin to stone for a bonus to armor'
    },
    'water': {
        'buff':effects.serenity,
        'description':'Turn your skin to stone for a bonus to armor'
    },
    'life': {
        'buff':effects.regeneration,
        'description':'Regenerate your wounds over time.'
    },
    'cold': {
        'buff':effects.regeneration,
        'description': ""
    },
    'arcane': {
        'buff':effects.regeneration,
        'description': ""
    },
    'radiant': {
        'buff':effects.regeneration,
        'description': ""
    },
    'dark': {
        'buff':effects.regeneration,
        'description': ""
    },
    'void': {
        'buff':effects.regeneration,
        'description': ""
    }
}

charm_summoning_summons = {
    'fire': {
        'summon': 'monster_fire_elemental',
        'duration': 15,
        'description':"Summon a fire elemental. It's attacks are deadly, but it won't last long in this world."
    },
    'earth': {
        'summon': 'monster_earth_elemental',
        'duration': 30,
        'description':"Summon an earth elemental. It moves slowly, but is very durable."
    },
    'air': {
        'summon': 'monster_air_elemental',
        'duration': 30,
        'description':"Summon an air elemental. It flies and moves quickly, but inflicts little damage."
    },
    'water': {
        'summon': 'monster_water_elemental',
        'duration': 30,
        'description': "Summon a water elemental. It does not attack, but rather disables nearby foes."
    },
    'life': {
        'summon': 'monster_lifeplant',
        'duration': 15,
        'description': "Summon a lifeplant. It will slowly heal nearby creatures over time."
    },
    'cold': {
        'summon': 'monster_ice_elemental',
        'duration': 30,
        'description': "Summon an ice elemental. It deals heavy damage, but is fragile."
    },
    'arcane': {
        'summon': 'monster_arcane_construct',
        'duration': 30,
        'description': "Summon an Arcane Construct. This artificial can fire magical energy from a distance, but is fragile."
    },
    'radiant': { #TODO: make divine servant
        'summon': 'monster_divine_servant',
        'duration': 150,
        'description': "Summon a Divine Servant. This heavenly creature will swear to protect you."
    },
    'dark': { #TODO: make shadow demon
        'summon': 'monster_shadow_demon',
        'duration': 150,
        'description': "Summon a Shadow Demon. This vicious creature of darkness will not bend to the will of mortals."
    },
    'void': { #TODO: make void horror
        'summon': 'monster_void_horror',
        'duration': 300,
        'description': "Who can tell what horrors this might summon? I hope you know what you're doing."
    }
}

charm_resist_extra_resists = {
    'fire':['burning'],
    'water':['exhaustion'],
    'air':['immobilize'],
    'earth':['stun'],
    'life':['poison'],
    'dark':['rot'],
    'ice':['freeze'],
    'arcane':['silence'],
    'radiant':['judgement'],
    'void':[]
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
        'Fire a bolt of roiling magma that melts floors',
        [
            {'stamina_cost':60,'charges':2},
            {'stamina_cost':50,'charges':3},
            {'stamina_cost':40,'charges':4}
        ],
        10)
}

essence_colors = {
    'normal' : libtcod.gray,
    'life' : libtcod.green,
    'fire' : libtcod.flame,
    'earth' : libtcod.sepia,
    'dark' : libtcod.dark_violet,
    'water' : libtcod.azure,
    'air' : libtcod.light_sky,
    'cold' : libtcod.lightest_azure,
    'radiant' : libtcod.lighter_yellow,
    'arcane' : libtcod.fuchsia,
    'void' : libtcod.darker_crimson
}