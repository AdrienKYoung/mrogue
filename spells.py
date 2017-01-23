import game as main
import consts
import libtcodpy as libtcod
import effects
import ui
import ai
import player
import combat

class Spell:
    def __init__(self, name, mana_cost, function, cost_string, description, int_requirement):
        self.name = name
        self.mana_cost = mana_cost
        self.function = function
        self.cost_string = cost_string
        self.description = description
        self.int_requirement = int_requirement

    def cast(self):
        success = self.function()
        if success:
            self.subtract_cost()
        return success

    def check_mana(self):
        pool = []
        for m in player.instance.mana:  # Create a mana pool that is a copy of the player's mana pool
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
                player.instance.mana.remove(mana)
        if 'normal' in self.mana_cost:  # Then remove normal mana
            for i in range(self.mana_cost['normal']):
                if 'normal' in player.instance.mana:  # First attempt to remove normal mana
                    player.instance.mana.remove('normal')
                else:
                    player.instance.mana.remove(player.instance.mana[len(player.instance.mana) - 1]) # Then use rightmost mana

def cast_fireball():
    ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
    (x, y) = ui.target_tile()
    if x is None: return 'cancelled'
    ui.message('The fireball explodes, burning everything within ' + str(consts.FIREBALL_RADIUS) + ' tiles!', libtcod.light_blue)
    main.create_fire(x,y,10)
    for obj in main.current_map.objects:
        if obj.distance(x, y) <= consts.FIREBALL_RADIUS and obj.fighter:
            ui.message('The ' + obj.name + ' gets burned for ' + str(consts.FIREBALL_DAMAGE) + ' damage!', libtcod.light_blue)
            obj.fighter.take_damage(consts.FIREBALL_DAMAGE)


def cast_confuse():
    ui.message('Choose a target with left-click, or right-click to cancel.', libtcod.white)
    monster = ui.target_monster(consts.CONFUSE_RANGE)
    if monster is None or monster.ai is None: return 'cancelled'
    else:
        if monster.fighter.apply_status_effect(effects.StatusEffect('confusion', consts.CONFUSE_NUM_TURNS, color=libtcod.pink, on_apply=set_confused_behavior)):
            ui.message('The ' + monster.name + ' is confused!', libtcod.light_blue)

def set_confused_behavior(object):
    if object.ai is not None:
        old_ai = object.ai.behavior
        object.ai.behavior = ai.ConfusedMonster(old_ai)
        object.ai.behavior.owner = object

def cast_lightning():
    monster = main.closest_monster(consts.LIGHTNING_RANGE)
    if monster is None:
        ui.message('No targets in range', libtcod.white)
        return 'cancelled'
    else:
        damage = consts.LIGHTNING_DAMAGE
        ui.message('A bolt of lightning strikes the ' + monster.name + '! It suffers ' + str(damage) + ' damage.', libtcod.light_blue)
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

    if combat.roll_to_hit(target, consts.FROG_TONGUE_ACC):
        ui.message('The frog pulls you from a distance with its tongue!', libtcod.dark_green)
        target.fighter.take_damage(consts.FROG_TONGUE_DMG)
        beam = main.beam(frog.x, frog.y, target.x, target.y)
        # target.x, target.y = beam[max(len(beam) - 3, 0)]
        pull_to = beam[max(len(beam) - 3, 0)]
        target.set_position(pull_to[0], pull_to[1])
    else:
        ui.message('The frog tries to grab you with its tongue, but misses!', libtcod.grey)


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
                ui.message('The manabolt hits the ' + monster.name + ', dealing ' + str(consts.MANABOLT_DMG) + ' damage!', libtcod.light_blue)
                monster.fighter.take_damage(consts.MANABOLT_DMG)
            else:
                ui.message('The manabolt misses the ' + monster.name + '.', libtcod.gray)
        else:
            ui.message('The manabolt hits the ' + main.current_map.tiles[target[0]][target[1]].tile_type + '.', libtcod.light_blue)
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
            ui.message('The ' + obj[0].name + ' is in the way.', libtcod.gray)
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


spell_library = {
    'manabolt' : Spell('manabolt', { 'normal' : 1 }, cast_manabolt, '[1 normal]'),
    'mend' : Spell('mend', { 'life' : 1 }, cast_mend, '[1 life]'),
    'ignite' : Spell('ignite', { 'fire' : 1 }, cast_ignite, '[1 fire]'),
}


mana_colors = {
    'normal' : libtcod.gray,
    'life' : libtcod.green,
    'fire' : libtcod.flame,
    'earth' : libtcod.sepia,
    'dark' : libtcod.dark_purple,
    'water' : libtcod.azure,
    'air' : libtcod.light_sky
}