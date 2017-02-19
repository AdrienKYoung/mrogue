

def channel(actor,delay,spell_name,delegate):
    is_player = actor is player.instance
    ui.message_flush(syntax.conjugate(is_player,['You begin',actor.name.capitalize() + ' begins']) + ' to cast ' + spell_name)
    if is_player:
        player.delay(delay,delegate,'channel-spell')
    else:
        actor.behavior.behavior.queue_action(delegate,delay)

def get_cast_time(actor,spell_name):
    base = abilities.data.get(spell_name).get('cast_time',0)
    if actor is None:
        actor = player.instance
        return main.clamp(base - int((actor.player_stats.int - 10) / 5), 0, 5)
    else:
        return base

def attack(actor=None, target=None):
    x,y = ui.target_tile(max_range=1)
    target = None
    for object in main.current_map.fighters:
        if object.x == x and object.y == y:
            target = object
            break
    if target is not None and target is not player.instance:
        result = player.instance.fighter.attack(target)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def attack_reach(actor=None, target=None):
    x, y = ui.target_tile(max_range=1)
    target = None
    for object in main.current_map.fighters:
        if object.x == x and object.y == y:
            target = object
            break
    if target is not None and target is not player.instance:
        result = player.reach_attack(target.x - actor.x, target.y - actor.y)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def bash_attack(actor=None, target=None):
    x,y = ui.target_tile(max_range=1)
    target = None
    for object in main.current_map.fighters:
        if object.x == x and object.y == y:
            target = object
            break
    if target is not None and target is not player.instance:
        result = player.bash_attack(target.x - actor.x,target.y - actor.y)
        if result != 'failed':
            return result
    return 'didnt-take-turn'

def berserk_self(actor=None, target=None):
    if actor is not None and actor.fighter is not None:
        if not actor.fighter.has_status('berserk') and not actor.fighter.has_status('exhausted'):
            actor.fighter.apply_status_effect(effects.berserk())
            if actor is not player.instance:
                ui.message('%s %s!' % (
                                syntax.name(actor.name).capitalize(),
                                syntax.conjugate(False, ('roar', 'roars'))), libtcod.red)
        else:
            if actor is player.instance:
                ui.message("You cannot go berserk right now.", libtcod.yellow)
            return 'didnt-take-turn'

def spawn_vermin(actor=None, target=None):
    #Filthy hackery to add some state
    if not hasattr(actor, 'summons'):
        actor.summons = []

    for s in actor.summons:  # clear dead things from summoned list
        if not s.fighter:
            actor.summons.remove(s)

    if len(actor.summons) < consts.VERMAN_MAX_SUMMONS:
        summon_choice = main.random_choice_index([e['weight'] for e in abilities.vermin_summons])
        summon_tiles = []
        for y in range(5):
            for x in range(5):
                pos = actor.x - 2 + x, actor.y - 2 + y
                if main.in_bounds(pos[0], pos[1]) and not main.is_blocked(pos[0], pos[1]):
                    summon_tiles.append(pos)
        for i in range(abilities.vermin_summons[summon_choice]['count']):
            if len(summon_tiles) > 0:
                pos = summon_tiles[libtcod.random_get_int(0, 0, len(summon_tiles) - 1)]
                spawn = main.spawn_monster(abilities.vermin_summons[summon_choice]['monster'], pos[0], pos[1])
                ui.message('A ' + spawn.name + " crawls from beneath the verman's cloak.", actor.color)
                spawn.fighter.loot_table = None
                actor.summons.append(spawn)
                summon_tiles.remove(pos)

def grapel(actor=None, target=None):
    #Blame the Bleshib
    if actor.distance_to(target) <= consts.FROG_TONGUE_RANGE and fov.monster_can_see_object(actor, target):
        if target.fighter.hp > 0 and main.beam_interrupt(actor.x, actor.y, target.x, target.y) == (target.x, target.y):
            spells.cast_frog_tongue(actor, target)
            return
        else:
            return 'didnt-take-turn'
    else:
        return 'didnt-take-turn'

def raise_zombie(actor=None, target=None):

    check_corpse = main.adjacent_tiles_diagonal(actor.x, actor.y)
    check_corpse.append((actor.x, actor.y))
    corpse = None
    for tile in check_corpse:
        corpses_here = main.get_objects(tile[0], tile[1], lambda o: o.name.startswith('remains of'))
        if len(corpses_here) > 0:
            corpse = corpses_here[0]
            break

    if corpse is not None:
        spawn_tile = main.find_closest_open_tile(corpse.x, corpse.y)
        ui.message('A dark aura emanates from the necroling... a corpse walks again.', libtcod.dark_violet)
        main.spawn_monster('monster_rotting_zombie', spawn_tile[0], spawn_tile[1])
        corpse.destroy()
        return 'rasied-zombie'
    else:
        return 'didnt-take-turn'


def fireball(actor=None, target=None):
    channel(actor, get_cast_time(actor,'ability_fireball'), 'fireball', lambda: _continuation_fireball(actor, target))

def _continuation_fireball(actor, target):
    x, y = 0, 0
    spell = abilities.data['ability_fireball']
    if actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
    else:
        x = target.x
        y = target.y
    if x is None: return 'cancelled'
    ui.message('The fireball explodes!', libtcod.flame)
    main.create_fire(x, y, 10)
    for obj in main.current_map.fighters:
        if obj.distance(x, y) <= spell['radius']:
            combat.spell_attack(actor.fighter, obj, 'ability_fireball')
    return 'success'

def arcane_arrow(actor=None, target=None):
    spell = abilities.data['ability_arcane_arrow']
    x, y = 0, 0
    if actor is None or actor is player.instance:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(spell['range'], 'beam_interrupt', default_target=default_target)
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is None: return 'cancelled'
    line = main.beam(actor.x, actor.y, x, y)
    if line is None or len(line) < 1: return 'cancelled'

    ui.render_projectile((actor.x, actor.y), (x, y), libtcod.fuchsia, None)

    for l in line:
        for obj in main.current_map.fighters:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj,'ability_arcane_arrow')
                return 'success'
    return 'failure'


def heat_ray(actor=None, target=None):
    spell = abilities.data['ability_heat_ray']
    line = None
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(spell['range'], 'beam_interrupt', default_target=default_target)
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is None: return 'cancelled'
    line = main.beam(actor.x, actor.y, x, y)
    if line is None or len(line) < 1: return 'cancelled'

    for obj in main.current_map.fighters:
        for l in line:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj,'ability_heat_ray')
    return 'success'


def flame_wall(actor=None, target=None):
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile()
        if x is None:
            return 'cancelled'
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is not None:
        main.create_fire(x, y, 10)
        return 'success'
    return 'failure'


def shatter_item(actor=None, target=None):
    x, y = 0, 0
    dc = 8
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile()
        if x is None:
            return 'cancelled'
        actor = player.instance
        choices = main.get_objects(x, y)
        if len(choices) > 1:
            target = choices[ui.menu('Which target?', [i.name for i in choices], 24)]
        elif len(choices) > 0:
            target = choices[0]
        else:
            return 'cancelled'
        dc += 4
    else:
        x, y = target.x, target.y

    if target is None:
        return 'cancelled'
    item = None
    inventory = None
    if target.fighter is not None:
        inventory = target.fighter.inventory
        if inventory is None or len(inventory) == 0:
            if actor == player.instance:
                ui.message('Target has no items', libtcod.light_blue)
            return 'cancelled'
        item = inventory[main.random_choice_index(inventory)]
        dc += 5
    elif target.item is not None:
        item = target

    if main.roll_dice('1d20') + main.roll_dice('1d{}'.format(actor.fighter.spell_power)) > dc:
        ui.message("{} shatters into pieces!".format(item.name), libtcod.flame)
        if inventory is not None:
            inventory.remove(item)
        item.destroy()
        for obj in main.current_map.fighters:
            if obj.distance(x, y) <= consts.FIREBALL_RADIUS:
                combat.spell_attack_ex(actor.fighter, obj, None, 'shrapnel', '4d4', 1, 'slashing', 0)
        return 'success'
    else:
        ui.message("Shatter failed to break {}!".format(item), libtcod.yellow)
        return 'success'


def magma_bolt(actor=None, target=None):
    spell = abilities.data['ability_magma_bolt']
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        (x, y) = ui.target_tile(max_range=spell['range'])
        actor = player.instance
        if x is None: return 'cancelled'
        target = main.get_monster_at_tile(x, y)
    else:
        x = target.x
        y = target.y
    if target is not None:
        combat.spell_attack(actor.fighter, target,'ability_magma_bolt')
    main.current_map.tiles[x][y].tile_type = 'lava'
    main.current_map.pathfinding.mark_blocked((x, y))
    main.changed_tiles.append((x, y))


def confuse():
    ui.message('Choose a target with left-click, or right-click to cancel.', libtcod.white)
    ui.render_message_panel()
    libtcod.console_flush()
    monster = main.target_monster(consts.CONFUSE_RANGE)
    if monster is None or monster.behavior is None:
        return 'cancelled'
    else:
        if monster.fighter.apply_status_effect(
                effects.StatusEffect('confusion', consts.CONFUSE_NUM_TURNS, color=libtcod.pink,
                                     on_apply=_set_confused_behavior)):
            ui.message('%s %s confused!' % (
                syntax.name(monster.name).capitalize(),
                syntax.conjugate(monster is player.instance, ('are', 'is'))), libtcod.light_blue)


def _set_confused_behavior(object):
    if object.behavior is not None:
        old_ai = object.behavior.behavior
        object.behavior.behavior = ai.ConfusedMonster(old_ai)
        object.behavior.behavior.owner = object

def heal():
    if player.instance.fighter.hp == player.instance.fighter.max_hp:
        ui.message('You are already at full health.', libtcod.white)
        return 'cancelled'

    ui.message('You feel better.', libtcod.white)
    player.instance.fighter.heal(consts.HEAL_AMOUNT)


def waterbreathing():
    player.instance.fighter.apply_status_effect(effects.StatusEffect('waterbreathing', 31, libtcod.light_azure))


def shielding():
    player.instance.fighter.shred = 0
    player.instance.fighter.apply_status_effect(effects.StatusEffect('shielded', 21, libtcod.dark_blue))


def frog_tongue(frog, target):
    ui.message("The frog's tongue lashes out at you!", libtcod.dark_green)
    result = combat.attack_ex(frog.fighter, target, 0, consts.FROG_TONGUE_ACC, consts.FROG_TONGUE_DMG, None, None,
                              ('pull', 'pulls'), 0, 0, 0)
    if result == 'hit':
        beam = main.beam(frog.x, frog.y, target.x, target.y)
        pull_to = beam[max(len(beam) - 3, 0)]
        target.set_position(pull_to[0], pull_to[1])

def ignite():
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

def dig(dx, dy):
    import player, dungeon
    changed_tiles = main.changed_tiles

    dig_x = player.instance.x + dx
    dig_y = player.instance.y + dy
    change_type = dungeon.branches[main.current_map.branch]['default_floor']
    if main.current_map.tiles[dig_x][dig_y].elevation != main.current_map.tiles[player.instance.x][player.instance.y].elevation:
        change_type = dungeon.branches[main.current_map.branch]['default_ramp']
    if main.current_map.tiles[dig_x][dig_y].diggable:
        main.current_map.tiles[dig_x][dig_y].tile_type = change_type
        changed_tiles.append((dig_x, dig_y))
        if main.current_map.pathfinding:
            main.current_map.pathfinding.mark_unblocked((dig_x, dig_y))
        fov.set_fov_properties(dig_x, dig_y, False)
        fov.set_fov_recompute()
        main.check_breakage(main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand'))
        return 'success'
    else:
        ui.message('You cannot dig there.', libtcod.lightest_gray)
        return 'failed'

def forge():
    weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
    if weapon is not None and weapon.owner.item.category == 'weapon':
        if weapon.quality == 'artifact':
            ui.message('Your ' + weapon.owner.name + ' shimmers briefly. It cannot be improved further by this magic.',
                       libtcod.orange)
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
        ui.message('Your ' + weapon.owner.name + ' emits a dull glow. This magic was only intended for weapons!',
                   libtcod.orange)
    else:
        ui.message('Your hands tingle briefly. This magic was only intended for weapons!', libtcod.orange)
    return True

def potion_essence(essence):
    return lambda : player.pick_up_essence(essence,player.instance)

def charm_resist():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    essence = player.instance.essence[ui.menu("Which essence?",player.instance.essence,24)]
    player.instance.fighter.apply_status_effect(effects.resistant(element=essence))
    if essence in spells.charm_resist_extra_resists:
        for effect in spells.charm_resist_extra_resists[essence]:
            player.instance.fighter.apply_status_effect(effects.resistant(effect=effect,color=spells.essence_colors[essence]),supress_message=True)
    player.instance.essence.remove(essence)

def charm_summoning():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    adj = main.adjacent_tiles_diagonal(player.instance.x, player.instance.y)

    # Get viable summoning position. Return failure if no position is available
    summon_positions = []
    for tile in adj:
        if not main.is_blocked(tile[0], tile[1]):
            summon_positions.append(tile)
    if len(summon_positions) == 0:
        ui.message('There is no room to summon an ally here.')
        return
    summon_pos = summon_positions[libtcod.random_get_int(0, 0, len(summon_positions) - 1)]

    # Select essence
    essence = player.instance.essence[ui.menu("Which essence?",player.instance.essence,24)]
    player.instance.essence.remove(essence)

    # Select monster type - default to goblin
    summon_type = 'monster_goblin'
    import monsters
    if essence in spells.charm_summoning_summons.keys() and spells.charm_summoning_summons[essence]['summon'] in monsters.proto.keys():
        summon_type = spells.charm_summoning_summons[essence]['summon']
    summon = main.spawn_monster(summon_type, summon_pos[0], summon_pos[1], team='ally')
    summon.behavior.follow_target = player.instance

    # Set summon duration
    t = spells.charm_summoning_summons[essence]['duration']
    summon.summon_time = t + libtcod.random_get_int(0, 0, t)

def charm_blessing():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    essence = player.instance.essence[ui.menu("Which essence?",player.instance.essence,24)]
    player.instance.fighter.apply_status_effect(spells.charm_blessing_effects[essence]['buff']())
    player.instance.essence.remove(essence)

def charm_battle():
    if len(player.instance.essence) < 1:
        ui.message("You don't have any essence.", libtcod.light_blue)
        return 'didnt-take-turn'
    essence = player.instance.essence[ui.menu("Which essence?",player.instance.essence,24)]
    import loot
    summoned_weapon = main.create_item(spells.charm_battle_effects[essence]['weapon'], material='', quality='')
    if summoned_weapon is None:
        return
    equipped_weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
    if equipped_weapon is not None:
        equipped_weapon.dequip()
    summoned_weapon.item.pick_up()

import libtcodpy as libtcod
import game as main
import consts
import syntax
import fov
import abilities
import effects
import spells
import ui
import ai
import player
import combat
