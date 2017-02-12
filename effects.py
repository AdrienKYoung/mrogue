import libtcodpy as libtcod
import game as main
import spells
import ui
import player

class StatusEffect:
    def __init__(self, name, time_limit=None, color=libtcod.white, stacking_behavior='refresh', on_apply=None, on_end=None, on_tick=None, message=None,
                 attack_power_mod=1.0,armor_mod=1.0,shred_mod=1.0,pierce_mod=1.0,attack_speed_mod=1.0,evasion_mod=1.0,spell_power_mod=1.0,
                 accuracy_mod=1.0, resistance_mod=[],weakness_mod=[], stacks=1):
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
        self.resistance_mod = resistance_mod
        self.weakness_mod = weakness_mod
        self.accuracy_mod = accuracy_mod
        self.stacking_behavior = stacking_behavior
        self.stacks = stacks


def burning(duration = 6, stacks = 1):
    return StatusEffect('burning', duration, libtcod.red, stacking_behavior='stack-refresh', stacks=stacks, on_tick=fire_tick, message="You are on fire!")

def exhausted(duration = 5):
    return StatusEffect('exhausted',duration,libtcod.yellow, message="You feel exhausted!")

def stunned(duration = 1):
    return StatusEffect('stunned',duration,libtcod.red, message="You have been stunned!")

def frozen(duration = 1):
    return StatusEffect('frozen',duration,libtcod.blue, message="You have been frozen solid!")

def judgement(duration = 10):
    return StatusEffect('judgement',duration,libtcod.yellow, message="A vengeful god watches your every move!")

def immobilized(duration = 5):
    return StatusEffect('immobilized', duration, libtcod.yellow, message="Your feet are held fast!")

def berserk(duration = 20):
    return StatusEffect('berserk',duration,libtcod.red,on_end=berserk_end, attack_power_mod=1.5, message="You are overcome by rage!")

def regeneration(duration = 10):
    return StatusEffect('regeneration',duration,libtcod.green,on_tick=regeneration_tick,message="Your wounds begin to close.")

def warp_weapon(duration = 20):
    return StatusEffect('warp',duration,libtcod.gray,message="Your weapon turns black!")

def poison(duration = 10):
    return StatusEffect('poisoned',duration,libtcod.yellow,message="You have been poisoned!")

def invulnerable(duration = 5):
    return StatusEffect('invulnerable',duration,libtcod.blue,message="A magical shield protects you from harm!")

def confusion(duration = 10):
    return StatusEffect('confusion',duration,libtcod.red,message="Madness takes hold of your mind!")

def rot(duration = -1):
    return StatusEffect('rot',duration,libtcod.red,message="Your flesh rots away!",on_apply=rot_apply,on_end=rot_end)

def stoneskin(duration=30):
    return StatusEffect('stoneskin',duration,libtcod.light_blue,armor_mod=1.5,message='Your skin turns to stone!')

def swiftness(duration=30):
    return StatusEffect('swiftness', duration, libtcod.light_blue, attack_speed_mod=1.3,message='Your body feels light!')

def serenity(duration=30):
    return StatusEffect('serenity', duration, libtcod.light_blue, evasion_mod=1.5, accuracy_mod=1.5, message='Your mind becomes calm.')

def sluggish(duration=5):
    return StatusEffect('sluggish', duration, libtcod.sepia, message='Your reaction time slows...')

def slowed(duration=10):
    return StatusEffect('slowed', duration, libtcod.dark_blue, message='Your pace slows...')

def resistant(element=None,effect=None,color=None,duration=99):
    if element is not None:
        return StatusEffect('resist ' + element,duration,spells.essence_colors[element],resistance_mod=[element],
                            message='You feel more resistant!')
    else:
        return StatusEffect('resist ' + effect, duration, color, resistance_mod=[effect],
                            message='You feel more resistant!')

def fire_tick(effect,object=None):
    if object is not None or object.fighter is not None:
        if main.current_map.tiles[object.x][object.y].is_water:
            object.fighter.remove_status('burning')
        damage = effect.stacks * 3
        if object is player.instance:
            ui.message("You burn for {} damage!".format(damage),libtcod.flame)
        object.fighter.take_damage(damage)

def regeneration_tick(effect,object=None):
    if object is not None or object.fighter is not None:
        object.fighter.heal(3)

def poison_tick(effect,object=None):
    if object is not None or object.fighter is not None:
        object.fighter.take_damage(2)

def rot_apply(object=None):
    if object is not None or object.fighter is not None:
        object.fighter.max_hp -= 20
        object.fighter.take_damage(20)

def rot_end(object=None):
    if object is not None or object.fighter is not None:
        object.fighter.max_hp += 20

def berserk_end(object=None):
    if object is not None or object.fighter is not None:
        object.fighter.apply_status_effect(exhausted())