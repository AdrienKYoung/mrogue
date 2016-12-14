import libtcodpy as libtcod
import game as main

class StatusEffect:
    def __init__(self, name, time_limit=None, color=libtcod.white, on_apply=None, on_end=None, on_tick=None, message=None):
        self.name = name
        self.time_limit = time_limit
        self.color = color
        self.on_apply = on_apply
        self.on_end = on_end
        self.on_tick = on_tick
        self.message = message


def burning(duration = 8):
    return StatusEffect('burning', duration, libtcod.red, on_tick=fire_tick, message="You are on fire!")

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
    return StatusEffect('berserk',duration,libtcod.red,on_end=berserk_end, message="You are overcome by rage!")

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

def fire_tick(object=None):
    if object is None or object.fighter is None or \
                    main.dungeon_map[object.x][object.y].tile_type == 'shallow water' or \
                    main.dungeon_map[object.x][object.y].tile_type == 'deep water':
        object.fighter.remove_status('burning')
    object.fighter.take_damage(5)

def regeneration_tick(object=None):
    if object is not None or object.fighter is not None:
        object.fighter.heal(5)

def poison_tick(object=None):
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