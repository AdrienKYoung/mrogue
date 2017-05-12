import libtcodpy
import player
import actions
import combat

table = {
    'weapon_battleaxe_of_pure_fire': {
        'name'               : 'battleaxe of pure fire',
        'category'           : 'weapon',
        'damage_type'        : 'fire',
        'subtype'            : 'axe',
        'char'               : 'P',
        'color'              : libtcodpy.flame,
        'type'               : 'item',
        'slot'               : 'both hands',
        'description'        : 'A battleaxe of pure flame, cleaving and burning all in its path.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'shred'              : 3,
        'accuracy'           : 3,
        'ctrl_attack'        : player.cleave_attack,
        'ctrl_attack_desc'   : 'Cleave - attack all adjacent enemies. Costs 2x stamina.',
        'weapon_dice'        : '2d12',
        'str_dice'           : 3,
        'on_hit'             : [combat.on_hit_burn],
        'attack_delay'       : 16,
        'crit_bonus'         : 1.5
    },
    'weapon_diamond_warhammer': {
        'name'               : 'diamond warhammer',
        'category'           : 'weapon',
        'subtype'            : 'mace',
        'damage_type'        : 'bludgeoning',
        'char'               : chr(157),
        'color'              : libtcodpy.sepia,
        'type'               : 'item',
        'slot'               : 'both hands',
        'description'        : 'A diamond warhammer, crushing its foes when wielded with strength.',
        'stamina_cost'       : 15,
        'str_requirement'    : 1,
        'shred'              : 2,
        'pierce'             : 3,
        'accuracy'           : 1,
        'weapon_dice'        : '1d8',
        'str_dice'           : 5,
        'on_hit'             : [actions.mace_stun],
        'attack_delay'       : 22,
        'crit_bonus'         : 1.5
    },
    'weapon_storm_mace': {
        'name'               : 'storm mace',
        'category'           : 'weapon',
        'damage_type'        : 'lightning',
        'subtype'            : 'mace',
        'char'               : chr(157),
        'color'              : libtcodpy.light_sky,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A storm mace, booming with thunder as chain-lightning arcs through its victims.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'shred'              : 2,
        'accuracy'           : 2,
        'weapon_dice'        : '3d6',
        'str_dice'           : 2,
        'on_hit'             : [combat.on_hit_chain_lightning],
        'attack_delay'       : 22,
        'crit_bonus'         : 1.5
    },
    'weapon_trident_of_raging_water': {
        'name'               : 'trident of raging water',
        'category'           : 'weapon',
        'subtype'            : 'polearm',
        'damage_type'        : 'stabbing',
        'char'               : libtcodpy.CHAR_ARROW_N,
        'color'              : libtcodpy.azure,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A trident of raging water, threatening foes from a distance and hindering their movements.',
        'stamina_cost'       : 12,
        'str_requirement'    : 1,
        'pierce'             : 2,
        'shred'              : 1,
        'accuracy'           : 2,
        'ctrl_attack'        : player.reach_attack, #could use a special reach attack that cleaves
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction.',
        'weapon_dice'        : '3d6',
        'str_dice'           : 3,
        'on_hit'             : [combat.on_hit_slow, combat.on_hit_sluggish],
        'attack_delay'       : 14,
        'crit_bonus'         : 1.5
    },
    'weapon_lifedrinker_dagger': { #lit. german: 'knife'. no english period term
        'name'               : 'lifedrinker dagger',
        'category'           : 'weapon',
        'damage_type'        : 'stabbing',
        'subtype'            : 'dagger',
        'char'               : '-',
        'color'              : libtcodpy.green,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : "A lifedrinker dagger, sustaining the life of it's wielder with the suffering of others",
        'stamina_cost'       : 8,
        'str_requirement'    : 1,
        'shred'              : 0,
        'accuracy'           : 5,
        'weapon_dice'        : '2d4',
        'str_dice'           : 1,
        'on_hit'             : [combat.on_hit_lifesteal],
        'attack_delay'       : 12,
        'crit_bonus'         : 3
    },
    'weapon_frozen_blade': {
        'name'               : 'frozen blade',
        'category'           : 'weapon',
        'subtype'            : 'sword',
        'damage_type'        : 'cold',
        'char'               : '/',
        'color'              : libtcodpy.lightest_gray,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A frozen blade, inflicting merciless wounds on individual targets.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'shred'              : 2,
        'accuracy'           : 4,
        'weapon_dice'        : '2d10',
        'str_dice'           : 2,
        'on_hit'             : [combat.on_hit_freeze],
        'attack_delay'       : 10,
        'crit_bonus'         : 2.5
    },
    'weapon_staff_of_force': {
        'name'               : 'staff of force',
        'category'           : 'weapon',
        'subtype'            : 'staff',
        'damage_type'        : 'bludgeoning',
        'char'               : '|',
        'color'              : libtcodpy.fuchsia,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A staff of force, humming with arcane energy that sends its targets flying.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'shred'              : 1,
        'accuracy'           : 3,
        'weapon_dice'        : '1d10',
        'str_dice'           : 1,
        'on_hit'             : [combat.on_hit_knockback],
        'attack_delay'       : 10,
        'crit_bonus'         : 1.5
    },
    'weapon_soul_reaper': {
        'name'               : 'soul reaper',
        'category'           : 'weapon',
        'subtype'            : 'polearm',
        'damage_type'        : 'slashing',
        'char'               : ')',
        'color'              : libtcodpy.dark_violet,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A soul reaper, a grim scythe that raises those it kills as zombies.',
        'stamina_cost'       : 10,
        'str_requirement'    : 1,
        'pierce'             : 1,
        'shred'              : 2,
        'accuracy'           : 2,
        'ctrl_attack'        : player.reach_attack, #could use a special reach attack that cleaves
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction.',
        'weapon_dice'        : '3d10',
        'str_dice'           : 2,
        'on_hit'             : [combat.on_hit_reanimate],
        'attack_delay'       : 18,
        'crit_bonus'         : 1.5
    },
}