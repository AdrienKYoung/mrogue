import libtcodpy
import spells
import game as main
import abilities
import player
import combat
import dungeon

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
        'scroll_lightning',
        'scroll_fireball',
        'scroll_confusion',
        'scroll_forge',
    ],

    'tomes_1': [
        #'tome_manabolt',
        #'tome_mend',
        #'tome_ignite',
        'book_lesser_fire'
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
    'charm' : { 'plural' : 'charms'}
}

weapon_qualities = {
    'broken' : {
        'dmg' : -3,
        'acc' : -3,
        'shred' : -1,
        'color' : libtcodpy.desaturated_red
    },
    'crude' : {
        'dmg' : -2,
        'acc' : -1,
        'break' : 5.0,
        'color' : libtcodpy.dark_sepia
    },
    '' : { # standard
        'dmg' : 0,
        'acc' : 0,
        'color' : libtcodpy.light_gray
    },
    'military' : {
        'dmg' : 1,
        'acc' : 1,
        'color' : libtcodpy.dark_orange
    },
    'fine' : {
        'dmg' : 2,
        'acc' : 2,
        'break' : -1.5,
        'color' : libtcodpy.sea
    },
    'masterwork' : {
        'dmg' : 3,
        'acc' : 3,
        'shred' : 1,
        'break' : -10.0,
        'color' : libtcodpy.green
    },
    'artifact' : {
        'dmg' : 5,
        'acc' : 5,
        'shred' : 1,
        'peirce' : 1,
        'break' : -1000.0,
        'color' : libtcodpy.yellow
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
}

proto = {

    #SCROLLS
    'scroll_lightning': {
        'name'          : 'Scroll of Lightning Bolt',
        'category'      : 'scroll',
        'char'          : '#',
        'on_use'        : spells.cast_lightning,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'Strikes the nearest foe with a powerful bolt'
    },

    'scroll_fireball': {
        'name'          : 'Scroll of Fireball',
        'category'      : 'scroll',
        'char'          : '#',
        'on_use'        : spells.cast_fireball,
        'color'         : libtcodpy.yellow,
        'type'          : 'item',
        'description'   : 'Fires a flaming projectile at a target that explodes on impact'
    },

    'scroll_confusion': {
        'name'          : 'Scroll of Confusion',
        'category'      : 'scroll',
        'char'          : '#',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_confuse,
        'type'          : 'item',
        'description'   : 'Inflicts confusion on an enemy, causing them to move about erratically.'
    },

    'scroll_forge': {
        'name' : 'Scroll of Forging',
        'category' : 'scroll',
        'char' : '#',
        'color': libtcodpy.yellow,
        'on_use' : spells.cast_forge,
        'type' : 'item',
        'description' : 'Upgrades the quality of your held weapon.'
    },

    #POTIONS
    'potion_healing': {
        'name'          : 'Potion of Healing',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_heal,
        'type'          : 'item',
        'description'   : 'Potion that heals wounds when consumed'
    },

    'potion_waterbreathing': {
        'name'          : 'Potion of Waterbreathing',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_waterbreathing,
        'type'          : 'item',
        'description'   : "Drinking this potion causes temporary gills to form on the drinker's throat, allowing him or "
                          "her to breath water like a fish."
    },

    'potion_shielding': {
        'name'          : 'Potion of Shielding',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_shielding,
        'type'          : 'item',
        'description'   : 'This oily metallic potion bolsters the defenses of anyone who drinks it, repairing shreded'
                          ' armor and temporarily enhancing its effectiveness'
    },

    'potion_lesser_fire': {
        'name'          : 'Potion of Raging Flames',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_potion_essence('fire'), #not a bug, returns a lambda
        'description'   : 'The essence of fires burns within this potion, and drinking it will bestow a single fire essence.'
    },
    'potion_lesser_earth': {
        'name'          : 'Potion of Waking Stone',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_potion_essence('earth'), #not a bug, returns a lambda
        'description'   : 'The essence of stone imbues potion, and drinking it will bestow a single earth essence.'
    },
    'potion_lesser_life': {
        'name'          : 'Potion of Fairy Blossoms',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_potion_essence('life'), #not a bug, returns a lambda
        'description'   : 'The essence of life blesses this potion, and drinking it will bestow a single life essence.'
    },
    'potion_lesser_air': {
        'name'          : 'Potion of Gentle Breeze',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_potion_essence('air'), #not a bug, returns a lambda
        'description'   : 'The essence of air swirls in this potion, and drinking it will bestow a single air essence.'
    },
    'potion_lesser_water': {
        'name'          : 'Potion of Crashing Waves',
        'type'          : 'item',
        'category'      : 'potion',
        'char'          : '!',
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_potion_essence('water'), #not a bug, returns a lambda
        'description'   : 'The essence of water is mixed into this potion, and drinking it will bestow a single water essence.'
    },

    #TOMES
    'tome_manabolt': {
        'name'          : 'Tome of Manabolt',
        'category'      : 'book',
        'char'          : '=',
        'color'         : libtcodpy.yellow,
        'learn_spell'   : 'manabolt',
        'type'          : 'item',
        'description'   : "A weathered book that holds the secrets of Manabolt."
    },

    'tome_mend': {
        'name'          : 'Tome of Mend',
        'category'      : 'book',
        'char'          : '=',
        'color'         : libtcodpy.yellow,
        'learn_spell'   : 'mend',
        'type'          : 'item',
        'description'   : "A weathered book that holds the secrets of Mend."
    },

    'tome_ignite': {
        'name'          : 'Tome of Ignite',
        'category'      : 'book',
        'char'          : '=',
        'color'         : libtcodpy.yellow,
        'learn_spell'   : 'ignite',
        'type'          : 'item',
        'description'   : "A weathered book that holds the secrets of Ignite."
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
    'weapon_messer': {
        'name'               : 'messer',
        'category'           : 'weapon',
        'damage_type'        : 'slashing',
        'subtype'        : 'knife',
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
        'ctrl_attack_desc'   : 'Reach-Attack - attack an enemy up to 2 spaces away in this direction. Deals 50% more '
                               'damage to enemies exactly 2 spaces away.',
        'weapon_dice'        : '2d5',
        'str_dice'           : 1,
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
        'ctrl_attack'        : player.dig,
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
    'weapon_mace': {
        'name'               : 'mace',
        'category'           : 'weapon',
        'subtype'        : 'club',
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
    'weapon_coal_mace': {
        'name'               : 'coal-brazer mace',
        'category'           : 'weapon',
        'damage_type'        : 'fire',
        'subtype'        : 'club',
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

    'charm_resistance' : {
        'name'          : 'Charm of Resistance',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_charm_resist,
        'description'   : 'When infused with essence, this charm grants resistance to that type of essence.'
    },

    'charm_blessing' : {
        'name'          : 'Charm of Blessings',
        'type'          : 'item',
        'category'      : 'charm',
        'char'          : chr(235),
        'color'         : libtcodpy.yellow,
        'on_use'        : spells.cast_charm_blessing,
        'description'   : 'When infused with essence, this charm grants magical blessings.'
    },

    #Books

    'book_lesser_fire' : {
        'name'          : 'Lesser Book of Fire',
        'category'      : 'book',
        'char'          : '#',
        'color'         : libtcodpy.red,
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
            'spell_fireball', 'spell_magma_bolt', 'spell_heat_ray', 'spell_fireball', 'spell_magma_bolt',
            'spell_shatter_item', 'spell_magma_bolt'
        ],
        'level_costs': [
            1,1,1,2,2,2,3,3,3,4,4,4
        ]
    },
}