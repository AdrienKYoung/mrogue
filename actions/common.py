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
import game as main
import ui
import libtcodpy as libtcod
import effects
import syntax
import fov
import spells
import consts

def attack():
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

def attack_reach(actor, target, context):
    if actor is None:
        actor = player.instance
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
    else:
        if abs(actor.x - target.x) <= 2 and abs(actor.y - target.y) <= 2:
            return actor.fighter.attack(target)
        else:
            return 'didnt-take-turn'


def cleave_attack(actor, target, context):
    if actor is None:
        actor = player.instance
    if actor is player.instance:
        return player.cleave_attack(0, 0)
    if isinstance(target, main.GameObject):
        dist = main.distance(actor.x, actor.y, target.x, target.y)
    else:
        dist = main.distance(actor.x, actor.y, target[0], target[1])
    if dist > 1:
        return 'didnt-take-turn'
    for adj in main.adjacent_tiles_diagonal(actor.x, actor.y):
        targets = main.get_objects(adj[0], adj[1], lambda o: o.fighter and o.fighter.team == 'ally')
        for t in targets:
            actor.fighter.attack(t)
    return 'success'

def reach_and_cleave_attack(actor, target, context):
    if actor is None:
        actor = player.instance
    if actor is player.instance:
        return player.reach_and_cleave_attack(0, 0)
    targets = main.get_fighters_in_burst(target[0], target[1], 1, condition=lambda o: o.fighter.team != actor.fighter.team, fov_source=actor)
    for t in targets:
        actor.fighter.attack(t)
    return 'success'

def bash_attack(actor):
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

def summon_equipment(actor, item):
    if actor is player.instance and len(player.instance.fighter.inventory) >= 26:
        ui.message('You are carrying too many items to summon another.')
        return 'didnt-take-turn'

    summoned_equipment = main.create_item(item, material='', quality='')
    if summoned_equipment is None:
        return

    expire_ticker = main.Ticker(15,summon_equipment_on_tick)
    equipped_item = None
    expire_ticker.old_left = None
    if summoned_equipment.equipment.slot == 'both hands':
        equipped_item = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')
        expire_ticker.old_left = main.get_equipped_in_slot(actor.fighter.inventory, 'left hand')
    elif summoned_equipment.equipment.slot == 'floating shield':
        #can't stack two shields
        equipped_item = actor.fighter.get_equipped_shield()
    else:
        equipped_item = main.get_equipped_in_slot(actor.fighter.inventory, summoned_equipment.equipment.slot)
    expire_ticker.old_equipment = equipped_item

    if equipped_item is not None:
        equipped_item.dequip()
    summoned_equipment.item.pick_up(actor,True)
    expire_ticker.equipment = summoned_equipment
    effect = effects.StatusEffect('summoned equipment', expire_ticker.max_ticks + 1, summoned_equipment.color)
    actor.fighter.apply_status_effect(effect)
    expire_ticker.effect = effect
    expire_ticker.owner = actor
    main.current_map.tickers.append(expire_ticker)

    if actor is player.instance:
        ui.message("A {} appears!".format(summoned_equipment.name),libtcod.white)

    return 'success'

def summon_equipment_on_tick(ticker):
    dead_flag = False
    dropped = False
    owner = ticker.owner
    if not owner or not owner.fighter:
        dead_flag = True
    elif not ticker.equipment.equipment.is_equipped:
        if owner is player.instance or fov.player_can_see(owner.x, owner.y):
            ui.message('The %s fades away as %s %s it from %s grasp.' %
                               (ticker.equipment.name.title(),
                                syntax.name(owner),
                                syntax.conjugate(owner is player.instance, ('release', 'releases')),
                                syntax.pronoun(owner, possesive=True)),
                                libtcod.light_blue)
        dead_flag = True
        dropped = True
    elif ticker.ticks > ticker.max_ticks:
        dead_flag = True
        if owner is player.instance or fov.player_can_see(owner.x, owner.y):
            ui.message("The %s fades away as it's essence depletes." % ticker.equipment.name.title(), libtcod.light_blue)
    if dead_flag:
        ticker.dead = True
        if ticker.equipment is not None:
            if hasattr(ticker.equipment.equipment, 'raised'):
                ticker.equipment.equipment.sh_raise()
            ticker.equipment.item.drop(no_message=True)
            ticker.equipment.destroy()
        if owner and owner.fighter:
            owner.fighter.remove_status('summoned equipment')
        if not dropped and owner and owner.fighter:
            if ticker.old_equipment is not None:
                ticker.old_equipment.equip()
            if ticker.old_left is not None:
                ticker.old_left.equip()

def summon_ally(name, duration, x=None, y=None):
    adj = main.adjacent_tiles_diagonal(player.instance.x, player.instance.y)

    # Get viable summoning position. Return failure if no position is available
    if x is None or y is None:
        summon_positions = []
        for tile in adj:
            if not main.is_blocked(tile[0], tile[1]):
                summon_positions.append(tile)
        if len(summon_positions) == 0:
            ui.message('There is no room to summon an ally here.')
            return
        summon_pos = summon_positions[libtcod.random_get_int(0, 0, len(summon_positions) - 1)]
    else:
        summon_pos = (x, y)

    # Select monster type - default to goblin
    import monsters
    if name in monsters.proto.keys():
        summon = main.spawn_monster(name, summon_pos[0], summon_pos[1], team='ally')
        if summon is not None:
            if summon.behavior is not None:
                summon.behavior.follow_target = player.instance

            # Set summon duration
            summon.summon_time = duration + libtcod.random_get_int(0, 0, duration)
        return 'success'
    else:
        return 'didnt-take-turn'

def disarm(target):
    if target is None or target.fighter is None:
        return 'failure'
    weapon = main.get_equipped_in_slot(target.fighter.inventory, 'right hand')
    if weapon is None:
        return 'failure'
    weapon.dequip(no_message=True)
    possible_tiles = []
    for x in range(target.x - 1, target.x + 2):
        for y in range(target.y - 1, target.y + 2):
            if not main.is_blocked(x, y, from_coord=(target.x, target.y), movement_type=1):
                possible_tiles.append((x, y))
    if len(possible_tiles) == 0:
        selected_tile = main.find_closest_open_tile(target.x, target.y)
    else:
        selected_tile = possible_tiles[libtcod.random_get_int(0, 0, len(possible_tiles) - 1)]
    weapon.owner.item.drop(no_message=True)
    weapon.owner.x = selected_tile[0]
    weapon.owner.y = selected_tile[1]
    ui.message('%s %s disarmed!' % (syntax.name(target).capitalize(), syntax.conjugate(target is player.instance, ('are', 'is'))), libtcod.red)
    return 'success'

def teleport(actor, x, y):
    if actor is None:
        actor = player.instance

    if actor is player.instance or fov.player_can_see(actor.x, actor.y):
        ui.message('%s %s in a crackle of magical energy!' %
                   (syntax.name(actor).capitalize(),
                    syntax.conjugate(actor is player.instance, ('vanish', 'vanishes'))),
                    spells.essence_colors['arcane'])
    actor.set_position(x, y)
    if actor is not player.instance and fov.player_can_see(actor.x, actor.y):
        ui.message('%s appears out of thin air!' % syntax.name(actor).capitalize(), spells.essence_colors['arcane'])
    return 'success'

def teleport_random(target):
    destination = main.find_random_open_tile()
    return teleport(target, destination[0], destination[1])

def dig_line(x, y, dx, dy, length, actor=None):
    if actor is None: actor = player.instance
    result = 'failure'
    for i in range(length):
        d = dig(x + dx * i, y + dy * i)
        if result != 'success':
            result = d
    if result == 'success':
        if actor is player.instance or fov.player_can_see(actor.x, actor.y):
            ui.message('The earth parts before %s.' % syntax.name(actor), spells.essence_colors['earth'])
    else:
        if actor is player.instance:
            ui.message('There is nothing to dig in that direction.', libtcod.gray)
    return result

def dig(dig_x, dig_y):
    import player, dungeon
    if dig_x < 0 or dig_y < 0 or dig_x >= consts.MAP_WIDTH or dig_y >= consts.MAP_HEIGHT:
        return 'failed'

    change_type = dungeon.branches[main.current_map.branch]['default_floor']
    if main.current_map.tiles[dig_x][dig_y].elevation != main.current_map.tiles[player.instance.x][player.instance.y].elevation:
        change_type = dungeon.branches[main.current_map.branch]['default_ramp']
    if main.current_map.tiles[dig_x][dig_y].diggable:
        main.current_map.tiles[dig_x][dig_y].tile_type = change_type
        main.changed_tiles.append((dig_x, dig_y))
        if main.current_map.pathfinding:
            main.current_map.pathfinding.mark_unblocked((dig_x, dig_y))
        fov.set_fov_properties(dig_x, dig_y, False)
        fov.set_fov_recompute()
        return 'success'
    else:
        return 'failed'


def heal(amount=consts.HEAL_AMOUNT, use_percentage=False):
    if use_percentage:
        amount = int(round(amount * player.instance.fighter.max_hp))
    if player.instance.fighter.hp == player.instance.fighter.max_hp:
        ui.message('You are already at full health.', libtcod.white)
        return 'cancelled'

    ui.message('You feel better.', libtcod.white)
    player.instance.fighter.heal(amount)

def knock_back(actor,target):
    # check for resistance
    if 'displacement' in target.fighter.immunities:
        if fov.player_can_see(target.x, target.y):
            ui.message('%s %s.' % (syntax.name(target).capitalize(), syntax.conjugate(
                target is player.instance, ('resist', 'resists'))), libtcod.gray)
        return 'resisted'

    # knock the target back one space. Stun it if it cannot move.
    direction = target.x - actor.x, target.y - actor.y  # assumes the instance is adjacent
    stun = False
    against = ''
    against_tile = main.current_map.tiles[target.x + direction[0]][target.y + direction[1]]
    if against_tile.blocks and not against_tile.is_pit:
        stun = True
        against = main.current_map.tiles[target.x + direction[0]][target.y + direction[1]].name
    elif against_tile.elevation != target.elevation and against_tile.tile_type != 'ramp' and \
                    main.current_map.tiles[target.x][target.y] != 'ramp':
        stun = True
        against = 'cliff'
    else:
        for obj in main.current_map.objects:
            if obj.x == target.x + direction[0] and obj.y == target.y + direction[1] and obj.blocks:
                stun = True
                against = obj.name
                break

    if stun:
        #  stun the target
        if target.fighter.apply_status_effect(
                effects.stunned(duration=2)):
            ui.message('%s %s with the %s, stunning %s!' % (
                syntax.name(target).capitalize(),
                syntax.conjugate(target is actor, ('collide', 'collides')),
                against,
                syntax.pronoun(target, objective=True)), libtcod.gold)
    else:
        ui.message('%s %s knocked backwards.' % (
            syntax.name(target).capitalize(),
            syntax.conjugate(target is actor, ('are', 'is'))), libtcod.gray)
        target.set_position(target.x + direction[0], target.y + direction[1])
        main.render_map()
        libtcod.console_flush()

def boomerang(actor, target, context):
    sprites = ['<', 'v', '>', '^']
    ui.render_projectile((actor.x, actor.y), (target.x, target.y), libtcod.yellow, sprites)
    attack_result = actor.fighter.attack(target)
    if attack_result == 'failed':
        return 'didnt-take-turn'
    catch_skill = 30
    if actor.player_stats:
        catch_skill = actor.player_stats.agi
    if main.roll_dice('1d' + str(catch_skill)) >= 10:
        #catch boomerang
        ui.render_projectile((target.x, target.y), (actor.x, actor.y), libtcod.yellow, sprites)
        if actor is player.instance:
            ui.message('You catch the boomerang as it returns to you', libtcod.gray)
    else:
        possible_tiles = []
        for y in range(actor.y - 2, actor.y + 2):
            for x in range(actor.x - 2, actor.x + 2):
                if x >= 0 and y >= 0 and x < consts.MAP_WIDTH and y < consts.MAP_HEIGHT and not main.is_blocked(x, y):
                    possible_tiles.append((x, y))
        if len(possible_tiles) == 0:
            selected_tile = main.find_closest_open_tile(target.x, target.y)
        else:
            selected_tile = possible_tiles[libtcod.random_get_int(0, 0, len(possible_tiles) - 1)]
        ui.render_projectile((target.x, target.y), (selected_tile[0], selected_tile[1]), libtcod.yellow, sprites)
        weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')
        weapon.owner.item.drop(no_message=True)
        weapon.owner.x = selected_tile[0]
        weapon.owner.y = selected_tile[1]
        if actor is player.instance or fov.player_can_see(actor.x, actor.y):
            ui.message('%s boomerang falls to the ground.' % syntax.name(target, possesive=True).capitalize(), libtcod.gray)
        libtcod.console_flush()
