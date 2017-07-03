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

import game as main
import libtcodpy as libtcod
import player
import syntax
import ui

def invoke_ability(ability_key, actor, target_override=None, spell_context=None):
    import abilities
    if actor is None:
        raise Exception('Missing parameter: actor')
    info = abilities.data[ability_key]
    if info is None:
        raise Exception("Invalid action key: {}".format(ability_key))
    function = info.get('function')
    if function is None:
        raise Exception("No function for action {}".format(ability_key))

    if spell_context is not None:
        info = dict(info.items() + spell_context.items())

    if 'require_weapon' in info:
        weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')
        if weapon is None or weapon.subtype != info['require_weapon']:
            ui.message('You need a {} to use this ability'.format(info['require_weapon']))
            return 'didnt-take-turn'

    if 'cast_time' in info.keys():
        if 'pre_cast' in info.keys():
            info['pre_cast']()
        else:
            ui.message_flush(
                syntax.conjugate(actor is player.instance, ['You begin', actor.name.capitalize() + ' begins']) + ' to cast ' + info['name'])
        if info.get('warning',False):
            targets = _get_ability_target(actor,info,target_override)
            info['warning_particles'] = _spawn_warning(actor,targets)
            target_override = targets
        delegate = lambda: _invoke_ability_continuation(info, actor, target_override, function)
        if actor is player.instance:
            player.delay(info['cast_time'], delegate, 'channel-spell')
        else:
            actor.behavior.behavior.queue_action(delegate, info['cast_time'])
        return 'success'
    else:
        return _invoke_ability_continuation(info, actor, target_override, function)


def _invoke_ability_continuation(info, actor, target_override, function):
    target = _get_ability_target(actor, info, target_override)

    if 'warning_particles' in info.keys():
        for p in info['warning_particles']:
            p.destroy()

    result = 'cancelled'
    if target is not None:
        result = function(actor,target,info)

    return result if result is not None else 'success'

def _get_ability_target(actor, info, target_override):
    targeting = info.get('targeting', 'pick')
    range = info.get('range', 1000)
    ground_targeting = info.get('target_ground', False)
    target = None
    burst = info.get('burst')

    if targeting == 'self' and burst is None:
        target = actor

    if target is None and targeting is not None:
        if actor is player.instance:
            ui.message_flush('Left-click a target tile, or right-click to cancel.', libtcod.white)
            default_target = None
            if ui.selected_monster is not None:
                default_target = ui.selected_monster.x, ui.selected_monster.y
            target = ui.target_tile(range, targeting, default_target=default_target)

        else:
            if target_override is not None and actor.distance_to(target_override) > range:
                target = None
                return target
            if targeting == 'pick':
                target = (target_override.x, target_override.y)
            elif targeting == 'cone':
                target = main.cone(actor.x, actor.y, target_override.x, target_override.y, max_range=info['range'])
            elif targeting == 'beam':
                target = main.beam(actor.x, actor.y, target_override.x, target_override.y)
            elif targeting == 'beam wide':
                # TODO: Support wide beam outside of player targeting
                raise Exception("Not supported")
            elif targeting == 'beam interrupt':
                target = main.beam_interrupt(actor.x, actor.y, target_override.x, target_override.y)
            elif targeting == 'summon':
                target = main.find_closest_open_tile(target_override.x, target_override.y)
            elif targeting == 'allies':
                target = target_override
            elif targeting == 'self':
                target = actor.x, actor.y

        if isinstance(target, tuple) and target[0] is None:
            target = None
        if target is None:
            return target

        if burst is not None and isinstance(target, tuple):
            if info.get('hits_friendlies', False):
                team = None
            elif info.get('team') is not None:
                team = info.get('team')
            else:
                team = actor.fighter.team
            info['origin'] = target[0], target[1]
            if not ground_targeting:
                target = main.get_fighters_in_burst(target[0], target[1], burst, actor, team)
            else:
                target = main.get_tiles_in_burst(target[0], target[1], burst)
        elif not ground_targeting and targeting != 'summon':
            if target is not None:
                if isinstance(target, list):
                    target = [main.get_monster_at_tile(*t) for t in target]
                else:
                    pos = target
                    target = None
                    for fighter in main.current_map.fighters:
                        if fighter.x == pos[0] and fighter.y == pos[1]:
                            target = fighter
                            break
    return target

def _spawn_warning(actor,tiles):
    warning_particles = []
    for tile in tiles:
        go = main.GameObject(tile[0], tile[1], 'X', 'Warning', libtcod.red,
                             description="Spell Warning. Source: {}".format(actor.name.capitalize()))
        main.current_map.add_object(go)
        warning_particles.append(go)