import player

def meets_requirements(perk):
    return True #TODO: actually check this

perk_keys = [
    'sorcery',
    'archmage',
    'essence_hunter',
    'spell_mastery',
    'solace',
    'scholar',
    'fire_affinity',
    'searing_mind',
    'pyromaniac',
    'water_affinity',
    'grip_of_the_depths',
    'aquatic',
    'earth_affinity',
    'stonecloak',
    'earthmeld',
    'air_affinity',
    'tailwind',
    'cold_affinity',
    'life_affinity',
    'arcane_affinity',
    'dark_affinity',
    'radiant_affinity',
    'void_affinity'
]

perk_list = {
    'sorcery' : {
        'name' : 'Sorcery',
        'description' : ['Your spells have 33%% more spell charges',
                         'Your spells have 66%% more spell charges',
                         'Your spells have 100%% more spell charges'],
        'max_rank' : 3,
        'values'   : [0.33,0.66,1.0],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Magic'
    },
    'archmage' : {
        'name' : 'Archmage',
        'description' : ['Reduce all spell cast times by one step'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires': 'sorcery_3',
        'category' : 'Magic'
    },
    'essence_hunter' : {
        'name' : 'Essence Hunter',
        'description' : ['Enemies killed by spells are 10%% more likely to drop essence',
                         'Enemies killed by spells are 15%% more likely to drop essence',
                         'Enemies killed by spells are 20%% more likely to drop essence'],
        'max_rank' : 3,
        'values'   : [0.1,0.15,0.2],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Magic'
    },
    'fire_affinity' : {
        'name' : 'Fire Affinity',
        'description' : ['You have 2 extra spellpower when casting Fire spells',
                         'You have 4 extra spellpower when casting Fire spells',
                         'You have 6 extra spellpower when casting Fire spells',
                         'You have 8 extra spellpower when casting Fire spells',
                         'You have 10 extra spellpower when casting Fire spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Fire Magic'
    },
    'water_affinity' : {
        'name' : 'Water Affinity',
        'description' : ['You have 2 extra spellpower when casting Water spells',
                         'You have 4 extra spellpower when casting Water spells',
                         'You have 6 extra spellpower when casting Water spells',
                         'You have 8 extra spellpower when casting Water spells',
                         'You have 10 extra spellpower when casting Water spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Water Magic'
    },
    'earth_affinity' : {
        'name' : 'Earth Affinity',
        'description' : ['You have 2 extra spellpower when casting Earth spells',
                         'You have 4 extra spellpower when casting Earth spells',
                         'You have 6 extra spellpower when casting Earth spells',
                         'You have 8 extra spellpower when casting Earth spells',
                         'You have 10 extra spellpower when casting Earth spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Earth Magic'
    },
    'air_affinity' : {
        'name' : 'Air Affinity',
        'description' : ['You have 2 extra spellpower when casting Air spells',
                         'You have 4 extra spellpower when casting Air spells',
                         'You have 6 extra spellpower when casting Air spells',
                         'You have 8 extra spellpower when casting Air spells',
                         'You have 10 extra spellpower when casting Air spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Air Magic'
    },
    'life_affinity' : {
        'name' : 'Life Affinity',
        'description' : ['You have 2 extra spellpower when casting Life spells',
                         'You have 4 extra spellpower when casting Life spells',
                         'You have 6 extra spellpower when casting Life spells',
                         'You have 8 extra spellpower when casting Life spells',
                         'You have 10 extra spellpower when casting Life spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Life Magic'
    },
    'cold_affinity' : {
        'name' : 'Cold Affinity',
        'description' : ['You have 2 extra spellpower when casting Cold spells',
                         'You have 4 extra spellpower when casting Cold spells',
                         'You have 6 extra spellpower when casting Cold spells',
                         'You have 8 extra spellpower when casting Cold spells',
                         'You have 10 extra spellpower when casting Cold spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Cold Magic'
    },
    'arcane_affinity' : {
        'name' : 'Arcane Affinity',
        'description' : ['You have 2 extra spellpower when casting Arcane spells',
                         'You have 4 extra spellpower when casting Arcane spells',
                         'You have 6 extra spellpower when casting Arcane spells',
                         'You have 8 extra spellpower when casting Arcane spells',
                         'You have 10 extra spellpower when casting Arcane spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Arcane Magic'
    },
    'dark_affinity' : {
        'name' : 'Dark Affinity',
        'description' : ['You have 2 extra spellpower when casting Dark spells',
                         'You have 4 extra spellpower when casting Dark spells',
                         'You have 6 extra spellpower when casting Dark spells',
                         'You have 8 extra spellpower when casting Dark spells',
                         'You have 10 extra spellpower when casting Dark spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Dark Magic'
    },
    'radiant_affinity' : {
        'name' : 'Radiant Affinity',
        'description' : ['You have 2 extra spellpower when casting Radiant spells',
                         'You have 4 extra spellpower when casting Radiant spells',
                         'You have 6 extra spellpower when casting Radiant spells',
                         'You have 8 extra spellpower when casting Radiant spells',
                         'You have 10 extra spellpower when casting Radiant spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Radiant Magic'
    },
    'void_affinity' : {
        'name' : 'Void Affinity',
        'description' : ['You have 2 extra spellpower when casting Void spells',
                         'You have 4 extra spellpower when casting Void spells',
                         'You have 6 extra spellpower when casting Void spells',
                         'You have 8 extra spellpower when casting Void spells',
                         'You have 10 extra spellpower when casting Void spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Void Magic'
    },
    'spell_mastery' : {
        'name' : 'Spell Mastery',
        'description' : ['Choose a max-level spell that you can cast from your equipped spellbook. The spell is'
                         ' memorized (can be cast at max level even without the appropriate spellbook equipped)',
                         'Choose a max-level spell that you can cast from your equipped spellbook. The spell is'
                         ' memorized (can be cast at max level even without the appropriate spellbook equipped)',
                         'Choose a max-level spell that you can cast from your equipped spellbook. The spell is'
                         ' memorized (can be cast at max level even without the appropriate spellbook equipped)'],
        'max_rank' : 3,
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Magic'
    },
    'solace' : {
        'name' : 'Solace',
        'description' : ['You take 50%% reduced damage while meditating'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Magic'
    },
    'scholar' : {
        'name' : 'Scholar',
        'description' : ['Spell INT requirements are reduced by 2',
                         'Spell INT requirements are reduced by 4',
                         'Spell INT requirements are reduced by 6'],
        'max_rank' : 3,
        'values' : [2, 4, 6],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Magic'
    },
    'searing_mind' : {
        'name' : 'Searing Mind',
        'description' : ['Your spells deal 10%% more damage.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'fire_affinity_3',
        'category' : 'Fire Magic'
    },
    'pyromaniac' : {
        'name' : 'Pyromaniac',
        'description' : ['Gain immunity to burning. Leave a fire trail behind you when you move.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'fire_affinity_5',
        'category' : 'Fire Magic'
    },
    'grip_of_the_depths' : {
        'name' : 'Grip of the Depths',
        'description' : ['Gain 50 stamina whenever an enemy drowns. Drowned enemies have a chance to drop water essence.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'water_affinity_3',
        'category' : 'Water Magic'
    },
    'aquatic' : {
        'name' : 'Aquatic',
        'description' : ['You cannot drown, gain bonus evasion in water, and ignore stamina costs for travelling '
                         'through water'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'water_affinity_5',
        'category' : 'Water Magic'
    },
    'stonecloak' : {
        'name' : 'Stonecloak',
        'description' : ['Gain temporary armor whenever you cast a spell'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'earth_affinity_3',
        'category' : 'Earth Magic'
    },
    'earthmeld' : {
        'name' : 'Earthmeld',
        'description' : ['You may move into walls (if you are not currently standing in a wall)'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'earth_affinity_5',
        'category' : 'Earth Magic'
    },
    'tailwind' : {
        'name' : 'Tailwind',
        'description' : ['After you cast a spell, if your next action is a move, it does not cost an action.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'air_affinity_3',
        'category' : 'Air Magic'
    },
}