import game as main
import consts
import math
import libtcodpy as libtcod


def cast_fireball():
    main.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
    (x, y) = main.target_tile()
    if x is None: return 'cancelled'
    main.message('The fireball explodes, burning everything within ' + str(consts.FIREBALL_RADIUS) + ' tiles!', libtcod.light_blue)
    
    for obj in main.objects:
        if obj.distance(x, y) <= consts.FIREBALL_RADIUS and obj.fighter:
            main.message('The ' + obj.name + ' gets burned for ' + str(consts.FIREBALL_DAMAGE) + ' damage!', libtcod.light_blue)
            obj.fighter.take_damage(consts.FIREBALL_DAMAGE)


def cast_confuse():
    main.message('Choose a target with left-click, or right-click to cancel.', libtcod.white)
    monster = main.target_monster(consts.CONFUSE_RANGE)
    if monster is None or monster.ai is None: return 'cancelled'
    else:
        if monster.fighter.apply_status_effect(main.StatusEffect('confusion', consts.CONFUSE_NUM_TURNS, color=libtcod.pink, on_apply=set_confused_behavior)):
            main.message('The ' + monster.name + ' is confused!', libtcod.light_blue)

def set_confused_behavior(object):
    if object.ai is not None:
        old_ai = object.ai.behavior
        object.ai.behavior = main.ConfusedMonster(old_ai)
        object.ai.behavior.owner = object

def cast_lightning():
    monster = main.closest_monster(consts.LIGHTNING_RANGE)
    if monster is None:
        main.message('No targets in range', libtcod.white)
        return 'cancelled'
    else:
        damage = consts.LIGHTNING_DAMAGE
        main.message('A bolt of lightning strikes the ' + monster.name + '! It suffers ' + str(damage) + ' damage.', libtcod.light_blue)
        monster.fighter.take_damage(damage)


def cast_heal():
    if main.player.fighter.hp == main.player.fighter.max_hp:
        main.message('You are already at full health.', libtcod.white)
        return 'cancelled'
        
    main.message('You feel better.', libtcod.white)
    main.player.fighter.heal(20)


def cast_waterbreathing():
    main.player.fighter.apply_status_effect(main.StatusEffect('waterbreathing', 31, libtcod.light_azure))


def cast_frog_tongue(frog, target):

    if main.roll_to_hit(target.fighter.evasion, consts.FROG_TONGUE_ACC):
        main.message('The frog pulls you from a distance with its toungue!', libtcod.dark_green)
        target.fighter.take_damage(consts.FROG_TONGUE_DMG)
        beam = main.beam(frog.x, frog.y, target.x, target.y)
        target.x, target.y = beam[max(len(beam) - 3, 0)]
        main.fov_recompute_fn()
    else:
        main.message('The frog tries to grab you with its tongue, but misses!', libtcod.grey)
