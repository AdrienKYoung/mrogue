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
        if combat.spell_attack_ex(actor.fighter, f, None, '4d10', 0, ['fire'], 0) == 'hit' and f.fighter is not None:
            f.fighter.apply_status_effect(effects.burning())

def icebomb(actor, target, context):
    (x, y) = context['origin']
    ui.render_projectile((actor.x, actor.y), (x, y), spells.essence_colors['cold'], chr(7))
    ui.render_explosion(x, y, 1, libtcod.white, libtcod.light_sky)
    if actor is player.instance or fov.player_can_see(x, y):
        ui.message('The icebomb explodes!', spells.essence_colors['cold'])
    for f in target:
        if combat.spell_attack_ex(actor.fighter, f, None, '3d10', 0, ['cold'], 0) == 'hit' and f.fighter is not None:
            f.fighter.apply_status_effect(effects.frozen(duration=6))

def timebomb(actor, target, context):
    (x, y) = main.find_closest_open_tile(target.x, target.y)
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
                    combat.spell_attack_ex(ticker.actor.fighter, f, None, '6d10', 0, ['lightning'], 0)

def holy_water(actor, target, context):
    import monsters
    if not target.fighter.has_flag(monsters.EVIL):
        if actor is player.instance:
            ui.message('That target is not vulnerable to holy water.', libtcod.gray)
        return 'cancelled'
    ui.render_projectile((actor.x, actor.y), (target.x, target.y), color=spells.essence_colors['water'], character=libtcod.CHAR_BLOCK2)
    combat.spell_attack_ex(actor.fighter, target, None, context['base_damage'], 0, context['element'], context['pierce'])
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
            syntax.pronoun(target.name, possesive=True)),
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
    target.apply_status_effect(effects.invulnerable(10))
