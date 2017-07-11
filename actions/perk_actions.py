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
import game as main
import libtcodpy as libtcod
import player
import ui
import abilities


def essence_fist(actor, target, context):
    ops = player.instance.essence
    choice = ui.menu('Which essence?',ops)
    if choice is not None:
        essence = ops[choice]
    else:
        return "didnt-take-turn"

    result = combat.attack_ex(player.instance.fighter,target,context['stamina_cost'],damage_multiplier=context['damage_multiplier'])
    if result != 'failed':
        player.instance.essence.remove(essence)
        return result

def sweep_attack(actor, target, context):
    weapon = main.get_equipped_in_slot(actor.fighter.inventory, 'right hand')

    if weapon is None or weapon.subtype != 'polearm':
        ui.message('You need a polearm to use this ability')
        return 'didnt-take-turn'

    targets = main.get_objects(actor.x,actor.y,distance=2, condition=lambda o: o.fighter is not None and o.fighter.team != 'ally')
    targets = [t for t in targets if (abs(t.x - actor.x) == 2 or abs(t.y - actor.y) == 2)]
    if len(targets) > 0:
        for enemy in targets:
            combat.attack_ex(actor.fighter,enemy,0, verb=('sweep','sweeps'))
        actor.fighter.adjust_stamina(-(weapon.stamina_cost * context['stamina_multiplier']))
        return True
    else:
        ui.message('There are no targets in range')
        return 'didnt-take-turn'


def blade_dance(actor, target, context):
    actor.swap_positions(target)
    actor.fighter.attack(target)

def pommel_strike(actor, target, context):
    combat.attack_ex(actor.fighter, target, int(actor.fighter.calculate_attack_stamina_cost() * 1.5),
                     verb=('pommel-strike', 'pommel-strikes'), shred_modifier=2)
    actor.fighter.apply_status_effect(effects.exhausted(5))

def skullsplitter(actor, target, context):
    combat.attack_ex(actor.fighter, target, int(actor.fighter.calculate_attack_stamina_cost() * 1.5),
                    damage_multiplier=1.5 * (2 - target.fighter.hp / target.fighter.max_hp))

def crush(actor, target, context):
    combat.attack_ex(actor.fighter, target, int(actor.fighter.calculate_attack_stamina_cost() * 1.5),
                     damage_multiplier=1.5 + ((target.fighter.armor + 1) / 20) * 2.5,
                     shred_modifier=1 + int(target.fighter.armor / 2))

def focus(actor, target, context):
    actor.fighter.apply_status_effect(effects.focused(duration=2))

def summon_guardian_angel(actor, target, context):
    x,y = target
    common.summon_ally('monster_guardian_angel', 30 + libtcod.random_get_int(0, 0, 15), x, y)
    ui.message('Your prayers have been answered!',libtcod.light_blue)

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
        common.attack(actor,target)

def learn_ability(ability):
    dat = abilities.data[ability]
    a = abilities.Ability(dat.get('name'), dat.get('description', ''), dat.get('function'), dat.get('cooldown', 0))
    player.instance.perk_abilities.append(a)