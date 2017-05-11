#mrogue, an interactive adventure game
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

from game import *
import fov
import consts
import game
import ui
import effects
import player
import syntax

def acquire_target(monster, priority=None):
    if not monster.fighter:
        return None

    if priority is not None:
        if monster.fighter.team != priority.fighter.team and fov.monster_can_see_object(monster, priority):
            return priority

    closest = None
    closest_dist = 10000
    if monster.fighter.team == 'ally':
        target_team = 'enemy'
    elif monster.fighter.team == 'enemy':
        target_team = 'ally'
    else:  # Neutral fighters acquire no targets
        return None
    for o in game.current_map.fighters:
        if o.fighter.team == target_team and o.fighter.hp > 0 and fov.monster_can_see_object(monster, o):
            dist = monster.distance_to(o)
            if closest is None or dist < closest_dist:
                closest = o
                closest_dist = dist
    return closest


def aggro_on_hit(monster, attacker):
    if attacker is None:
        return
    if fov.monster_can_see_object(monster, attacker):
        if libtcod.random_get_int(0, 0, 1) == 0:
        # 50% chance to aggro onto the attacker
            monster.behavior.behavior.target = attacker
            monster.behavior.behavior.last_seen_position = attacker.x, attacker.y
            monster.behavior.ai_state = 'pursuing'
    else:
        monster.behavior.behavior.wander_destination = attacker.x, attacker.y
        monster.behavior.behavior.ai_state = 'wandering'


class AI_Default:

    def __init__(self):
        self.last_seen_position = None
        self.wander_destination = None
        self.target = None
        self._queued_action = None
        self._delay_turns = 0

    def act(self, ai_state):
        if ai_state == 'pursuing':
            return self.pursue()
        elif ai_state == 'wandering':
            return self.wander()
        elif ai_state == 'following':
            return self.follow()
        elif ai_state == 'channeling':
            return self.channel()
        else:
            return self.rest()

    def follow(self):
        monster = self.owner
        target = acquire_target(monster)
        if target is not None:
            self.last_seen_position = target.x, target.y
            self.target = target
            monster.behavior.ai_state = 'pursuing'
            return 0.0
        if monster.behavior.follow_target is None:
            monster.behavior.ai_state = 'resting'
            return 0.0
        monster.move_astar(monster.behavior.follow_target.x, monster.behavior.follow_target.y)
        return monster.behavior.move_speed

    def rest(self):
        monster = self.owner
        if monster.behavior.follow_target is not None:
            monster.behavior.ai_state = 'following'
            return 0.0
        target = acquire_target(monster)
        if target is not None:
            self.last_seen_position = target.x, target.y
            self.target = target
            monster.behavior.ai_state = 'pursuing'
            return 0.0
        return 1.0

    def pursue(self):
        monster = self.owner
        if self.target is None or self.target.fighter is None or self.target.fighter.hp <= 0:
            if monster.behavior.follow_target is not None:
                monster.behavior.ai_state = 'following'
            else:
                monster.behavior.ai_state = 'wandering'
            self.target = None
            self.last_seen_position = None
            return 0.0
        if fov.monster_can_see_object(monster, self.target):
            self.last_seen_position = self.target.x, self.target.y
            # Handle default ability use behavior
            if not monster.fighter.has_status('silence'):
                for a in monster.fighter.abilities:
                    if a.current_cd <= 0 and game.roll_dice('1d10') > 5:
                        # Use abilities when they're up
                        if a.use(monster, self.target) != 'didnt-take-turn':
                            return monster.behavior.attack_speed

            if monster.fighter.range > 1 and monster.distance_to(self.target) <= monster.fighter.range:
                monster.fighter.attack(self.target)
                ui.render_projectile([monster.x, monster.y], [self.target.x, self.target.y], libtcod.white)
                if monster.behavior is not None:
                    return monster.behavior.attack_speed

            # Handle moving
            if not is_adjacent_diagonal(monster.x, monster.y, self.target.x, self.target.y):
                monster.move_astar(self.target.x, self.target.y)
                if monster.behavior is not None: #need this check because the monster may die while moving
                    return monster.behavior.move_speed
                else:
                    return 1

            # Handle attacking
            else:
                monster.fighter.attack(self.target)
                if monster.behavior is not None:
                    return monster.behavior.attack_speed
                else:
                    return 1

        elif self.last_seen_position is not None and not\
                (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
            result = monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])
            if result == 'failure':
                self.last_seen_position = None
                return 1.0
            return monster.behavior.move_speed
        else:
            monster.behavior.ai_state = 'wandering'
            return 0.0

    def wander(self):
        monster = self.owner
        target = acquire_target(monster)
        if target is not None:
            self.last_seen_position = target.x, target.y
            self.target = target
            self.wander_destination = None
            monster.behavior.ai_state = 'pursuing'
            return 0.0
        else:
            if self.wander_destination is None or \
                    (monster.x == self.wander_destination[0] and monster.y == self.wander_destination[1]):
                rand_pos = libtcod.random_get_int(0, 0, consts.MAP_WIDTH), libtcod.random_get_int(0, 0, consts.MAP_HEIGHT)
                self.wander_destination = game.find_closest_open_tile(rand_pos[0], rand_pos[1])
            monster.move_astar(self.wander_destination[0], self.wander_destination[1])
            return monster.behavior.move_speed

    def channel(self):
        monster = self.owner
        if self._delay_turns < 1:
            self._queued_action()
            if monster.behavior.follow_target is not None:
                monster.behavior.ai_state = 'following'
            target = acquire_target(monster)
            if target is not None:
                self.last_seen_position = target.x, target.y
                self.target = target
                monster.behavior.ai_state = 'pursuing'
            else:
                monster.behavior.ai_state = 'resting'
        self._delay_turns -= 1
        return 1.0

    def on_get_hit(self, attacker,damage):
        aggro_on_hit(self.owner, attacker)

    def queue_action(self,action,delay):
        self._queued_action = action
        self._delay_turns = delay
        self.owner.behavior.ai_state = 'channeling'

class AI_Reeker:

    def act(self, ai_state):
        monster = self.owner
        monster.behavior.ai_state = 'idle'
        if fov.player_can_see(monster.x, monster.y):
            for i in range(consts.REEKER_PUFF_MAX):
                if libtcod.random_get_int(0, 0, 10) < 3:
                    # create puff
                    position = random_position_in_circle(consts.REEKER_PUFF_RADIUS)
                    puff_pos = (clamp(monster.x + position[0], 1, consts.MAP_WIDTH - 2),
                                clamp(monster.y + position[1], 1, consts.MAP_HEIGHT - 2))
                    if not game.current_map.tiles[puff_pos[0]][puff_pos[1]].blocks and len(get_objects(puff_pos[0], puff_pos[1],
                                                        lambda o: o.name == 'reeker gas' or o.name == 'reeker')) == 0:
                        puff = GameObject(puff_pos[0], puff_pos[1], libtcod.CHAR_BLOCK3,
                                          'reeker gas', libtcod.dark_fuchsia, description='a puff of reeker gas',
                                          misc=ReekerGasBehavior())
                        game.current_map.add_object(puff)
        return monster.behavior.attack_speed


class AI_Sentry:

    def __init__(self):
        self.target = None
        self._queued_action = None
        self._delay_turns = 0

    def act(self, ai_state):
        monster = self.owner
        if self.target is None or self.target.fighter is None or \
                        monster.distance_to(self.target) > monster.fighter.range or \
                        not fov.monster_can_see_object(monster, self.target):
            self.target = acquire_target(monster)

        if self.target is not None:
            # Handle default ability use behavior
            if not monster.fighter.has_status('silence'):
                for a in monster.fighter.abilities:
                    if a.current_cd <= 0 and game.roll_dice('1d10') > 5:
                        # Use abilities when they're up
                        if a.use(monster, self.target) != 'didnt-take-turn':
                            return monster.behavior.attack_speed

            if is_adjacent_diagonal(monster.x, monster.y, self.target.x, self.target.y):
                monster.fighter.attack(self.target)
                if monster.behavior is not None:
                    return monster.behavior.attack_speed
                else:
                    return 1
        return 1


class AI_Lifeplant:

    def act(self, ai_state):
        monster = self.owner
        for obj in game.current_map.fighters:
            if is_adjacent_diagonal(obj.x, obj.y, monster.x, monster.y):
                obj.fighter.heal(libtcod.random_get_int(0, 1, 2))
        return monster.behavior.attack_speed


class AI_TunnelSpider:

    def __init__(self):
        self.closest_web = None
        self.last_seen_position = None
        self.target = None

    def act(self, ai_state):
        monster = self.owner
        if ai_state == 'resting':
            target = acquire_target(monster)
            if target is not None:
                self.last_seen_position = target.x, target.y
                self.target = target
                monster.behavior.ai_state = 'pursuing'
                return 0.0
            elif object_at_tile(monster.x, monster.y, 'spiderweb') is None:
                monster.behavior.ai_state = 'retreating'
                return 0.0
            else:
                return 1.0
        elif ai_state == 'retreating':
            self.closest_web = self.find_closest_web()
            if self.closest_web is None:
                monster.behavior.ai_state = 'pursuing'
                return 0.0
            else:
                monster.move_astar(self.closest_web.x, self.closest_web.y)
                if object_at_tile(monster.x, monster.y, 'spiderweb') is not None:
                    monster.behavior.ai_state = 'resting'
                return monster.behavior.move_speed
        elif ai_state == 'pursuing':
            if self.target is None or self.target.fighter is None or self.target.fighter.hp <= 0:
                monster.behavior.ai_state = 'resting'
                self.target = None
                self.last_seen_position = None
                return 0.0
            if is_adjacent_diagonal(monster.x, monster.y, self.target.x, self.target.y) and self.target.fighter.hp > 0:
                monster.fighter.attack(self.target)
                return monster.behavior.attack_speed
            self.closest_web = self.find_closest_web()
            if self.closest_web is not None and monster.distance_to(self.closest_web) > consts.TUNNEL_SPIDER_MAX_WEB_DIST:
                monster.behavior.ai_state = 'retreating'
                return 0.0
            elif fov.monster_can_see_object(monster, self.target):
                monster.move_astar(self.target.x, self.target.y)
                self.last_seen_position = self.target.x, self.target.y
                return monster.behavior.move_speed
            elif self.last_seen_position is not None and not \
                    (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
                monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])
                return monster.behavior.move_speed
            else:
                monster.behavior.ai_state = 'retreating'
                return 0.0
        else:
            monster.behavior.ai_state = 'resting'
            return 1.0  # pass the turn

    def on_get_hit(self, attacker,damage):
        aggro_on_hit(self.owner, attacker)

    def find_closest_web(self):
        closest_web = None
        closest_dist = consts.TUNNEL_SPIDER_MAX_WEB_DIST
        for obj in game.current_map.objects:
            if obj.name == 'spiderweb':
                if closest_web is None or self.owner.distance_to(obj) < closest_dist:
                    closest_web = obj
                    closest_dist = self.owner.distance_to(obj)
        return closest_web


class ConfusedMonster:
    def __init__(self, old_ai, num_turns=consts.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def act(self, ai_state):
        obj = self.owner
        obj.behavior.ai_state = 'wandering'
        if self.num_turns > 0:
            obj.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
            return obj.behavior.move_speed
        else:
            obj.behavior.behavior = self.old_ai
            if fov.player_can_see(obj.x, obj.y):
                ui.message('%s %s no longer confused.' % (
                    syntax.name(obj).capitalize(),
                    syntax.conjugate(obj is player.instance, ('are', 'is'))), libtcod.light_grey)
            return 0.0


class AI_General:
    def __init__(self, move_speed=1.0, attack_speed=1.0, behavior=AI_Default()):
        self.turn_ticker = 0.0
        self.behavior = behavior
        self.base_move_speed = 1.0 / move_speed  # High speed = low delay.
        self.base_attack_speed = 1.0 / attack_speed
        self.ai_state = 'resting'
        self.follow_target = None

    def take_turn(self):
        #self.turn_ticker += self.speed
        #while self.turn_ticker > 1.0:
        #    if not (self.owner.fighter and (self.owner.fighter.has_status('stunned') or self.owner.fighter.has_status('frozen'))):
        #        self.behavior.act()
        #    self.turn_ticker -= 1.0

        while self.turn_ticker < 1.0:
            if self.owner.fighter and (self.owner.fighter.has_status('stunned') or self.owner.fighter.has_status('frozen')):
                self.turn_ticker += 1.0
            else:
                self.turn_ticker += self.behavior.act(self.ai_state)
        self.turn_ticker -= 1.0

    def get_hit(self, attacker):
        if hasattr(self.behavior, 'on_get_hit') and self.behavior.on_get_hit is not None:
            self.behavior.on_get_hit(attacker,0)

    @property
    def move_speed(self):
        monster = self.owner
        speed = self.base_move_speed
        if monster.fighter and monster.fighter.has_status('slowed'):
            speed *= 2.0
        if monster.fighter is not None and monster.fighter.has_attribute('attribute_fast_swimmer'):
            if game.current_map.tiles[monster.x][monster.y].is_water:
                speed *= 0.5
        return speed

    @property
    def attack_speed(self):
        monster = self.owner
        speed = self.base_move_speed
        if monster.fighter and monster.fighter.has_status('exhausted'):
            speed *= 2.0
        return speed

class ReekerGasBehavior:
    def __init__(self):
        self.ticks = consts.REEKER_PUFF_DURATION

    def on_tick(self, object=None):
        self.ticks -= 1
        if self.ticks == consts.REEKER_PUFF_DURATION * 2 / 3:
            self.owner.char = libtcod.CHAR_BLOCK2
        elif self.ticks == consts.REEKER_PUFF_DURATION / 3:
            self.owner.char = libtcod.CHAR_BLOCK1
        elif self.ticks <= 0:
            self.owner.destroy()
            return
        #self.owner.char = str(self.ticks)
        for obj in game.get_objects(self.owner.x, self.owner.y,
                                    lambda o: o.fighter is not None and o.name != 'reeker' and o.name != 'blastcap'):
            if self.ticks >= consts.REEKER_PUFF_DURATION - 1:
                if fov.player_can_see(obj.x, obj.y):
                    ui.message('A foul-smelling cloud of gas begins to form around %s.' % syntax.name(obj), libtcod.fuchsia)
            else:
                if fov.player_can_see(obj.x, obj.y):
                    ui.message('%s %s on the foul gas.' % (
                        syntax.name(obj).capitalize(),
                        syntax.conjugate(obj is player.instance, ('choke', 'chokes'))), libtcod.fuchsia)
                obj.fighter.take_damage(consts.REEKER_PUFF_DAMAGE)


class FireBehavior:
    def __init__(self,temp):
        self.temperature = temp

    def on_tick(self, object=None):
        if self.temperature > 8:
            self.owner.color = libtcod.Color(255,244,247)
        elif self.temperature > 6:
            self.owner.color = libtcod.Color(255,219,20)
        elif self.temperature > 4:
            self.owner.color = libtcod.Color(250,145,20)
        elif self.temperature > 2:
            self.owner.color = libtcod.Color(232,35,0)
        else:
            self.owner.color = libtcod.Color(100,100,100)

        self.temperature -= 1
        if self.temperature == 0:
            self.owner.destroy()
        else:
            for obj in game.get_objects(self.owner.x, self.owner.y, lambda o: o.fighter is not None):
                obj.fighter.apply_status_effect(effects.burning())
            # Spread to adjacent tiles
            if self.temperature < 9: # don't spread on the first turn
                for tile in adjacent_tiles_diagonal(self.owner.x, self.owner.y):
                    if libtcod.random_get_int(0, 1, 100) <= game.current_map.tiles[tile[0]][tile[1]].flammable:
                        game.create_fire(tile[0], tile[1], 10)
                    if game.current_map.tiles[tile[0]][tile[1]].is_ice:
                        game.melt_ice(tile[0], tile[1])
