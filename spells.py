import game as main
import consts
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
    if monster is None: return 'cancelled'
    else:
        old_ai = monster.ai
        monster.ai = main.ConfusedMonster(old_ai)
        monster.ai.owner = monster
        main.message('The ' + monster.name + ' is confused!', libtcod.light_blue)
    
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
