import libtcodpy
import game as main
import player
import combat
import dungeon
import spells
import actions

table = {
    'weapons_0': [
        'weapon_dagger',
        'weapon_hatchet',
        'weapon_longsword',
        'weapon_mace',
        'weapon_spear',
    ],

     'weapons_1': [
        'weapon_dagger',
        'weapon_hatchet',
        'weapon_longsword',
        'weapon_mace',
        'weapon_spear',
        'weapon_pickaxe',
    ],

    'weapons_2' : [
        'weapon_dagger',
        'weapon_hatchet',
        'weapon_longsword',
        'weapon_mace',
        'weapon_spear',
        'weapon_pickaxe',
    ],

    'armor_0': [
        'equipment_shield',
        'equipment_leather_armor',
        'equipment_iron_helm',
        'equipment_vambraces'
    ],

    'armor_1': [
        'equipment_shield',
        'equipment_leather_armor',
        'equipment_iron_helm',
        'equipment_mail_skirt',
        'equipment_vambraces',
        'equipment_mail_armor'
    ],

    'armor_2' : [
        'equipment_iron_helm',
        'equipment_mail_skirt',
        'equipment_vambraces',
        'equipment_mail_armor',
        'equipment_brigandine',
        'equipment_great_helm',
        'equipment_pauldrons',
        'equipment_greaves'
    ],

    'armor_3' : [
        'equipment_brigandine',
        'equipment_great_helm',
        'equipment_pauldrons',
        'equipment_greaves',
        'equipment_spaulders',
        'equipment_armet_helm',
        'equipment_plate_armor',
    ],

     'consumables_1': [
        'potion_healing',
        'potion_healing',
        'potion_healing',
        'potion_waterbreathing',
        'potion_shielding',
        'potion_shielding',
        'scroll_fireball',
        'scroll_confusion',
        'scroll_forge',
    ],

    'tomes_1': [
        #'tome_manabolt',
        #'tome_mend',
        #'tome_ignite',
        'book_lesser_fire'
    ],

    'gems_1': [
        'gem_lesser_fire',
        'gem_lesser_water',
        'gem_lesser_earth',
        'gem_lesser_air',
        'gem_lesser_cold',
        'gem_lesser_life',
        'gem_lesser_arcane',
    ]
}

def item_from_table(branch,loot_table=None):
    if loot_table is None:
        loot_table = choose_loot_table(branch)

    if loot_table is None:
        return None

    if not loot_table in table:
        return None

    loot_level=int(loot_table.split('_')[1])
    category=loot_table.split('_')[0]

    while main.roll_dice('1d20') == 20:
        loot_level += 1 #oh lawdy
        tmp = category+'_'+str(loot_level)
        if not tmp in table.keys():
            loot_level-=1
            break

    loot_table = category+'_'+str(loot_level)

    item_id = table[loot_table][libtcodpy.random_get_int(0,0,len(table[loot_table]))-1]
    material = None
    quality = None
    if category == 'weapon':
        material = choose_material(loot_level)
        quality = choose_quality(loot_level)

    return main.create_item(item_id, material, quality)

def choose_loot_table(branch):
    b = dungeon.branches[branch]
    if b.get('loot') is None:
        return None
    else:
        return main.random_choice(b['loot'])

def choose_material(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 20 * loot_level, 150))
    if roll < 5:
        return choose_material(loot_level + 5)
    elif roll < 15:
        return 'wooden'
    elif roll < 30:
        return 'bronze'
    elif roll < 95:
        return 'iron'
    elif roll < 105:
        return 'steel'
    elif roll < 120:
        return 'crystal'
    elif roll < 130:
        return 'meteor'
    elif roll < 140:
        return 'aetherwood'
    else:
        return 'blightstone'


def choose_quality(loot_level=0):
    roll = libtcodpy.random_get_int(0, 0, min(100 + 20 * loot_level, 130))
    if roll < 5:
        return choose_quality(loot_level + 5)
    elif roll < 10:
        return 'broken'
    elif roll < 20:
        return 'crude'
    elif roll < 90:
        return '' # standard
    elif roll < 100:
        return 'military'
    elif roll < 110:
        return 'fine'
    elif roll < 120:
        return 'masterwork'
    else:
        return 'artifact'

item_categories = {
    'weapon' : { 'plural' : 'weapons' },
    'armor' : { 'plural' : 'armor' },
    'scroll' : { 'plural' : 'scrolls' },
    'potion' : { 'plural' : 'potions' },
    'book' : { 'plural' : 'books' },
    'charm' : { 'plural' : 'charms'},
    'gem' : { 'plural' : 'gems'}
}

qualities = {
    'broken' : {
        'dmg' : -3,
        'acc' : -3,
        'shred' : -1,
        'color' : libtcodpy.desaturated_red,
        'ev' : -5,
        'ar' : -1,
        'weight' : 0
    },
    'crude' : {
        'dmg' : -2,
        'acc' : -1,
        'break' : 5.0,
        'color' : libtcodpy.dark_sepia,
        'ev' : -1,
        'ar' : 0,
        'weight' : 1
    },
    '' : { # standard
        'dmg' : 0,
        'acc' : 0,
        'color' : libtcodpy.light_gray,
        'ev' : 0,
        'ar' : 0,
        'weight' : 0
    },
    'military' : {
        'dmg' : 1,
        'acc' : 1,
        'color' : libtcodpy.dark_orange,
        'ev' : 0,
        'ar' : 0,
        'weight' : -1
    },
    'fine' : {
        'dmg' : 2,
        'acc' : 2,
        'break' : -1.5,
        'color' : libtcodpy.sea,
        'ev' : 1,
        'ar' : 0,
        'weight' : -2
    },
    'masterwork' : {
        'dmg' : 3,
        'acc' : 3,
        'shred' : 1,
        'break' : -10.0,
        'color' : libtcodpy.green,
        'ev' : 2,
        'ar' : 0,
        'weight' : -3
    },
    'artifact' : {
        'dmg' : 5,
        'acc' : 5,
        'shred' : 1,
        'peirce' : 1,
        'break' : -1000.0,
        'color' : libtcodpy.yellow,
        'ev' : 3,
        'ar' : 1,
        'weight' : -5
    },
}

weapon_materials = {
    'wooden' : {
        'dmg' : -2,
        'acc' : 1,
        'break' : 5.0
    },
    'bronze' : {
        'dmg' : 0,
        'acc' : 0,
        'break' : 1.5
    },
    'iron' : {
        'dmg' : 0,
        'acc' : 0,
        'shred' : 1
    },
    'steel' : {
        'dmg' : 1,
        'acc' : 1,
        'shred' : 2,
        'break' : -5.0
    },
    'crystal' : {
        'dmg' : 3,
        'acc' : -2,
        'pierce' : 1,
        'break' : -1000.0
    },
    'meteor' : {
        'dmg' : 5,
        'acc' : -2,
        'shred' : 1,
        'break' : -5.0
    },
    'aetherwood' : {
        'dmg' : 2,
        'acc' : 3,
        'shred' : 1,
        'break' : -15.0
    },
    'blightstone' : {
        'dmg' : 0,
        'acc' : 0,
        'autoshred' : 1,
        'break' : -5.0
    },
    '' : {
        'dmg' : 0,
        'acc' : 0,
        'shred' : 0
    },
}

armor_materials = {
    'rst_slashing' :
        {'adjective' : 'reinforced'},
    'rst_piercing' :
        {'adjective' : 'hardened'},
    'rst_bludgeoning' :
        {'adjective' : 'padded'},
    'rst_fire' :
        {'adjective' : 'fire-proof'},
    'rst_electric' :
        {'adjective' : 'insulated'},
    'rst_cold' :
        {'adjective' : 'fur-lined'},
    'rst_spell' :
        {'adjective' : 'enchanted'},
    'rst_dark' :
        {'adjective' : 'blessed'},
    'rst_radiant' :
        {'adjective' : 'infernal'},
}

proto = {

    #SCROLLS
    'scroll_fireball': {
        'name'          : 'Scroll of Fireball',
        'category'      : 'scroll',
        'char'          : '#',
        'on_use'        : actions.fireball,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'Fires a flaming projectile at a target that explodes on impact'
    },

    'scroll_confusion': {
        'name'          : 'Scroll of Confusion',
        'category'      : 'scroll',
        'char'          : '#',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.confuse,
        'type'          : 'item',
        'description'   : 'Inflicts confusion on an enemy, causing them to move about erratically.'
    },

    'scroll_forge': {
        'name' : 'Scroll of Forging',
        'category' : 'scroll',
        'char' : '#',
        'color': libtcodpy.yellow,
        'on_use' : actions.forge,
        'type' : 'item',
        'description' : 'Upgrades the quality of your held weapon.'
    },

    #POTIONS
    'potion_healing': {
        'name'          : 'Potion of Healing',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.heal,
        'type'          : 'item',
        'description'   : 'Potion that heals wounds when consumed'
    },

    'potion_waterbreathing': {
        'name'          : 'Potion of Waterbreathing',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.waterbreathing,
        'type'          : 'item',
        'description'   : "Drinking this potion causes temporary gills to form on the drinker's throat, allowing him or "
                          "her to breath water like a fish."
    },

    'potion_shielding': {
        'name'          : 'Potion of Shielding',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.shielding,
        'type'          : 'item',
        'description'   : 'This oily metallic potion bolsters the defenses of anyone who drinks it, repairing shreded'
                          ' armor and temporarily enhancing its effectiveness'
    },

    # GEMS
    'gem_lesser_fire': {
        'name'          : 'Rough Ruby',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['fire'],
        'on_use'        : actions.potion_essence('fire'), #not a bug, returns a lambda
        'description'   : 'The essence of fire burns within this gemstone. Absorbing it will bestow a single fire essence.'
    },
    'gem_lesser_earth': {
        'name'          : 'Rough Garnet',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['earth'],
        'on_use'        : actions.potion_essence('earth'), #not a bug, returns a lambda
        'description'   : 'The essence of earth resonates within this gemstone. Absorbing it will bestow a single earth essence.'
    },
    'gem_lesser_life': {
        'name'          : 'Rough Emerald',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['life'],
        'on_use'        : actions.potion_essence('life'), #not a bug, returns a lambda
        'description'   : 'The essence of life emanates from this gemstone. Absorbing it will bestow a single life essence.'
    },
    'gem_lesser_air': {
        'name'          : 'Rough Quartz',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['air'],
        'on_use'        : actions.potion_essence('air'), #not a bug, returns a lambda
        'description'   : 'The essence of air swirls in this crystal. Absorbing it will bestow a single air essence.'
    },
    'gem_lesser_water': {
        'name'          : 'Rough Aquamarine',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['water'],
        'on_use'        : actions.potion_essence('water'), #not a bug, returns a lambda
        'description'   : 'The essence of water flows through this gemstone. Absorbing it will bestow a single water essence.'
    },
    'gem_lesser_cold': {
        'name'          : 'Rough Zircon',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['cold'],
        'on_use'        : actions.potion_essence('cold'), #not a bug, returns a lambda
        'description'   : 'The essence of cold chills the surface of this gemstone. Absorbing it will bestow a single cold essence.'
    },
    'gem_lesser_arcane': {
        'name'          : 'Rough Amethyst',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['arcane'],
        'on_use'        : actions.potion_essence('arcane'), #not a bug, returns a lambda
        'description'   : 'The essence of arcana hums within this gemstone. Absorbing it will bestow a single arcane essence.'
    },
    'gem_lesser_radiance': {
        'name'          : 'Rough Diamond',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['radiant'],
        'on_use'        : actions.potion_essence('radiant'), #not a bug, returns a lambda
        'description'   : 'The essence of radiance shines through this gemstone. Absorbing it will bestow a single radiant essence.'
    },
    'gem_lesser_dark': {
        'name'          : 'Rough Onyx',
        'type'          : 'item',
        'category'      : 'gem',
        'char'          : chr(4),
        'color'         : spells.essence_colors['dark'],
        'on_use'        : actions.potion_essence('dark'), #not a bug, returns a lambda
        'description'   : 'The essence of dark envelops this gemstone. Absorbing it will bestow a single dark essence.'
    },

    #WEAPONS
    'weapon_longsword': {
        'name'               : 'longsword',
        'category'           : 'weapon',
        'subtype'        : 'sword',
        'damage_type'        : 'slashing',
        'char'               : '/',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A hand-and-a-half cruciform sword',
        'stamina_cost'       : 10,
        'str_requirement'    : 12,
        'shred'              : 1,
        'accuracy'           : 1,
        'weapon_dice'        : '2d6',
        'str_dice'           : 2,
        'attack_delay'       : 14
    },
    'weapon_greatsword': { #called a spadone or montante in historical circles, but no one will recognize that
        'name'               : 'greatsword',
        'category'           : 'weapon',
        'subtype'            : 'sword',
        'damage_type'        : 'slashing',
        'char'               : '/',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A huge greatsword, made for fighting many foes at once.',
        'stamina_cost'       : 12,
        'str_requirement'    : 16,
        'shred'              : 2,
        'accuracy'           : 1,
        'weapon_dice'        : '3d6',
        'str_dice'           : 3,
        'attack_delay'       : 14
    },
    'weapon_dagger': {
        'name'               : 'dagger',
        'category'           : 'weapon',
        'subtype'        : 'knife',
        'damage_type'        : 'stabbing',
        'char'               : '-',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A small double-edged knife. Deals triple damage to incapacitated targets',
        'stamina_cost'       : 6,
        'str_requirement'    : 10,
        'shred'              : 0,
        'accuracy'           : 5,
        'weapon_dice'        : '2d4',
        'str_dice'           : 1,
        'attack_delay'       : 12,
        'crit_bonus'         : 3.0
    },
    'weapon_messer': { #lit. german: 'knife'. no english period term
        'name'               : 'messer',
        'category'           : 'weapon',
        'damage_type'        : 'slashing',
        'subtype'            : 'knife',
        'char'               : '-',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A long knife, made for dueling',
        'stamina_cost'       : 6,
        'str_requirement'    : 10,
        'shred'              : 0,
        'accuracy'           : 5,
        'weapon_dice'        : '2d4',
        'str_dice'           : 2,
        'attack_delay'       : 12,
        'crit_bonus'         : 2
    },
    'weapon_spear': {
        'name'               : 'spear',
        'category'           : 'weapon',
        'subtype'        : 'polearm',
        'damage_type'        : 'stabbing',
        'char'               : libtcodpy.CHAR_ARROW_N,
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A light thrusting spear',
        'stamina_cost'       : 10,
        'str_requirement'    : 12,
        'ability'            : 'ability_thrust',
        'pierce'             : 1,
        'shred'              : 0,
        'accuracy'           : 1,
        'ctrl_attack'        : player.reach_attack,
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction.',
        'weapon_dice'        : '2d10',
        'str_dice'           : 1,
        'attack_delay'       : 14
    },
    'weapon_halberd': {
        'name'               : 'halberd',
        'category'           : 'weapon',
        'subtype'            : 'polearm',
        'damage_type'        : 'slashing',
        'char'               : libtcodpy.CHAR_ARROW_N,
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'both hands',
        'description'        : 'A superior two-handed polearm with a spike, axe and hook on its head.',
        'stamina_cost'       : 12,
        'str_requirement'    : 16,
        'pierce'             : 1,
        'shred'              : 0,
        'accuracy'           : 2,
        'ctrl_attack'        : player.reach_attack, #could use a special reach attack that cleaves
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction.',
        'weapon_dice'        : '3d6',
        'str_dice'           : 3,
        'attack_delay'       : 14
    },
    'weapon_pickaxe': {
        'name'               : 'pickaxe',
        'category'           : 'weapon',
        'subtype'            : 'axe',
        'damage_type'        : 'stabbing',
        'char'               : 'T',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               :'right hand',
        'description'        : 'A heavy digging implement used by miners. Can be used to dig through the walls '
                               'of the dungeon',
        'stamina_cost'       : 18,
        'str_requirement'    : 14,
        'pierce'             : 1,
        'shred'              : 1,
        'accuracy'           : -3,
        'ctrl_attack'        : actions.dig,
        'ctrl_attack_desc'   : 'Dig - dig through walls in this direction.',
        'break'              : 5.0,
        'weapon_dice'        : '1d4',
        'str_dice'           : 3,
        'attack_delay'       : 28
    },
    'weapon_hatchet': {
        'name'               : 'hatchet',
        'category'           : 'weapon',
        'subtype'            : 'axe',
        'damage_type'        : 'slashing',
        'char'               : 'p',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A one-handed axe made for cutting wood.',
        'stamina_cost'       : 9,
        'str_requirement'    : 10,
        'shred'              : 1,
        'accuracy'           : 3,
        'ctrl_attack'        : player.cleave_attack,
        'ctrl_attack_desc'   : 'Cleave - attack all adjacent enemies. Costs 2x stamina.',
        'weapon_dice'        : '1d6',
        'str_dice'           : 2,
        'attack_delay'       : 16
    },
    'weapon_dane_axe': {
        'name'               : 'dane axe',
        'category'           : 'weapon',
        'subtype'            : 'axe',
        'damage_type'        : 'slashing',
        'char'               : 'P',
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'both hands',
        'description'        : 'A massive, two handed axe made for smashing shields and armor.',
        'stamina_cost'       : 12,
        'str_requirement'    : 18,
        'shred'              : 3,
        'accuracy'           : 3,
        'ctrl_attack'        : player.cleave_attack,
        'ctrl_attack_desc'   : 'Cleave - attack all adjacent enemies. Costs 2x stamina.',
        'weapon_dice'        : '2d10',
        'str_dice'           : 3,
        'attack_delay'       : 16
    },
    'weapon_mace': {
        'name'               : 'mace',
        'category'           : 'weapon',
        'subtype'            : 'club',
        'damage_type'        : 'bludgeoning',
        'char'               : chr(157),
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A one-handed flanged mace. Good against armored enemies',
        'stamina_cost'       : 10,
        'str_requirement'    : 13,
        'shred'              : 2,
        'accuracy'           : 2,
        'weapon_dice'        : '1d6',
        'str_dice'           : 2,
        'on_hit'             : [combat.on_hit_stun],
        'attack_delay'       : 18
    },
    'weapon_warhammer': {
        'name'               : 'warhammer',
        'category'           : 'weapon',
        'subtype'            : 'club',
        'damage_type'        : 'bludgeoning',
        'char'               : chr(157),
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'both hands',
        'description'        : 'A heavy hammer head mounted to a haft. Made for slaying armored foes outright.',
        'stamina_cost'       : 15,
        'str_requirement'    : 20,
        'shred'              : 2,
        'pierce'             : 3,
        'accuracy'           : 1,
        'weapon_dice'        : '1d8',
        'str_dice'           : 4,
        'on_hit'             : [combat.on_hit_stun],
        'attack_delay'       : 20
    },
    'weapon_coal_mace': {
        'name'               : 'coal-brazer mace',
        'category'           : 'weapon',
        'damage_type'        : 'fire',
        'subtype'            : 'club',
        'char'               : chr(157),
        'color'              : libtcodpy.yellow,
        'type'               : 'item',
        'slot'               : 'right hand',
        'description'        : 'A one-handed mace, fitted with a grate for burning coals.',
        'stamina_cost'       : 10,
        'str_requirement'    : 13,
        'shred'              : 2,
        'accuracy'           : 2,
        'weapon_dice'        : '1d6',
        'str_dice'           : 2,
        'on_hit'             : [combat.on_hit_stun],
        'attack_delay'       : 22
    },

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
        'attack_delay'       : 16
    },
    'weapon_diamond_warhammer': {
        'name'               : 'diamond warhammer',
        'category'           : 'weapon',
        'subtype'            : 'club',
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
        'on_hit'             : [combat.on_hit_stun],
        'attack_delay'       : 22
    },
    'weapon_storm_mace': {
        'name'               : 'storm mace',
        'category'           : 'weapon',
        'damage_type'        : 'lightning',
        'subtype'            : 'club',
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
        'attack_delay'       : 22
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
        'attack_delay'       : 14
    },
    'weapon_lifedrinker_dagger': { #lit. german: 'knife'. no english period term
        'name'               : 'lifedrinker dagger',
        'category'           : 'weapon',
        'damage_type'        : 'slashing',
        'subtype'            : 'knife',
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
        'crit_bonus'         : 2
    },
    'weapon_frozen_blade': {
        'name'               : 'frozen blade',
        'category'           : 'weapon',
        'subtype'            : 'sword',
        'damage_type'        : 'slashing',
        'char'               : '/',
        'color'              : libtcodpy.lightest_azure,
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
        'attack_delay'       : 10
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
        'attack_delay'       : 10
    },
    'weapon_soul_reaper': {
        'name'               : 'soul reaper',
        'category'           : 'weapon',
        'subtype'            : 'polearm',
        'damage_type'        : 'stabbing',
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
        'attack_delay'       : 18
    },

    #ARMOR
    'equipment_shield': {
        'name'          : 'Shield',
        'category'      : 'armor',
        'char'          : chr(233), #theta
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'slot'          : 'left hand',
        'description'   : 'An iron kite shield.',
        'ability'       : 'block', #not implemented
        'evasion_bonus' : -2

    },

    'equipment_leather_armor': {
        'name'          : 'Leather Armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'slot'          : 'body',
        'description'   : 'A hardened leather vest.',
        'evasion_bonus' : -1
    },

    'equipment_mail_armor': {
        'name'          : 'Mail Armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 3,
        'evasion_bonus' : -3,
        'slot'          : 'body',
        'description'   : 'A coat of mail made of interlocking iron rings'
    },

    'equipment_brigandine': {
        'name'          : 'Brigandine',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 5,
        'evasion_bonus' : -5,
        'slot'          : 'body',
        'description'   : 'A vest of articulated steel plates'
    },

    'equipment_plate_armor': {
        'name'          : 'Plate armor',
        'category'      : 'armor',
        'char'          : chr(6), #spade
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 7,
        'evasion_bonus' : -7,
        'slot'          : 'body',
        'description'   : 'A hardened steel breastplate'
    },

    'equipment_boob_plate': {
        'name'          : 'Boob Plate',
        'category'      : 'armor',
        'char'          : chr(235), #infinity
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 6,
        'evasion_bonus' : -4,
        'slot'          : 'body',
        'description'   : 'A steel bra that deflects harm from the entire torso by an unknown mechanism'
    },

    'equipment_iron_helm': {
        'name'          : 'Iron Helm',
        'category'      : 'armor',
        'char'          : chr(167),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'evasion_bonus' : -1,
        'slot'          : 'head',
        'description'   : 'A conical iron helm with a nose guard'
    },

    'equipment_great_helm': {
        'name'          : 'Great Helm',
        'category'      : 'armor',
        'char'          : chr(167),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -3,
        'slot'          : 'head',
        'description'   : 'A large cylindrical steel helm. Very heavy and cumbersome'
    },

    'equipment_armet_helm': {
        'name'          : 'Armet Helm',
        'category'      : 'armor',
        'char'          : chr(167),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -1,
        'slot'          : 'head',
        'description'   : 'A crested steel helm with visor and bevor.'
    },

    'equipment_witch_hat': {
        'name'          : 'Witch Hat',
        'category'      : 'armor',
        'char'          : '^',
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 0,
        'evasion_bonus' : 0,
        'slot'          : 'head',
        'description'   : 'A black pointed hat, suitable for the fashionable culdron stirrer.',
        'resistances'   : ['fire','burning']
    },

    'equipment_vambraces' : {
        'name'          : 'Vambraces',
        'category'      : 'armor',
        'char'          : chr(34),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'evasion_bonus' : 0,
        'slot'          : 'arms',
        'description'   : 'A steel forearm guard'
    },

    'equipment_pauldrons' : {
        'name'          : 'Pauldrons',
        'category'      : 'armor',
        'char'          : chr(34),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -3,
        'slot'          : 'arms',
        'description'   : 'A single piece steel shoulder plate'
    },

    'equipment_spaulders' : {
        'name'          : 'Spaulders',
        'category'      : 'armor',
        'char'          : chr(34),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -1,
        'slot'          : 'arms',
        'description'   : 'Articulated steel plates that protect the arms and shoulders'
    },

    'equipment_mail_skirt' : {
        'name'          : 'Mail Skirt',
        'category'      : 'armor',
        'char'          : chr(239),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 1,
        'evasion_bonus' : -1,
        'slot'          : 'legs',
        'description'   : 'A simple skirt of mail that protects the legs'
    },

    'equipment_greaves' : {
        'name'          : 'Greaves',
        'category'      : 'armor',
        'char'          : chr(239),
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'armor_bonus'   : 2,
        'evasion_bonus' : -2,
        'slot'          : 'legs',
        'description'   : 'Steel plates that protect the shins'
    },

    #Charms

    'charm_battle' : {
        'name'          : 'Charm of Battle',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.charm_battle,
        'description'   : 'When infused with essence, this charm summons an elemental weapon.'
    },

    'charm_resistance' : {
        'name'          : 'Charm of Resistance',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.charm_resist,
        'description'   : 'When infused with essence, this charm grants resistance to that type of essence.'
    },

    'charm_blessing' : {
        'name'          : 'Charm of Blessings',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.charm_blessing,
        'description'   : 'When infused with essence, this charm grants magical blessings.'
    },

    'charm_summoning' : {
        'name'          : 'Charm of Summoning',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : actions.charm_summoning,
        'description'   : 'When infused with essence, this charm summons an elemental being as an ally.'
    },

    #Books

    'book_lesser_fire' : {
        'name'          : 'Lesser Book of Fire',
        'category'      : 'book',
        'char'          : '#',
        'color'         : libtcodpy.flame,
        'type'          : 'item',
        'slot'          : 'left hand',
        'description'   : 'A basic book of fire magic',
        'essence':'fire',
        'level' : 1,
        'spells': [
            'spell_heat_ray',
            'spell_flame_wall',
            'spell_fireball',
            'spell_shatter_item',
            'spell_magma_bolt'
        ],
        'levels': [
            'spell_heat_ray', 'spell_flame_wall', 'spell_heat_ray', 'spell_fireball', 'spell_shatter_item',
            'spell_fireball', 'spell_magma_bolt', 'spell_heat_ray','spell_flame_wall', 'spell_fireball',
            'spell_magma_bolt', 'spell_shatter_item', 'spell_magma_bolt'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,3,4,4,4
        ]
    },
}