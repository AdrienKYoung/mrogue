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
import spells
import ui
import fov
import common

def healing_trance(actor, target, context):
    actor.fighter.apply_status_effect(effects.stunned(duration=15))
    actor.fighter.apply_status_effect(effects.regeneration(duration=15))


def mass_heal(actor,target, context):
    for unit in target:
        unit.fighter.apply_status_effect(effects.regeneration())
        amount = int(round(0.25 * unit.fighter.max_hp))
        unit.fighter.heal(amount)
        ui.message("{} {} healed!".format(syntax.conjugate(unit is player.instance,['You',unit.name]),
                   syntax.conjugate(unit is player.instance,['were','was'])), libtcod.white)
    return 'success'

def mass_cleanse(actor,target, context):
    for unit in target:
        effects = list(player.instance.fighter.status_effects)
        for status in effects:
            if status.cleanseable:
                player.instance.fighter.remove_status(status.name)

def mass_reflect(actor,target, context):
    for unit in target:
        unit.fighter.apply_status_effect(effects.reflect_magic())

def firebomb(actor, target, context):
    (x, y) = context['origin']
    ui.render_projectile((actor.x, actor.y), (x, y), spells.essence_colors['fire'], chr(7))
    ui.render_explosion(x, y, 1, libtcod.yellow, libtcod.flame)
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('The firebomb explodes!', spells.essence_colors['fire'])
    for f in target:
        if combat.attack_magical(actor.fighter, f, 'ability_fire_bomb') == 'hit' and f.fighter is not None:
            f.fighter.apply_status_effect(effects.burning())

def icebomb(actor, target, context):
    (x, y) = context['origin']
    ui.render_projectile((actor.x, actor.y), (x, y), spells.essence_colors['cold'], chr(7))
    ui.render_explosion(x, y, 1, libtcod.white, libtcod.light_sky)
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('The icebomb explodes!', spells.essence_colors['cold'])
    for f in target:
        if combat.attack_magical(actor.fighter, f, 'ability_ice_bomb') == 'hit' and f.fighter is not None:
            f.fighter.apply_status_effect(effects.frozen(duration=context['freeze_duration']))

def timebomb(actor, target, context):
    (x, y) = target[0], target[1]
    rune = main.GameObject(x, y, chr(21), 'time bomb', spells.essence_colors['arcane'],
                           description='"I prepared explosive runes this morning"')
    main.current_map.add_object(rune)
    rune_ticker = main.Ticker(context['delay'], _timebomb_ticker)
    rune_ticker.rune = rune
    rune_ticker.actor = actor
    main.current_map.tickers.append(rune_ticker)
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('A glowing rune forms...', spells.essence_colors['arcane'])

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
                    combat.attack_magical(ticker.actor.fighter, f, 'data_time_bomb_explosion')

def holy_water(actor, target, context):
    import monsters
    if not target.fighter.has_flag(monsters.EVIL):
        if actor is player.instance:
            ui.message('That target is not vulnerable to holy water.', libtcod.gray)
        return 'cancelled'
    ui.render_projectile((actor.x, actor.y), (target.x, target.y), color=spells.essence_colors['water'], character=libtcod.CHAR_BLOCK2)
    combat.attack_magical(actor.fighter, target, 'ability_holy_water')
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.stunned(duration=(3 + main.roll_dice('1d6'))))
    return 'success'

def create_teleportal(actor, target, context):
    x,y = target
    portal = main.GameObject(x, y, 9, 'teleportal', spells.essence_colors['arcane'], on_tick=teleportal_on_tick)
    portal.timer = 4
    main.current_map.add_object(portal)
    main.changed_tiles.append((x, y))
    if fov.player_can_see(x, y):
        ui.message('A volatile portal opens. In a few moments it will teleport creatures standing near it.',
                   spells.essence_colors['arcane'])
    return 'success'

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
                common.teleport(obj, destination[0], destination[1])
        teleportal.destroy()


def hardness(target):
    target.fighter.shred = 0
    target.fighter.apply_status_effect(effects.stoneskin(21))
    if target is player.instance or fov.player_can_see(target.x, target.y):
        ui.message('%s armor is repaired and %s skin becomes as hard as stone.' % (
            syntax.name(target, possesive=True).capitalize(),
            syntax.pronoun(target, possesive=True)),
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

def invulnerable(actor, target, context):
    target.fighter.apply_status_effect(effects.invulnerable(10))

def summon_elemental(actor, target, context):
    return common.summon_ally(context['summon'], context['duration_base'] + main.roll_dice(context['duration_variance']))

def summon_lifeplant(actor, target, context):
    return common.summon_ally('monster_lifeplant', context['duration_base'] + main.roll_dice(context['duration_variance']))

def summon_weapon(actor, target, context):
    return common.summon_equipment(actor, context['item'])

def farmers_talisman_dig(actor, target, context):
    x, y = target[0], target[1]
    direction = x - player.instance.x, y - player.instance.y
    depth = context['min_depth'] + main.roll_dice(context['depth_variance'])
    return common.dig_line(player.instance.x, player.instance.y, direction[0], direction[1], depth)

def create_terrain(actor, target, context):
    import dungeon, mapgen
    (x, y) = target[0], target[1]

    terrain = context['terrain_type']
    if terrain == 'wall':
        terrain = dungeon.branches[main.current_map.branch]['default_wall']

    tiles = main.adjacent_tiles_orthogonal(x, y)
    tiles.append((x, y))

    main.create_temp_terrain(terrain, tiles, 100)
    if terrain == 'shallow water':
        main.create_temp_terrain('deep water', [(x, y)], 100)
    if terrain == 'grass floor':
        mapgen.scatter_reeds(tiles, 75)
        for t in tiles:
            fov.set_fov_properties(t[0], t[1], len(main.get_objects(t[0], t[1], lambda o: o.blocks_sight)) > 0,
                                   elevation=main.current_map.tiles[t[0]][t[1]].elevation)

def acid_flask(actor, target, context):
    (x, y) = context['origin']
    ui.render_projectile((actor.x, actor.y), (x, y), libtcod.lime, character='!')
    ui.render_explosion(x, y, 1, libtcod.lightest_lime, libtcod.dark_lime)
    for t in target:
        combat.attack_magical(actor.fighter, t, 'ability_acid_flask')

def frostfire(actor, target, context):
    main.create_frostfire(target[0], target[1])

def vitality_potion(actor, target, context):
    actor.fighter.apply_status_effect(effects.vitality())