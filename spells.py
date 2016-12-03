import game as main
import consts
import libtcodpy as libtcod

class Spell:
    def __init__(self, name, mana_cost, function, cost_string):
        self.name = name
        self.mana_cost = mana_cost
        self.function = function
        self.cost_string = cost_string

    def cast(self):
        success = self.function()
        if success:
            self.subtract_cost()
        return success

    def check_mana(self):
        pool = []
        for m in main.player.mana:  # Create a mana pool that is a copy of the player's mana pool
            pool.append(m)
        for mana in self.mana_cost:
            if mana == 'normal':  # First check every mana cost other than 'normal'
                continue
            else:
                for i in range(self.mana_cost[mana]):
                    if mana in pool:
                        pool.remove(mana)  # If this mana exists in the pool, remove it and continue looping
                    else:
                        return False  # Special mana does not exist in the pool - failure
        if 'normal' in self.mana_cost:
            if len(pool) < self.mana_cost['normal']:
                return False
        return True

    def subtract_cost(self):
        for mana in self.mana_cost:  # First remove special mana
            if mana == 'normal':
                continue
            for i in range(self.mana_cost[mana]):
                main.player.mana.remove(mana)
        if 'normal' in self.mana_cost:  # Then remove normal mana
            for i in range(self.mana_cost['normal']):
                if 'normal' in main.player.mana:  # First attempt to remove normal mana
                    main.player.mana.remove('normal')
                else:
                    main.player.mana.remove(main.player.mana[len(main.player.mana) - 1]) # Then use rightmost mana

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
    main.player.fighter.heal(consts.HEAL_AMOUNT)


def cast_waterbreathing():
    main.player.fighter.apply_status_effect(main.StatusEffect('waterbreathing', 31, libtcod.light_azure))


def cast_frog_tongue(frog, target):

    if main.roll_to_hit(target, consts.FROG_TONGUE_ACC):
        main.message('The frog pulls you from a distance with its toungue!', libtcod.dark_green)
        target.fighter.take_damage(consts.FROG_TONGUE_DMG)
        beam = main.beam(frog.x, frog.y, target.x, target.y)
        # target.x, target.y = beam[max(len(beam) - 3, 0)]
        pull_to = beam[max(len(beam) - 3, 0)]
        target.set_position(pull_to[0], pull_to[1])
        main.fov_recompute_fn()
    else:
        main.message('The frog tries to grab you with its tongue, but misses!', libtcod.grey)

def cast_manabolt():
    default = None
    if main.selected_monster is not None:
        default = main.selected_monster.x, main.selected_monster.y
    target = main.target_tile(consts.MANABOLT_RANGE, 'beam_interrupt', acc_mod=consts.MANABOLT_ACC, default_target=default)
    if target[0] is not None:
        monster = main.get_monster_at_tile(target[0], target[1])
        if monster is not None:
            if main.roll_to_hit(monster, main.player.fighter.accuracy * consts.MANABOLT_ACC):
                main.message('The manabolt hits the ' + monster.name + ', dealing ' + str(consts.MANABOLT_DMG) + ' damage!', libtcod.light_blue)
                monster.fighter.take_damage(consts.MANABOLT_DMG)
            else:
                main.message('The manabolt misses the ' + monster.name + '.', libtcod.gray)
        else:
            main.message('The manabolt hits the ' + main.dungeon_map[target[0]][target[1]].tile_type + '.', libtcod.light_blue)
        return True
    return False

def cast_mend():
    if main.player.fighter.hp < main.player.fighter.max_hp:
        main.player.fighter.heal(consts.MEND_HEAL)
        main.message('A soft green glow passes over you as your wounds are healed.', libtcod.light_blue)
        return True
    else:
        main.message('You have no need of mending.', libtcod.light_blue)
        return False

spell_library = {
    'manabolt' : Spell('manabolt', { 'normal' : 1 }, cast_manabolt, '[1 normal]'),
    'mend' : Spell('mend', { 'life' : 1 }, cast_mend, '[1 life]')

}

mana_colors = {
    'normal' : libtcod.gray,
    'life' : libtcod.green
}