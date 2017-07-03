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
import common
import fov

def swap(actor,target,_):
    actor.swap_positions(target)

def mace_stun(attacker, target, damage):
    scaling_factor = 1
    stun_duration = 1
    if target.fighter is None:
        return
    if(attacker is player.instance):
        scaling_factor = attacker.player_stats.str / 10
        if main.has_skill('ringing_blows'):
            scaling_factor *= 1.5
            stun_duration = 2
    if libtcod.random_get_float(0,0.0,1.0) * scaling_factor > 0.85:
        if attacker == player.instance:
            ui.message("Your " + main.get_equipped_in_slot(player.instance.fighter.inventory,'right hand').owner.name.title() + " rings out!",libtcod.blue)
        target.fighter.apply_status_effect(effects.stunned(stun_duration))

def disarm_attack(actor,target,damage):
    if main.roll_dice('1d5') == 5:
        common.disarm(target)

def poison_attack(actor,target,damage):
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

def on_hit_judgement(attacker, target, damage):
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.judgement(stacks=main.roll_dice('2d6')))


def on_hit_rot(attacker, target, damage):
    if target.fighter is not None:
        target.fighter.apply_status_effect(effects.rot())

def on_hit_curse(attacker, target, damage):
    if target.fighter is not None and libtcod.random_get_int(0,0,20) < damage:
        target.fighter.apply_status_effect(effects.cursed())


def on_hit_sting(attacker, target, damage):
    if target.fighter is None:
        return
    target.fighter.apply_status_effect(effects.StatusEffect('stung', 3, libtcod.flame), dc=8)


def zombie_on_hit(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 0, 100) < 20:
        ui.message('%s grabs %s! %s cannot move!' % (
                        syntax.name(attacker).capitalize(),
                        syntax.name(target),
                        syntax.pronoun(target.name).capitalize()), libtcod.yellow)
        target.fighter.apply_status_effect(effects.immobilized(3))

def on_hit_burn(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 1, 10) <= 7:
        target.fighter.apply_status_effect(effects.burning())

def on_hit_freeze(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 1, 10) <= 3:
        target.fighter.apply_status_effect(effects.frozen(duration=3))

def on_hit_slow(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 1, 10) <= 7:
        target.fighter.apply_status_effect(effects.slowed(duration=5))

def on_hit_sluggish(attacker, target, damage):
    if target.fighter is None:
        return
    if libtcod.random_get_int(0, 1, 10) <= 7:
        target.fighter.apply_status_effect(effects.sluggish(duration=5))

def on_hit_chain_lightning(attacker, target, damage, zapped=None):
    if zapped is None:
        zapped = [target]
    else:
        zapped.append(target)
    if target.fighter is None:
        return
    damage = combat.roll_damage_ex('1d10', '0d0', target.fighter.armor, 5, 'lightning', 1.0,
                            target.fighter.resistances)

    if damage > 0:
        combat.attack_text_ex(attacker.fighter, target, None, None, damage, 'lightning', float(damage) / float(target.fighter.max_hp))

        target.fighter.take_damage(damage, attacker=attacker)
        for adj in main.adjacent_tiles_diagonal(target.x, target.y):
            for obj in main.current_map.fighters:
                if obj.x == adj[0] and obj.y == adj[1] and obj.fighter.team != attacker.fighter.team and obj not in zapped:
                    on_hit_chain_lightning(attacker, obj, damage, zapped)
    else:
        ui.message('The shock does not damage %s' % syntax.name(target), libtcod.grey)

def on_hit_lifesteal(attacker, target, damage):
    attacker.fighter.heal(damage)

def on_hit_knockback(attacker, target, damage, force=6):
    if target.fighter is None:
        return

    if 'displacement' in target.fighter.immunities:
        if fov.player_can_see(target.x, target.y):
            ui.message('%s %s.' % (syntax.name(target).capitalize(), syntax.conjugate(
                target is player.instance, ('resist', 'resists'))), libtcod.gray)
        return

    diff_x = target.x - attacker.x
    diff_y = target.y - attacker.y
    if diff_x > 0:
        diff_x = diff_x / abs(diff_x)
    if diff_y > 0:
        diff_y = diff_y / abs(diff_y)
    direction = (diff_x, diff_y)

    steps=0
    while steps <= force:
        steps += 1
        against = main.get_objects(target.x + direction[0], target.y + direction[1], lambda o: o.blocks)
        if against is None or len(against) == 0:
            against = syntax.name(main.current_map.tiles[target.x + direction[0]][target.y + direction[1]])
        else:
            against = 'the ' + against.name
        if not target.move(direction[0], direction[1]):
            # Could not move
            damage = combat.roll_damage_ex('%dd4' % steps, '0d0', target.fighter.armor, 0, 'budgeoning', 1.0,
                                    target.fighter.resistances)
            ui.message('%s %s backwards and collides with %s, taking %d damage.' % (
                syntax.name(target).capitalize(),
                syntax.conjugate(target is player.instance, ('fly', 'flies')),
                against,
                damage), libtcod.gray)
            target.fighter.take_damage(damage, attacker=attacker)
            steps = force + 1

def on_hit_reanimate(attacker, target, damage):
    main.raise_dead(attacker,target)

table = {
    'on_hit_swap': swap,
    'on_hit_stun': mace_stun,
    'on_hit_disarm': disarm_attack,
    'on_hit_poison': poison_attack,
    'on_hit_oil': oil_attack,
    'on_hit_immobilize': immobilize_attack,
    'on_hit_toxic': toxic_attack,
    'on_hit_judgement': on_hit_judgement,
    'on_hit_rot': on_hit_rot,
    'on_hit_curse': on_hit_curse,
    'on_hit_sting': on_hit_sting,
    'on_hit_burn': on_hit_burn,
    'on_hit_freeze': on_hit_freeze,
    'on_hit_slow': on_hit_slow,
    'on_hit_reanimate': on_hit_reanimate,
    'on_hit_sluggish': on_hit_sluggish,
    'on_hit_chain_lightning': on_hit_chain_lightning,
    'on_hit_knockback': on_hit_knockback,
    'zombie_on_hit': zombie_on_hit,
}