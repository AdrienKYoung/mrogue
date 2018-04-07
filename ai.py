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

import consts
import libtcodpy as libtcod


def acquire_target(monster, priority=None, target_team=None, target_self=False, check_los=True):

    if target_team is None:
        if monster.fighter.team == 'ally':
            target_team = 'enemy'
        elif monster.fighter.team == 'enemy':
            target_team = 'ally'

    if not monster.fighter:
        return None

    if priority is not None:
        if priority.fighter.team == target_team and (fov.monster_can_see_object(monster, priority) or not check_los):
            return priority

    closest = None
    closest_dist = 10000
    for o in game.current_map.fighters:
        if o.fighter.team == target_team and o.fighter.hp > 0 and (fov.monster_can_see_object(monster, o) or not check_los):
            if o is monster and not target_self:
                continue
            dist = monster.distance_to(o)
            if closest is None or dist < closest_dist:
                closest = o
                closest_dist = dist
    return closest

def target_damaged_ally(actor):
    if actor is None or actor.fighter is None:
        return None
    target = None
    most_damage = 1.0
    for ally in game.get_fighters_in_burst(actor.x, actor.y, consts.TORCH_RADIUS, actor,
                                           condition=lambda o: o.fighter.team == actor.fighter.team):
        if ally.fighter is not None:
            damage = float(ally.fighter.hp) / float(ally.fighter.max_hp)
            if damage < most_damage:
                most_damage = damage
                target = ally
    return target

def target_random_ally(actor):
    if actor is None or actor.fighter is None:
        return None
    allies = game.get_fighters_in_burst(actor.x, actor.y, consts.TORCH_RADIUS, actor,
                                        condition=lambda o: o.fighter.team == actor.fighter.team)
    return allies[libtcod.random_get_int(0, 0, len(allies) - 1)]

def target_clear_line_of_fire(actor):
    if actor is None or \
            actor.behavior is None or \
            actor.behavior.behavior is None or \
            actor.behavior.behavior.target is None or \
            actor.fighter is None:
        return None

    target = actor.behavior.behavior.target
    if game.beam_interrupt(actor.x, actor.y, target.x, target.y) == (target.x, target.y):
        return target
    return None

def target_open_space_near_target(actor):
    if actor is None or \
            actor.behavior is None or \
            actor.behavior.behavior is None or \
            actor.behavior.behavior.target is None or \
            actor.fighter is None:
        return None
    target = actor.behavior.behavior.target
    return game.find_closest_open_tile(target.x, target.y)

def target_self_no_buff_refresh_meta(status):
    return lambda a: _target_self_no_buff_refresh(a, status)

def _target_self_no_buff_refresh(actor, status):
    if actor is None or \
            actor.behavior is None or \
            actor.behavior.behavior is None or \
            actor.behavior.behavior.target is None or \
            actor.fighter is None or\
            actor.fighter.has_status(status):
        return None
    return actor

def aggro_on_hit(monster, attacker):
    if attacker is None:
        return
    if fov.monster_can_see_object(monster, attacker):
        if libtcod.random_get_int(0, 0, 1) == 0:
            # 50% chance to aggro onto the attacker if the monster already has a target
            monster.behavior.behavior.target = attacker
            monster.behavior.behavior.last_seen_position = attacker.x, attacker.y
            monster.behavior.ai_state = 'pursuing'
    elif monster.behavior.ai_state != 'pursuing':
        monster.behavior.behavior.wander_path = game.get_path_to_point((monster.x, monster.y), game.find_closest_open_tile(attacker.x, attacker.y), monster.movement_type)
        monster.behavior.ai_state = 'wandering'

def pursue(behavior):
    monster = behavior.owner
    if behavior.target is None or behavior.target.fighter is None or behavior.target.fighter.hp <= 0:
        behavior.target = None
        behavior.last_seen_position = None
        return 'target-died'
    if fov.monster_can_see_object(monster, behavior.target):
        behavior.last_seen_position = behavior.target.x, behavior.target.y
        # Handle default ability use behavior
        if use_abilities(behavior) == 'ability-used':
            if monster.behavior is None:
                return 'dead'
            else:
                return 'ability-used'

        if attack_target_ranged(behavior) == 'attacked':
            if monster.behavior is None:
                return 'dead'
            else:
                return 'attacked'

        # Handle moving
        if not game.is_adjacent_diagonal(monster.x, monster.y, behavior.target.x, behavior.target.y):
            monster.move_astar(behavior.target.x, behavior.target.y)
            if monster.behavior is not None: #need this check because the monster may die while moving
                return 'moved'
            else:
                return 'dead'

        # Handle attacking
        else:
            monster.fighter.attack(behavior.target)
            if monster.behavior is not None:
                return 'attacked'
            else:
                return 'dead'

    elif behavior.last_seen_position is not None and not\
            (behavior.last_seen_position[0] == monster.x and behavior.last_seen_position[1] == monster.y):
        result = monster.move_astar(behavior.last_seen_position[0], behavior.last_seen_position[1])
        if result == 'failure':
            behavior.last_seen_position = None
        return 'moved'
    else:
       return 'lost-target'

def follow(behavior):
    monster = behavior.owner
    if use_abilities(behavior) == 'ability-used':
        if monster.behavior is None:
            return 'dead'
        else:
            return 'ability-used'
    target = acquire_target(monster)
    if target is not None:
        behavior.last_seen_position = target.x, target.y
        behavior.target = target
        return 'acquired-target'
    if monster.behavior.follow_target is None:
        return 'no-follow-target'
    monster.move_astar(monster.behavior.follow_target.x, monster.behavior.follow_target.y)
    return 'followed'

def rest(behavior):
    monster = behavior.owner
    if monster.behavior.follow_target is not None:
        return 'has-follow-target'
    target = acquire_target(monster)
    if target is not None:
        behavior.last_seen_position = target.x, target.y
        behavior.target = target
        return 'acquired-target'
    return 'rested'

def wander(behavior):
    monster = behavior.owner
    target = acquire_target(monster)
    if target is not None:
        behavior.last_seen_position = target.x, target.y
        behavior.target = target
        behavior.wander_path = None
        return 'acquired-target'
    else:
        if behavior.wander_path is None or len(behavior.wander_path) == 0:
            rand_x = libtcod.random_get_int(0, min(1, monster.x - 10), max(consts.MAP_WIDTH - 2, monster.x + 10))
            rand_y = libtcod.random_get_int(0, min(1, monster.y - 10), max(consts.MAP_HEIGHT - 2, monster.y + 10))
            rand_pos = rand_x, rand_y
            rand_pos = game.find_closest_open_tile(rand_pos[0], rand_pos[1])
            if rand_pos is None:
                return 'wandered'
            behavior.wander_path = game.get_path_to_point((monster.x, monster.y), rand_pos, monster.movement_type, None)
            if behavior.wander_path is None:
                return 'wandered'
        old_pos = monster.x, monster.y
        next_move = monster.x, monster.y
        while next_move == old_pos and len(behavior.wander_path) > 0:
            next_move = behavior.wander_path.pop(0)
        monster.move(next_move[0] - monster.x, next_move[1] - monster.y)
        if old_pos == (monster.x, monster.y):
            monster.behavior.wander_path= None
        return 'wandered'

def channel(behavior):
    if behavior.delay_turns < 1:
        behavior.queued_action()
        return 'finished-channel'
    behavior.delay_turns -= 1
    return 'channelled'

def avoid(behavior):
    monster = behavior.owner
    behavior.target = acquire_target(monster) # ensure that target is closest enemy
    if behavior.target is None or behavior.target.fighter is None or behavior.target.fighter.hp <= 0:
        return 'no-enemies-in-sight'

    # Use abilities
    if use_abilities(behavior) == 'ability-used':
        if monster.behavior is None:
            return 'dead'
        else:
            return 'ability-used'

    if fov.monster_can_see_object(monster, behavior.target):
        # Avoid enemies
        dist = monster.distance_to(behavior.target)
        if dist <= consts.AVOID_DISTANCE:
            exclude = []
            for enemy in game.get_fighters_in_burst(monster.x, monster.y, consts.TORCH_RADIUS, monster,
                                        condition=lambda o: o.fighter.team == game.opposite_team(monster.fighter.team)):
                for y in range(enemy.y - consts.AVOID_DISTANCE, enemy.y + consts.AVOID_DISTANCE + 1):
                    for x in range(enemy.x - consts.AVOID_DISTANCE, enemy.x + consts.AVOID_DISTANCE + 1):
                        if game.distance(monster.x, monster.y, x, y) <= consts.AVOID_DISTANCE:
                            exclude.append((x, y))
            flee_point = game.find_closest_open_tile(monster.x, monster.y, exclude)
            monster.move_astar(flee_point[0], flee_point[1])
            return 'fled'

        # Ranged attack
        if attack_target_ranged(behavior) == 'attacked':
            if monster.behavior is None:
                return 'dead'
            else:
                return 'attacked'

        # Move towards follow target
        if monster.behavior.follow_target is None:
            monster.behavior.follow_target = acquire_target(monster, target_team=monster.fighter.team)
        if monster.behavior.follow_target is not None:
            monster.move_astar(monster.behavior.follow_target.x, monster.behavior.follow_target.y)
            return 'followed'
        else:
            return 'no-allies-in-sight'
    else:
        return 'no-enemies-in-sight'

def use_abilities(behavior):
    monster = behavior.owner
    if not monster.fighter.has_status('silence'):
        for a in monster.fighter.abilities:
            if a.current_cd <= 0 and game.roll_dice('1d10') > 5:
                # Use abilities when they're up
                fnc = abilities.data[a.ability_id].get('target_function')
                if fnc is None:
                    ability_target = behavior.target
                    if a.intent == 'aggressive':
                        ability_target = behavior.target
                    elif a.intent == 'support':
                        ability_target = acquire_target(monster, target_team=monster.fighter.team, target_self=True)
                else:
                    ability_target = fnc(monster)
                if ability_target is not None and a.use(monster, ability_target) != 'didnt-take-turn':
                    return 'ability-used'
    return 'no-ability'

def attack_target_ranged(behavior):
    monster = behavior.owner
    distance_to = monster.distance_to(behavior.target)
    if monster.fighter.range > 1 and distance_to <= monster.fighter.range:
        if monster.fighter.attack(behavior.target) != 'failed':
            ui.render_projectile([monster.x, monster.y], [behavior.target.x, behavior.target.y], libtcod.white)
        if monster.behavior is not None:
            return 'attacked'
    return 'no-attack'


class AI_Support:

    def __init__(self):
        self.last_seen_position = None
        self.wander_path = None
        self.target = None
        self.queued_action = None
        self.delay_turns = 0

    def act(self, ai_state):
        monster = self.owner

        if ai_state == 'resting':

            result = rest(self)
            if result == 'acquired-target':
                monster.behavior.ai_state = 'avoiding'
                return 0.0
            elif result == 'has-follow-target':
                monster.behavior.ai_state = 'following'
                return 0.0
            elif result == 'rested':
                return 1.0

        elif ai_state == 'avoiding':

            result = avoid(self)
            if result == 'no-enemies-in-sight':
                friendly = acquire_target(monster, target_team=monster.fighter.team, check_los=False)
                if friendly is not None:
                    monster.behavior.follow_target = friendly
                    monster.behavior.ai_state = 'following'
                else:
                    monster.behavior.ai_state = 'resting'
                return 0.0
            elif result == 'attacked' or result == 'ability-used':
                return monster.behavior.attack_speed
            elif result == 'fled' or result == 'followed':
                return monster.behavior.move_speed
            elif result == 'no-allies-in-sight':
                ally = acquire_target(monster, target_team=monster.fighter.team, check_los=False)
                if ally is not None:
                    monster.behavior.follow_target = ally
                    monster.behavior.ai_state = 'following'
                    return 0.0
                return 1.0
            elif result == 'dead':
                return 1.0

        elif ai_state == 'following':

            result = follow(self)
            if result == 'acquired-target':
                monster.behavior.ai_state = 'avoiding'
                return 0.0
            elif result == 'no-follow-target':
                monster.behavior.ai_state = 'resting'
                return 0.0
            elif result == 'followed':
                return monster.behavior.move_speed
            elif result == 'ability-used':
                return monster.behavior.attack_speed
            elif result == 'dead':
                return 1.0

        return 1.0

    def queue_action(self,action,delay):
        self.queued_action = action
        self.delay_turns = delay
        self.owner.behavior.ai_state = 'channeling'


class AI_Ambush:
    def __init__(self, radius, timer):
        self.active = False
        self.radius = radius
        self.timer = timer

    def act(self, ai_state):
        monster = self.owner
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                monster.change_behavior(AI_Default())
                monster.behavior.ai_state = 'pursuing'
                monster.fighter.stealth = None
                monster.blocks = True
                game.current_map.fighters.append(monster)
        elif game.distance(monster.x,monster.y,player.instance.x,player.instance.y) <= self.radius:
                self.active = True
        return 1

class AI_Default:

    def __init__(self):
        self.last_seen_position = None
        self.wander_path = None
        self.target = None
        self.queued_action = None
        self.delay_turns = 0

    def act(self, ai_state):
        monster = self.owner

        if ai_state == 'pursuing':

            result = pursue(self)
            if result == 'target-died':
                if monster.behavior.follow_target is not None:
                    monster.behavior.ai_state = 'following'
                else:
                    monster.behavior.ai_state = 'wandering'
                return 0.0
            elif result == 'moved':
                return monster.behavior.move_speed
            elif result == 'attacked' or result == 'ability-used':
                return monster.behavior.attack_speed
            elif result == 'lost-target':
                monster.behavior.ai_state = 'wandering'
                return 0.0
            elif result == 'dead':
                return 1.0

        elif ai_state == 'wandering':

            result = wander(self)
            if result == 'acquired-target':
                monster.behavior.ai_state = 'pursuing'
            elif result == 'wandered':
                return monster.behavior.move_speed

        if hasattr(self, "_delay_turns") and self._delay_turns < 1:
            self._queued_action()
            if monster.fighter is None or monster.behavior is None:
                return
            if monster.behavior.follow_target is not None:
                monster.behavior.ai_state = 'following'
            target = acquire_target(monster)
            if target is not None:
                self.last_seen_position = target.x, target.y
                self.target = target
                monster.behavior.ai_state = 'pursuing'
                return 0.0

        elif ai_state == 'following':

            result = follow(self)
            if result == 'acquired-target':
                monster.behavior.ai_state = 'pursuing'
                return 0.0
            elif result == 'no-follow-target':
                monster.behavior.ai_state = 'resting'
                return 0.0
            elif result == 'followed':
                return monster.behavior.move_speed
            elif result == 'ability-used':
                return monster.behavior.attack_speed
            elif result == 'dead':
                return 1.0

        elif ai_state == 'channeling':

            result = channel(self)
            if result == 'channelled':
                return 1.0
            elif result == 'finished-channel':
                if monster.behavior.follow_target is not None:
                    monster.behavior.ai_state = 'following'
                target = acquire_target(monster)
                if target is not None:
                    self.last_seen_position = target.x, target.y
                    self.target = target
                    monster.behavior.ai_state = 'pursuing'
                else:
                    monster.behavior.ai_state = 'resting'
                return 1.0

        elif ai_state == 'resting':

            result = rest(self)
            if result == 'acquired-target':
                monster.behavior.ai_state = 'pursuing'
                return 0.0
            elif result == 'has-follow-target':
                monster.behavior.ai_state = 'following'
                return 0.0
            elif result == 'rested':
                return 1.0
        return 1.0

    def on_get_hit(self, attacker,damage):
        aggro_on_hit(self.owner, attacker)

    def queue_action(self,action,delay):
        self.queued_action = action
        self.delay_turns = delay
        self.owner.behavior.ai_state = 'channeling'


class AI_Reeker:

    def act(self, ai_state):
        monster = self.owner
        monster.behavior.ai_state = 'idle'
        if fov.player_can_see(monster.x, monster.y):
            for i in range(consts.REEKER_PUFF_MAX):
                if libtcod.random_get_int(0, 0, 10) < 3:
                    # create puff
                    position = game.random_position_in_circle(consts.REEKER_PUFF_RADIUS)
                    puff_pos = (game.clamp(monster.x + position[0], 1, consts.MAP_WIDTH - 2),
                                game.clamp(monster.y + position[1], 1, consts.MAP_HEIGHT - 2))
                    game.create_reeker_gas(puff_pos[0], puff_pos[1])
        return monster.behavior.attack_speed


class AI_Sentry:

    def __init__(self):
        self.target = None
        self._queued_action = None
        self._delay_turns = 0

    def on_get_hit(self, attacker,damage):
        aggro_on_hit(self.owner, attacker)

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

            if game.is_adjacent_diagonal(monster.x, monster.y, self.target.x, self.target.y):
                monster.fighter.attack(self.target)
                if monster.behavior is not None:
                    return monster.behavior.attack_speed
                else:
                    return 1
        return 1


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
            elif game.object_at_tile(monster.x, monster.y, 'spiderweb') is None:
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
                if game.object_at_tile(monster.x, monster.y, 'spiderweb') is not None:
                    monster.behavior.ai_state = 'resting'
                return monster.behavior.move_speed
        elif ai_state == 'pursuing':
            if self.target is None or self.target.fighter is None or self.target.fighter.hp <= 0:
                monster.behavior.ai_state = 'resting'
                self.target = None
                self.last_seen_position = None
                return 0.0
            if game.is_adjacent_diagonal(monster.x, monster.y, self.target.x, self.target.y) and self.target.fighter.hp > 0:
                monster.fighter.attack(self.target)
                if monster.fighter is None:
                    return 1.0
                return monster.behavior.attack_speed
            self.closest_web = self.find_closest_web()
            if self.closest_web is not None and monster.distance_to(self.closest_web) > consts.TUNNEL_SPIDER_MAX_WEB_DIST:
                monster.behavior.ai_state = 'retreating'
                return 0.0
            elif fov.monster_can_see_object(monster, self.target):
                monster.move_astar(self.target.x, self.target.y)
                self.last_seen_position = self.target.x, self.target.y
                if monster.fighter is None:
                    return 1.0
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
            if self.owner.fighter is not None:
                if self.owner.fighter.has_status('stunned') or self.owner.fighter.has_status('frozen'):
                    self.turn_ticker += 1.0
                else:
                    cost = self.behavior.act(self.ai_state)
                    if cost is not None:
                        self.turn_ticker += cost
        self.turn_ticker -= 1.0

    def get_hit(self, attacker):
        if self.owner.fighter.team == 'neutral':
            if self.owner.npc:
                self.owner.fighter.team = game.opposite_team(attacker.fighter.team)
                self.owner.npc.deactivate()
        if hasattr(self.behavior, 'on_get_hit') and self.behavior.on_get_hit is not None:
            self.behavior.on_get_hit(attacker,0)

    @property
    def move_speed(self):
        monster = self.owner
        speed = self.base_move_speed
        if monster.fighter is not None:
            if monster.fighter.has_status('slowed'):
                speed *= 2.0
            if monster.fighter.has_status('hasted'):
                speed *= 0.5
            if monster.fighter.has_attribute('attribute_fast_swimmer'):
                if game.current_map.tiles[monster.x][monster.y].is_water:
                    speed *= 0.5
        return speed

    @property
    def attack_speed(self):
        monster = self.owner
        speed = self.base_move_speed
        if monster.fighter is not None:
            if monster.fighter.has_status('hasted'):
                speed *= 0.5
            if monster.fighter.has_status('exhausted'):
                speed *= 2.0
        return speed

class ReekerGasBehavior:
    def __init__(self, duration=consts.REEKER_PUFF_DURATION):
        self.ticks = duration
        self.new = True

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
                                    lambda o: o.fighter is not None and not o.fighter.has_flag(8)):
            if self.new:
                if fov.player_can_see(obj.x, obj.y):
                    ui.message('A foul-smelling cloud of gas begins to form around %s.' % syntax.name(obj), libtcod.fuchsia)
            else:
                if fov.player_can_see(obj.x, obj.y):
                    ui.message('%s %s on the foul gas.' % (
                        syntax.name(obj).capitalize(),
                        syntax.conjugate(obj is player.instance, ('choke', 'chokes'))), libtcod.fuchsia)
                obj.fighter.take_damage(consts.REEKER_PUFF_DAMAGE)
        self.new = False


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
                obj.fighter.apply_status_effect(effects.burning(), dc=None)
            # Spread to adjacent tiles
            if self.temperature < 9: # don't spread on the first turn
                for tile in game.adjacent_tiles_diagonal(self.owner.x, self.owner.y):
                    if libtcod.random_get_int(0, 1, 100) <= game.current_map.tiles[tile[0]][tile[1]].flammable:
                        game.create_fire(tile[0], tile[1], 10)
                    if game.current_map.tiles[tile[0]][tile[1]].is_ice:
                        game.melt_ice(tile[0], tile[1])

class FrostfireBehavior:
    def __init__(self, temp):
        self.temperature = temp

    def on_tick(self, object=None):
        if self.temperature > 8:
            self.owner.color = libtcod.white
        elif self.temperature > 6:
            self.owner.color = libtcod.lightest_sky
        elif self.temperature > 4:
            self.owner.color = libtcod.light_sky
        elif self.temperature > 2:
            self.owner.color = libtcod.sky
        else:
            self.owner.color = libtcod.desaturated_sky

        self.temperature -= 1
        if self.temperature == 0:
            self.owner.destroy()
        else:
            for obj in game.get_objects(self.owner.x, self.owner.y, lambda o: o.fighter is not None):
                obj.fighter.apply_status_effect(effects.frozen(duration=5), dc=None)
            if self.temperature < 9: # don't spread on the first turn
                for adj in game.adjacent_tiles_diagonal(self.owner.x, self.owner.y):
                    tile = game.current_map.tiles[adj[0]][adj[1]]
                    if libtcod.random_get_int(0, 1, 100) <= 20 and (tile.is_water or tile.tile_type == 'lava'):
                        game.create_frostfire(adj[0], adj[1])


import effects
import fov
import game
import player
import syntax
import ui
from actions import abilities
