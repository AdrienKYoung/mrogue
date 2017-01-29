from game import *
import fov
import consts
import game
import ui
import effects
import player

class AI_Default:

    def __init__(self):
        self.last_seen_position = None

    def act(self):
        monster = self.owner
        if fov.monster_can_see_object(monster, player.instance):

            #Handle default ability use behavior
            for a in self.owner.fighter.abilities:
                if a.current_cd <= 0:
                    #Use abilities when they're up
                    if a.use(self.owner) != 'didnt-take-turn':
                        return


            #Handle moving
            if not is_adjacent_diagonal(monster.x, monster.y, player.instance.x, player.instance.y):
                monster.move_astar(player.instance.x, player.instance.y)

            #Handle attacking
            elif player.instance.fighter.hp > 0:
                monster.fighter.attack(player.instance)
            self.last_seen_position = (player.instance.x, player.instance.y)
        elif self.last_seen_position is not None and not\
                (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
            result = monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])
            if result == 'failure':
                self.last_seen_position = None


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
                    ui.message('A foul-smelling cloud of gas begins to form around the ' + obj.name, libtcod.fuchsia)
            else:
                if fov.player_can_see(obj.x, obj.y):
                    ui.message('The ' + obj.name + ' chokes on the foul gas.', libtcod.fuchsia)
                obj.fighter.take_damage(consts.REEKER_PUFF_DAMAGE,'poison')


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
                    if game.current_map.tiles[tile[0]][tile[1]].flammable:
                        if libtcod.random_get_int(0, 0, 8) == 0:
                            game.create_fire(tile[0], tile[1], 10)


class AI_Reeker:

    def act(self):
        monster = self.owner
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


class AI_TunnelSpider:

    def __init__(self):
        self.closest_web = None
        self.state = 'resting'
        self.last_seen_position = None

    def act(self):
        monster = self.owner
        if self.state == 'resting':
            if fov.monster_can_see_object(monster, player.instance):
                self.state = 'hunting'
                self.act()
            elif object_at_tile(monster.x, monster.y, 'spiderweb') is None:
                self.state = 'retreating'
                self.act()
        elif self.state == 'retreating':
            self.closest_web = self.find_closest_web()
            if self.closest_web is None:
                self.state = 'hunting'
                self.act()
            else:
                monster.move_astar(self.closest_web.x, self.closest_web.y)
                if object_at_tile(monster.x, monster.y, 'spiderweb') is not None:
                    self.state = 'resting'
        elif self.state == 'hunting':
            if is_adjacent_diagonal(monster.x, monster.y, player.instance.x, player.instance.y) and player.instance.fighter.hp > 0:
                monster.fighter.attack(player.instance)
                return
            self.closest_web = self.find_closest_web()
            if self.closest_web is not None and monster.distance_to(self.closest_web) > consts.TUNNEL_SPIDER_MAX_WEB_DIST:
                self.state = 'retreating'
                self.act()
            elif fov.monster_can_see_object(monster, player.instance):
                    monster.move_astar(player.instance.x, player.instance.y)
                    self.last_seen_position = (player.instance.x, player.instance.y)
            elif self.last_seen_position is not None and not \
                    (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
                monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])

    def find_closest_web(self):
        closest_web = None
        closest_dist = consts.TUNNEL_SPIDER_MAX_WEB_DIST
        for obj in game.current_map.objects:
            if obj.name == 'spiderweb':
                if closest_web is None or self.owner.distance_to(obj) < closest_dist:
                    closest_web = obj
                    closest_dist = self.owner.distance_to(obj)
        return closest_web


class AI_General:
    def __init__(self, speed=1.0, behavior=AI_Default()):
        self.turn_ticker = 0.0
        self.speed = speed
        self.behavior = behavior

    def take_turn(self):
        self.turn_ticker += self.speed
        while self.turn_ticker > 1.0:
            if not (self.owner.fighter and (self.owner.fighter.has_status('stunned') or self.owner.fighter.has_status('frozen'))):
                self.behavior.act()
            self.turn_ticker -= 1.0


class ConfusedMonster:
    def __init__(self, old_ai, num_turns=consts.CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def act(self):
        if self.num_turns > 0:
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            self.owner.ai.behavior = self.old_ai
            if fov.player_can_see(self.owner.x, self.owner.y):
                ui.message('The ' + self.owner.name + ' is no longer confused.', libtcod.light_grey)

