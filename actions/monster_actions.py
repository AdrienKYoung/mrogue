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

import libtcodpy as libtcod
import game as main
import combat
import effects
import player
import syntax
import ui
import fov
import spells


def berserk_self(actor, target, context):
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

def spawn_vermin(actor, target, context):
    #Filthy hackery to add some state
    if not hasattr(actor, 'summons'):
        actor.summons = []

    for s in actor.summons:  # clear dead things from summoned list
        if not s.fighter:
            actor.summons.remove(s)

    if len(actor.summons) < context['max_summons']:
        summon_choice = main.random_choice_index([e['weight'] for e in context['summons']])
        summon_tiles = []
        for y in range(5):
            for x in range(5):
                pos = actor.x - 2 + x, actor.y - 2 + y
                if main.in_bounds(pos[0], pos[1]) and not main.is_blocked(pos[0], pos[1]):
                    summon_tiles.append(pos)
        for i in range(context['summons'][summon_choice]['count']):
            if len(summon_tiles) > 0:
                pos = summon_tiles[libtcod.random_get_int(0, 0, len(summon_tiles) - 1)]
                spawn = main.spawn_monster(context['summons'][summon_choice]['monster'], pos[0], pos[1])
                ui.message('A ' + spawn.name + " crawls from beneath the verman's cloak.", actor.color)
                spawn.fighter.loot_table = None
                actor.summons.append(spawn)
                summon_tiles.remove(pos)

def spawn_spiders(actor, target, context):
    #Filthy hackery to add some state
    if not hasattr(actor, 'summons'):
        actor.summons = []

    for s in actor.summons:  # clear dead things from summoned list
        if not s.fighter:
            actor.summons.remove(s)

    if len(actor.summons) < context['max_summons']:
        summon_tiles = []
        for y in range(3):
            for x in range(3):
                pos = actor.x - 1 + x, actor.y - 1 + y
                if main.in_bounds(pos[0], pos[1]) and not main.is_blocked(pos[0], pos[1]):
                    summon_tiles.append(pos)
        summon_count = main.roll_dice(context['summons_per_cast'])
        for i in range(summon_count):
            if len(summon_tiles) > 0 and len(actor.summons) < context['max_summons']:
                pos = summon_tiles[libtcod.random_get_int(0, 0, len(summon_tiles) - 1)]
                spawn = main.spawn_monster('monster_tunnel_spider', pos[0], pos[1])
                ui.message('A ' + spawn.name + " crawls from beneath %s cloak." % syntax.name(actor, possesive=True), actor.color)
                actor.summons.append(spawn)
                summon_tiles.remove(pos)
        return 'success'
    return 'cancelled'

def web_bomb(actor, target, context):
    if actor is player.instance:
        ui.message('Yo implement this', libtcod.red)
        return 'failure'

    main.tunnel_spider_spawn_web(target)
    if actor is player.instance or fov.player_can_see(target.x, target.y):
        ui.message('%s summons spiderwebs.' % syntax.name(actor).capitalize(), actor.color)
    return 'success'

def heal_other(actor, target, context):
    if actor is player.instance:
        ui.message('Yo implement this', libtcod.red)
        return 'failure'

    ui.render_explosion(target.x, target.y, 0, libtcod.lightest_green, libtcod.green)
    amount = main.roll_dice('3d4')
    target.fighter.heal(amount)
    ui.message('%s %s %s for %d damage.' % (
        syntax.name(actor).capitalize(),
        syntax.conjugate(actor is player.instance, ('heal', 'heals')),
        syntax.name(target, reflexive=actor),
        amount), libtcod.green)
    return 'success'

def haste(actor, target, context):
    target.fighter.apply_status_effect(effects.hasted(duration=context['duration']))
    ui.render_explosion(target.x, target.y, 0, libtcod.lightest_fuchsia, libtcod.fuchsia)
    ui.message('%s %s hasted.' % (
        syntax.name(target).capitalize(),
        syntax.conjugate(target is player.instance, ('are', 'is'))), spells.essence_colors['arcane'])
    return 'success'

def throw_net(actor, target, context):
    if actor is player.instance:
        ui.message('Yo implement this', libtcod.red)
        return 'failure'

    dist = actor.distance_to(target)
    if dist > context['range']:
        return 'cancelled'

    ui.message('%s %s a net at %s.' % (
        syntax.name(actor).capitalize(),
        syntax.conjugate(actor is player.instance, ('throw', 'throws')),
        syntax.name(target)), libtcod.gold)
    ui.render_projectile((actor.x, actor.y), (target.x, target.y), libtcod.gold, character='#')
    target.fighter.apply_status_effect(effects.immobilized(duration=context['duration']),
                                       context['save_dc'],source_fighter=actor)

    return 'success'

def raise_zombie(actor, target, context):
    corpse = None
    for tile in target:
        corpses_here = main.get_objects(tile[0], tile[1], lambda o: o.name.startswith('remains of'))
        if len(corpses_here) > 0:
            corpse = corpses_here[0]
            break

    if corpse is not None:
        ui.message('A dark aura emanates from %s... a corpse walks again.' % syntax.name(actor), libtcod.dark_violet)
        main.raise_dead(actor,corpse)
        return 'rasied-zombie'
    else:
        return 'didnt-take-turn'

def reeker_breath(actor, target, context):
    #TODO: Upgrade this to use auto targeting
    x = target.x
    y = target.y
    tiles = main.cone(actor.x,actor.y,x,y,max_range=context['range'])

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
                combat.attack_magical(actor.fighter, obj, 'ability_reeker_breath')

def flame_breath(actor, target, context):
    for tile in target:
        main.melt_ice(tile[0], tile[1])
        t = main.current_map.tiles[tile[0]][tile[1]]
        if t.flammable or main.roll_dice('1d2') == 1:
            main.create_fire(tile[0],tile[1],12)

        for obj in main.current_map.fighters:
            if obj.x == tile[0] and obj.y == tile[1]:
                combat.attack_magical(actor.fighter, obj, 'ability_flame_breath')
                if obj.fighter is not None:
                    obj.fighter.apply_status_effect(effects.burning(), context['save_dc'], actor)

    return 'success'

def great_dive(actor,target, context):
    ui.message("{} {} into the ground!".format(
        syntax.name(actor).capitalize(),
        syntax.conjugate(actor is player.instance, ['slam', 'slams'])
    ))

    for obj in main.current_map.fighters:
        if (obj.x, obj.y) in target:
            combat.attack_ex(actor.fighter, obj, 0)

    x,y = context['origin']
    if not main.is_blocked(x, y):
        actor.set_position(x, y)
    else:
        for t in target:
            if not main.is_blocked(t[0], t[1]):
                actor.set_position(t[0], t[1])
                break

def great_dive_channel(actor,target):
    ui.message("{} {} high into the air!".format(
        syntax.name(actor).capitalize(),
        syntax.conjugate(actor is player.instance, ['rise', 'rises'])
    ))

def summon_demon(actor,data):
    choice = main.random_choice(data['summons'])
    actor.fighter.take_damage(100000)
    main.spawn_monster(choice, actor.x,actor.y)

def frog_tongue(actor, target, context):
    if target.fighter.hp > 0:
        ui.message("The frog's tongue lashes out at %s!" % syntax.name(target), libtcod.dark_green)
        result = combat.attack_ex(actor.fighter, target, 0, accuracy_modifier=1.5, damage_multiplier=1.5, verb=('pull', 'pulls'))
        if result == 'hit':
            if 'displacement' in target.fighter.immunities:
                if fov.player_can_see(target.x, target.y):
                    ui.message('%s %s.' % (syntax.name(target).capitalize(), syntax.conjugate(
                        target is player.instance, ('resist', 'resists'))), libtcod.gray)
                return 'success'
            beam = main.beam(actor.x, actor.y, target.x, target.y)
            pull_to = beam[max(len(beam) - 3, 0)]
            target.set_position(pull_to[0], pull_to[1])

def dragonweed_pull(actor, target, context):
    if target.fighter.hp > 0:
        ui.message("The dragonweed's stem lashes out at %s!" % syntax.name(target), libtcod.dark_green)
        result = combat.attack_ex(actor.fighter, target, 0, accuracy_modifier=1.5, damage_multiplier=0.75, verb=('pull', 'pulls'))
        if result == 'hit' and target.fighter is not None:
            if 'displacement' in target.fighter.immunities:
                if fov.player_can_see(target.x, target.y):
                    ui.message('%s %s.' % (syntax.name(target).capitalize(), syntax.conjugate(
                        target is player.instance, ('resist', 'resists'))), libtcod.gray)
                return 'success'
            beam = main.beam(actor.x, actor.y, target.x, target.y)
            pull_to = beam[max(len(beam) - 3, 0)]
            target.set_position(pull_to[0], pull_to[1])
            if main.roll_dice('1d10') <= 5:
                target.fighter.apply_status_effect(effects.immobilized(duration=2), context['save_dc'], actor)

def silence(actor,target, context):
    if target.fighter.apply_status_effect(effects.silence(duration=context.get('duration', 10)),
                                          dc=context.get('base_dc', 20) + actor.fighter.spell_power(['arcane']),
                                          source_fighter=actor.fighter,
                                          supress_message=True):
        if actor is player.instance or target is player.instance or fov.player_can_see(target.x, target.y):
            ui.message('%s %s silenced!' % (
                syntax.name(target).capitalize(),
                syntax.conjugate(target is player.instance, ('are', 'is'))), libtcod.light_blue)

def confuse(actor,target, context):
    import consts
    if target.fighter.apply_status_effect(
            effects.StatusEffect('confusion', consts.CONFUSE_NUM_TURNS, color=libtcod.pink,
                                 )):
        ui.message('%s %s confused!' % (
            syntax.name(target).capitalize(),
            syntax.conjugate(target is player.instance, ('are', 'is'))), libtcod.light_blue)

def wild_growth(actor, target, context):
    import mapgen
    terrain = main.current_map.tiles[target.x][target.y].tile_type
    if target.fighter and target.fighter.has_status('immobilized'):
        return 'cancelled'
    if terrain == 'grass floor':
        if target.fighter:
            if target is player.instance or fov.player_can_see(target.x, target.y):
                ui.message('The grass sprouts a tangle of grasping vines!', libtcod.lime)
            duration = main.roll_dice(context['root_duration'])
            immobilized = target.fighter.apply_status_effect(effects.immobilized(
                duration=duration), dc=context['save_dc'])
            if immobilized:
                target.fighter.apply_status_effect(effects.StatusEffect('wild growth', time_limit=duration,
                           color=libtcod.lime, on_tick=wild_growth_tick, message='You are gripped by writhing vines!',
                           description='This unit will take damage every turn', cleanseable=True), dc=None)
    else:
        if target is player.instance or fov.player_can_see(target.x, target.y):
            ui.message('Grass springs from the %s...' % terrain, libtcod.lime)
        grass = mapgen.create_terrain_patch((target.x, target.y), 'grass floor', min_patch=4, max_patch=12, overwrite=False)
        for tile in grass:
            main.changed_tiles.append(tile)

def wild_growth_tick(effect, object):
    import abilities
    if object is not None and object.fighter is not None:
        spell = abilities.data['ability_wild_growth']
        object.fighter.take_damage(main.roll_dice(spell['damage_per_tick'], normalize_size=4))