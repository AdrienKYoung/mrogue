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

import combat
import common
import effects
import fov
import game as main
import libtcodpy as libtcod
import player
import spells
import syntax
import ui
import abilities


def heat_ray(actor, target, context):
    end = (target[len(target) - 1][0], target[len(target) - 1][1])
    ui.render_projectile((actor.x, actor.y), end, libtcod.flame, libtcod.CHAR_BLOCK3)

    for obj in main.current_map.fighters:
        for l in target:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj,'ability_heat_ray')

    main.melt_ice(end[0], end[1])


def flame_wall(actor, target, context):
    main.create_fire(target[0], target[1], 10)

def fireball(actor, target, context):
    (x, y) = context['origin']
    if actor is not player.instance and not fov.monster_can_see_tile(actor, x, y):
        return 'cancelled'
    ui.message('The fireball explodes!', libtcod.flame)
    ui.render_explosion(x, y, 1, libtcod.yellow, libtcod.flame)
    for obj in target:
        combat.spell_attack(actor.fighter, obj, 'ability_fireball')
        if obj.fighter is not None:
            obj.fighter.apply_status_effect(effects.burning())

    for _x in range(x - 1, x + 2):
        for _y in range(y - 1, y + 2):
            main.melt_ice(_x, _y)

def shatter_item(actor, target, context):
    x, y = 0, 0
    dc = context['save_dc']
    if actor is player.instance:  # player is casting
        ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
        (x, y) = ui.target_tile()
        if x is None:
            return 'cancelled'
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
        damage_factor = 4
        if item.equipment is not None:
            damage_factor = item.equipment.weight
        for obj in main.current_map.fighters:
            if obj.distance(x, y) <= context['burst']:
                combat.spell_attack_ex(actor.fighter, obj, None, '2d{}'.format(damage_factor), context['dice'], ['slashing'], 0)
        return 'success'
    else:
        ui.message("Shatter failed to break the {}!".format(item.name), libtcod.yellow)
        return 'success'

def magma_bolt(actor, target, context):
    for tile in target:
        main.create_temp_terrain('lava', [tile], main.roll_dice(context['lava_duration']))
        for fighter in main.current_map.fighters:
            if fighter.x == tile[0] and fighter.y == tile[1]:
                combat.spell_attack(actor.fighter, fighter, 'ability_magma_bolt')

def frozen_orb(actor, target, context):
    if combat.spell_attack(actor.fighter, target,'ability_frozen_orb') == 'hit' and target.fighter is not None:
        target.fighter.apply_status_effect(effects.slowed(),context['save_dc'] + actor.fighter.spell_power)

def flash_frost(actor, target, context):
    target.fighter.apply_status_effect(effects.frozen(5))
    if actor is player.instance or fov.player_can_see(target.x, target.y):
        ui.message('%s %s frozen solid!' %
                   (syntax.name(target).capitalize(),
                    syntax.conjugate(target is player.instance, ('are', 'is'))),
                    spells.essence_colors['cold'])

def ice_shards(actor, target, context):
    ui.message('Razor shards of ice blast out!',libtcod.white)
    dc = context['save_dc'] + actor.fighter.spell_power

    for tile in target:
        reed = main.object_at_tile(tile[0], tile[1], 'reeds')
        if reed is not None:
            reed.destroy()
        for obj in main.current_map.fighters:
            if obj.x == tile[0] and obj.y == tile[1]:
                combat.spell_attack(actor.fighter, obj, 'ability_ice_shards')
                if obj.fighter is not None:
                    obj.fighter.apply_status_effect(effects.slowed(), dc=dc, source_fighter=actor)
                    obj.fighter.apply_status_effect(effects.bleeding(), dc=dc, source_fighter=actor)

def snowstorm(actor, target, context):
    import actions
    (x, y) = target
    storm = main.GameObject(x, y, '@', 'Snowstorm', libtcod.lightest_azure, summon_time=10)
    storm.on_tick_specified = lambda o: actions.invoke_ability('ability_snowstorm_tick', storm, spell_context={'caster': actor, 'team': actor.fighter.team})
    storm.creator = actor
    main.current_map.add_object(storm)

def snowstorm_tick(actor,target,context):
    caster = context['caster']
    dc = context['save_dc'] + caster.fighter.spell_power
    for t in target:
        if main.roll_dice('1d10') > 7:
            combat.spell_attack(caster.fighter,t,'ability_snowstorm')
            if t.fighter is not None:
                t.fighter.apply_status_effect(effects.slowed(), dc, caster)
                t.fighter.apply_status_effect(effects.blinded(), dc, caster)
            fx = main.GameObject(t.x,t.y,'*','cloud of snow',libtcod.lightest_azure,summon_time=2)
            main.current_map.objects.append(fx)

def avalanche(actor, target, context):
    for l in target:
        for obj in main.current_map.fighters:
            if obj.x == l[0] and obj.y == l[1]:
                combat.spell_attack(actor.fighter, obj, 'ability_avalanche')
                if obj.fighter is not None:
                    obj.fighter.apply_status_effect(effects.immobilized(), context['save_dc'], actor)
        if libtcod.random_get_int(0, 0, 3) > 0:
            tile = main.current_map.tiles[l[0]][l[1]]
            if tile.is_floor and tile.tile_type != 'snow drift' and tile.tile_type != 'ice':
                tile.tile_type = 'snow drift'
                main.changed_tiles.append(l)
            if tile.is_water:
                tile.tile_type = 'ice'
                main.changed_tiles.append(l)

def hex(actor,target, context):
    target.fighter.apply_status_effect(effects.cursed(),context['save_dc'] + actor.fighter.spell_power,actor)

def defile(actor, target, context):
    objects = main.get_objects(target[0], target[1],
                               condition=lambda o: o.is_corpse or o.fighter and o is not actor is not None)
    if len(objects) == 0:
        if actor is player.instance:
            ui.message('There is no body to defile here.', libtcod.gray)
        return 'cancelled'
    elif len(objects) == 1:
        target = objects[0]
    else:
        index = ui.menu('Defile what?', [o.name for o in objects])
        if index is None or index < 0 or index >= len(objects):
            return 'cancelled'
        target = objects[index]

    if target.is_corpse:
        main.raise_dead(actor,target, duration=100)
    elif target.fighter.subtype == 'undead' or target.fighter.subtype == 'fiend':
        target.fighter.heal(int(target.fighter.max_hp / 3))
        ui.message("Dark magic strengthens {}!".format(target.name))
    else:
        combat.spell_attack(actor.fighter, target, 'ability_defile')

def shackles_of_the_dead(actor,target, context):
    for t in target:
        t.fighter.apply_status_effect(
            effects.immobilized(duration=context['duration'] + (actor.fighter.spell_power / 5)),
            context['save_dc'] + actor.fighter.spell_power, actor)

def sacrifice(actor, target, context):
    actor.fighter.take_damage(min(30,int(actor.fighter.hp / 2)), attacker=actor)
    damage_mod = float(actor.fighter.max_hp - actor.fighter.hp )/ float(actor.fighter.max_hp)
    ui.render_explosion(actor.x, actor.y, 1, libtcod.violet, libtcod.darkest_violet)
    for f in target:
        combat.spell_attack_ex(actor.fighter, f, None, context['base_damage'], context['dice'], ['death'],
                               context['pierce'], 0, damage_mod=1 + damage_mod, defense_type='will')

def corpse_dance(actor, target, context):
    x, y = target
    ui.render_explosion(x, y, context['radius'], libtcod.violet, libtcod.light_yellow)
    ui.message("{} calls the dead to dance!".format(syntax.conjugate(actor is player.instance,["You",actor.name.capitalize()])))

    for o in main.get_objects(x,y,None,context['radius']):
        if o is not None and o.is_corpse:
            main.raise_dead(actor,o)
        if o.fighter is not None and o.fighter.team == actor.fighter.team and o.fighter.subtype == 'undead':
            o.fighter.apply_status_effect(effects.swiftness(context['buff_duration']))
            o.fighter.apply_status_effect(effects.berserk(context['buff_duration']))

def bless(actor, target, context):
    target.fighter.apply_status_effect(effects.blessed())

def smite(actor, target, context):
    import monsters
    dc = context['save_dc'] + actor.fighter.spell_power
    combat.spell_attack(actor.fighter, target,'ability_smite')
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.judgement(main.roll_dice('2d8')), dc, actor)
        if target.fighter.has_flag(monsters.EVIL):
            target.fighter.apply_status_effect(effects.stunned())
    return 'success'

def castigate(actor, target, context):
    origin = context['origin']
    ui.render_explosion(origin[0], origin[1], 1, libtcod.violet, libtcod.light_yellow)
    dc = context['save_dc'] + actor.fighter.spell_power
    for f in target:
        f.fighter.apply_status_effect(effects.judgement(stacks=main.roll_dice('3d8')), dc, actor)

#player only
def blessed_aegis(actor, target, context):
    common.summon_equipment('shield_blessed_aegis')

def holy_lance(actor, target, context):
    import actions
    x, y = context['origin']
    ui.render_explosion(x, y, context['burst'], libtcod.violet, libtcod.light_yellow)

    spell_context = {
        'stamina_cost' : context['stamina_cost'],
        'charges' : context['charges'],
        'caster' : actor,
        'team' : actor.fighter.team,
    }
    lance = main.GameObject(x, y, chr(23), 'Holy Lance', libtcod.light_azure,
                            on_tick=lambda o: actions.invoke_ability('ability_holy_lance_tick', o,
                                                                     spell_context=spell_context), summon_time=10)
    main.current_map.add_object(lance)

    for obj in main.get_fighters_in_burst(x,y,context['burst'],lance,actor.fighter.team):
            combat.spell_attack(actor.fighter, obj, 'ability_holy_lance')
    return 'success'


def holy_lance_tick(actor, target, context):
    caster = context['caster']
    ui.render_explosion(actor.x, actor.y, context['burst'], libtcod.violet, libtcod.light_yellow)
    for f in target:
        combat.spell_attack(caster.fighter, f, 'ability_holy_lance_tick')


def green_touch(actor, target, context):
    x,y = target
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
    x,y = target
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

def summon_dragonweed(actor, target, context):
    x,y = target
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
    if ticker.ticks >= ticker.max_ticks:
        ticker.dead = True
        ui.message("The dragonweed sapling matures.", libtcod.dark_chartreuse)
        x = ticker.seed.x
        y = ticker.seed.y
        ticker.seed.destroy()
        for obj in main.get_objects(x, y, lambda o: o.blocks):
            t = main.find_closest_open_tile(x, y)
            obj.set_position(t[0], t[1])
        common.summon_ally('monster_dragonweed', 10 + libtcod.random_get_int(0, 0, 20), x, y)

def bramble(actor, target, context):
    ui.message('Thorny brambles spring from %s fingertips!' % syntax.name(actor, possesive=True), spells.essence_colors['life'])
    for tile in target:
        _bramble = main.GameObject(tile[0], tile[1], 'x', 'bramble', libtcod.dark_lime, on_step=bramble_on_step,
                                   summon_time=context['duration_base'] + main.roll_dice(context['duration_variance']))
        _bramble.summoner = actor
        main.current_map.add_object(_bramble)
    return 'success'

def bramble_on_step(_bramble, obj):
    if obj is _bramble.summoner:
        return
    elif obj.fighter is not None:
        spell = abilities.data['ability_bramble']
        obj.fighter.take_damage(main.roll_dice(spell['damage'], normalize_size=4), attacker=_bramble.summoner)
        if obj.fighter is not None:
            obj.fighter.apply_status_effect(effects.bleeding(duration=spell['bleed_duration']))
        _bramble.destroy()

def strangleweeds(actor, target, context):
    hit = False
    for f in main.get_fighters_in_burst(actor.x, actor.y, context['range'], actor, actor.fighter.team):
        tile = main.current_map.tiles[f.x][f.y]
        if tile.tile_type == 'grass floor':
            if actor is player.instance or fov.player_can_see(f.x, f.y):
                ui.message('Writhing vines grip %s and hold %s in place!' % (syntax.name(f), syntax.pronoun(f)),
                           spells.essence_colors['life'])
            f.fighter.apply_status_effect(effects.immobilized(duration=context['duration']))
            f.fighter.apply_status_effect(effects.StatusEffect('strangleweeds', time_limit=context['duration'],
                           color=libtcod.lime, on_tick=strangleweed_on_tick, message='The strangleweeds crush you!',
                           description='This unit will take damage every turn', cleanseable=True))
            hit = True
    if hit:
        return 'success'
    else:
        if actor is player.instance:
            ui.message("You can't see any susceptible targets.", libtcod.gray)
        return 'cancelled'

def strangleweed_on_tick(effect, object):
    if object is not None and object.fighter is not None:
        spell = abilities.data['ability_strangleweeds']
        object.fighter.take_damage(main.roll_dice(spell['tick_damage'], normalize_size=4))

def arcane_arrow(actor, target, context):
    ui.render_projectile((actor.x, actor.y), (target.x, target.y), libtcod.fuchsia, None)
    combat.spell_attack(actor.fighter, target, 'ability_arcane_arrow')