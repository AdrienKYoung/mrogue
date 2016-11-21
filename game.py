import libtcodpy as libtcod
import math
import textwrap
import shelve
import consts
import terrain
import random

#############################################
# Classes
#############################################


class StatusEffect:
    def __init__(self, name, time_limit=None, color=libtcod.white, on_apply=None, on_end=None):
        self.name = name
        self.time_limit = time_limit
        self.color = color
        self.on_apply = on_apply
        self.on_end = on_end


class Equipment:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0, attack_damage_bonus=0, armor_bonus=0, evasion_bonus=0, spell_power_bonus=0, stamina_cost=0, str_requirement=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.is_equipped = False
        self.attack_damage_bonus = attack_damage_bonus
        self.armor_bonus = armor_bonus
        self.evasion_bonus = evasion_bonus
        self.spell_power_bonus = spell_power_bonus
        self.stamina_cost = stamina_cost
        self.str_requirement = str_requirement
        
    def toggle(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()
            
    def equip(self):
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.orange)
        
    def dequip(self):
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.orange)


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
            if libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
                message('The ' + self.owner.name + ' is no longer confused.', libtcod.light_grey)


class Item:
    def __init__(self, use_function=None, type='item'):
        self.use_function = use_function
        self.type = type
        
    def pick_up(self):
        if self.type == 'item':
            if len(inventory) >= 26:
                message('Your inventory is too full to pick up ' + self.owner.name)
            else:
                inventory.append(self.owner)
                objects.remove(self.owner)
                message('You picked up a ' + self.owner.name + '!', libtcod.light_grey)
                equipment = self.owner.equipment
                if equipment and get_equipped_in_slot(equipment.slot) is None:
                    equipment.equip()
        elif self.type == 'spell':
            if len(memory) >= player.playerStats.max_memory:
                message('You cannot hold any more spells in your memory!', libtcod.purple)
            else:
                memory.append(self.owner)
                objects.remove(self.owner)
                message(str(self.owner.name) + ' has been added to your memory.', libtcod.purple)
            
    def use(self):
        if self.owner.equipment:
            self.owner.equipment.toggle()
            return
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                if self.type == 'item':
                    inventory.remove(self.owner)
                elif self.type == 'spell':
                    memory.remove(self.owner)
            else:
                return 'cancelled'
                
    def drop(self):
        if self.owner.equipment:
            self.owner.equipment.dequip();
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.white)


class PlayerStats:

    def __init__(self, int=10, wiz=10, str=10, agi=10):
        self.base_int = int
        self.base_wiz = wiz
        self.base_str = str
        self.base_agi = agi

    @property
    def int(self):
        return self.base_int

    @property
    def wiz(self):
        return self.base_wiz

    @property
    def str(self):
        return self.base_str

    @property
    def agi(self):
        return self.base_agi

    @property
    def max_memory(self):
        return 3 + math.floor(self.wiz / 4)


class Fighter:

    def __init__(self, hp=1, defense=0, power=0, xp=0, stamina=0, armor=0, evasion=0, accuracy=1.0, attack_damage=1,
                 damage_variance=0.15, spell_power=0, death_function=None, loot_table=None, breath=6,
                 can_breath_underwater=False, resistances=[]):
        self.xp = xp
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.death_function = death_function
        self.max_stamina = stamina
        self.stamina = stamina
        self.loot_table = loot_table
        self.base_armor = armor
        self.base_evasion = evasion
        self.base_attack_damage = attack_damage
        self.base_damage_variance = damage_variance
        self.base_spell_power = spell_power
        self.base_accuracy = accuracy
        self.max_breath = breath
        self.breath = breath
        self.can_breath_underwater = can_breath_underwater
        self.resistances = resistances
        self.status_effects = []

    def adjust_stamina(self, amount):
        self.stamina += amount
        if self.stamina < 0:
            self.stamina = 0
        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)
                if self.owner != player:
                    player.fighter.xp += self.xp
            
    def attack(self, target):

        if self.owner.name == 'player':
            stamina_cost = consts.UNARMED_STAMINA_COST / (self.owner.playerStats.str / consts.UNARMED_STAMINA_COST)
            if get_equipped_in_slot('right hand') is not None:
                stamina_cost = int((float(get_equipped_in_slot('right hand').stamina_cost) / (float(self.owner.playerStats.str) / float(get_equipped_in_slot('right hand').str_requirement))))
            if self.stamina < stamina_cost:
                message("You can't find the strength to swing your weapon!", libtcod.light_yellow)
                return 'failed'
            else:
                self.adjust_stamina(-stamina_cost)

        if roll_to_hit(target.fighter.evasion, self.accuracy):
            # Target was hit
            damage = self.attack_damage * (1.0 - self.damage_variance + libtcod.random_get_float(0, 0, 2 * self.damage_variance))
            damage *= (consts.ARMOR_FACTOR / (consts.ARMOR_FACTOR + target.fighter.armor))
            damage = math.ceil(damage)
            damage = int(damage)
            if damage > 0:
                message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' damage!', libtcod.grey)
                target.fighter.take_damage(damage)
            else:
                message(self.owner.name.capitalize() + ' attacks ' + target.name + ', but the attack is deflected!', libtcod.grey)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ', but misses!', libtcod.grey)
    
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def on_tick(self):
        # Manage breath/drowning
        if dungeon_map[self.owner.x][self.owner.y].tile_type == 'deep water':
            if not (self.can_breath_underwater or self.has_status('waterbreathing')):
                if self.breath > 0:
                    self.breath -= 1
                else:
                    drown_damage = int(self.max_hp / 4)
                    message('The ' + self.owner.name + ' drowns, suffering ' + str(drown_damage) + ' damage!',
                            libtcod.blue)
                    self.take_damage(drown_damage)
        elif self.breath < self.max_breath:
            self.breath += 1

        # Manage status effect timers
        removed_effects = []
        for effect in self.status_effects:
            if effect.time_limit is not None:
                effect.time_limit -= 1
                if effect.time_limit <= 0:
                    removed_effects.append(effect)
        for effect in removed_effects:
            if effect.on_end is not None:
                effect.on_end(self.owner)
            self.status_effects.remove(effect)

    def apply_status_effect(self, new_effect):
        # check for immunity
        for resist in self.resistances:
            if resist == new_effect.name:
                if libtcod.map_is_in_fov(fov_map, self.owner.x, self.owner.y):
                    message('The ' + self.owner.name + ' resists.')
                return False
        # check for existing matching effects
        for effect in self.status_effects:
            if effect.name == new_effect.name:
                # refresh the effect
                effect.time_limit = new_effect.time_limit
        self.status_effects.append(new_effect)
        if new_effect.on_apply is not None:
            new_effect.on_apply(self.owner)
        return True

    def has_status(self, name):
        for effect in self.status_effects:
            if effect.name == name:
                return True
        return False

    @property
    def accuracy(self):
        return self.base_accuracy

    @property
    def damage_variance(self):
        return self.base_damage_variance

    @property
    def attack_damage(self):
        bonus = sum(equipment.attack_damage_bonus for equipment in get_all_equipped(self.owner))
        if self.owner.playerStats:
            return self.base_attack_damage + self.owner.playerStats.str + bonus
        else:
            return self.base_attack_damage + bonus

    @property
    def armor(self):
        bonus = sum(equipment.armor_bonus for equipment in get_all_equipped(self.owner))
        return self.base_armor + bonus

    @property
    def evasion(self):
        bonus = sum(equipment.evasion_bonus for equipment in get_all_equipped(self.owner))
        if self.owner.playerStats:
            return self.base_evasion + self.owner.playerStats.agi + bonus
        else:
            return self.base_evasion + bonus

    @property
    def spell_power(self):
        bonus = sum(equipment.spell_power_bonus for equipment in get_all_equipped(self.owner))
        if self.owner.playerStats:
            return self.base_spell_power + self.owner.playerStats.int + bonus
        else:
            return self.base_spell_power + bonus

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self.base_power + bonus
        
    @property
    def defense(self):
        bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus
        
    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus


class AI_GiantFrog:

    def __init__(self):
        self.last_seen_position = None
        self.tongue_cooldown = 0

    def act(self):
        monster = self.owner
        if self.tongue_cooldown > 0:
            self.tongue_cooldown -= 1
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(player) < 2:
                if player.fighter.hp > 0:
                    monster.fighter.attack(player)
                return
            elif monster.distance_to(player) <= consts.FROG_TONGUE_RANGE and self.tongue_cooldown == 0:
                if player.fighter.hp > 0 and beam_interrupt(monster.x, monster.y, player.x, player.y) == (player.x, player.y):
                    spells.cast_frog_tongue(monster, player)
                    self.tongue_cooldown = libtcod.random_get_int(0, 1, consts.FROG_TONGUE_COOLDOWN)
                    return

            monster.move_astar(player.x, player.y)
            self.last_seen_position = (player.x, player.y)

        elif self.last_seen_position is not None and not \
                (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
            monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])


class AI_Default:

    def __init__(self):
        self.last_seen_position = None

    def act(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(player) >= 2:
                monster.move_astar(player.x, player.y)

            elif player.fighter.hp > 0:
                monster.fighter.attack(player)
            self.last_seen_position = (player.x, player.y)
        elif self.last_seen_position is not None and not\
                (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
            monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])


class ReekerGasBehavior:
    def __init__(self):
        self.ticks = consts.REEKER_PUFF_DURATION

    def on_tick(self):
        self.ticks -= 1
        if self.ticks == consts.REEKER_PUFF_DURATION * 2 / 3:
            self.owner.char = libtcod.CHAR_BLOCK2
        elif self.ticks == consts.REEKER_PUFF_DURATION / 3:
            self.owner.char = libtcod.CHAR_BLOCK1
        elif self.ticks <= 0:
            objects.remove(self.owner)
            return
        #self.owner.char = str(self.ticks)
        for obj in objects:
            if obj.x == self.owner.x and obj.y == self.owner.y and obj.fighter:
                if obj.name != 'reeker':
                    obj.fighter.take_damage(consts.REEKER_PUFF_DAMAGE)
                    if libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
                        message('The ' + obj.name + ' chokes on the foul gas.', libtcod.fuchsia)

class AI_Reeker:

    def act(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            for i in range(consts.REEKER_PUFF_MAX):
                if libtcod.random_get_int(0, 0, 10) < 3:
                    # create puff
                    position = random_position_in_circle(consts.REEKER_PUFF_RADIUS)
                    puff_pos = (monster.x + position[0], monster.y + position[1])
                    if not dungeon_map[puff_pos[0]][puff_pos[1]].blocks and object_at_tile(puff_pos[0], puff_pos[1], 'reeker gas') is None:
                        puff = GameObject(monster.x + position[0], monster.y + position[1], libtcod.CHAR_BLOCK3,
                                          'reeker gas', libtcod.dark_fuchsia, description='a puff of reeker gas',
                                          misc=ReekerGasBehavior())
                        objects.append(puff)


class AI_TunnelSpider:

    def __init__(self):
        self.closest_web = None
        self.state = 'resting'
        self.last_seen_position = None

    def act(self):
        monster = self.owner
        if self.state == 'resting':
            if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
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
            if monster.distance_to(player) < 2 and player.fighter.hp > 0:
                monster.fighter.attack(player)
                return
            self.closest_web = self.find_closest_web()
            if self.closest_web is not None and monster.distance_to(self.closest_web) > consts.TUNNEL_SPIDER_MAX_WEB_DIST:
                self.state = 'retreating'
                self.act()
            elif libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
                    monster.move_astar(player.x, player.y)
                    self.last_seen_position = (player.x, player.y)
            elif self.last_seen_position is not None and not \
                    (self.last_seen_position[0] == monster.x and self.last_seen_position[1] == monster.y):
                monster.move_astar(self.last_seen_position[0], self.last_seen_position[1])

    def find_closest_web(self):
        closest_web = None
        closest_dist = consts.TUNNEL_SPIDER_MAX_WEB_DIST
        for obj in objects:
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
            self.behavior.act()
            self.turn_ticker -= 1.0


class GameObject:

    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None, equipment=None,
                 playerStats=None, always_visible=False, interact=None, description=None, on_create=None,
                 update_speed=1.0, misc=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.always_visible = always_visible
        self.interact = interact
        self.description = description
        self.on_create = on_create
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        #if self.ai:
        #    self.ai.owner = self
        if self.ai:
            self.ai = AI_General(update_speed, ai)
            self.ai.behavior.owner = self
        self.item = item
        if self.item:
            self.item.owner = self
        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self
            self.item = Item()
            self.item.owner = self
        self.playerStats = playerStats
        if self.playerStats:
            self.playerStats.owner = self
        if on_create is not None:
            on_create(self)
        self.misc = misc
        if self.misc:
            self.misc.owner = self
        
    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            if self.fighter is not None:
                web = object_at_tile(self.x, self.y, 'spiderweb')
                if web is not None and not self.name == 'tunnel_spider':
                    message('The ' + self.name + ' struggles against the web.')
                    objects.remove(web)
                    return True
                cost = dungeon_map[self.x][self.y].stamina_cost
                if cost > 0 and self is player: # only the player cares about stamina costs (at least for now. I kind of like it this way) -T
                    if self.fighter.stamina >= cost:
                        self.fighter.adjust_stamina(-cost)
                    else:
                        message("You don't have the stamina leave this space!", libtcod.light_yellow)
                        return False
                else:
                    self.fighter.adjust_stamina(consts.STAMINA_REGEN_MOVE)     # gain stamina for moving across normal terrain
            self.x += dx
            self.y += dy
            return True

    def draw(self):
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or
                (self.always_visible and dungeon_map[self.x][self.y].explored)):
            offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2
            libtcod.console_set_default_foreground(mapCon, self.color)
            libtcod.console_put_char(mapCon, self.x - offsetx, self.y - offsety, self.char, libtcod.BKGND_NONE)
        
    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
        
    def move_astar(self, target_x, target_y):

        if self.x == target_x and self.y == target_y:
            return

        fov = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
        
        # Scan the map and set all walls to unwalkable
        for y1 in range(consts.MAP_HEIGHT):
            for x1 in range(consts.MAP_WIDTH):
                libtcod.map_set_properties(fov, x1, y1, not dungeon_map[x1][y1].blocks_sight, not dungeon_map[x1][y1].blocks)
        
        # Scan all objects to see if there are objects that must be navigated around
        for obj in objects:
            if obj.blocks and obj != self and not (obj.x == target_x and obj.y == target_y):
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)
                
        # 1.41 is the diagonal cost of movement. Set to 1 to equal axial movement, or 0 to disallow diagonals
        my_path = libtcod.path_new_using_map(fov, 1.41)
        libtcod.path_compute(my_path, self.x, self.y, target_x, target_y)
        
        # check if the path exists, and in this case, also the path is shorter than 25 tiles
        # if the path is too long (travels around rooms and hallways) just use basic AI instead
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # find the next coordinate in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                self.x = x
                self.y = y
        else:
            # Use the old function instead
            self.move_towards(target_x, target_y)
            
        # delete path to free memory
        libtcod.path_delete(my_path)
        
    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
        
    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def on_tick(self):
        if self.fighter:
            self.fighter.on_tick()
        if self.misc and hasattr(self.misc, 'on_tick'):
            self.misc.on_tick()



class Tile:
    
    def __init__(self, tile_type='stone floor'):
        self.explored = False
        self.tile_type = tile_type

    @property
    def name(self):
        return terrain.data[self.tile_type].name

    @property
    def blocks(self):
        return terrain.data[self.tile_type].blocks

    @property
    def blocks_sight(self):
        return terrain.data[self.tile_type].blocks_sight

    @property
    def tile_char(self):
        return terrain.data[self.tile_type].char

    @property
    def color_fg(self):
        return terrain.data[self.tile_type].foreground_color

    @property
    def color_bg(self):
        return terrain.data[self.tile_type].background_color

    @property
    def description(self):
        return terrain.data[self.tile_type].description

    @property
    def stamina_cost(self):
        return terrain.data[self.tile_type].stamina_cost

    @property
    def jumpable(self):
        return terrain.data[self.tile_type].jumpable


class Rect:

    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
        
    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

                
#############################################
# General Functions
#############################################

# This function exists so files outside game.py can modify this global variable.
# Hopefully there's a better way to do this    -T
def fov_recompute_fn():
    global fov_recompute
    fov_recompute = True


def roll_to_hit(evasion,  accuracy):
    chance_to_hit = consts.EVADE_FACTOR / (consts.EVADE_FACTOR + evasion)
    chance_to_hit *= accuracy
    return libtcod.random_get_float(0, 0, 1) < chance_to_hit

def random_position_in_circle(radius):
    r = libtcod.random_get_float(0, 0.0, float(radius))
    theta = libtcod.random_get_float(0, 0.0, 2.0 * math.pi)
    return (int(round(r * math.cos(theta))), int(round(r * math.sin(theta))))

def object_at_tile(x, y, name):
    for obj in objects:
        if obj.x == x and obj.y == y and obj.name == name:
            return obj
    return None

def make_spiderweb(obj):
    for x in range(3):
        for y in range(3):
            makeweb = (x == 1 and y == 1) or (libtcod.random_get_int(0, 0, 2) == 0 and not is_blocked(obj.x + x - 1, obj.y + y - 1))
            if makeweb:
                web = GameObject(obj.x + x - 1, obj.y + y - 1, '*', 'spiderweb', libtcod.lightest_gray,
                                 description='a web of spider silk. Stepping into a web will impede movement for a turn.')
                objects.append(web)
                web.send_to_back()

def get_all_equipped(obj):
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []


def get_equipped_in_slot(slot):
    for obj in inventory:
        if obj.equipment and obj.equipment.is_equipped and obj.equipment.slot == slot:
            return obj.equipment
    return None


def from_dungeon_level(table):
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0


def random_choice(chances_dict):
    chances = chances_dict.values()
    strings = chances_dict.keys()
    return strings[random_choice_index(chances)]


def random_choice_index(chances):
    dice = libtcod.random_get_int(0, 1, sum(chances))
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
        if dice <= running_sum:
            return choice
        choice += 1


def level_up(altar = None):
    player.level += 1
    message('You grow stronger! You have reached level ' + str(player.level) + '!', libtcod.green)
    choice = None
    while choice == None:
        choice = menu('Level up! Choose a stat to raise:\n',
        ['Constitution (+20 HP, from ' + str(player.fighter.base_max_hp) + ')',
            'Strength (+1 attack, from ' + str(player.fighter.base_power) + ')',
            'Agility (+1 defense, from ' + str(player.fighter.base_defense) + ')',
            'Intelligence (increases spell damage)',
            'Wisdom (increases spell slots, spell utility)'
         ], consts.LEVEL_SCREEN_WIDTH)

    if choice == 0:
        player.fighter.max_hp += 20
        player.fighter.hp += 20
    elif choice == 1:
        player.playerStats.str += 1
    elif choice == 2:
        player.playerStats.agi += 1
    elif choice == 3:
        player.playerStats.int += 1
    elif choice == 4:
        player.playerStats.wiz += 1

    if altar:
        objects.remove(altar)


def next_level():
    global dungeon_level

    message('You descend...', libtcod.white)
    dungeon_level += 1
    make_map()
    initialize_fov()


def player_death(player):
    global game_state
    message('You\'re dead, sucka.', libtcod.grey)
    game_state = 'dead'
    player.char = '%'
    player.color = libtcod.dark_red


def monster_death(monster):
    if monster.fighter.loot_table is not None:
        drop = get_loot(monster.fighter)
        if drop:
            objects.append(drop)
            drop.send_to_back()
    message(monster.name.capitalize() + ' is dead!', libtcod.red)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()


def target_monster(max_range=None):
    while True:
        (x, y) = target_tile(max_range)
        if x is None:
            return None
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj.ai:
                return obj
        return None


def object_at_coords(x, y):
    global dungeon_map

    ops = [t for t in objects if (t.x == x and t.y == y)]
    if len(ops) > 1:
        menu_choice = menu("Which object?", [o.name for o in ops], 20)
        if menu_choice is not None:
            return ops[menu_choice]
        else:
            return None
    elif len(ops) == 0:
        return dungeon_map[x][y]
    else:
        return ops[0]


def target_tile(max_range=None, targeting_type='pick'):
    global key, mouse

    cursor = GameObject(0, 0, ' ', 'cursor', libtcod.white)
    objects.append(cursor)
    cursor.x = player.x
    cursor.y = player.y
    x = player.x
    y = player.y
    oldMouseX = mouse.cx
    oldMouseY = mouse.cy
    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2
    selected_x = player.x
    selected_y = player.y

    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()

        # Render range shading
        libtcod.console_clear(ui)
        libtcod.console_set_key_color(ui, libtcod.magenta)
        for draw_x in range(consts.MAP_WIDTH):
            for draw_y in range(consts.MAP_HEIGHT):
                if round((player.distance(draw_x + offsetx, draw_y + offsety))) > max_range:
                    libtcod.console_put_char_ex(ui, draw_x, draw_y, ' ', libtcod.light_yellow, libtcod.black)
                else:
                    libtcod.console_put_char_ex(ui, draw_x, draw_y, ' ', libtcod.light_yellow, libtcod.magenta)
        libtcod.console_blit(ui, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, 0, 0, 0, 0.2)
        # Render cursor
        libtcod.console_set_default_background(ui, libtcod.magenta)
        libtcod.console_clear(ui)
        if targeting_type == 'beam' or targeting_type == 'beam_interrupt':
            libtcod.line_init(player.x, player.y, cursor.x, cursor.y)
            line_x, line_y = libtcod.line_step()
            while (not line_x is None):
                libtcod.console_put_char_ex(ui, line_x - offsetx, line_y - offsety, ' ', libtcod.white, libtcod.yellow)
                line_x, line_y = libtcod.line_step()
        libtcod.console_put_char_ex(ui, selected_x - offsetx, selected_y - offsety, ' ', libtcod.light_yellow, libtcod.white)

        libtcod.console_blit(ui, 0, 0, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, 0, 0, 0, 0.4)


        if key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            x -= 1
        if key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            x += 1
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            y -= 1
        if key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            y += 1
        if key.vk == libtcod.KEY_KP7:
            x -= 1
            y -= 1
        if key.vk == libtcod.KEY_KP9:
            x += 1
            y -= 1
        if key.vk == libtcod.KEY_KP1:
            x -= 1
            y += 1
        if key.vk == libtcod.KEY_KP3:
            x += 1
            y += 1

        if oldMouseX != mouse.cx or oldMouseY != mouse.cy:
            x, y = mouse.cx + offsetx, mouse.cy + offsety

        cursor.x = x
        cursor.y = y

        selected_x = cursor.x
        selected_y = cursor.y
        beam_values = []

        if targeting_type == 'beam_interrupt':
            selected_x, selected_y = beam_interrupt(player.x, player.y, cursor.x, cursor.y)
        elif targeting_type == 'beam':
            beam_values = beam(player.x, player.y, cursor.x, cursor.y)
            selected_x, selected_y = beam_values[len(beam_values) - 1]

        if (mouse.lbutton_pressed or key.vk == libtcod.KEY_ENTER) and libtcod.map_is_in_fov(fov_map, x, y):
            if max_range is None or round((player.distance(x, y))) <= max_range:
                objects.remove(cursor)
                if targeting_type == 'beam':
                    return beam_values
                else:
                    return selected_x, selected_y
            else:
                objects.remove(cursor)
                return None, None  # out of range
            
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            objects.remove(cursor)
            return None, None  # cancelled

        oldMouseX = mouse.cx
        oldMouseY = mouse.cy


def beam(sourcex, sourcey, destx, desty):
    libtcod.line_init(sourcex, sourcey, destx, desty)
    line_x, line_y = libtcod.line_step()
    beam_values = []
    while line_x is not None:
        coord = line_x, line_y
        beam_values.append(coord)
        line_x, line_y = libtcod.line_step()
    # beam_values.append(destx, desty) TODO: need to test this
    return beam_values


def beam_interrupt(sourcex, sourcey, destx, desty):
    libtcod.line_init(sourcex, sourcey, destx, desty)
    line_x, line_y = libtcod.line_step()
    while line_x is not None:
        if is_blocked(line_x, line_y):  # beam interrupt scans until it hits something
            return line_x, line_y
        line_x, line_y = libtcod.line_step()
    return destx, desty


def closest_monster(max_range):
    closest_enemy = None
    closest_dist = max_range + 1

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            dist = player.distance_to(object)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy = object
    return closest_enemy


def inventory_menu(header):
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'
            options.append(text)
        
    index = menu(header, options, consts.INVENTORY_WIDTH)
    if index is None or len(inventory) == 0: return None
    return inventory[index].item


def msgbox(text, width=50):
    menu(text, [], width)


def menu(header, options, width):
    global window

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, consts.SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0

    height = len(options) + header_height

    libtcod.console_clear(window)
    render_all()
    libtcod.console_flush()


    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
    y = header_height
    letter_index = ord('a')
    
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1
        
    x = consts.SCREEN_WIDTH / 2 - width / 2
    y = consts.SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)
    
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None


def get_names_under_mouse():

    global mouse

    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2
    (x, y) = (mouse.cx + offsetx, mouse.cy + offsety)
    names = [obj.name for obj in objects if (obj.x == x and obj.y == y and (libtcod.map_is_in_fov(fov_map, obj.x, obj.y)
                            or (obj.always_visible and dungeon_map[obj.x][obj.y].explored)) and obj.name != 'cursor')]
    names = ', '.join(names)
    return names.capitalize()


def message(new_msg, color = libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, consts.MSG_WIDTH)
    
    for line in new_msg_lines:
        if len(game_msgs) == consts.MSG_HEIGHT:
            del game_msgs[0]
        game_msgs.append((line, color))


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)
    
    libtcod.console_set_default_background(rightPanel, back_color)
    libtcod.console_rect(rightPanel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(rightPanel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(rightPanel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
        
    libtcod.console_set_default_foreground(rightPanel, libtcod.white)
    libtcod.console_print_ex(rightPanel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))


def is_blocked(x, y):
    global dungeon_map
    if dungeon_map[x][y].blocks:
        return True
        
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
            
    return False


def get_room_spawns(room):
    return [[k, libtcod.random_get_int(0, v[0], v[1])] for (k, v) in room['spawns'].items()]


def spawn_monster(name, room):
    x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
    y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
    if not is_blocked(x, y):
        p = monsters.proto[name]
        fighter_component = Fighter(hp=p['hp'], attack_damage=p['attack_damage'], armor=p['armor'],
                                    evasion=p['evasion'], accuracy=p['accuracy'], xp=0,
                                    death_function=monster_death, loot_table=loot.table[p.get('loot', 'default')],
                                    can_breath_underwater=True, resistances=p['resistances'])
        monster = GameObject(x, y, p['char'], p['name'], p['color'], blocks=True, fighter=fighter_component,
                             ai=p['ai'](), description=p['description'], on_create=p['on_create'], update_speed=p['speed'])
        objects.append(monster)


def spawn_item(name, x, y):
        p = loot.proto[name]
        item_component = Item(use_function=p.get('on_use'))
        equipment_component = None
        if p['type'] == 'equipment':
            equipment_component = Equipment(
                slot=p['slot'],
                attack_damage_bonus=p.get('attack_damage_bonus', 0),
                armor_bonus=p.get('armor_bonus', 0),
                max_hp_bonus=p.get('max_hp_bonus', 0),
                evasion_bonus=p.get('evasion_bonus', 0),
                spell_power_bonus=p.get('spell_power_bonus', 0),
                stamina_cost=p.get('stamina_cost', 0),
                str_requirement=p.get('str_requirement', 0)
            )
        item = GameObject(x, y, p['char'], p['name'], p.get('color', libtcod.white), item=item_component,
                          equipment=equipment_component, always_visible=True)
        objects.append(item)
        item.send_to_back()


def place_objects(room):
    max_items = from_dungeon_level([[1, 1], [2, 4], [4, 7]])
    item_chances = {'potion_healing':70, 'spell_lightning':10, 'spell_confusion':10, 'spell_fireball':10 }
    item_chances['equipment_longsword'] = 25
    item_chances['equipment_shield'] = 25

    table = dungeon.table[get_dungeon_level()]['versions']
    for i in range(libtcod.random_get_int(0, 0, 4)):  # temporary line to spawn multiple monster groups in a room
        spawns = get_room_spawns(table[random_choice_index([e['weight'] for e in table])])
        for s in spawns:
            for n in range(0,s[1]):
                spawn_monster(s[0],room)
            
    num_items = libtcod.random_get_int(0, 0, max_items)
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
        
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            spawn_item(choice, x, y)


def check_boss(level):
    global spawned_bosses

    for (k,v) in dungeon.bosses.items():
        chance = v.get(level)
        if chance is not None and spawned_bosses.get(k) is None:
            if chance >= libtcod.random_get_int(0,0,100):
                spawned_bosses[k] = True
                return k
    return None


def create_room(room):
    global dungeon_map
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            dice = libtcod.random_get_int(0, 0, 3)
            dice = 2
            if dice == 0:
                dungeon_map[x][y].tile_type = 'shallow water'
            elif dice == 1:
                dungeon_map[x][y].tile_type = 'deep water'
            else:
                dungeon_map[x][y].tile_type = 'stone floor'


def create_h_tunnel(x1, x2, y):
    global dungeon_map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        dungeon_map[x][y].tile_type = 'stone floor'


def create_v_tunnel(y1, y2, x):
    global dungeon_map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        dungeon_map[x][y].tile_type = 'stone floor'


def make_map():
    global dungeon_map, objects, stairs, dungeon_level, spawned_bosses
    
    objects = [player]

    dungeon_map = [[ Tile('stone wall')
        for y in range(consts.MAP_HEIGHT) ]
            for x in range(consts.MAP_WIDTH) ]

    rooms = []
    spawned_bosses = {}
    num_rooms = 0
    
    for r in range(consts.MAX_ROOMS):
        w = libtcod.random_get_int(0, consts.ROOM_MIN_SIZE, consts.ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, consts.ROOM_MIN_SIZE, consts.ROOM_MAX_SIZE)
        x = libtcod.random_get_int(0, 0, consts.MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, consts.MAP_HEIGHT - h - 1)
        
        new_room = Rect(x, y, w, h)
        
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
                
        if not failed:
            create_room(new_room)
            (new_x, new_y) = new_room.center()
            
            if num_rooms == 0:
                player.x = new_x
                player.y = new_y
            else:
                (prev_x, prev_y) = rooms[num_rooms-1].center()
                if libtcod.random_get_int(0, 0, 1) == 0:
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
            place_objects(new_room)
            rooms.append(new_room)
            num_rooms += 1

    #Generate every-floor random features
    sample = random.sample(rooms,2)
    x,y = sample[0].center()
    stairs = GameObject(x, y, '<', 'stairs downward', libtcod.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()
    x, y = sample[1].center()
    level_shrine = GameObject(x,y, '=', 'shrine of power', libtcod.white, always_visible=True, interact=level_up)
    objects.append(level_shrine)
    level_shrine.send_to_back()
    boss = check_boss(get_dungeon_level())
    if boss is not None:
        spawn_monster(boss,sample[1])

def get_dungeon_level():
    global dungeon_level
    return "dungeon_{}".format(dungeon_level)

def player_move_or_attack(dx, dy):

    x = player.x + dx
    y = player.y + dy
    
    target = None
    for object in objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
            
    if target is not None:
        return player.fighter.attack(target) != 'failed'
    else:
        value = player.move(dx, dy)
        fov_recompute_fn()
        return value


def get_loot(monster):
    loot_table = monster.loot_table
    drop = loot_table[libtcod.random_get_int(0,0,len(loot_table) - 1)]
    if drop:
        proto = loot.proto[drop]
        item = Item(use_function=proto['on_use'], type=proto['type'])
        return GameObject(monster.owner.x, monster.owner.y, proto['char'], proto['name'], proto['color'], item=item)


def handle_keys():
 
    global game_state, stairs
    global key
    
    # key = libtcod.console_check_for_keypress()  #real-time
    # key = libtcod.console_wait_for_keypress(True)  #turn-based
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  #exit game
 
    if game_state == 'playing':

        # movement keys - assume fov_recompute is true, then set to false if no movement
        key_char = chr(key.c)
        moved = False
        if key.vk == libtcod.KEY_UP:
            moved = player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_DOWN:
            moved = player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_LEFT:
            moved = player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT:
            moved = player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_KP7:
            moved = player_move_or_attack(-1, -1)
        elif key.vk == libtcod.KEY_KP8:
            moved = player_move_or_attack(0, -1)
        elif key.vk == libtcod.KEY_KP9:
            moved = player_move_or_attack(1, -1)
        elif key.vk == libtcod.KEY_KP4:
            moved = player_move_or_attack(-1, 0)
        elif key.vk == libtcod.KEY_KP6:
            moved = player_move_or_attack(1, 0)
        elif key.vk == libtcod.KEY_KP1:
            moved = player_move_or_attack(-1, 1)
        elif key.vk == libtcod.KEY_KP2:
            moved = player_move_or_attack(0, 1)
        elif key.vk == libtcod.KEY_KP3:
            moved = player_move_or_attack(1, 1)
        elif key.vk == libtcod.KEY_KP5 or key_char == 's':
            player.fighter.adjust_stamina(consts.STAMINA_REGEN_WAIT) # gain stamina for standing still
            moved = True  # so that this counts as a turn passing
            pass
        else:
            if key_char == 'g':
                for object in objects:
                    if object.x == player.x and object.y == player.y:
                        if object.item:
                            object.item.pick_up()
                            return 'picked-up-item'
                        elif object.interact:
                            object.interact(object)
            if key_char == 'i':
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    use_result = chosen_item.use()
                    if use_result == 'cancelled':
                        return 'didnt-take-turn'
                    else:
                        return 'used-item'
            if key_char == 'd':
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
                    return 'dropped-item'
            if key_char == ',' and key.shift:
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()
            if key_char == 'c':
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\n\nMaximum HP: ' +
                       str(player.fighter.max_hp) + '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' +
                       str(player.fighter.defense),
                       consts.CHARACTER_SCREEN_WIDTH)
            if key_char == 'z':
                if len(memory) == 0:
                    message('You have no spells in your memory to cast.', libtcod.purple)
                elif dungeon_map[player.x][player.y].tile_type == 'deep water':
                    message('You cannot cast spells underwater.', libtcod.purple)
                else:
                    cast_spell()
                    return 'casted-spell'
            if key_char == 'j':
                if player.fighter.stamina >= consts.JUMP_STAMINA_COST:
                    if dungeon_map[player.x][player.y].jumpable:
                        return jump()
                    else:
                        message('You cannot jump from this terrain!', libtcod.light_yellow)
                else:
                    message("You don't have the stamina to jump!", libtcod.light_yellow)
            if key_char == 'e':
                x, y = target_tile()
                if x is not None and y is not None:
                    obj = object_at_coords(x, y)
                    if obj and hasattr(obj, 'description') and obj.description is not None:
                        menu(obj.name + '\n' + obj.description, ['back'], 20)
                    elif obj is not None:
                        menu(obj.name, ['back'], 20)
            return 'didnt-take-turn'
        if not moved:
            return 'didnt-take-turn'


def jump():
    global player

    web = object_at_tile(player.x, player.y, 'spiderweb')
    if web is not None:
        message('The player struggles against the web.')
        objects.remove(web)
        return 'webbed'

    message('Jump to where?', libtcod.white)

    render_all()
    libtcod.console_flush()
    (x, y) = target_tile(consts.BASE_JUMP_RANGE, 'pick')
    if x is not None and y is not None:
        if not is_blocked(x, y):
            player.x = x
            player.y = y
            fov_recompute_fn()
            player.fighter.adjust_stamina(-consts.JUMP_STAMINA_COST)
            return 'jumped'
        else:
            message('There is something in the way.', libtcod.white)
            return 'didnt-take-turn'

    message('Out of range.', libtcod.white)
    return 'didnt-take-turn'


def cast_spell():
    message('Cast which spell?', libtcod.purple)

    render_all()
    libtcod.console_flush()

    choice = libtcod.console_wait_for_keypress(True).c - 48

    if choice > 0 and choice < len(memory) + 1:
        memory[choice - 1].item.use()
    else:
        message('No such spell.', libtcod.purple)


def clear_map():
    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            libtcod.console_put_char_ex(mapCon, x - offsetx, y - offsety, 219, libtcod.black, libtcod.black)


def render_all():

    global fov_map, color_dark_wall, color_lit_wall
    global color_dark_ground, color_lit_ground
    global fov_recompute

    if not in_game:
        return

    libtcod.console_set_default_foreground(mapCon, libtcod.white)
    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, consts.TORCH_RADIUS, consts.FOV_LIGHT_WALLS, consts.FOV_ALGO)
    
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            # wall = dungeon_map[x][y].blocks_sight
            visible = libtcod.map_is_in_fov(fov_map, x, y)
            # color_fg = copy.copy(dungeon_map[x][y].color_fg)
            # color_bg = copy.copy(dungeon_map[x][y].color_bg)
            color_fg = libtcod.Color(dungeon_map[x][y].color_fg[0], dungeon_map[x][y].color_fg[1], dungeon_map[x][y].color_fg[2])
            color_bg = libtcod.Color(dungeon_map[x][y].color_bg[0], dungeon_map[x][y].color_bg[1], dungeon_map[x][y].color_bg[2])
            if not visible:
                if dungeon_map[x][y].explored:
                    libtcod.color_scale_HSV(color_fg, 0.1, 0.4)
                    libtcod.color_scale_HSV(color_bg, 0.1, 0.4)
                    libtcod.console_put_char_ex(mapCon, x - offsetx, y - offsety, dungeon_map[x][y].tile_char, color_fg, color_bg)
            else:
                libtcod.console_put_char_ex(mapCon, x - offsetx, y - offsety, dungeon_map[x][y].tile_char, color_fg, color_bg)
                dungeon_map[x][y].explored = True

    # draw all objects in the list
    for object in objects:
        if object != player:
            object.draw()
    player.draw()
    
    libtcod.console_blit(mapCon, 0, 0, consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT, 0, 0, 0)

    # RENDER RIGHT PANEL

    libtcod.console_set_default_background(rightPanel, libtcod.black)
    libtcod.console_clear(rightPanel)

    render_bar(1, 1, consts.BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.dark_red, libtcod.darker_red)

    render_bar(1, 2, consts.BAR_WIDTH, 'Stamina', player.fighter.stamina, player.fighter.max_stamina,
                   libtcod.dark_green, libtcod.darker_green)

    # Breath
    if player.fighter.breath < player.fighter.max_breath:
        breath_text = ''
        for num in range(0, player.fighter.breath):
            breath_text += 'O '
        libtcod.console_set_default_foreground(rightPanel, libtcod.dark_blue)
        libtcod.console_print(rightPanel, 1, 3, breath_text)
        libtcod.console_set_default_foreground(rightPanel, libtcod.white)

    # Base stats
    libtcod.console_print(rightPanel, 1, 5, 'INT: ' + str(player.playerStats.int))
    libtcod.console_print(rightPanel, 1, 6, 'WIZ: ' + str(player.playerStats.wiz))
    libtcod.console_print(rightPanel, 1, 7, 'STR: ' + str(player.playerStats.str))
    libtcod.console_print(rightPanel, 1, 8, 'AGI: ' + str(player.playerStats.agi))

    # Level/XP
    libtcod.console_print(rightPanel, 1, 10, 'Lvl: ' + str(player.level))
    libtcod.console_print(rightPanel, 1, 11, 'XP:  ' + str(player.fighter.xp))

    drawHeight = 13

    # Status effects
    if len(player.fighter.status_effects) > 0:
        for effect in player.fighter.status_effects:
            libtcod.console_set_default_foreground(rightPanel, effect.color)
            libtcod.console_print(rightPanel, 1, drawHeight, effect.name + ' (' + str(effect.time_limit) + ')')
            drawHeight += 1
        drawHeight += 1
        libtcod.console_set_default_foreground(rightPanel, libtcod.white)

    # Spells in memory
    libtcod.console_print(rightPanel, 1, drawHeight, 'Spells in memory:')
    y = 1
    for spell in memory:
        libtcod.console_print(rightPanel, 1, drawHeight + y, str(y) + ') ' + spell.name)
        y += 1

    libtcod.console_blit(rightPanel, 0, 0, consts.RIGHT_PANEL_WIDTH, consts.RIGHT_PANEL_HEIGHT, 0, consts.MAP_VIEWPORT_WIDTH, 0)

    # RENDER BOTTOM PANEL

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)
    
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, consts.MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    libtcod.console_set_default_foreground(panel, libtcod.light_grey)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())
        
    libtcod.console_blit(panel, 0, 0, consts.SCREEN_WIDTH, consts.PANEL_HEIGHT, 0, 0, consts.PANEL_Y)

    # RENDER UI OVERLAY

    libtcod.console_set_default_background(ui, libtcod.black)
    libtcod.console_clear(ui)

    under = get_names_under_mouse()

    if under != '':
        unders = under.split(', ')
        y = 1
        max_width = 0
        for line in unders:
            libtcod.console_print(ui, mouse.cx, mouse.cy + y, line.capitalize())
            if len(line) > max_width: max_width = len(line)
            y += 1
        libtcod.console_blit(ui, mouse.cx, mouse.cy + 1, max_width, y - 1, 0, mouse.cx, mouse.cy + 1, 1.0, 0.5)

 
#############################################
# Initialization & Main Loop
#############################################

def main_menu():
    img = libtcod.image_load('menu_background.png')
    
    while not libtcod.console_is_window_closed():
        libtcod.image_blit_2x(img, 0, 0, 0)
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT /2 - 8, libtcod.BKGND_NONE, libtcod.CENTER,
            'TUTORIAL: THE ROGUELIKE')
        libtcod.console_print_ex(0, consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
            'by Tyler Soberanis')
        
        choice = menu('', ['NEW GAME', 'CONTINUE', 'QUIT'], 24)
        
        if choice == 0: #new game
            new_game()
            play_game()
        elif choice == 1:
            try:
                load_game()
            except:
                msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:
            break
    

def new_game():
    global player, inventory, game_msgs, game_state, dungeon_level, memory, in_game

    in_game = True

    #create object representing the player
    fighter_component = Fighter(hp=100, xp=0, stamina=100, death_function=player_death)
    player = GameObject(25, 23, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, playerStats=PlayerStats(), description='You, the fearless adventurer!')
    player.level = 1
    
    #generate map
    dungeon_level = 1
    make_map()
    initialize_fov()
    game_state = 'playing'
    
    inventory = []
    item = GameObject(0, 0, '#', 'scroll of bullshit', libtcod.yellow, item=Item(use_function=spells.cast_fireball), description='the sword you started with')
    waterbreathing = GameObject(0, 0, '!', 'potion of waterbreathing', libtcod.yellow, item=Item(use_function=spells.cast_waterbreathing), description='This potion allows the drinker to breath underwater for a short time.')

    inventory.append(item)
    inventory.append(waterbreathing)

    memory = []
    # spell = GameObject(0, 0, '?', 'mystery spell', libtcod.yellow, item=Item(use_function=spells.cast_lightning, type="spell"))
    # memory.append(spell)

    #Welcome message
    game_msgs = []

    spawn_item('spell_confusion', player.x, player.y)

    message('Welcome to the dungeon...', libtcod.gold)


def initialize_fov():
    global fov_recompute, fov_map
    
    libtcod.console_clear(con)
    
    fov_recompute = True
    
    fov_map = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not dungeon_map[x][y].blocks_sight, not dungeon_map[x][y].blocks)


def save_game():
    file = shelve.open('savegame', 'n')
    file['map'] = dungeon_map
    file['objects'] = objects
    file['player_index'] = objects.index(player)
    file['stairs_index'] = objects.index(stairs)
    file['inventory'] = inventory
    file['memory'] = memory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['dungeon_level'] = dungeon_level
    file.close()


def load_game():
    global dungeon_map, objects, player, inventory, memory, game_msgs, game_state, dungeon_level, stairs, in_game

    in_game = True

    file = shelve.open('savegame', 'r')
    dungeon_map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]
    stairs = objects[file['stairs_index']]
    inventory = file['inventory']
    memory = file['memory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    dungeon_level = file['dungeon_level']
    file.close()
    
    initialize_fov()


def play_game():
    global key, mouse, game_state, in_game
    player_action = None
    
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():

        # render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()
        libtcod.console_flush()
    
        # erase the map so it can be redrawn next frame
        clear_map()

        # handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            in_game = False
            break

        # Let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            player.on_tick()
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
                if object is not player:
                    object.on_tick()
5

# my modules
import spells
import loot
import monsters
import dungeon

in_game = False
libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT, 'Let\'s Try Making a Roguelike', False)
libtcod.sys_set_fps(consts.LIMIT_FPS)
con = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
window = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
mapCon = libtcod.console_new(consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT)
ui = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
panel = libtcod.console_new(consts.SCREEN_WIDTH, consts.PANEL_HEIGHT)
rightPanel = libtcod.console_new(consts.RIGHT_PANEL_WIDTH, consts.RIGHT_PANEL_HEIGHT)
