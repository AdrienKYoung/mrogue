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
import npc
import common

def on_death_summon(obj,context):
    ui.message('%s is dead!' % syntax.name(obj).capitalize(), libtcod.red)
    obj.fighter = None
    main.current_map.fighters.remove(obj)
    obj.destroy()

    if context.get('require_tile') is not None:
        tile_at_location = main.current_map.tiles[obj.x][obj.y]
        if context['require_tile'] != tile_at_location.tile_type:
            return

    if 'message' in context.keys():
        ui.message(context['message'])

    monster = main.spawn_monster(context['monster'], obj.x, obj.y)
    monster.fighter.apply_status_effect(effects.stunned(1)) #summoning sickness
    if 'duration' in context:
        monster.summon_time = context['duration']

    if ui.selected_monster is obj:
        main.changed_tiles.append((obj.x, obj.y))
        ui.selected_monster = None
        ui.auto_target_monster()

def scum_glob_death(glob, context):
    ui.message('%s divides!' % syntax.name(glob).capitalize(), libtcod.red)
    pos = glob.x, glob.y
    glob.fighter = None
    glob.destroy()
    for i in range(3):
        spawn = main.find_closest_open_tile(pos[0], pos[1])
        main.spawn_monster('monster_scum_glob_small', spawn[0], spawn[1])
        tile = main.current_map.tiles[spawn[0]][spawn[1]]
        if not tile.is_water and not tile.tile_type == 'oil' and not tile.is_ramp:
            tile.tile_type = 'oil'

    if ui.selected_monster is glob:
        main.changed_tiles.append(pos)
        ui.selected_monster = None
        ui.auto_target_monster()


def blastcap_explode(blastcap, context):
    blastcap.fighter = None
    main.current_map.fighters.remove(blastcap)
    ui.render_explosion(blastcap.x, blastcap.y, 1, libtcod.gold, libtcod.white, distance_h='manhattan')
    ui.message('The blastcap explodes with a BANG, stunning nearby creatures!', libtcod.gold)
    for obj in main.current_map.fighters:
        if main.is_adjacent_orthogonal(blastcap.x, blastcap.y, obj.x, obj.y):
            if obj.fighter.apply_status_effect(effects.stunned(duration=context['duration'])):
                ui.message('%s %s stunned!' % (
                                syntax.name(obj).capitalize(),
                                syntax.conjugate(obj is player.instance, ('are', 'is'))), libtcod.gold)

    if ui.selected_monster is blastcap:
        main.changed_tiles.append((blastcap.x, blastcap.y))
        ui.selected_monster = None
        ui.auto_target_monster()

    blastcap.destroy()
    return

def bomb_beetle_death(beetle, context):

    ui.message('%s is dead!' % syntax.name(beetle).capitalize(), libtcod.red)
    beetle.char = 149
    beetle.color = libtcod.black
    beetle.blocks = True
    beetle.fighter = None
    beetle.behavior = None
    beetle.name = 'beetle bomb'
    beetle.description = 'The explosive carapace of a blast beetle. In a few turns, it will explode!'
    beetle.bomb_timer = 3
    beetle.on_tick = bomb_beetle_corpse_tick
    if hasattr(beetle, 'recoverable_ammo'):
        main.drop_ammo(beetle.x, beetle.y, beetle.recoverable_ammo)
        del beetle.recoverable_ammo
    main.current_map.fighters.remove(beetle)

    if ui.selected_monster is beetle:
        main.changed_tiles.append((beetle.x, beetle.y))
        ui.selected_monster = None
        ui.auto_target_monster()


def bomb_beetle_corpse_tick(object=None, context=None):
    if object is None:
        return
    object.bomb_timer -= 1
    if object.bomb_timer > 2:
        object.color = libtcod.black
    elif object.bomb_timer > 1:
        object.color = libtcod.darkest_red
    elif object.bomb_timer > 0:
        object.color = libtcod.red
    elif object.bomb_timer <= 0:
        ui.message('The bomb beetle corpse explodes!', libtcod.orange)
        ui.render_explosion(object.x, object.y, 1, libtcod.yellow, libtcod.flame)
        main.create_fire(object.x, object.y, 10)
        for tile in main.adjacent_tiles_diagonal(object.x, object.y):
            if libtcod.random_get_int(0, 0, 3) != 0:
                main.create_fire(tile[0], tile[1], 10)
                main.melt_ice(tile[0], tile[1])
            monster = main.get_objects(tile[0], tile[1], lambda o: o.fighter is not None)
            if len(monster) > 0:
                monster[0].fighter.take_damage(main.roll_dice('22d3'))
                if monster[0].fighter is not None:
                    monster[0].fighter.apply_status_effect(effects.burning())
        object.destroy()

table = {
    'on_death_summon': on_death_summon,
    'on_death_scum_glob': scum_glob_death,
    'on_death_blastcap': blastcap_explode,
    'on_death_bomb': bomb_beetle_death,
    'default': main.monster_death,
    'player': player.on_death,
}