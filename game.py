import libtcodpy as libtcod
import math
import textwrap
import shelve
import consts
import terrain

#############################################
# Classes
#############################################


class Equipment:
    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0, attack_damage_bonus=0, armor_bonus=0, evasion_bonus=0, spell_power_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.is_equipped = False
        self.attack_damage_bonus = attack_damage_bonus
        self.armor_bonus = armor_bonus
        self.evasion_bonus = evasion_bonus
        self.spell_power_bonus = spell_power_bonus
        
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
        
    def take_turn(self):
        if self.num_turns > 0:
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1
        else:
            self.owner.ai = self.old_ai
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
                 can_breath_underwater=False):
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

        chance_to_hit = consts.EVADE_FACTOR / (consts.EVADE_FACTOR + target.fighter.evasion)
        chance_to_hit *= self.accuracy
        if libtcod.random_get_float(0, 0, 1) < chance_to_hit:
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
        if map[self.owner.x][self.owner.y].tile_type == 'deep water':
            if not self.can_breath_underwater:
                if self.breath > 0:
                    self.breath -= 1
                else:
                    drown_damage = int(self.max_hp / 4)
                    message('The ' + self.owner.name + ' drowns, suffering ' + str(drown_damage) + ' damage!',
                            libtcod.blue)
                    self.take_damage(drown_damage)
        elif self.breath < self.max_breath:
            self.breath += 1

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


class BasicMonster:

    def __init__(self, speed=1.0):
        self.turn_ticker = 0.0
        self.speed = speed

    def take_turn(self):
        self.turn_ticker += self.speed
        while self.turn_ticker > 1.0:
            self.act()
            self.turn_ticker -= 1.0

    def act(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(player) >= 2:
                monster.move_astar(player.x, player.y)

            elif player.fighter.hp > 0:
                monster.fighter.attack(player)


class GameObject:

    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None, equipment=None, playerStats=None, always_visible=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.always_visible = always_visible
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
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
        
    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            if self.fighter is not None:
                cost = map[self.x][self.y].stamina_cost
                if cost > 0:
                    if self.fighter.stamina >= cost:
                        self.fighter.adjust_stamina(-cost)
                    else:
                        if self.name == 'player':
                            message("You don't have the stamina leave this space!", libtcod.light_yellow)
                        return False
                else:
                    self.fighter.adjust_stamina(consts.STAMINA_REGEN_MOVE)     # gain stamina for moving across normal terrain
            self.x += dx
            self.y += dy
            return True

    def draw(self):
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or
                (self.always_visible and map[self.x][self.y].explored)):
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
        fov = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
        
        # Scan the map and set all walls to unwalkable
        for y1 in range(consts.MAP_HEIGHT):
            for x1 in range(consts.MAP_WIDTH):
                libtcod.map_set_properties(fov, x1, y1, not map[x1][y1].blocks_sight, not map[x1][y1].blocks)
        
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


def check_level_up():
    level_up_xp = consts.LEVEL_UP_BASE + player.level * consts.LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('You grow stronger! You have reached level ' + str(player.level) + '!', libtcod.green)
        choice = None
        while choice == None:
            choice = menu('Level up! Choose a stat to raise:\n',
            ['Constitution (+20 HP, from ' + str(player.fighter.base_max_hp) + ')',
                'Strength (+1 attack, from ' + str(player.fighter.base_power) + ')',
                'Agility (+1 defense, from ' + str(player.fighter.base_defense) + ')'], consts.LEVEL_SCREEN_WIDTH)
                
        if choice == 0:
            player.fighter.max_hp += 20
            player.fighter.hp += 20
        elif choice == 1:
            player.fighter.power += 1
        elif choice == 2:
            player.fighter.defense += 1


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
            if obj.x == x and obj.y == y:
                return obj


def target_tile(max_range=None):
    global key, mouse

    cursor = GameObject(0, 0, 219, 'cursor', libtcod.white)
    objects.append(cursor)
    x = player.x
    y = player.y
    oldMouseX = mouse.cx
    oldMouseY = mouse.cy
    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2

    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()

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

        if ((mouse.lbutton_pressed or key.vk == libtcod.KEY_ENTER) and libtcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            objects.remove(cursor)
            return x, y
            
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            objects.remove(cursor)
            return None, None

        oldMouseX = mouse.cx
        oldMouseY = mouse.cy


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
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, consts.SCREEN_HEIGHT, header)
    if header == '': header_height = 0
    
    height = len(options) + header_height
    window = libtcod.console_new(width, height)
    
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
    names = [obj.name for obj in objects
                if (obj.x == x and obj.y == y and (libtcod.map_is_in_fov(fov_map, obj.x, obj.y) or (obj.always_visible and map[obj.x][obj.y].explored)))]
    names = ', '.join(names)
    return names.capitalize()


def message(new_msg, color = libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, consts.MSG_WIDTH)
    
    for line in new_msg_lines:
        if len(game_msgs) == consts.MSG_HEIGHT:
            del game_msgs[0]
        game_msgs.append( (line, color) )


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
    global map

    if map[x][y].blocks:
        return True
        
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
            
    return False


def place_objects(room):

    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])
    monster_chances = {}
    monster_chances['goblin'] = 80
    monster_chances['golem'] = from_dungeon_level([[10, 1], [50, 3], [130, 6]])
    # monster_chances['creature'] = from_dungeon_level([[20, 2], [35, 4], [80, 8]])
    
    max_items = from_dungeon_level([[1, 1], [2, 4], [4, 7]])
    item_chances = { 'heal':70, 'lightning':10, 'confuse':10, 'fireball':10 }
    item_chances['sword'] = 25
    item_chances['shield'] = 25

    num_monsters = libtcod.random_get_int(0, 0, max_monsters)
    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
        
        if not is_blocked(x, y):
            choice = random_choice(monster_chances)
            # HACK ALERT HACK ALERT
            # choice = 'goblin'
            # HACK ALERT HACK ALERT
            if choice == 'golem':
                fighter_component = Fighter(hp=100, attack_damage=30, armor=50, evasion=5, accuracy=0.5, xp=75,
                                            death_function=monster_death, loot_table=loot.table['default'],
                                            can_breath_underwater=True)
                ai_component = BasicMonster(speed=0.5)
                monster = GameObject(x, y, 'G', 'golem', libtcod.sepia, blocks=True, fighter=fighter_component, ai=ai_component)
            elif choice == 'goblin':
                fighter_component = Fighter(hp=20, attack_damage=10, armor=5, evasion=15, accuracy=0.65, xp=75,
                                            death_function=monster_death, loot_table=loot.table['default'],
                                            can_breath_underwater=True)
                ai_component = BasicMonster(speed=0.8)
                monster = GameObject(x, y, 'g', 'goblin', libtcod.desaturated_green, blocks=True, fighter=fighter_component, ai=ai_component)
                
            objects.append(monster)
            
    num_items = libtcod.random_get_int(0, 0, max_items)
    for i in range(num_items):
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
        
        if not is_blocked(x, y):
            choice = random_choice(item_chances)
            if choice == 'heal':
                item_component = Item(use_function=spells.cast_heal)
                item = GameObject(x, y, '!', 'healing potion', libtcod.yellow, item=item_component, always_visible=True)
            elif choice == 'confuse':
                item_component = Item(use_function=spells.cast_confuse)
                item = GameObject(x, y, '#', 'scroll of confusion', libtcod.yellow, item=item_component, always_visible=True)
            elif choice == 'fireball':
                item_component = Item(use_function=spells.cast_fireball)
                item = GameObject(x, y, '#', 'scroll of fireball', libtcod.yellow, item=item_component, always_visible=True)
            elif choice == 'lightning':
                item_component = Item(use_function=spells.cast_lightning)
                item = GameObject(x, y, '#', 'scroll of lightning bolt', libtcod.yellow, item=item_component, always_visible=True)
            elif choice == 'sword':
                equipment_component = Equipment(slot='right hand', attack_damage_bonus=10)
                item = GameObject(x, y, '/', 'sword', libtcod.yellow, equipment=equipment_component, always_visible = True)
            elif choice == 'shield':
                equipment_component = Equipment(slot='left hand', armor_bonus=5)
                item = GameObject(x, y, '[', 'shield', libtcod.yellow, equipment=equipment_component, always_visible = True)
            objects.append(item)
            item.send_to_back()


def create_room(room):
    global map
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            dice = libtcod.random_get_int(0, 0, 3)
            dice = 1
            if dice == 0:
                map[x][y].tile_type = 'shallow water'
            elif dice == 1:
                map[x][y].tile_type = 'deep water'
            else:
                map[x][y].tile_type = 'stone floor'


def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
            map[x][y].tile_type = 'stone floor'


def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
            map[x][y].tile_type = 'stone floor'


def make_map():
    global map, objects, stairs
    
    objects = [player]
    
    map = [[ Tile('stone wall')
        for y in range(consts.MAP_HEIGHT) ]
            for x in range(consts.MAP_WIDTH) ]

    rooms = []
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
            
    stairs = GameObject(new_x, new_y, '<', 'stairs downward', libtcod.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()


def player_move_or_attack(dx, dy):

    global fov_recompute
    
    x = player.x + dx
    y = player.y + dy
    
    target = None
    for object in objects:
        if object.x == x and object.y == y and object.fighter is not None:
            target = object
            break
            
    if target is not None:
        player.fighter.attack(target)
        return True
    else:
        value = player.move(dx, dy)
        fov_recompute = True
        return value


def get_loot(monster):
    loot_table = monster.loot_table
    drop = loot_table[libtcod.random_get_int(0,0,len(loot_table) - 1)]
    if drop:
        proto = loot.proto[drop]
        item = Item(use_function=proto['on_use'], type=proto['type'])
        return GameObject(monster.owner.x,monster.owner.y,proto['char'],proto['name'],proto['color'],item=item)


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
        fov_recompute = True
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
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        return 'picked-up-item'
            if key_char == 'i':
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
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
                level_up_xp = consts.LEVEL_UP_BASE + player.level * consts.LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' +
                       str(player.fighter.xp) + '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' +
                       str(player.fighter.max_hp) + '\nAttack: ' + str(player.fighter.power) + '\nDefense: ' +
                       str(player.fighter.defense),
                       consts.CHARACTER_SCREEN_WIDTH)
            if key_char == 'z':
                if len(memory) == 0:
                    message('You have no spells in your memory to cast.', libtcod.purple)
                elif map[player.x][player.y].tile_type == 'deep water':
                    message('You cannot cast spells underwater.', libtcod.purple)
                else:
                    cast_spell()
                    return 'casted-spell'
            return 'didnt-take-turn'
        if not moved:
            return 'didnt-take-turn'


def cast_spell():
    message('Cast which spell?', libtcod.purple)

    render_all();
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
            libtcod.console_put_char_ex(mapCon, x - offsetx, y - offsety, ' ', libtcod.black, libtcod.black)


def render_all():

    global fov_map, color_dark_wall, color_lit_wall
    global color_dark_ground, color_lit_ground
    global fov_recompute

    libtcod.console_set_default_foreground(mapCon, libtcod.white)
    offsetx, offsety = player.x - consts.MAP_VIEWPORT_WIDTH / 2, player.y - consts.MAP_VIEWPORT_HEIGHT / 2

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, consts.TORCH_RADIUS, consts.FOV_LIGHT_WALLS, consts.FOV_ALGO)
    
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            # wall = map[x][y].blocks_sight
            visible = libtcod.map_is_in_fov(fov_map, x, y)
            # color_fg = copy.copy(map[x][y].color_fg)
            # color_bg = copy.copy(map[x][y].color_bg)
            color_fg = libtcod.Color(map[x][y].color_fg[0], map[x][y].color_fg[1], map[x][y].color_fg[2])
            color_bg = libtcod.Color(map[x][y].color_bg[0], map[x][y].color_bg[1], map[x][y].color_bg[2])
            if not visible:
                if map[x][y].explored:
                    libtcod.color_scale_HSV(color_fg, 0.1, 0.4)
                    libtcod.color_scale_HSV(color_bg, 0.1, 0.4)
                    libtcod.console_put_char_ex(mapCon, x - offsetx, y - offsety, map[x][y].tile_char, color_fg, color_bg)
            else:
                libtcod.console_put_char_ex(mapCon, x - offsetx, y - offsety, map[x][y].tile_char, color_fg, color_bg)
                map[x][y].explored = True

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

    # Spells in memory
    libtcod.console_print(rightPanel, 1, 13, 'Spells in memory:')
    y = 1
    for spell in memory:
        libtcod.console_print(rightPanel, 1, 13 + y, str(y) + ') ' + spell.name)
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

    libtcod.console_set_default_background(ui_util, libtcod.black)
    libtcod.console_clear(ui_util)

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
    global player, inventory, game_msgs, game_state, dungeon_level, memory
    
    #create object representing the player
    fighter_component = Fighter(hp=100, xp=0, stamina=100, death_function=player_death)
    player = GameObject(25, 23, '@', 'player', libtcod.white, blocks=True, fighter=fighter_component, playerStats=PlayerStats())
    player.level = 1
    
    #generate map
    dungeon_level = 1
    make_map()
    initialize_fov()
    game_state = 'playing'
    
    inventory = []
    item = GameObject(0, 0, '#', 'scroll of bullshit', libtcod.yellow, item=Item(use_function=spells.cast_fireball))
    inventory.append(item)

    memory = []
    # spell = GameObject(0, 0, '?', 'mystery spell', libtcod.yellow, item=Item(use_function=spells.cast_lightning, type="spell"))
    # memory.append(spell)

    #Welcome message
    game_msgs = []
    message('Welcome to the dungeon...', libtcod.gold)


def initialize_fov():
    global fov_recompute, fov_map
    
    libtcod.console_clear(con)
    
    fov_recompute = True
    
    fov_map = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].blocks_sight, not map[x][y].blocks)


def save_game():
    file = shelve.open('savegame', 'n')
    file['map'] = map
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
    global map, objects, player, inventory, memory, game_msgs, game_state, dungeon_level, stairs

    file = shelve.open('savegame', 'r')
    map = file['map']
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
    global key, mouse
    player_action = None
    
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():

        # render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()
        libtcod.console_flush()

        # check for level up
        check_level_up()
    
        # erase the map so it can be redrawn next frame
        clear_map()

        # handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        # Let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            player.on_tick()
            for object in objects:
                if object.ai:
                    object.ai.take_turn()
                    object.on_tick()


# my modules
import spells
import loot

libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT, 'Let\'s Try Making a Roguelike', False)
libtcod.sys_set_fps(consts.LIMIT_FPS)
con = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
mapCon = libtcod.console_new(consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT)
ui = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
ui_util = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
panel = libtcod.console_new(consts.SCREEN_WIDTH, consts.PANEL_HEIGHT)
rightPanel = libtcod.console_new(consts.RIGHT_PANEL_WIDTH, consts.RIGHT_PANEL_HEIGHT)
