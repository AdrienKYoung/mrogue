#mrogue, an interactive adventure game
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

import consts

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
        return main.clamp(base - int((actor.player_stats.int - 10) / 5) - main.has_skill('archmage'), 0, 5)
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


def cleave_attack(actor=None, target=None):
    if actor is None:
        actor = player.instance
    if actor is player.instance:
        return player.cleave_attack(0, 0)
    if actor.distance_to(target) > 1:
        return 'didnt-take-turn'
    for adj in main.adjacent_tiles_diagonal(actor.x, actor.y):
        targets = main.get_objects(adj[0], adj[1], lambda o: o.fighter and o.fighter.team == 'ally')
        for t in targets:
            actor.fighter.attack(t)
    return 'success'

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

def recover_shield(actor=None, target=None):
    if actor is None:
        actor = player.instance
    if actor is not player.instance:  # this should only ever be used by the player
        return 'failure'
    sh = player.instance.fighter.get_equipped_shield()
    if sh is not None:
        cost = sh.sh_raise_cost
        if player.instance.fighter.stamina >= cost:
            player.instance.fighter.adjust_stamina(-sh.sh_raise_cost)
            sh.sh_raise()
            return 'success'
        else:
            ui.message("You don't have enough stamina to raise your shield (Need %d)." % sh.sh_raise_cost, libtcod.gray)
            return 'didnt-take-turn'
    else:
        ui.message("You have no shield to raise.", libtcod.gray)
        return 'didnt-take-turn'

# todo: make more interesting
def essence_fist(actor=None, target=None):
    ability_data = abilities.data['ability_essence_fist']
    x,y = ui.target_tile(max_range=1)
    if x is None:
        return 'didnt-take-turn'

    ops = player.instance.essence
    choice = ui.menu('Which essence?',ops)
    if choice is not None:
        essence = ops[choice]
    else:
        return "didnt-take-turn"

    target = None
    for object in main.current_map.fighters:
        if object.x == x and object.y == y:
            target = object
            break
    if target is not None and target is not player.instance:
        result = combat.attack_ex(player.instance.fighter,target,ability_data['stamina_cost'],damage_multiplier=ability_data['damage_multiplier'])
        if result != 'failed':
            player.instance.essence.remove(essence)
            return result
    return 'didnt-take-turn'

def sweep_attack(actor=None, target=None):
    weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')
    ability_data = abilities.data['ability_sweep']

    if weapon is None or weapon.subtype != 'polearm':
        ui.message('You need a polearm to use this ability')
        return 'didnt-take-turn'

    targets = main.get_objects(actor.x,actor.y,distance=2, condition=lambda o: o.fighter is not None and o.fighter.team != 'ally')
    targets = [t for t in targets if (abs(t.x - actor.x) == 2 or abs(t.y - actor.y) == 2)]
    if len(targets) > 0:
        for enemy in targets:
            combat.attack_ex(actor.fighter,enemy,0, verb=('sweep','sweeps'))
        actor.fighter.adjust_stamina(-(weapon.stamina_cost * ability_data['stamina_multiplier']))
        return True
    else:
        ui.message('There are no targets in range')
        return 'didnt-take-turn'

#note: doesn't support unarmed attacks
def weapon_attack_ex(ability, actor, target):
    weapon = None
    ability_data = abilities.data[ability]

    if actor is None or actor is player.instance:
        actor = player.instance
        weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')

        require_weapon = ability_data.get('require_weapon')
        if require_weapon is not None and (weapon is None or weapon.subtype != require_weapon):
            ui.message('You need a {} to use that ability'.format(require_weapon), libtcod.yellow)
            return 'didnt-take-turn'

        x, y = ui.target_tile(max_range=ability_data.get('max_range',1))
        for object in main.current_map.fighters:
            if object.x == x and object.y == y:
                target = object
                break

        if target is None or target is player.instance:
            return 'didnt-take-turn'
    else:
        weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')

    if target is not None:

        on_hit = weapon.on_hit
        if ability_data.get('on_hit') is not None:
            on_hit.append(ability_data.get('on_hit'))

        damage_multiplier = ability_data.get('damage_multiplier',1)
        if callable(damage_multiplier):
            damage_multiplier = damage_multiplier(actor,target)

        shred_bonus = ability_data.get('shred_bonus',0)
        if callable(shred_bonus):
            shred_bonus = shred_bonus(actor,target)

        result = combat.attack_ex(actor.fighter, target, int(weapon.stamina_cost * ability_data.get('stamina_multiplier',1)),
                                  accuracy_modifier=ability_data.get('accuracy_multiplier',1),
                                  damage_multiplier=damage_multiplier,
                                  guaranteed_shred_modifier=weapon.guaranteed_shred_bonus +
                                                            ability_data.get('guaranteed_shred_bonus',0),
                                  pierce_modifier=weapon.pierce_bonus + ability_data.get('pierce_bonus',0),
                                  shred_modifier=weapon.shred_bonus + shred_bonus,
                                  verb=ability_data.get('verb'), on_hit=on_hit)

        if result != 'failed' and result != 'didnt-take-turn':
            return result
    return 'didnt-take-turn'

#automates some nasty currying needed to pass ability into on_hit functions
def on_hit_tx(delegate,ability):
    return lambda a,b,c: delegate(ability,a,b,c)

def exhaust_self(ability,actor,*_):
    ability_data = abilities.data[ability]
    actor.fighter.apply_status_effect(effects.exhausted(ability_data['exhaustion_duration']))

def swap(actor,target,_):
    actor.swap_positions(target)

def mace_stun(attacker, target, damage):
    scaling_factor = 1
    stun_duration = 2
    if target.fighter is None:
        return
    if(attacker is player.instance):
        scaling_factor = attacker.player_stats.str / 10
        if main.has_skill('ringing_blows'):
            scaling_factor *= 1.5
            stun_duration = 3
    if libtcod.random_get_float(0,0.0,1.0) * scaling_factor > 0.85:
        if attacker == player.instance:
            ui.message("Your " + main.get_equipped_in_slot(player.instance.fighter.inventory,'right hand').owner.name.title() + " rings out!",libtcod.blue)
        target.fighter.apply_status_effect(effects.stunned())

def berserk_self(actor=None, target=None):
    if actor is not None and actor.fighter is not None:
        if not actor.fighter.has_status('berserk') and not actor.fighter.has_status('exhausted'):
            actor.fighter.apply_status_effect(effects.berserk())
            if actor is not player.instance:
                ui.message('%s %s!' % (
                                syntax.name(actor).capitalize(),
                                syntax.conjugate(False, ('roar', 'roars'))), libtcod.red)
            return 'success'
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

def spawn_spiders(actor=None, target=None):
    #Filthy hackery to add some state
    ability = abilities.data['ability_summon_spiders']
    if not hasattr(actor, 'summons'):
        actor.summons = []

    for s in actor.summons:  # clear dead things from summoned list
        if not s.fighter:
            actor.summons.remove(s)

    if len(actor.summons) < ability['max_summons']:
        summon_tiles = []
        for y in range(3):
            for x in range(3):
                pos = actor.x - 1 + x, actor.y - 1 + y
                if main.in_bounds(pos[0], pos[1]) and not main.is_blocked(pos[0], pos[1]):
                    summon_tiles.append(pos)
        summon_count = main.roll_dice(ability['summons_per_cast'])
        for i in range(summon_count):
            if len(summon_tiles) > 0 and len(actor.summons) < ability['max_summons']:
                pos = summon_tiles[libtcod.random_get_int(0, 0, len(summon_tiles) - 1)]
                spawn = main.spawn_monster('monster_tunnel_spider', pos[0], pos[1])
                ui.message('A ' + spawn.name + " crawls from beneath %s cloak." % syntax.name(actor, possesive=True), actor.color)
                actor.summons.append(spawn)
                summon_tiles.remove(pos)
        return 'success'
    return 'cancelled'

def web_bomb(actor=None, target=None):
    if actor is None:
        ui.message('Yo implement this', libtcod.red)
        return 'failure'
    if target is not None:
        main.tunnel_spider_spawn_web(target)
        if actor is player.instance or fov.player_can_see(target.x, target.y):
            ui.message('%s summons spiderwebs.' % syntax.name(actor).capitalize(), actor.color)
        return 'success'
    return 'cancelled'

def raise_zombie(actor=None, target=None):
    if actor is None:
        actor = player.instance
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
        ui.message('A dark aura emanates from %s... a corpse walks again.' % syntax.name(actor), libtcod.dark_violet)
        zombie = main.spawn_monster('monster_rotting_zombie', spawn_tile[0], spawn_tile[1])
        if actor is player.instance:
            zombie.fighter.team = 'ally'
            zombie.behavior.follow_target = player.instance
        corpse.destroy()
        return 'rasied-zombie'
    else:
        return 'didnt-take-turn'


def fireball(actor=None, target=None):
    if actor is None:
        actor = player.instance
    channel(actor, get_cast_time(actor,'ability_fireball'), 'fireball', lambda: _continuation_fireball(actor, target))
    return 'success'

def _continuation_fireball(actor, target):
    x, y = 0, 0
    spell = abilities.data['ability_fireball']
    if actor is player.instance:  # player is casting
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'], default_target=default_target)
    else:
        x = target.x
        y = target.y
    if x is None: return 'cancelled'
    ui.message('The fireball explodes!', libtcod.flame)
    ui.render_explosion(x, y, 1, libtcod.yellow, libtcod.flame)
    for obj in main.current_map.fighters:
        if obj.distance(x, y) <= spell['radius']:
            combat.spell_attack(actor.fighter, obj, 'ability_fireball')
            if obj.fighter is not None:
                obj.fighter.apply_status_effect(effects.burning())
    for _x in range(x - 1, x + 2):
        for _y in range(y - 1, y + 2):
            main.melt_ice(_x, _y)
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

def offhand_shot(actor=None, target=None):
    x, y = 0, 0

    if actor is None:
        actor = player.instance

    weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'left hand')

    if actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(*ui.target_tile(weapon.range, 'pick', default_target=default_target))

    if target is not None:
        ui.render_projectile((actor.x, actor.y), (target.x, target.y), libtcod.white)
        combat.attack_ex(actor.fighter,target,0,verb=("shoot","shoots"),weapon=weapon)
        return 'success'
    else:
        return "cancelled"

def focus(actor=None, target=None):
    if actor is None:
        actor = player.instance
    actor.fighter.apply_status_effect(effects.focused(duration=2))
    return 'success'

def healing_trance(actor=None, target=None):
    if actor is None:
        actor = player.instance
    if actor.fighter:
        actor.fighter.apply_status_effect(effects.stunned(duration=15))
        actor.fighter.apply_status_effect(effects.regeneration(duration=15))
        return 'success'
    return 'cancelled'

def reeker_breath(actor=None, target=None):
    if actor is None:
        actor = player.instance
    spell = abilities.data['ability_reeker_breath']
    if actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        tiles = ui.target_tile(max_range=spell['range'], targeting_type='cone')
    else:
        x = target.x
        y = target.y
        tiles = main.cone(actor.x,actor.y,x,y,max_range=spell['range'])

    if tiles is None or len(tiles) == 0 or tiles[0] is None:
        return 'cancelled'

    if fov.player_can_see(target.x, target.y) or actor is player.instance:
        ui.message('%s %s a cloud of acrid fumes!' %
                   (syntax.name(actor).capitalize(),
                    syntax.conjugate(actor is player.instance, ('breathe', 'breathes'))), libtcod.fuchsia)
    for tile in tiles:
        main.create_reeker_gas(tile[0], tile[1], duration=main.roll_dice('1d6')+3)
        for obj in main.current_map.fighters:
            if obj.x == tile[0] and obj.y == tile[1]:
                combat.spell_attack(actor.fighter, obj, 'ability_reeker_breath')
1
def flame_breath(actor=None, target=None):
    x, y = 0, 0
    if actor is None:
        actor = player.instance
    spell = abilities.data['ability_flame_breath']
    if actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        tiles = ui.target_tile(max_range=spell['range'], targeting_type='cone')
    else:
        x = target.x
        y = target.y
        tiles = main.cone(actor.x,actor.y,x,y,max_range=spell['range'])

    if tiles is None or len(tiles) == 0 or tiles[0] is None or tiles[1] is None:
        return 'cancelled'

    for tile in tiles:
        t = main.current_map.tiles[tile[0]][tile[1]]
        if t.flammable or main.roll_dice('1d2') == 1:
            main.create_fire(tile[0],tile[1],12)

        for obj in main.current_map.fighters:
            if obj.x == tile[0] and obj.y == tile[1]:
                combat.spell_attack(actor.fighter, obj, 'ability_flame_breath')
                if obj.fighter is not None:
                    obj.fighter.apply_status_effect(effects.burning())

    return 'success'

def great_dive(actor=None,target=None):
    x,y = 0,0
    data = abilities.data['ability_great_dive']
    if actor is None:  # player is casting
        actor = player.instance
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=data['range'])
    else:
        x = target.x
        y = target.y

    warning_particles = []
    if actor is not player.instance:
        for tile in main.adjacent_inclusive(x,y):
            go = main.GameObject(tile[0],tile[1],'X','Warning',libtcod.red,
                                 description="Spell Warning. Source: {}".format(actor.name.capitalize()))
            main.current_map.add_object(go)
            warning_particles.append(go)

    ui.message("{} {} high into the air!".format(
        syntax.name(actor).capitalize(),
        syntax.conjugate(actor is player.instance, ['rise','rises'])
    ))

    channel(actor, get_cast_time(actor,'ability_great_dive'), 'ability_great_dive',
            lambda: _continuation_great_dive(actor, x,y,warning_particles))
    return 'success'

def _continuation_great_dive(actor,x,y,ui_particles):
    data = abilities.data['ability_great_dive']
    for p in ui_particles:
        p.destroy()

    ui.message("{} {} into the ground!".format(
        syntax.name(actor).capitalize(),
        syntax.conjugate(actor is player.instance, ['slam', 'slams'])
    ))

    tiles = main.adjacent_inclusive(x,y)
    for obj in main.current_map.fighters:
        if (obj.x,obj.y) in tiles:
            combat.attack_ex(actor.fighter,obj,0)

    if not main.is_blocked(x,y):
        actor.set_position(x,y)
    else:
        for t in tiles:
            if not main.is_blocked(t[0],t[1]):
                actor.set_position(t[0],t[1])
                break

def heat_ray(actor=None, target=None):
    spell = abilities.data['a' \
                           'bility_heat_ray']
    line = None
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        tiles = ui.target_tile(spell['range'], 'beam', default_target=default_target)
        actor = player.instance
    else:
        x = target.x
        y = target.y
        tiles = main.beam(actor.x, actor.y, x, y)
    if tiles is None or len(tiles) < 1 or tiles[0] is None or tiles[0][0] is None: return 'cancelled'
    end = (tiles[len(tiles) - 1][0], tiles[len(tiles) - 1][1])
    ui.render_projectile((actor.x, actor.y), end, libtcod.flame, libtcod.CHAR_BLOCK3)

    for obj in main.current_map.fighters:
        for l in tiles:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj,'ability_heat_ray')

    main.melt_ice(end[0], end[1])

    return 'success'


def flame_wall(actor=None, target=None):
    x, y = 0, 0
    spell = abilities.data['ability_flame_wall']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
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
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile()
        if x is None:
            return 'cancelled'
        actor = player.instance
        choices = main.get_objects(x, y, lambda o:o.fighter and o.fighter.inventory and len(o.fighter.inventory) > 0)
        if len(choices) == 0:
            choices = main.get_objects(x, y, lambda o:o.item is not None)
        if len(choices) > 1:
            target = choices[ui.menu('Which target?', [i.name for i in choices], 24)]
        elif len(choices) > 0:
            target = choices[0]
        else:
            ui.message('No valid targets here', libtcod.gray)
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
        item = inventory[libtcod.random_get_int(0, 0, len(inventory) - 1)]
        dc += 5
    elif target.item is not None:
        item = target

    if main.roll_dice('1d20') + main.roll_dice('1d{}'.format(actor.fighter.spell_power)) > dc:
        ui.render_explosion(x, y, 1, libtcod.yellow, libtcod.flame)
        ui.message("The {} shatters into pieces!".format(item.name), libtcod.flame)
        if inventory is not None:
            inventory.remove(item)
        item.destroy()
        for obj in main.current_map.fighters:
            if obj.distance(x, y) <= consts.FIREBALL_RADIUS:
                combat.spell_attack_ex(actor.fighter, obj, None, '4d4', 1, 'slashing', 0)
        return 'success'
    else:
        ui.message("Shatter failed to break the {}!".format(item.name), libtcod.yellow)
        return 'success'


def magma_bolt(actor=None, target=None):
    spell = abilities.data['ability_magma_bolt']
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
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
    return 'success'

def avalanche(actor=None, target=None):
    spell = abilities.data['ability_avalanche']
    x, y = 0, 0
    if actor is None:
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        tiles = ui.target_tile(spell['range'], 'beam_wide', default_target=default_target)
        actor = player.instance
    else:
        x = target.x
        y = target.y
        tiles = main.beam(actor.x, actor.y, x, y)
    if tiles is None or len(tiles) < 1 or tiles[0] is None or tiles[0][0] is None:
        return 'cancelled'

    for l in tiles:
        for obj in main.current_map.fighters:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj, 'ability_avalanche')
                if actor.fighter is not None:
                    actor.fighter.apply_status_effect(effects.immobilized())
        if libtcod.random_get_int(0, 0, 3) > 0:
            tile = main.current_map.tiles[l[0]][l[1]]
            if tile.is_floor and tile.tile_type != 'snow drift' and tile.tile_type != 'ice':
                tile.tile_type = 'snow drift'
                main.changed_tiles.append(l)
            if tile.is_water:
                tile.tile_type = 'ice'
                main.changed_tiles.append(l)

    return 'success'

def frozen_orb(actor=None, target=None):
    spell = abilities.data['ability_frozen_orb']
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=spell['range'], default_target=default_target)
        actor = player.instance
        if x is None: return 'cancelled'
        target = main.get_monster_at_tile(x, y)
    if target is not None:
        if combat.spell_attack(actor.fighter, target,'ability_frozen_orb') == 'hit' and target.fighter is not None:
            target.fighter.apply_status_effect(effects.slowed())
        return 'success'

def flash_frost(actor=None, target=None):
    spell = abilities.data['ability_flash_frost']
    x, y = 0, 0
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        actor = player.instance
        if x is None: return 'cancelled'
        target = main.get_monster_at_tile(x, y)
    if target is not None:
        target.fighter.apply_status_effect(effects.frozen(5))
        if actor is player.instance or fov.player_can_see(target.x, target.y):
            ui.message('%s %s frozen solid!' %
                       (syntax.name(target).capitalize(),
                        syntax.conjugate(target is player.instance, ('are', 'is'))),
                        spells.essence_colors['cold'])
        return 'success'
    else:
        if actor is player.instance:
            ui.message('There is no one to freeze here.', libtcod.gray)
        return 'didnt-take-turn'

def ice_shards(actor=None, target=None):
    x, y = 0, 0
    if actor is None:
        actor = player.instance
    spell = abilities.data['ability_ice_shards']
    if actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        tiles = ui.target_tile(max_range=spell['range'], targeting_type='cone')
    else:
        tiles = [(target.x, target.y)]
        x = target.x
        y = target.y
    if tiles is None or len(tiles) == 0 or tiles[0] is None or tiles[1] is None: return 'cancelled'
    for tile in tiles:
        reed = main.object_at_tile(tile[0], tile[1], 'reeds')
        if reed is not None:
            reed.destroy()
        for obj in main.current_map.fighters:
            if obj.x == tile[0] and obj.y == tile[1]:
                combat.spell_attack(actor.fighter, obj, 'ability_ice_shards')
                if obj.fighter is not None:
                    obj.fighter.apply_status_effect(effects.slowed())
                    obj.fighter.apply_status_effect(effects.bleeding())
    return 'success'

def snowstorm(actor=None, target=None):
    x, y = 0, 0
    spell = abilities.data['ability_snowstorm']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        if x is None:
            return 'cancelled'
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is not None:
        zone = main.Zone(spell['radius'],_snowstorm_tick,_snowstorm_tick)
        storm = main.GameObject(x,y,'@','Snowstorm',libtcod.light_azure,zones=[zone],summon_time=10)
        storm.creator = actor
        return 'success'
    else:
        return 'failure'

def _snowstorm_tick(actor,target):
    if main.roll_dice('1d10' > 7):
        combat.spell_attack(actor.owner.creator.fighter,target,'ability_snowstorm')
        target.fighter.apply_status_effect(effects.slowed())
        target.fighter.apply_status_effect(effects.blinded())
        fx = main.GameObject(target.x,target.y,'*','cloud of cold',libtcod.light_azure,summon_time=2)
        main.current_map.objects.append(fx)

def hex(actor=None,target=None):
    x, y = 0, 0
    spell = abilities.data['ability_hex']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=spell['range'], default_target=default_target)
        if x is None: return 'cancelled'
        actor = player.instance
        target = main.get_monster_at_tile(x, y)
    if target is not None:
        target.fighter.apply_status_effect(effects.cursed())
    return 'success'

def defile(actor=None,target=None):
    x, y = 0, 0
    spell = abilities.data['ability_defile']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=spell['range'], default_target=default_target)
        if x is None: return 'cancelled'
        actor = player.instance
        target = main.object_at_coords(x, y)
    if target is not None:
        if target.is_corpse:
            main.raise_dead(actor,target, duration=100)
        elif target.fighter is not None and (target.fighter.subtype == 'undead' or target.fighter.subtype == 'fiend'):
            target.fighter.heal(int(target.fighter.max_hp / 3))
            ui.message("Dark magic strengthens {}!".format(target.name))
        elif target.fighter is not None:
            combat.spell_attack(actor.fighter, target, 'ability_defile')
    return 'success'

def shackles_of_the_dead(actor=None,target=None):
    x, y = 0, 0
    spell = abilities.data['ability_defile']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=spell['range'], default_target=default_target)
        if x is None: return 'cancelled'
        actor = player.instance
    else:
        x = target.x
        y = target.y

    for (_x,_y) in main.adjacent_tiles_diagonal(x,y):
        obj = main.get_monster_at_tile(_x,_y)
        if obj is not None:
            obj.fighter.apply_status_effect(effects.immobilized())
    return 'success'

def sacrifice(actor=None,target=None):
    if actor is None:
        actor = player.instance

    spell = abilities.data['ability_sacrifice']
    actor.fighter.take_damage(min(30,int(actor.fighter.hp / 2)), attacker=actor)
    damage_mod = int((actor.fighter.max_hp - actor.fighter.hp )/ actor.fighter.max_hp)
    ui.render_explosion(actor.x, actor.y, 1, libtcod.violet, libtcod.darkest_violet)

    for (_x,_y) in main.adjacent_tiles_diagonal(actor.x,actor.y):
        obj = main.get_monster_at_tile(_x,_y)
        if obj is not None and obj.fighter.team == 'enemy':
            combat.spell_attack_ex(actor.fighter,obj,None,spell['base_damage'],0,'death',spell['pierce'],0,1 + damage_mod)
    return 'success'

def corpse_dance(actor=None,target=None):
    x, y = 0, 0
    spell = abilities.data['ability_corpse_dance']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        if x is None: return 'cancelled'
        actor = player.instance
    else:
        x = actor.x
        y = actor.y

    ui.render_explosion(x, y, spell['radius'], libtcod.violet, libtcod.light_yellow)
    ui.message("{} calls the dead to dance!".format(syntax.conjugate(actor is player.instance,["You",actor.name.capitalize()])))

    for o in main.get_objects(x,y,None,spell['radius']):
        if o is not None and o.is_corpse:
            main.raise_dead(actor,o)

        if o.fighter is not None and o.fighter.team == actor.fighter.team and o.fighter.subtype == 'undead':
            o.fighter.apply_status_effect(effects.swiftness(spell['buff_duration']))
            o.fighter.apply_status_effect(effects.berserk(spell['buff_duration']))
    return 'success'

def bless(actor=None, target=None):
    if actor is None:
        actor = player.instance
    actor.fighter.apply_status_effect(effects.blessed())
    return 'success'

def smite(actor=None, target=None):
    spell = abilities.data['ability_smite']
    x, y = 0, 0
    if actor is None or actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(*ui.target_tile(spell['range'],'pick', default_target=default_target))
        actor = player.instance

    if target is None:
        return 'cancelled'

    combat.spell_attack(actor.fighter, target,'ability_smite')
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.judgement(main.roll_dice('2d8')))
        if(target.fighter.has_flag('EVIL')):
            target.fighter.apply_status_effect(effects.stunned())
    return 'success'

def castigate(actor=None, target=None):
    if actor is None:
        actor = player.instance

    ui.render_explosion(actor.x, actor.y, 1, libtcod.violet, libtcod.light_yellow)
    for (_x,_y) in main.adjacent_tiles_diagonal(actor.x,actor.y):
        obj = main.get_monster_at_tile(_x,_y)
        if obj is not None and obj.fighter.team == 'enemy':
            obj.fighter.apply_status_effect(effects.judgement(stacks=main.roll_dice('3d8')))

#player only
def blessed_aegis(actor=None, target=None):
    if actor is None:
        actor = player.instance

    summon_equipment('shield_blessed_aegis')

def holy_lance(actor=None, target=None):
    x, y = 0, 0
    spell = abilities.data['ability_holy_lance']
    if actor is None:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        if x is None:
            return 'cancelled'
        actor = player.instance
    else:
        x = target.x
        y = target.y
    if x is not None:
        ui.render_explosion(x, y, spell['radius'], libtcod.violet, libtcod.light_yellow)

        lance = main.GameObject(x, y, chr(23), 'Holy Lance', libtcod.light_azure, on_tick=_holy_lance_tick, summon_time=10)
        lance.creator = actor
        main.current_map.add_object(lance)

        for obj in main.get_fighters_in_burst(x,y,spell['radius'],lance,actor.fighter.team):
                combat.spell_attack(actor.fighter, obj, 'ability_holy_lance')
        return 'success'
    else:
        return 'failure'


def _holy_lance_tick(actor):
    spell = abilities.data['ability_holy_lance']
    ui.render_explosion(actor.x, actor.y, spell['radius'], libtcod.violet, libtcod.light_yellow)
    for obj in main.get_fighters_in_burst(actor.x, actor.y, spell['radius'], actor, actor.creator.fighter.team):
        combat.spell_attack(actor.fighter, obj, 'ability_holy_lance_tick')

def green_touch(actor=None, target=None):
    spell = abilities.data['ability_green_touch']
    if actor is None:
        actor = player.instance
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        if x is None: return 'cancelled'
    else:
        x = target.x
        y = target.y

    import mapgen
    t = main.current_map.tiles[x][y]
    if not t.is_floor:
        if actor is player.instance:
            ui.message('You cannot grow grass here.', libtcod.gray)
        return 'cancelled'
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('Grass springs from the ground!', spells.essence_colors['life'])
    grass = mapgen.create_terrain_patch((x, y), 'grass floor', min_patch=4, max_patch=12)
    mapgen.scatter_reeds(grass, probability=30)
    for tile in grass:
        main.changed_tiles.append(tile)
        fov.set_fov_properties(tile[0], tile[1], len(main.get_objects(tile[0], tile[1], lambda o: o.blocks_sight)) > 0,
                               elevation=main.current_map.tiles[tile[0]][tile[1]].elevation)
    return 'success'

def fungal_growth(actor=None, target=None):
    spell = abilities.data['ability_fungal_growth']
    if actor is None:
        actor = player.instance
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        if x is None: return 'cancelled'
        corpse = main.get_objects(x, y, lambda o: o.is_corpse)
        if len(corpse) == 0:
            ui.message('No suitable corpses here.', libtcod.gray)
            return 'cancelled'
        target = corpse[0]

    if not target.is_corpse:
        return 'failure'
    main.spawn_monster('monster_blastcap', target.x, target.y)
    if actor is player.instance or fov.player_can_see(target.x, target.y):
        ui.message('A blastcap grows from %s.' % syntax.name(target), spells.essence_colors['life'])
    target.destroy()
    return 'success'

def summon_dragonweed(actor=None, target=None):
    spell = abilities.data['ability_summon_dragonweed']
    if actor is None:
        actor = player.instance
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile(max_range=spell['range'])
        if x is None: return 'cancelled'
    else:
        (x, y) = main.find_closest_open_tile(target.x, target.y)
    tile = main.current_map.tiles[x][y]
    if tile.tile_type != 'grass floor':
        if actor is player.instance:
            ui.message('The dragonseed must be planted on grass.', libtcod.gray)
        return 'cancelled'
    seed = main.GameObject(x, y, 'w', 'dragonweed sapling', libtcod.dark_chartreuse,
                           description='A small, scaly blulb surrounded by sharp, thin leaves. In a few turns, '
                                       'it will grow into a full-sized Dragonweed.')
    main.current_map.add_object(seed)
    seed_ticker = main.Ticker(4, _dragonseed_ticker)
    seed_ticker.seed = seed
    main.current_map.tickers.append(seed_ticker)
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('A dragonseed is planted...', libtcod.dark_chartreuse)
    return 'success'

def _dragonseed_ticker(ticker):
    dead_flag = False
    if ticker.ticks >= ticker.max_ticks:
        ticker.dead = True
        ui.message("The dragonweed sapling matures.", libtcod.dark_chartreuse)
        x = ticker.seed.x
        y = ticker.seed.y
        ticker.seed.destroy()
        for obj in main.get_objects(x, y, lambda o: o.blocks):
            t = main.find_closest_open_tile(x, y)
            obj.set_position(t[0], t[1])
        summon_ally('monster_dragonweed', 10 + libtcod.random_get_int(0, 0, 20), x, y)

def battle_cry(actor=None,target=None):
    if actor is None:
        actor = player.instance

    for unit in main.current_map.fighters:
        if unit.fighter.team != actor.fighter.team:
            unit.fighter.apply_status_effect(effects.cursed(20))
            if unit.behavior is not None and hasattr(unit.behavior,'ai_state'):
                unit.behavior.ai_state = 'pursuing'
                unit.behavior.last_seen_position = player.instance.x, player.instance.y

    ui.message("{} {} out a battle cry!".format(
        syntax.conjugate(actor is player.instance,['You',actor.name]),
        syntax.conjugate(actor is player.instance,['let','lets'])
    ))

    return 'success'

def mass_heal(actor=None,target=None):
    if actor is None:
        actor = player.instance

    for unit in main.current_map.fighters:
        if unit.fighter.team == actor.fighter.team:
            unit.fighter.apply_status_effect(effects.regeneration())
            amount = int(round(0.25 * unit.fighter.max_hp))
            unit.fighter.heal(amount)
            ui.message("{} {} healed!".format(syntax.conjugate(unit is player.instance,['You',unit.name]),
                       syntax.conjugate(unit is player.instance,['were','was'])), libtcod.white)
    return 'success'

def mass_cleanse(actor=None,target=None):
    if actor is None:
        actor = player.instance

    for unit in main.current_map.fighters:
        if unit.fighter.team == actor.fighter.team:
            effects = list(player.instance.fighter.status_effects)
            for status in effects:
                if status.cleanseable:
                    player.instance.fighter.remove_status(status.name)
    return 'success'

def mass_reflect(actor=None,target=None):
    if actor is None:
        actor = player.instance

    for unit in main.current_map.fighters:
        if unit.fighter.team == actor.fighter.team:
            unit.fighter.apply_status_effect(effects.reflect_magic())
    return 'success'

def firebomb(actor=None, target=None):
    if actor is None:
        actor = player.instance
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=6, default_target=default_target, targeting_type='beam_interrupt')
        if x is None: return 'cancelled'
        actor = player.instance
    else:
        (x, y) = target.x, target.y
    ui.render_projectile((actor.x, actor.y), (x, y), spells.essence_colors['fire'], chr(7))
    ui.render_explosion(x, y, 1, libtcod.yellow, libtcod.flame)
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('The firebomb explodes!', spells.essence_colors['fire'])
    for adj in main.adjacent_inclusive(x, y):
        for f in main.current_map.fighters:
            if f.x == adj[0] and f.y == adj[1]:
                if combat.spell_attack_ex(actor.fighter, f, None, '4d10', 0, 'fire', 0) == 'hit' and f.fighter is not None:
                    f.fighter.apply_status_effect(effects.burning())

def icebomb(actor=None, target=None):
    if actor is None:
        actor = player.instance
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=6, default_target=default_target, targeting_type='beam_interrupt')
        if x is None: return 'cancelled'
        actor = player.instance
    else:
        (x, y) = target.x, target.y
    ui.render_projectile((actor.x, actor.y), (x, y), spells.essence_colors['cold'], chr(7))
    ui.render_explosion(x, y, 1, libtcod.white, libtcod.light_sky)
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('The icebomb explodes!', spells.essence_colors['cold'])
    for adj in main.adjacent_inclusive(x, y):
        for f in main.current_map.fighters:
            if f.x == adj[0] and f.y == adj[1]:
                if combat.spell_attack_ex(actor.fighter, f, None, '3d10', 0, 'cold', 0) == 'hit' and f.fighter is not None:
                    f.fighter.apply_status_effect(effects.frozen(duration=6))

def timebomb(actor=None, target=None):
    if actor is None:
        actor = player.instance
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=6, default_target=default_target)
        if x is None: return 'cancelled'
    else:
        (x, y) = main.find_closest_open_tile(target.x, target.y)
    rune = main.GameObject(x, y, chr(21), 'time bomb', spells.essence_colors['arcane'],
                           description='"I prepared explosive runes this morning"')
    main.current_map.add_object(rune)
    rune_ticker = main.Ticker(3, _timebomb_ticker)
    rune_ticker.rune = rune
    rune_ticker.actor = actor
    main.current_map.tickers.append(rune_ticker)
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('A glowing rune forms...', spells.essence_colors['arcane'])
    return 'success'

def _timebomb_ticker(ticker):
    if ticker.ticks >= ticker.max_ticks:
        ticker.dead = True
        ui.message("The rune explodes!", spells.essence_colors['arcane'])
        ui.render_explosion(ticker.rune.x, ticker.rune.y, 1, libtcod.white, spells.essence_colors['arcane'])
        x = ticker.rune.x
        y = ticker.rune.y
        ticker.rune.destroy()
        for adj in main.adjacent_inclusive(x, y):
            for f in main.current_map.fighters:
                if f.x == adj[0] and f.y == adj[1]:
                    combat.spell_attack_ex(ticker.actor.fighter, f, None, '6d10', 0, 'lightning', 0)

def holy_water(actor=None, target=None):
    import monsters
    if actor is None:
        actor = player.instance
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        (x, y) = ui.target_tile(max_range=2, default_target=default_target, targeting_type='beam_interrupt')
        if x is None: return 'cancelled'
        target = main.get_monster_at_tile(x, y)
        if target is None:
            ui.message('No susceptible targets here.', libtcod.gray)
            return 'cancelled'
        actor = player.instance
    else:
        (x, y) = target.x, target.y
    if not target.fighter.has_flag(monsters.EVIL):
        if actor is player.instance:
            ui.message('That target is not vulnerable to holy water.', libtcod.gray)
        return 'cancelled'
    ui.render_projectile((actor.x, actor.y), (target.x, target.y), color=spells.essence_colors['water'], character=libtcod.CHAR_BLOCK2)
    combat.spell_attack_ex(actor.fighter, target, None, '8d10', 0, 'radiance', 3)
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.stunned(duration=(3 + main.roll_dice('1d6'))))
    return 'success'

def knock_back(actor,target):
    # check for resistance
    if 'displacement' in target.fighter.getImmunities() + target.fighter.getResists():
        if fov.player_can_see(target.x, target.y):
            ui.message('%s %s.' % (syntax.name(target).capitalize(), syntax.conjugate(
                target is player.instance, ('resist', 'resists'))), libtcod.gray)
        return 'resisted'

    # knock the target back one space. Stun it if it cannot move.
    direction = target.x - actor.x, target.y - actor.y  # assumes the instance is adjacent
    stun = False
    against = ''
    against_tile = main.current_map.tiles[target.x + direction[0]][target.y + direction[1]]
    if against_tile.blocks:
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
                syntax.pronoun(target.name, objective=True)), libtcod.gold)
    else:
        ui.message('%s %s knocked backwards.' % (
            syntax.name(target).capitalize(),
            syntax.conjugate(target is actor, ('are', 'is'))), libtcod.gray)
        target.set_position(target.x + direction[0], target.y + direction[1])
        main.render_map()
        libtcod.console_flush()

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
                syntax.name(monster).capitalize(),
                syntax.conjugate(monster is player.instance, ('are', 'is'))), libtcod.light_blue)

def silence(actor=None,target=None):
    if actor is None:  # player is casting
        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(*ui.target_tile(abilities.data['ability_silence']['range'], 'pick', default_target=default_target))

    if target is None:
        return 'cancelled'
    elif target.fighter.apply_status_effect(effects.silence(),True):
        ui.message('%s %s silenced!' % (
            syntax.name(target).capitalize(),
            syntax.conjugate(target is player.instance, ('are', 'is'))), libtcod.light_blue)

def check_doom(obj=None):
    fx = [f for f in obj.fighter.status_effects if f.name == 'doom']
    if len(fx) > 0 and fx[0].stacks >= 13:
        ui.message("Death comes for {}".format(obj.name),libtcod.dark_crimson)
        obj.fighter.take_damage(obj.fighter.max_hp)

def blade_dance(actor=None, target=None):
    if actor is None or actor is player.instance: # player is casting
        #check for equipped sword
        weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
        if weapon is None or weapon.subtype != 'sword':
            ui.message('You cannot do that without a sword.', libtcod.white)
            return 'didnt-take-turn'

        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(
            *ui.target_tile(abilities.data['ability_blade_dance']['range'], 'pick', default_target=default_target))
    else:
        target = main.get_monster_at_tile(target[0], target[1])

    if target is None:
        return 'didnt-take-turn'
    else:
        actor.swap_positions(target)
        actor.fighter.attack(target)

def pommel_strike(actor=None, target=None):
    if actor is None or actor is player.instance: # player is casting
        #check for equipped sword
        weapon = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
        if weapon is None or weapon.subtype != 'sword':
            ui.message('You cannot do that without a sword.', libtcod.white)
            return 'didnt-take-turn'

        ui.message('Left-click a target tile, or right-click to cancel.', libtcod.white)
        ui.render_message_panel()
        libtcod.console_flush()
        default_target = None
        if ui.selected_monster is not None:
            default_target = ui.selected_monster.x, ui.selected_monster.y
        target = main.get_monster_at_tile(
            *ui.target_tile(abilities.data['ability_pommel_strike']['range'], 'pick', default_target=default_target))
    else:
        target = main.get_monster_at_tile(target[0], target[1])

    if target is None:
        return 'didnt-take-turn'
    else:
        combat.attack_ex(actor.fighter, target, int(actor.fighter.calculate_attack_stamina_cost() * 1.5),
                         verb=('pommel-strike', 'pommel-strikes'), shred_modifier=2)

def _set_confused_behavior(object):
    if object.behavior is not None:
        old_ai = object.behavior.behavior
        object.behavior.behavior = ai.ConfusedMonster(old_ai)
        object.behavior.behavior.owner = object

def heal(amount=consts.HEAL_AMOUNT, use_percentage=False):
    if use_percentage:
        amount = int(round(amount * player.instance.fighter.max_hp))
    if player.instance.fighter.hp == player.instance.fighter.max_hp:
        ui.message('You are already at full health.', libtcod.white)
        return 'cancelled'

    ui.message('You feel better.', libtcod.white)
    player.instance.fighter.heal(amount)


def waterbreathing():
    player.instance.fighter.apply_status_effect(effects.StatusEffect('waterbreathing', 31, libtcod.light_azure))


def hardness(actor=None):
    if actor is None:
        actor = player.instance
    if actor.fighter is None:
        return 'failure'
    actor.fighter.shred = 0
    actor.fighter.apply_status_effect(effects.stoneskin(21))
    if actor is player.instance or fov.player_can_see(actor.x, actor.y):
        ui.message('%s armor is repaired and %s skin becomes as hard as stone.' % (
            syntax.name(actor, possesive=True).capitalize(),
            syntax.pronoun(actor.name, possesive=True)),
            spells.essence_colors['earth'])
    return 'success'

def cleanse():
    effects = list(player.instance.fighter.status_effects)

    cleansed = False
    for status in effects:
        if status.cleanseable:
            cleansed = True
            player.instance.fighter.remove_status(status.name)
    if cleansed:
        ui.message("You feel refreshed.")
        return 'success'
    else:
        ui.message("You aren't afflicted with any harmful effects")
        return 'didnt-take-turn'


def invulnerable():
    player.instance.fighter.apply_status_effect(effects.invulnerable(10))
    return 'success'

def frog_tongue(actor, target):
    if actor.distance_to(target) <= consts.FROG_TONGUE_RANGE and fov.monster_can_see_object(actor, target):
        if target.fighter.hp > 0 and main.beam_interrupt(actor.x, actor.y, target.x, target.y) == (target.x, target.y):
            ui.message("The frog's tongue lashes out at %s!" % syntax.name(target), libtcod.dark_green)
            result = combat.attack_ex(actor.fighter, target, 0, accuracy_modifier=1.5, damage_multiplier=1.5, verb=('pull', 'pulls'))
            if result == 'hit':
                if 'displacement' in target.fighter.getImmunities() + target.fighter.getResists():
                    if fov.player_can_see(target.x, target.y):
                        ui.message('%s %s.' % (syntax.name(target).capitalize(), syntax.conjugate(
                            target is player.instance, ('resist', 'resists'))), libtcod.gray)
                    return 'success'
                beam = main.beam(actor.x, actor.y, target.x, target.y)
                pull_to = beam[max(len(beam) - 3, 0)]
                target.set_position(pull_to[0], pull_to[1])
            return 'success'
    return 'didnt-take-turn'

def dragonweed_pull(actor, target):
    if actor.distance_to(target) <= 3 and fov.monster_can_see_object(actor, target):
        if target.fighter.hp > 0 and main.beam_interrupt(actor.x, actor.y, target.x, target.y) == (target.x, target.y):
            ui.message("The dragonweed's stem lashes out at %s!" % syntax.name(target), libtcod.dark_green)
            result = combat.attack_ex(actor.fighter, target, 0, accuracy_modifier=1.5, damage_multiplier=0.75, verb=('pull', 'pulls'))
            if result == 'hit':
                if 'displacement' in target.fighter.getImmunities() + target.fighter.getResists():
                    if fov.player_can_see(target.x, target.y):
                        ui.message('%s %s.' % (syntax.name(target).capitalize(), syntax.conjugate(
                            target is player.instance, ('resist', 'resists'))), libtcod.gray)
                    return 'success'
                beam = main.beam(actor.x, actor.y, target.x, target.y)
                pull_to = beam[max(len(beam) - 3, 0)]
                target.set_position(pull_to[0], pull_to[1])
                if target.fighter is not None and main.roll_dice('1d10') <= 5:
                    target.fighter.apply_status_effect(effects.immobilized(duration=2))
            return 'success'
    return 'didnt-take-turn'

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
                syntax.name(obj[0]).capitalize(),
                syntax.conjugate(obj[0] is player.instance, ('are', 'is'))), libtcod.gray)
            return False
        ui.message('You conjure a spark of flame, igniting the ' + tile.name + '!', libtcod.flame)
        main.create_fire(target[0], target[1], 10)
        return True
    return False


def on_hit_judgement(attacker, target, damage):
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.judgement(stacks=main.roll_dice('2d6')))

def pickaxe_dig(dx, dy):
    result = dig(player.instance.x + dx, player.instance.y + dy)
    if result == 'failed':
        ui.message('You cannot dig there.', libtcod.orange)
    else:
        item = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
        if item is not None:
            main.check_breakage(item)

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

forge_targets = ['weapon','armor']

def forge():
    import loot
    choices = [i for i in player.instance.fighter.inventory if i.equipment is not None and i.equipment.category in forge_targets]

    if len(choices) < 1:
        ui.message('You have no items to forge.',libtcod.orange)
        return 'didnt-take-turn'

    index = ui.menu('Forge what?',[c.name for c in choices])
    if index is None:
        ui.message('Cancelled.',libtcod.orange)
        return 'didnt-take-turn'
    target = choices[index].equipment

    if target.quality == 'artifact':
        ui.message('Your ' + target.owner.name + ' shimmers briefly. It cannot be improved further by this magic.',
                   libtcod.orange)
    elif target.category == 'weapon' and target.material == '': #can't forge summoned weapons
        ui.message('The %s cannot be altered by this magic.' % target.owner.name, libtcod.orange)
    else:
        ui.message('Your ' + target.owner.name + ' glows bright orange!', libtcod.orange)

        index = loot.quality_progression.index(target.quality)
        new_quality = loot.quality_progression[index + 1]
        main.set_quality(target, new_quality)
        ui.message('It is now a ' + target.owner.name + '.', libtcod.orange)
    return True

def aquatic(target):
    import pathfinding
    target.movement_type = target.movement_type | pathfinding.AQUATIC

def flight(target):
    import pathfinding
    target.movement_type = target.movement_type | pathfinding.FLYING

def auto_res(target):
    target.fighter.apply_status_effect(effects.auto_res())

def lichform(target):
    target.fighter.max_hp = int(target.fighter.max_hp * 0.7)
    target.fighter.hp = min(target.fighter.hp,target.fighter.max_hp)
    target.fighter.apply_status_effect(effects.lichform())

def gaze_into_the_void(target):
    for i in range(3): player.pick_up_essence('void',player.instance)

def vanguard(target):
    player.instance.add_zone(main.Zone(1,on_enter=vanguard_attack))

def vanguard_attack(actor,target):
    weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')
    if weapon is not None and weapon.subtype == 'polearm':
        attack(actor,target)

def skullsplitter_calc_damage_bonus(actor,target):
    return 1.5 * ( 2 - target.fighter.hp / target.fighter.max_hp)

def crush_calc_damage_bonus(actor,target):
    return 1.5 + (target.fighter.armor+1 / 20) * 2.5

def crush_calc_shred_bonus(actor,target):
    return 1 + int(target.fighter.armor / 2)

def summon_guardian_angel():
    adj = main.adjacent_tiles_diagonal(player.instance.x, player.instance.y)

    # Get viable summoning position. Return failure if no position is available
    summon_positions = []
    for tile in adj:
        if not main.is_blocked(tile[0], tile[1]):
            summon_positions.append(tile)
    if len(summon_positions) == 0:
        return 'failed'
    summon_pos = summon_positions[libtcod.random_get_int(0, 0, len(summon_positions) - 1)]

    # Select monster type - default to goblin
    summon_type = 'monster_guardian_angel'
    summon = main.spawn_monster(summon_type, summon_pos[0], summon_pos[1], team='ally')
    summon.behavior.follow_target = player.instance

    # Set summon duration
    summon.summon_time = 30 + libtcod.random_get_int(0, 0, 15)
    ui.message('Your prayers have been answered!',libtcod.light_blue)
    return 'success'

def summon_roaches(actor, attacker, damage):
    if not hasattr(actor, 'summon_limit') or not hasattr(actor, 'summons'):
        actor.summon_limit = 8
        actor.summons = []
    remove = []
    for s in actor.summons:
        if s.fighter is None or not s in main.current_map.fighters:
            remove.append(s)
    for s in remove:
        actor.summons.remove(s)

    if len(actor.summons) >= actor.summon_limit:
        return
    if fov.player_can_see(actor.x, actor.y):
        ui.message('Cockroaches crawl from %s wounds!' % syntax.name(actor, possesive=True), libtcod.dark_magenta)
    for adj in main.adjacent_tiles_diagonal(actor.x, actor.y):
        if len(actor.summons) >= actor.summon_limit:
            break
        if not main.is_blocked(adj[0], adj[1]) and libtcod.random_get_int(0, 1, 10) <= 5:
            actor.summons.append(main.spawn_monster('monster_cockroach', adj[0], adj[1]))

def poison_attack_1(actor,target,damage):
    if main.roll_dice('1d10') > target.fighter.armor:
        target.fighter.apply_status_effect(effects.poison())

def oil_attack(actor, target, damage):
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.oiled())

def immobilize_attack(actor, target, damage):
    if target.fighter is not None and main.roll_dice('1d10') <= 5:
        target.fighter.apply_status_effect(effects.immobilized(duration=2))

def toxic_attack(actor, target, damage):
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.toxic())

def potion_essence(essence):
    return lambda : use_gem(essence)

def use_gem(essence):
    if player.instance.fighter.item_equipped_count('equipment_ring_of_alchemy') > 0:
        old_essence = essence
        essence = main.opposite_essence(essence)
        if old_essence != essence:
            ui.message('Your ring of alchemy glows!', spells.essence_colors[essence])
    player.pick_up_essence(essence, player.instance)

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

def teleport_random(actor=None):
    destination = main.find_random_open_tile()
    return teleport(actor, destination[0], destination[1])

def teleportal_on_tick(teleportal):
    if not hasattr(teleportal, 'timer'):
        teleportal.timer = 3
        return
    else:
        teleportal.timer -= 1
    if teleportal.timer <= 0:
        destination = main.find_random_open_tile()
        for obj in main.get_objects(teleportal.x, teleportal.y):
            if obj is not teleportal:
                teleport(obj, destination[0], destination[1])
        teleportal.destroy()

def create_teleportal(x, y):
    portal = main.GameObject(x, y, 9, 'teleportal', spells.essence_colors['arcane'], on_tick=teleportal_on_tick)
    portal.timer = 4
    main.current_map.add_object(portal)
    main.changed_tiles.append((x, y))
    if fov.player_can_see(x, y):
        ui.message('A volatile portal opens. In a few moments it will teleport creatures standing near it.',
                   spells.essence_colors['arcane'])
    return 'success'

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
        summon.behavior.follow_target = player.instance

        # Set summon duration
        summon.summon_time = duration + libtcod.random_get_int(0, 0, duration)
        return 'success'
    else:
        return 'didnt-take-turn'

def summon_equipment(item):
    if len(player.instance.fighter.inventory) >= 26:
        ui.message('You are carrying too many items to summon another.')
        return 'didnt-take-turn'

    summoned_equipment = main.create_item(item, material='', quality='')
    if summoned_equipment is None:
        return

    expire_ticker = main.Ticker(15,summon_equipment_on_tick)
    equipped_item = None
    expire_ticker.old_left = None
    if summoned_equipment.equipment.slot == 'both hands':
        equipped_item = main.get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
        expire_ticker.old_left = main.get_equipped_in_slot(player.instance.fighter.inventory, 'left hand')
    elif summoned_equipment.equipment.slot == 'floating shield':
        #can't stack two shields
        equipped_item = player.instance.fighter.get_equipped_shield()
    else:
        equipped_item = main.get_equipped_in_slot(player.instance.fighter.inventory, summoned_equipment.equipment.slot)
    expire_ticker.old_equipment = equipped_item

    if equipped_item is not None:
        equipped_item.dequip()
    summoned_equipment.item.pick_up(player.instance,True)
    expire_ticker.equipment = summoned_equipment
    effect = effects.StatusEffect('summoned equipment', expire_ticker.max_ticks + 1, summoned_equipment.color)
    player.instance.fighter.apply_status_effect(effect)
    expire_ticker.effect = effect
    main.current_map.tickers.append(expire_ticker)

    ui.message("A {} appears!".format(summoned_equipment.name),libtcod.white)

    return 'success'

def summon_equipment_on_tick(ticker):
    dead_flag = False
    dropped = False
    if not ticker.equipment.equipment.is_equipped:
        ui.message('The %s fades away as you release it from your grasp.' % ticker.equipment.name.title(), libtcod.light_blue)
        dead_flag = True
        dropped = True
    elif ticker.ticks > ticker.max_ticks:
        dead_flag = True
        ui.message("The %s fades away as it's essence depletes." % ticker.equipment.name.title(), libtcod.light_blue)
    if dead_flag:
        ticker.dead = True
        if ticker.equipment is not None:
            ticker.equipment.item.drop(no_message=True)
            ticker.equipment.destroy()
        player.instance.fighter.remove_status('summoned equipment')
        if not dropped:
            if ticker.old_equipment is not None:
                ticker.old_equipment.equip()
            if ticker.old_left is not None:
                ticker.old_left.equip()

def learn_ability(ability):
    dat = abilities.data[ability]
    a = abilities.Ability(dat.get('name'), dat.get('description', ''), dat.get('function'), dat.get('cooldown', 0))
    player.instance.perk_abilities.append(a)

import libtcodpy as libtcod
import game as main
import syntax
import fov
import abilities
import effects
import spells
import ui
import ai
import player
import combat
