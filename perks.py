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

import player
import actions
import actions.perk_actions
import game as main
import consts

def meets_requirements(perk):
    if consts.DEBUG_FREE_PERKS:
        return True

    requirement = perk_list[perk].get('requires')
    if requirement is None:
        return True
    lvl = requirement.split(' ')
    if len(lvl) > 1:
        lvl = int(lvl[len(lvl) - 1])
        requirement = requirement.split(' ')[0]
        return main.has_skill(requirement) >= lvl
    else:
        return main.has_skill(requirement)

perk_keys = [
    'focus',
    'ravager',
    'adrenaline',
    'combat_training',
    'martial_paragon',
    'dagger_mastery',
    'find_the_gap',
    'cut_and_run',
    'death_from_above',
    'sword_mastery',
    'pommel_strike',
    'blade_dance',
    'riposte',
    'axe_mastery',
    'wild_swings',
    'skullsplitter',
    'lord_of_the_fray',
    'polearm_mastery',
    'sweep',
    'vanguard',
    'gatekeeper',
    'mace_mastery',
    'ringing_blows',
    'crush',
    'rising_storm',
    'unarmed_mastery',
    'steel_fist',
    'flying_knee_smash',
    'essence_fist',
    'fist_of_foretold_demise',
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
    'flight',
    'cold_affinity',
    'spellshards',
    'frostbite',
    'life_affinity',
    'vitality',
    'resurrection',
    'arcane_affinity',
    'death_affinity',
    'blood_magic',
    'lichform',
    'radiance_affinity',
    'guardian_of_light',
    'heir_to_the_heavens',
    'void_affinity',
    'gaze_into_the_void',
]

demon_powers = [
    'vampirism',
    'bloodlust',
    'dark_aura'
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
        'requires': 'sorcery 3',
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
    'death_affinity' : {
        'name' : 'Death Affinity',
        'description' : ['You have 2 extra spellpower when casting Death spells',
                         'You have 4 extra spellpower when casting Death spells',
                         'You have 6 extra spellpower when casting Death spells',
                         'You have 8 extra spellpower when casting Death spells',
                         'You have 10 extra spellpower when casting Death spells'],
        'max_rank' : 5,
        'values'   : [2,4,6,8,10],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Death Magic'
    },
    'radiance_affinity' : {
        'name' : 'Radiant Affinity',
        'description' : ['You have 2 extra spellpower when casting Radiance spells',
                         'You have 4 extra spellpower when casting Radiance spells',
                         'You have 6 extra spellpower when casting Radiance spells',
                         'You have 8 extra spellpower when casting Radiance spells',
                         'You have 10 extra spellpower when casting Radiance spells'],
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
        'category' : 'Magic',
        'on_acquire' : player.level_spell_mastery
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
        'requires' : 'fire_affinity 3',
        'category' : 'Fire Magic'
    },
    'pyromaniac' : {
        'name' : 'Pyromaniac',
        'description' : ['Gain immunity to burning. Leave a fire trail behind you when you move.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'fire_affinity 5',
        'category' : 'Fire Magic'
    },
    'grip_of_the_depths' : {
        'name' : 'Grip of the Depths',
        'description' : ['Gain 50 stamina whenever an enemy drowns. Drowned enemies have a chance to drop water essence.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'water_affinity 3',
        'category' : 'Water Magic'
    },
    'aquatic' : {
        'name' : 'Aquatic',
        'description' : ['You cannot drown, gain bonus evasion in water, and ignore stamina costs for travelling '
                         'through water'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'water_affinity 5',
        'category' : 'Water Magic',
        'on_acquire': lambda: actions.perk_actions.aquatic(player.instance)
    },
    'stonecloak' : {
        'name' : 'Stonecloak',
        'description' : ['Gain temporary armor whenever you cast a spell'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'earth_affinity 3',
        'category' : 'Earth Magic'
    },
    'earthmeld' : {  #todo
        'name' : 'Earthmeld',
        'description' : ['You may move into walls (if you are not currently standing in a wall)'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'earth_affinity 5',
        'category' : 'Earth Magic'
    },
    'tailwind' : {
        'name' : 'Tailwind',
        'description' : ['After you cast a spell, if your next action is a move, it does not cost an action.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'air_affinity 3',
        'category' : 'Air Magic'
    },
    'flight' : {
        'name' : 'Flight',
        'description' : ['Your base movement type becomes Flying'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'air_affinity 5',
        'category' : 'Air Magic',
        'on_acquire': lambda: actions.perk_actions.flight(player.instance)
    },
    'vitality' : {
        'name' : 'Vitality',
        'description' : ['Healing effects are 25%% more effective'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'life_affinity 3',
        'category' : 'Life Magic'
    },
    'resurrection' : {
        'name' : 'Resurrection',
        'description' : ['Upon death, resurrect with full health, once...'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'life_affinity 5',
        'category' : 'Life Magic',
        'on_acquire': lambda: actions.perk_actions.auto_res(player.instance)
    },
    'spellshards' : {
        'name' : 'Spellshards',
        'description' : ['Damage dealt by your spells has +2 shred'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'cold_affinity 3',
        'category' : 'Cold Magic'
    },
    'frostbite' : {
        'name' : 'Frostbite',
        'description' : ['All visible enemies below 50%% health are slowed'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'cold_affinity 5',
        'category' : 'Cold Magic'
    },
    'blood_magic' : {
        'name' : 'Blood Magic',
        'description' : ['You can cast spells without the required stamina, at the cost of health.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'death_affinity 3',
        'category' : 'Death Magic'
    },
    'lichform' : {
        'name' : 'Lichform',
        'description' : ['Sacrifice 30%% of your maximum health. Gain resistance to all status effects and'
                         'damage types, and immunity to death magic.'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'death_affinity 5',
        'category' : 'Death Magic',
        'on_acquire': lambda: actions.perk_actions.lichform(player.instance)
    },
    'guardian_of_light' : {
        'name' : 'Guardian of Light',
        'description' : ['You and your allies have +2 armor'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'radiance_affinity 3',
        'category' : 'Radiant Magic'
    },
    'heir_to_the_heavens' : {
        'name' : 'Heir to the Heavens',
        'description' : ['Whenever you take critical damage, a guardian angel is summoned to aid you'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'radiance_affinity 5',
        'category' : 'Radiant Magic'
    },
    'gaze_into_the_void' : {
        'name' : 'Gaze Into the Void',
        'description' : ['Gain 3 Void essence'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'on_acquire': lambda: actions.perk_actions.gaze_into_the_void(player.instance),
        'requires' : 'void_affinity 3',
        'category' : 'Void Magic'
    },
    'focus': {
        'name': 'Focus',
        'description': ['Ability: Gain increased accuracy for your next attack',
                        'Ability: Gain increased accuracy for your next attack',
                        'Ability: Gain increased accuracy for your next attack'],
        'max_rank': 3,
        'sp_cost': 10,
        'on_acquire': player.learn_ability('ability_focus'),
        'requires': None,
        'category': 'Martial'
    },
    'ravager' : {
        'name' : 'Ravager',
        'description' : ['Deal 10%% more damage to unarmored enemies',
                         'Deal 20%% more damage to unarmored enemies',
                         'Deal 30%% more damage to unarmored enemies'],
        'max_rank' : 3,
        'values' : [0.1, 0.2, 0.3],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Martial'
    },
    'adrenaline' : {
        'name' : 'Adrenaline',
        'description' : ['Chance to gain stamina upon taking damage. Chances increases as health decreases'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Martial'
    },
    'combat_training' : {
        'name' : 'Combat Training',
        'description' : ['Attacks cost 10%% less stamina',
                         'Attacks cost 20%% less stamina',
                         'Attacks cost 30%% less stamina'],
        'max_rank' : 3,
        'values' : [0.1, 0.2, 0.3],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Martial'
    },
    'dagger_mastery' : {
        'name' : 'Dagger Mastery',
        'description' : ['Gain 2 extra attack damage when wielding daggers',
                         'Gain 4 extra attack damage when wielding daggers',
                         'Gain 6 extra attack damage when wielding daggers',
                         'Gain 8 extra attack damage when wielding daggers',
                         'Gain 10 extra attack damage when wielding daggers',
                         'Gain 12 extra attack damage when wielding daggers',
                         'Gain 14 extra attack damage when wielding daggers'],
        'max_rank' : 7,
        'values' : [2, 4, 6, 8, 10, 12, 14],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Daggers'
    },
    'sword_mastery' : {
        'name' : 'Sword Mastery',
        'description' : ['Gain 2 extra attack damage when wielding swords',
                         'Gain 4 extra attack damage when wielding swords',
                         'Gain 6 extra attack damage when wielding swords',
                         'Gain 8 extra attack damage when wielding swords',
                         'Gain 10 extra attack damage when wielding swords',
                         'Gain 12 extra attack damage when wielding swords',
                         'Gain 14 extra attack damage when wielding swords'],
        'max_rank' : 7,
        'values' : [2, 4, 6, 8, 10, 12, 14],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Swords'
    },
    'axe_mastery' : {
        'name' : 'Axe Mastery',
        'description' : ['Gain 2 extra attack damage when wielding axes',
                         'Gain 4 extra attack damage when wielding axes',
                         'Gain 6 extra attack damage when wielding axes',
                         'Gain 8 extra attack damage when wielding axes',
                         'Gain 10 extra attack damage when wielding axes',
                         'Gain 12 extra attack damage when wielding axes',
                         'Gain 14 extra attack damage when wielding axes'],
        'max_rank' : 7,
        'values' : [2, 4, 6, 8, 10, 12, 14],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Axes'
    },
    'polearm_mastery' : {
        'name' : 'Polearm Mastery',
        'description' : ['Gain 2 extra attack damage when wielding polearms',
                         'Gain 4 extra attack damage when wielding polearms',
                         'Gain 6 extra attack damage when wielding polearms',
                         'Gain 8 extra attack damage when wielding polearms',
                         'Gain 10 extra attack damage when wielding polearms',
                         'Gain 12 extra attack damage when wielding polearms',
                         'Gain 14 extra attack damage when wielding polearms'],
        'max_rank' : 7,
        'values' : [2, 4, 6, 8, 10, 12, 14],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Polearms'
    },
    'mace_mastery' : {
        'name' : 'Mace Mastery',
        'description' : ['Gain 2 extra attack damage when wielding maces',
                         'Gain 4 extra attack damage when wielding maces',
                         'Gain 6 extra attack damage when wielding maces',
                         'Gain 8 extra attack damage when wielding maces',
                         'Gain 10 extra attack damage when wielding maces',
                         'Gain 12 extra attack damage when wielding maces',
                         'Gain 14 extra attack damage when wielding maces'],
        'max_rank' : 7,
        'values' : [2, 4, 6, 8, 10, 12, 14],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Maces'
    },
    'unarmed_mastery' : {
        'name' : 'Unarmed Mastery',
        'description' : ['Gain 2 extra attack damage when not wielding a weapon',
                         'Gain 4 extra attack damage when not wielding a weapon',
                         'Gain 6 extra attack damage when not wielding a weapon',
                         'Gain 8 extra attack damage when not wielding a weapon',
                         'Gain 10 extra attack damage when not wielding a weapon',
                         'Gain 12 extra attack damage when not wielding a weapon',
                         'Gain 14 extra attack damage when not wielding a weapon'],
        'max_rank' : 7,
        'values' : [2, 4, 6, 8, 10, 12, 14],
        'sp_cost' : 20,
        'requires' : None,
        'category' : 'Unarmed Combat'
    },
    'pommel_strike' : {
        'name' : 'Pommel Strike',
        'description' : ['Ability (requires sword): Make an attack with +2 shred'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'on_acquire': player.learn_ability('ability_pommel_strike'),
        'requires' : 'sword_mastery 3',
        'category' : 'Swords'
    },
    'blade_dance' : {
        'name' : 'Blade Dance',
        'description' : ['Ability (requires sword): Swap places with an adjacent monster and make an attack against it'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'on_acquire': player.learn_ability('ability_blade_dance'),
        'requires' : 'sword_mastery 5',
        'category' : 'Swords',
    },
    'riposte' : {
        'name' : 'Riposte',
        'description' : ['Attacks against an enemy that missed you last turn are critical hits'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'sword_mastery 7',
        'category' : 'Swords'
    },
    'find_the_gap' : {
        'name' : 'Find the Gap',
        'description' : ['Your attacks with daggers gain pierce 1'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'dagger_mastery 3',
        'category' : 'Daggers'
    },
    'cut_and_run' : {
        'name' : 'Cut and Run',
        'description' : ['After damaging an enemy with a dagger, if your next action is a move, '
                         'it does not cost an action'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'dagger_mastery 5',
        'category' : 'Daggers'
    },
    'death_from_above' : {
        'name' : 'Death from Above',
        'description' : ['Your jump attacks have no accuracy penalty and deal 50%% more damage'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'dagger_mastery 7',
        'category' : 'Daggers'
    },
    'wild_swings' : {
        'name' : 'Wild Swings',
        'description' : ['Dealing damage with axes deals 1d6 damage to enemies adjacent to the target'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'axe_mastery 3',
        'category' : 'Axes'
    },
    'skullsplitter' : {
        'name' : 'Skullsplitter',
        'description' : ['Ability (requires axe): Attack a single target for massive bonus damage that increases the '
                         'closer the target is to death'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'on_acquire': player.learn_ability('ability_skullsplitter'),
        'requires' : 'axe_mastery 5',
        'category' : 'Axes'
    },
    'lord_of_the_fray' : {
        'name' : 'Lord of the Fray',
        'description' : ['Gain increased attack damage for each adjacent enemy'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'axe_mastery 7',
        'category' : 'Axes'
    },
    'sweep' : {
        'name' : 'Sweep',
        'description' : ['Ability (requires polearm): Attack all enemies at a range of exactly 2'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'on_acquire': player.learn_ability('ability_sweep'),
        'requires' : 'polearm_mastery 3',
        'category' : 'Polearms'
    },
    'vanguard' : {
        'name' : 'Vanguard',
        'description' : ['Get a free attack on enemies that move into a space adjacent to you when '
                         'you are wielding a spear'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'polearm_mastery 5',
        'category' : 'Polearms'
    },
    'gatekeeper' : {
        'name' : 'Gatekeeper',
        'description' : ['Chance to knock back enemies with melee attacks'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'polearm_mastery 7',
        'category' : 'Polearms'
    },
    'ringing_blows' : {
        'name' : 'Ringing Blows',
        'description' : ['Increased chance to stun with maces. Stuns inflicted by mace hits last 1 more turn'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'mace_mastery 3',
        'category' : 'Maces'
    },
    'crush' : {
        'name' : 'Crush',
        'description' : ["Ability (requires mace): Make an attack that gains damage and shred "
                         "for each point of your target's armor"],
        'max_rank' : 1,
        'sp_cost' : 20,
        'on_acquire' : player.learn_ability('ability_crush'),
        'requires' : 'mace_mastery 5',
        'category' : 'Maces'
    },
    'rising_storm' : {
        'name' : 'Rising Storm',
        'description' : ['If you have not attacked in the last 3 turns, your next attack deals bonus damage'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'mace_mastery 7',
        'category' : 'Maces'
    },
    'martial_paragon' : {
        'name' : 'Martial Paragon',
        'description' : ['Your weapon attacks have increase strength bonuses'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : None, #ToDo: check for one of several learned skills
        'category' : 'Martial'
    },
    'steel_fist' : {
        'name' : 'Steel Fist',
        'description' : ['Your unarmed attacks deal 1d6 weapon damage and have two strength dice'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'unarmed_mastery 1',
        'category' : 'Unarmed Combat'
    },
    'flying_knee_smash' : {
        'name' : 'Flying Knee Smash',
        'description' : ['Your jump attacks made while unarmed deal double damage'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'unarmed_mastery 3',
        'category' : 'Unarmed Combat'
    },
    'essence_fist' : {
        'name' : 'Essence Fist',
        'description' : ['Ability: Consume an essence to deal high elemental damage'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'on_acquire' : player.learn_ability('ability_essence_fist'),
        'requires' : 'unarmed_mastery 5',
        'category' : 'Unarmed Combat'
    },
    'fist_of_foretold_demise' : {
        'name' : 'Fist of Foretold Demise',
        'description' : ['Your unarmed attacks inflict 1d2 doom stacks'],
        'max_rank' : 1,
        'sp_cost' : 20,
        'requires' : 'unarmed_mastery 7',
        'category' : 'Unarmed Combat'
    },

    #Demonic Powers
    'vampirism' : {
        'name' : 'Vampirism',
        'description' : ['You heal damage when you kill enemies'],
        'values': [2,3,4],
        'max_rank' : 3,
        'corruption_dice': '30d6'
    },
    'bloodlust' : {
        'name' : 'Bloodlust',
        'description' : ['You restore stamina when you kill enemies'],
        'values': [5,7,10],
        'max_rank' : 3,
        'corruption_dice': '30d6'
    },
    'dark_aura' : {
        'name' : 'Dark Aura',
        'description' : ['You curse nearby enemies'],
        'values': [1,2,3],
        'max_rank' : 3,
        'corruption_dice': '30d6'
    }
}
