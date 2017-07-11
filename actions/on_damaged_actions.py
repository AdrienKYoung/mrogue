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
import fov
import ui
import consts

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

def on_damaged_teleport(actor, attacker, damage):
    valid_teleports = []
    for x in range(attacker.x - 5, attacker.x + 5):
        if x < 0 or x >= consts.MAP_WIDTH - 1:
            continue
        for y in range(attacker.y - 5, attacker.y + 5):
            if y < 0 or y >= consts.MAP_HEIGHT - 1:
                continue
            if fov.monster_can_see_tile(actor, x, y):
                if not main.is_blocked(x, y, movement_type=actor.movement_type, is_player=actor is player.instance):
                    valid_teleports.append((x, y))
    final_teleports = []
    if attacker is not None:
        for vt in valid_teleports:
            if fov.monster_can_see_tile(attacker, vt[0], vt[1]):
                final_teleports.append(vt)
    else:
        final_teleports = list(valid_teleports)
    final_teleports.sort(key=lambda o: main.distance(o[0], o[1], actor.x, actor.y))
    index = len(final_teleports) - main.roll_dice('1d%d' % min(len(final_teleports), 5))
    teleport_position = final_teleports[index]

    ui.render_explosion(actor.x, actor.y, 0, libtcod.fuchsia, libtcod.white)
    actor.set_position(teleport_position[0], teleport_position[1])
    ui.render_explosion(actor.x, actor.y, 0, libtcod.fuchsia, libtcod.white)

table = {
    'on_damaged_summon_roaches': summon_roaches,
    'on_damaged_teleport': on_damaged_teleport,
    'player_get_hit': player.on_get_hit,
}