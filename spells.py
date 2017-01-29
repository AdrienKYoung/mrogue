import libtcodpy as libtcod
import game as main
import consts
import effects
import ui
import ai
import player
import combat
import syntax


class Spell:
    def __init__(self, name, function, description, levels, int_requirement = 10):
        self.name = name
        self.function = function
        self.description = description
        self.levels = levels
        self.int_requirement = int_requirement
        self.max_level = len(levels)

def cast_fireball():
    ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
    (x, y) = ui.target_tile()
    if x is None: return 'cancelled'
    ui.message('The fireball explodes, burning everything within ' + str(consts.FIREBALL_RADIUS) + ' tiles!', libtcod.flame)
    main.create_fire(x,y,10)
    for obj in main.current_map.objects:
        if obj.distance(x, y) <= consts.FIREBALL_RADIUS and obj.fighter:
            ui.message('%s %s burned for %d damage!' % (
                            syntax.name(obj.name).capitalize(),
                            syntax.conjugate(obj is player.instance, ('are','is')),
                            consts.FIREBALL_DAMAGE), libtcod.flame)
            obj.fighter.take_damage(consts.FIREBALL_DAMAGE)
    return 'success'


def cast_confuse():
    ui.message('Choose a target with left-click, or right-click to cancel.', libtcod.white)
    monster = main.target_monster(consts.CONFUSE_RANGE)
    if monster is None or monster.behavior is None: return 'cancelled'
    else:
        if monster.fighter.apply_status_effect(effects.StatusEffect('confusion', consts.CONFUSE_NUM_TURNS, color=libtcod.pink, on_apply=set_confused_behavior)):
            ui.message('%s %s confused!' % (
                            syntax.name(monster.name).capitalize(),
                            syntax.conjugate(monster is player.instance, ('are', 'is'))), libtcod.light_blue)

def set_confused_behavior(object):
    if object.behavior is not None:
        old_ai = object.behavior.behavior
        object.behavior.behavior = ai.ConfusedMonster(old_ai)
        object.behavior.behavior.owner = object

def cast_lightning():
    monster = main.closest_monster(consts.LIGHTNING_RANGE)
    if monster is None:
        ui.message('No targets in range', libtcod.white)
        return 'cancelled'
    else:
        damage = consts.LIGHTNING_DAMAGE
        ui.message('A bolt of lightning strikes %s! %s %s %d damage.' % (
                    syntax.name(monster.name),
                    syntax.pronoun(monster.name),
                    syntax.conjugate(monster is player.instance, ('suffer', 'suffers')),
                    damage), libtcod.light_blue)
        monster.fighter.take_damage(damage)


def cast_heal():
    if player.instance.fighter.hp == player.instance.fighter.max_hp:
        ui.message('You are already at full health.', libtcod.white)
        return 'cancelled'
        
    ui.message('You feel better.', libtcod.white)
    player.instance.fighter.heal(consts.HEAL_AMOUNT)


def cast_waterbreathing():
    player.instance.fighter.apply_status_effect(effects.StatusEffect('waterbreathing', 31, libtcod.light_azure))


def cast_shielding():
    player.instance.fighter.shred = 0
    player.instance.fighter.apply_status_effect(effects.StatusEffect('shielded', 21, libtcod.dark_blue))


def cast_frog_tongue(frog, target):

    ui.message("The frog's tongue lashes out at you!", libtcod.dark_green)
    result = combat.attack_ex(frog.fighter, target, 0, consts.FROG_TONGUE_ACC, consts.FROG_TONGUE_DMG, 0, None, ('pull', 'pulls'), 0, 0, 0)
    if result == 'hit':
        beam = main.beam(frog.x, frog.y, target.x, target.y)
        pull_to = beam[max(len(beam) - 3, 0)]
        target.set_position(pull_to[0], pull_to[1])

def cast_manabolt():
    default = None
    if ui.selected_monster is not None:
        default = ui.selected_monster.x, ui.selected_monster.y
    target = ui.target_tile(consts.MANABOLT_RANGE, 'beam_interrupt', acc_mod=consts.MANABOLT_ACC, default_target=default)
    if target[0] is not None:
        #visual effect
        bolt = main.GameObject(player.instance.x, player.instance.y, 7, 'bolt', color=libtcod.light_blue)
        line = main.beam(player.instance.x, player.instance.y, target[0], target[1])
        main.current_map.add_object(bolt)
        for p in line:
            bolt.set_position(p[0], p[1])
            main.render_map()
            libtcod.console_flush()
        bolt.destroy()
        #game effect
        monster = main.get_monster_at_tile(target[0], target[1])
        if monster is not None:
            if combat.roll_to_hit(monster, player.instance.fighter.accuracy * consts.MANABOLT_ACC):
                ui.message('The manabolt strikes %s, dealing %d damage!' % (syntax.name(monster.name), consts.MANABOLT_DMG), libtcod.light_blue)
                monster.fighter.take_damage(consts.MANABOLT_DMG)
            else:
                ui.message('The manabolt misses %s.' % syntax.name(monster.name), libtcod.gray)
        else:
            ui.message('The manabolt hits the %s.' % main.current_map.tiles[target[0]][target[1]].tile_type, libtcod.light_blue)
        return True
    return False


def cast_ignite():
    target = ui.target_tile(consts.IGNITE_RANGE)
    if target[0] is not None and target[1] is not None:
        tile = main.current_map.tiles[target[0]][target[1]]
        if tile.blocks:
            ui.message('The ' + tile.name + ' is in the way.', libtcod.gray)
            return False
        elif tile.tile_type == 'shallow water' or tile.tile_type == 'deep water':
            ui.message('You cannot ignite water.', libtcod.gray)
            return False
        obj = main.get_objects(target[0], target[1], lambda o: o.blocks)
        if len(obj) > 0:
            ui.message('%s %s in the way' % (
                            syntax.name(obj[0].name).capitalize(),
                            syntax.conjugate(obj[0] is player.instance, ('are', 'is'))), libtcod.gray)
            return False
        ui.message('You conjure a spark of flame, igniting the ' + tile.name + '!', libtcod.flame)
        main.create_fire(target[0], target[1], 10)
        return True
    return False


def cast_mend():
    if player.instance.fighter.hp < player.instance.fighter.max_hp:
        player.instance.fighter.heal(consts.MEND_HEAL)
        ui.message('A soft green glow passes over you as your wounds are healed.', libtcod.light_blue)
        return True
    else:
        ui.message('You have no need of mending.', libtcod.light_blue)
        return False


def cast_forge():
    weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
    if weapon is not None and weapon.owner.item.category == 'weapon':
        if weapon.quality == 'artifact':
            ui.message('Your ' + weapon.owner.name + ' shimmers briefly. It cannot be improved further by this magic.', libtcod.orange)
        else:
            ui.message('Your ' + weapon.owner.name + ' glows bright orange!', libtcod.orange)

            new_quality = ''
            if weapon.quality == 'broken':
                new_quality = 'crude'
            elif weapon.quality == 'crude':
                new_quality = ''
            elif weapon.quality == '':
                new_quality = 'military'
            elif weapon.quality == 'military':
                new_quality = 'fine'
            elif weapon.quality == 'fine':
                new_quality = 'masterwork'
            elif weapon.quality == 'masterwork':
                new_quality = 'artifact'
            main.set_quality(weapon, new_quality)
            ui.message('It is now a ' + weapon.owner.name + '.', libtcod.orange)
    elif weapon is not None and weapon.owner.item.category != 'weapon':
        ui.message('Your ' + weapon.owner.name + ' emits a dull glow. This magic was only intended for weapons!', libtcod.orange)
    else:
        ui.message('Your hands tingle briefly. This magic was only intended for weapons!', libtcod.orange)
    return True

def cast_potion_essence(essence):
    return lambda : player.pick_up_essence(essence,player.instance)

library = {
    #'manabolt' : Spell('manabolt', { 'normal' : 1 }, cast_manabolt, '[1 normal]',"",0),
    #'mend' : Spell('mend', { 'life' : 1 }, cast_mend, '[1 life]',"",0),
    #'ignite' : Spell('ignite', { 'fire' : 1 }, cast_ignite, '[1 fire]',"",0),
    'spell_heat_ray' : Spell(
        'heat ray',
        cast_fireball,
        'Fire a ray of magical heat in a line',
        [
            {'stamina_cost':30,'charges':3},
            {'stamina_cost':25,'charges':4},
            {'stamina_cost':20,'charges':5}
        ],
        10),

    'spell_flame_wall' : Spell(
        'flame wall',
        cast_fireball,
        'Create a wall of flames',
        [
            {'stamina_cost':40,'charges':1},
            {'stamina_cost':35,'charges':2}
        ],
        10),

    'spell_fireball' : Spell(
        'fireball',
        cast_fireball,
        'Fling an exploding fireball',
        [
            {'stamina_cost':50,'charges':1},
            {'stamina_cost':45,'charges':2},
            {'stamina_cost':40,'charges':2}
        ],
        10),

    'spell_shatter_item' : Spell(
        'shatter item',
        cast_fireball,
        'Overheat items to shatter them',
        [
            {'stamina_cost':50,'charges':2}
            ,{'stamina_cost':40,'charges':3}
        ],
        10),

    'spell_magma_bolt' : Spell(
        'magma bolt',
        cast_fireball,
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
    'void' : libtcod.darker_crimson
}