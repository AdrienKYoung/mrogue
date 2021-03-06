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

class StatusEffect:
    def __init__(self, name, time_limit=None, color=libtcod.white, stacking_behavior='refresh', on_apply=None, on_end=None, on_tick=None, message=None,
                 attack_power_mod=1.0,armor_mod=1.0,shred_mod=1.0,pierce_mod=1.0,attack_speed_mod=1.0,evasion_mod=1.0,spell_power_mod=1.0, spell_resist_mod=1.0,
                 accuracy_mod=1.0, resistance_mod={}, stacks=1, description='', cleanseable=True, will_mod=1.0, fortitude_mod=1.0, target_defense=None,
                 aftereffect = None):
        self.name = name
        self.time_limit = time_limit
        self.color = color
        self.on_apply = on_apply
        self.on_end = on_end
        self.on_tick = on_tick
        self.message = message
        self.attack_power_mod = attack_power_mod
        self.armor_mod = armor_mod
        self.shred_mod = shred_mod
        self.pierce_mod = pierce_mod
        self.attack_speed_mod = attack_speed_mod
        self.evasion_mod = evasion_mod
        self.spell_power_mod = spell_power_mod
        self.spell_resist_mod = spell_resist_mod
        self.resistance_mod = dict(resistance_mod)
        self.accuracy_mod = accuracy_mod
        self.stacking_behavior = stacking_behavior
        self.stacks = stacks
        self.description = description
        self.cleanseable = cleanseable
        self.will_mod = will_mod
        self.fortitude_mod = fortitude_mod
        self.target_defense = target_defense
        self.aftereffect = aftereffect

def burning(duration = 6, stacks = 1):
    return StatusEffect('burning', duration, spells.essence_colors['fire'], stacking_behavior='stack-refresh', stacks=stacks,
                        on_tick=fire_tick, message="You are on fire!", on_apply=burn_apply,
                        description='This unit will take fire damage at the end of every turn.', cleanseable=True,
                        target_defense='fortitude')

def exhausted(duration = 10):
    return StatusEffect('exhausted',duration,libtcod.yellow, message="You feel exhausted!",
                        description='This unit deals reduced damage.', cleanseable=True, target_defense='fortitude')

def cursed(duration = 10):
    return StatusEffect('cursed',duration,spells.essence_colors['death'], message="You have been cursed!",
                        description='This unit has reduced defenses.', armor_mod=0.65, spell_resist_mod=0.65,
                        evasion_mod=0.5, cleanseable=True, target_defense='will')

def stunned(duration = 1):
    return StatusEffect('stunned',duration,libtcod.red, message="You have been stunned!",
                        description='This unit cannot act.', stacking_behavior='ignore', target_defense='fortitude')

def stung(duration = 3):
    return StatusEffect('stung', duration, libtcod.orange, message="The bite stings!",
                        description='This unit takes increased damage.', target_defense='fortitude')

def frozen(duration = 1):
    return StatusEffect('frozen',duration,spells.essence_colors['cold'], message="You have been frozen solid!",
                        description='This unit cannot act.', on_apply=freeze_apply, target_defense='fortitude')

def judgement(duration = 30, stacks=10):
    return StatusEffect('judgement',duration,spells.essence_colors['radiance'], message="You are marked for judgement!", stacks=stacks,
                        description='This unit could be punished with smiting.', stacking_behavior='stack-refresh',
                        cleanseable=True, on_apply=check_judgement)

def immobilized(duration = 5):
    return StatusEffect('immobilized', duration, libtcod.yellow, message="Your feet are held fast!",
                        description='This unit cannot move.', cleanseable=True, evasion_mod=0.5, target_defense='fortitude')

def berserk(duration = 20):
    return StatusEffect('berserk',duration,libtcod.red, aftereffect=exhausted(), attack_power_mod=1.5, stacking_behavior='refresh',
                        message="You are overcome by rage!",
                        description='This unit attacks harder and faster.')

def regeneration(duration = 10):
    return StatusEffect('regeneration', duration, libtcod.green, on_tick=regeneration_tick,
                        message="Your wounds begin to close.",
                        description='This unit heals at the end of every turn.', cleanseable=False)

def warp_weapon(duration = 20):
    return StatusEffect('warp', duration, libtcod.gray, message="Your weapon turns black!",
                        description="This unit's weapon deals severe void damage.", cleanseable=False)

def poison(duration = 30):
    fx = StatusEffect('poisoned', duration, libtcod.yellow, message="You have been poisoned!",
                        description="This unit takes poison damage slowly.", on_tick=poison_tick,
                        stacking_behavior='extend', cleanseable=True, target_defense='fortitude')
    fx.timer = 0
    return fx

def toxic(duration = 30):
    return StatusEffect('toxic', duration, libtcod.chartreuse, message="You feel sick...", description=
                        'This unit heals half as much and takes triple damage from poison', cleanseable=True,
                        target_defense='fortitude')

def bleeding(duration = 5):
    return StatusEffect('bleeding', duration, libtcod.red, message="You are bleeding badly!",
                        description="This unit takes damage at the end of every turn.", on_tick=bleed_tick,
                        cleanseable=True, target_defense='fortitude')

def invulnerable(duration = 5):
    return StatusEffect('invulnerable', duration, spells.essence_colors['radiance'], message="A golden shield protects you from harm!",
                        description='This unit is immune to damage.', cleanseable=False)

def confusion(duration = 10):
    return StatusEffect('confusion', duration, libtcod.red, message="Madness takes hold of your mind!",
                        description='This unit spends its turn moving erratically.', target_defense='will',
                        on_apply=_set_confused_behavior)

def silence(duration=10):
    return StatusEffect('silence', duration, libtcod.red, message="You have been silenced!",
                        description='This unit cannot cast spells.', stacking_behavior='ignore', cleanseable=True,
                        target_defense='will')

def rot(duration = None):
    return StatusEffect('rot', duration, libtcod.red, message="Your flesh rots away!", on_apply=rot_apply,
                        on_end=rot_end, description='This unit has reduced maximum HP.', stacks=1,
                        stacking_behavior='stack-refresh', cleanseable=True, target_defense='fortitude')

def stoneskin(duration=30):
    return StatusEffect('stoneskin', duration, spells.essence_colors['earth'], armor_mod=1.5,
                        description='This unit has increased armor.', cleanseable=False)

def swiftness(duration=30):
    return StatusEffect('swiftness', duration, libtcod.light_blue, attack_speed_mod=1.3,
                        message='Your body feels light!', description='This unit makes faster attacks.', cleanseable=False)

def serenity(duration=30):
    return StatusEffect('serenity', duration, libtcod.light_blue, evasion_mod=1.5, accuracy_mod=1.5,
                        message='Your mind becomes calm.',
                        description='This unit has increased evasion and accuracy.', cleanseable=False)

def blessed(duration=20):
    return StatusEffect('blessed', duration, libtcod.light_blue, armor_mod=1.5, spell_power_mod=1.25, spell_resist_mod=1.5,
                        message="You are blessed by radiance!", description="This unit has increased armor, spell resist, and spell power")

def blinded(duration=10):
    return StatusEffect('serenity', duration, libtcod.light_blue, accuracy_mod=0.35,
                        message="Your can't see anything!",
                        description='This unit has sharply decreased accuracy.', cleanseable=True, target_defense='will')

def sluggish(duration=5):
    return StatusEffect('sluggish', duration, libtcod.sepia, message='Your reaction time slows...',
                        description='This unit has decreased evasion', target_defense='fortitude')

def slowed(duration=10):
    return StatusEffect('slowed', duration, libtcod.yellow, message='Your pace slows...',
                        description='This unit takes longer to take its turn.', cleanseable=True, target_defense='fortitude')

def agile(duration=30):
    return StatusEffect('agile', duration, libtcod.light_blue, evasion_mod=1.5,message='You speed up.',
                        description='This unit has increased evasion.', cleanseable=False)

def free_move(duration=2):
    return StatusEffect('free move', duration, libtcod.blue, description='Moving does not cost an action.', cleanseable=False)

def solace(duration=None):
    return StatusEffect('solace', duration, libtcod.blue, description='This unit takes half damage from all sources', cleanseable=False)

def off_balance(duration=2):
    return StatusEffect('off balance', duration, libtcod.red,
                        description='This unit is vulnerable to a critical strike.', cleanseable=False)

def auto_res(duration=None):
    return StatusEffect('auto-res', duration, libtcod.light_blue, message="You are blessed by life itself!",
                        description='This unit will come back to life with full health when killed.', cleanseable=False)

def reflect_magic(duration=20):
    return StatusEffect('reflect-magic', duration, libtcod.light_blue, message="You are protected against magic!",
                        description='Harmful magic will be returned to its caster.', cleanseable=False)

def doom(duration=5,stacks=1):
    return StatusEffect('doom',duration, libtcod.dark_crimson, stacking_behavior='stack-refresh', message='Death comes closer...',
                        on_apply=check_doom, description='At 13 stacks, this unit instantly dies.')

def oiled(duration=20):
    return StatusEffect('oiled', duration, libtcod.dark_gray, message='You are covered in oil!',
                        description='This unit has reduced accuracy and takes triple damage from burning.', cleanseable=True)

def lichform(duration=None):
    return StatusEffect('lichform',None,libtcod.darker_crimson,spell_resist_mod=1.5,resistance_mod=
    {'fire' : 3,'cold' : 3,'lightning' : 3,'poisoned' : 'immune','radiance' : 3,'death' : 'immune','void' : 3,'doom' :
        'immune','slugish' : 'immune','cursed' : 'immune', 'stunned' : 'immune','slowed' : 'immune','burning' : 'immune'
        ,'judgement' : 'immune','confusion' : 'immune','frozen' : 'immune','immobilized' : 'immune','exhausted' :
         'immune','rot' : 'immune','frostbite' : 'immune'},
        message="Dark magic infuses your soul as you sacrifice your body to undeath!",
        description='This unit is a lich, gaining resistance to all damage and immunity to death magic.', cleanseable=False)

def resistant(element=None,effect=None,color=None,duration=99):
    import spells
    if element is not None:
        return StatusEffect('resist ' + element,duration,spells.essence_colors[element],resistance_mod={element: 1},
                            message='You feel more resistant!', description='This unit is resistant to %s.' % element, cleanseable=False)
    else:
        return StatusEffect('resist ' + effect, duration, color, resistance_mod={effect : 1},
                            message='You feel more resistant!', description='This unit is resistant to %s.' % effect, cleanseable=False)

def focused(duration=1):
    return StatusEffect('focused', duration, libtcod.white, message='You focus on your target...',
                        description='This unit has increased accuracy', cleanseable=False)

def levitating(duration=100):
    return StatusEffect('levitating', duration, spells.essence_colors['air'],
                        message='You rise into the air...', description='This unit is levitating magically.',
                        cleanseable=False, on_end=levitation_end)

def hasted(duration=10):
    return StatusEffect('hasted', duration, spells.essence_colors['arcane'], message='Your movements become a blur.',
                        description='This unit moves twice as fast')

def meditate(duration=None):
    return StatusEffect('meditate', time_limit=duration,
                                      color=libtcod.yellow, description='Meditating will renew your missing spells.')

def vitality(duration=10):
    return StatusEffect('vitality', time_limit=duration, color=spells.essence_colors['life'], message=
                        'You feel healthy.', description='You are regenerating health and incoming damage is halved.',
                        on_tick=regeneration_tick)

def abated(effect, duration=30):
    return StatusEffect('{} abated'.format(effect.name), time_limit=duration, cleanseable=False,
                        color=libtcod.yellow, description='Your {} has abated for now'.format(effect.name), aftereffect=effect)

def unstable(duration=1):
    return StatusEffect('unstable', time_limit=duration, color=libtcod.flame, message="You feel like you might explode!",
                        description="Attacking this unit will cause a large explosion!")

#TODO - Move these to actions
def burn_apply(effect, object=None):
    if object is not None and object.fighter is not None and object.fighter.has_status('frozen'):
        object.fighter.remove_status('frozen')

def freeze_apply(effect, object=None):
    if object is not None and object.fighter is not None and object.fighter.has_status('burning'):
        object.fighter.remove_status('burning')

def fire_tick(effect,object=None):
    if object is not None and object.fighter is not None:
        if main.current_map.tiles[object.x][object.y].is_water:
            object.fighter.remove_status('burning')
        damage = effect.stacks * 3
        if object.fighter.has_status('oiled'):
            damage *= 3
        if object is player.instance:
            ui.message("You burn for {} damage!".format(damage),libtcod.flame)
        object.fighter.take_damage(damage)

def regeneration_tick(effect,object=None):
    if object is not None and object.fighter is not None:
        object.fighter.heal(3)

def poison_tick(effect,object=None):
    if object is not None and object.fighter is not None:
        if object.fighter.has_status('toxic'):
            object.fighter.take_damage(1, affect_shred=False)
        elif hasattr(effect,'timer'):
            if effect.timer > 2:
                object.fighter.take_damage(1, affect_shred=False)
                effect.timer = 0
            else:
                effect.timer += 1
        else:
            effect.timer = 0

def bleed_tick(effect, object=None):
    if object is not None and object.fighter is not None:
        damage = effect.stacks * 3
        if object is player.instance:
            ui.message("You bleed out for {} damage...".format(damage), libtcod.dark_red)
        object.fighter.take_damage(damage, affect_shred=False)

def rot_apply(effect,object=None):
    if object is not None and object.fighter is not None:
        object.fighter.max_hp -= 10 * effect.stacks
        object.fighter.take_damage(10 * effect.stacks)

def rot_end(effect,object=None):
    if object is not None and object.fighter is not None:
        object.fighter.max_hp += 10 * effect.stacks

def berserk_end(effect, object=None):
    if object is not None and object.fighter is not None:
        object.fighter.apply_status_effect(exhausted())

def check_judgement(effect, obj=None):
    fx = [f for f in obj.fighter.status_effects if f.name == 'judgement']
    if len(fx) > 0 and fx[0].stacks >= 100:
        ui.render_explosion(obj.x, obj.y, 2, libtcod.white, spells.essence_colors['radiance'])
        ui.message("%s %s judged!" % (syntax.name(obj).capitalize(), syntax.conjugate(obj is player.instance, ('are', 'is'))), libtcod.light_yellow)
        obj.fighter.take_damage(int(obj.fighter.max_hp / 3))
        obj.fighter.remove_status('judgement')

def levitation_end(effect, obj=None):
    if obj is not None:
        obj.set_position(obj.x, obj.y)


def _set_confused_behavior(object):
    import ai
    if object.behavior is not None:
        old_ai = object.behavior.behavior
        object.behavior.behavior = ai.ConfusedMonster(old_ai)
        object.behavior.behavior.owner = object

def check_doom(effect, obj=None):
    fx = [f for f in obj.fighter.status_effects if f.name == 'doom']
    if len(fx) > 0 and fx[0].stacks >= 13:
        ui.message("Death comes for {}".format(obj.name),libtcod.dark_crimson)
        obj.fighter.take_damage(obj.fighter.max_hp)

import ui
import player
import spells
import syntax
