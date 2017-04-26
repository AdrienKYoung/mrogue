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
import ui
import player
import actions

class StatusEffect:
    def __init__(self, name, time_limit=None, color=libtcod.white, stacking_behavior='refresh', on_apply=None, on_end=None, on_tick=None, message=None,
                 attack_power_mod=1.0,armor_mod=1.0,shred_mod=1.0,pierce_mod=1.0,attack_speed_mod=1.0,evasion_mod=1.0,spell_power_mod=1.0, spell_resist_mod=1.0,
                 accuracy_mod=1.0, resistance_mod=[],weakness_mod=[], stacks=1, description='', cleanseable=True):
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
        self.resistance_mod = resistance_mod
        self.weakness_mod = weakness_mod
        self.accuracy_mod = accuracy_mod
        self.stacking_behavior = stacking_behavior
        self.stacks = stacks
        self.description = description
        self.cleanseable = False


def burning(duration = 6, stacks = 1):
    return StatusEffect('burning', duration, libtcod.red, stacking_behavior='stack-refresh', stacks=stacks,
                        on_tick=fire_tick, message="You are on fire!",
                        description='This unit will take fire damage at the end of every turn.')

def exhausted(duration = 10):
    return StatusEffect('exhausted',duration,libtcod.yellow, message="You feel exhausted!",
                        description='This unit deals reduced damage.', attack_power_mod=0.55)

def cursed(duration = 10):
    return StatusEffect('exhausted',duration,libtcod.yellow, message="You have been cursed!",
                        description='This unit has reduced defenses.', armor_mod=0.65, spell_resist_mod=0.65,
                        evasion_mod=0.5)

def stunned(duration = 1):
    return StatusEffect('stunned',duration,libtcod.red, message="You have been stunned!",
                        description='This unit cannot act.')

def frozen(duration = 1):
    return StatusEffect('frozen',duration,libtcod.blue, message="You have been frozen solid!",
                        description='This unit cannot act.')

def judgement(duration = 10):
    return StatusEffect('judgement',duration,libtcod.yellow, message="A vengeful god watches your every move!",
                        description='This unit will be punished for evil deeds.')

def immobilized(duration = 5):
    return StatusEffect('immobilized', duration, libtcod.yellow, message="Your feet are held fast!",
                        description='This unit cannot move.')

def berserk(duration = 20):
    return StatusEffect('berserk',duration,libtcod.red, on_end=berserk_end, attack_power_mod=1.5,
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
                        description="This unit takes poison damage slowly.", on_tick=poison_tick, stacking_behavior='extend')
    fx.timer = 0
    return fx

def bleeding(duration = 5):
    return StatusEffect('bleeding', duration, libtcod.red, message="You are bleeding badly!",
                        description="This unit takes damage at the end of every turn.", on_tick=bleed_tick)

def invulnerable(duration = 5):
    return StatusEffect('invulnerable', duration, libtcod.blue, message="A golden shield protects you from harm!",
                        description='This unit is immune to damage.', cleanseable=False)

def confusion(duration = 10):
    return StatusEffect('confusion', duration, libtcod.red, message="Madness takes hold of your mind!",
                        description='This unit spends its turn moving erratically.')

def silence(duration=3):
    return StatusEffect('silence', duration, libtcod.red, message="You have been silenced!",
                        description='This unit cannot cast spells.')

def rot(duration = -1):
    return StatusEffect('rot', duration, libtcod.red, message="Your flesh rots away!", on_apply=rot_apply,
                        on_end=rot_end, description='This unit has reduced maximum HP.')

def stoneskin(duration=30):
    return StatusEffect('stoneskin', duration, libtcod.light_blue, armor_mod=1.5, message='Your skin turns to stone!',
                        description='This unit has increased armor.', cleanseable=False)

def swiftness(duration=30):
    return StatusEffect('swiftness', duration, libtcod.light_blue, attack_speed_mod=1.3,
                        message='Your body feels light!', description='This unit makes faster attacks.', cleanseable=False)

def serenity(duration=30):
    return StatusEffect('serenity', duration, libtcod.light_blue, evasion_mod=1.5, accuracy_mod=1.5,
                        message='Your mind becomes calm.',
                        description='This unit has increased evasion and accuracy.', cleanseable=False)

def blinded(duration=10):
    return StatusEffect('serenity', duration, libtcod.light_blue, accuracy_mod=0.35,
                        message="Your can't see anything!",
                        description='This unit has sharply decreased accuracy.')

def sluggish(duration=5):
    return StatusEffect('sluggish', duration, libtcod.sepia, message='Your reaction time slows...',
                        description='This unit has decreased evasion')

def slowed(duration=10):
    return StatusEffect('slowed', duration, libtcod.yellow, message='Your pace slows...',
                        description='This unit takes longer to take its turn.')

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

def doom(duration=5,stacks=1):
    return StatusEffect('doom',duration, libtcod.dark_crimson, stacking_behavior='stack-refresh', message='Death comes closer...',
                        on_apply=actions.check_doom, description='At 13 stacks, this unit instantly dies.')

def lichform(duration=None):
    return StatusEffect('lichform',None,libtcod.darker_crimson,spell_resist_mod=1.5,resistance_mod=
        ['fire','cold','lightning','poison','radiant','dark','void','doom','slugish','curse'
         'stunned','slowed','burning','judgement','confusion','frozen','immobilized','exhausted','rot','frostbite'],
        message="Dark magic infuses your soul as you sacrifice your body to undeath!",
        description='This unit is a lich, gaining resistance to all damage and immunity to death magic.', cleanseable=False)

def resistant(element=None,effect=None,color=None,duration=99):
    import spells
    if element is not None:
        return StatusEffect('resist ' + element,duration,spells.essence_colors[element],resistance_mod=[element],
                            message='You feel more resistant!', description='This unit is resistant to %s.' % element, cleanseable=False)
    else:
        return StatusEffect('resist ' + effect, duration, color, resistance_mod=[effect],
                            message='You feel more resistant!', description='This unit is resistant to %s.' % effect, cleanseable=False)

def fire_tick(effect,object=None):
    if object is not None and object.fighter is not None:
        if main.current_map.tiles[object.x][object.y].is_water:
            object.fighter.remove_status('burning')
        damage = effect.stacks * 3
        if object is player.instance:
            ui.message("You burn for {} damage!".format(damage),libtcod.flame)
        object.fighter.take_damage(damage)

def regeneration_tick(effect,object=None):
    if object is not None and object.fighter is not None:
        object.fighter.heal(3)

def poison_tick(effect,object=None):
    if object is not None and object.fighter is not None:
        if hasattr(effect,'timer'):
            if effect.timer > 2:
                object.fighter.take_damage(1)
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
        object.fighter.take_damage(damage)

def rot_apply(object=None):
    if object is not None and object.fighter is not None:
        object.fighter.max_hp -= 20
        object.fighter.take_damage(20)

def rot_end(object=None):
    if object is not None and object.fighter is not None:
        object.fighter.max_hp += 20

def berserk_end(object=None):
    if object is not None and object.fighter is not None:
        object.fighter.apply_status_effect(exhausted())