import libtcodpy as libtcod
import math
import shelve
import consts
import world
import syntax
import collections

#############################################
# Classes
#############################################


class Equipment:
    def __init__(self, slot, category, max_hp_bonus=0, attack_damage_bonus=0,
                 armor_bonus=0, evasion_bonus=0, spell_power_bonus=0, stamina_cost=0, str_requirement=0, shred_bonus=0,
                 guaranteed_shred_bonus=0, pierce=0, accuracy=0, ctrl_attack=None, ctrl_attack_desc=None,
                 break_chance=0.0, weapon_dice=None, str_dice=None, on_hit=None, damage_type=None, attack_speed_bonus=0,
                 attack_delay=0, essence=None,spell_list=None,level_progression=None,level_costs=None,resistances=[],
                 crit_bonus=1.0,subtype=None, spell_resist_bonus=0,starting_level=0):
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.category = category
        self.is_equipped = False
        self.attack_damage_bonus = attack_damage_bonus
        self.armor_bonus = armor_bonus
        self.evasion_bonus = evasion_bonus
        self.spell_power_bonus = spell_power_bonus
        self.spell_resist_bonus = spell_resist_bonus
        self.stamina_cost = stamina_cost
        self.str_requirement = str_requirement
        self.shred_bonus = shred_bonus
        self.guaranteed_shred_bonus = guaranteed_shred_bonus
        self.pierce_bonus = pierce
        self.accuracy_bonus = accuracy
        self.ctrl_attack = ctrl_attack
        self.break_chance = break_chance
        self.crit_bonus = crit_bonus
        self.ctrl_attack_desc = ctrl_attack_desc
        self._weapon_dice = weapon_dice
        self.str_dice = str_dice
        self.on_hit = on_hit #expects list
        self.damage_type = damage_type
        self.attack_speed_bonus = attack_speed_bonus
        self.attack_delay = attack_delay
        self.resistances = list(resistances)
        self.essence = essence
        self.level = 0
        self.subtype = subtype
        if level_progression is not None:
            self.max_level = len(level_progression)
        self.level_progression = level_progression
        if spell_list is not None:
            default_level = 0
            if level_progression is None:
                default_level = 1
            self.spell_list = {s:default_level for s in spell_list}
            self.flat_spell_list = spell_list
            self.level_costs = level_costs
            self.spell_charges = {}
            self.refill_spell_charges()
        for i in range(starting_level):
            self.level_up(True)

    @property
    def weapon_dice(self):
        if self._weapon_dice is not None:
            d = self._weapon_dice.split('d')
            dice_size = max(int(d[1]) + (2 * self.attack_damage_bonus), 1)
            return "{}d{}".format(d[0],dice_size)
        else:
            return "+0"

    def toggle(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()
            
    def equip(self):
        if self.slot == 'both hands':
            rh = get_equipped_in_slot(player.instance.fighter.inventory, 'right hand')
            lh = get_equipped_in_slot(player.instance.fighter.inventory, 'left hand')
            if rh is not None: rh.dequip()
            if lh is not None: lh.dequip()
        else:
            old_equipment = get_equipped_in_slot(player.instance.fighter.inventory, self.slot)
            if old_equipment is not None:
                old_equipment.dequip()
        self.is_equipped = True
        ui.message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.orange)
        
    def dequip(self):
        self.is_equipped = False
        ui.message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.orange)

    def print_description(self, console, x, y, width):
        print_height = 1
        if self.str_requirement != 0:
            if player.instance.player_stats.str < self.str_requirement:
                libtcod.console_set_default_foreground(console, libtcod.red)
            else:
                libtcod.console_set_default_foreground(console, libtcod.dark_green)
            libtcod.console_print(console, x, y + print_height, 'Strength Required: ' + str(self.str_requirement))
            print_height += 1
            libtcod.console_set_default_foreground(console, libtcod.white)
        libtcod.console_print(console, x, y + print_height, 'Slot: ' + self.slot)
        print_height += 2
        if self.level_progression is not None and self.level_progression != 0:
            libtcod.console_print(console, x, y + print_height, 'Level: ' + str(self.level) + '/' + str(self.max_level))
            print_height += 1
        if self.armor_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Armor: ' + str(self.armor_bonus))
            print_height += 1
        if self.weapon_dice != '+0':
            r = dice_range(self.weapon_dice, normalize_size=4)
            libtcod.console_print(console, x, y + print_height, 'Damage: ' + str(r[0]) + '-' + str(r[1]))
            print_height += 1
        if self.str_dice is not None and self.str_dice > 0:
            r = dice_range(str(self.str_dice)+'d'+str(player.instance.player_stats.str), normalize_size=4)
            libtcod.console_print(console, x, y + print_height, 'Strength Bonus: ' + str(r[0]) + '-' + str(r[1]))
            print_height += 1
        if self.accuracy_bonus != 0:
            acc_str = 'Accuracy: '
            if self.accuracy_bonus > 0:
                acc_str += '+'
            libtcod.console_print(console, x, y + print_height, acc_str + str(self.accuracy_bonus))
            print_height += 1
        if self.attack_delay != 0:
            attacks = max(round(float(player.instance.fighter.attack_speed) / float(self.attack_delay), 1), 1.0)
            libtcod.console_print(console, x, y + print_height, 'Attack Speed: ' + str(attacks))
            print_height += 1
        if self.attack_damage_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Damage: ' + str(self.attack_damage_bonus))
            print_height += 1
        if self.evasion_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Evade: ' + str(self.evasion_bonus))
            print_height += 1
        if self.guaranteed_shred_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Auto-shred: ' + str(self.guaranteed_shred_bonus))
            print_height += 1
        if self.max_hp_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Bonus HP: ' + str(self.max_hp_bonus))
            print_height += 1
        if self.pierce_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Pierce: ' + str(self.pierce_bonus))
            print_height += 1
        if self.shred_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Shred: ' + str(self.shred_bonus))
            print_height += 1
        if self.spell_power_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Spell Power: ' + str(self.spell_power_bonus))
            print_height += 1
        if self.spell_resist_bonus != 0:
            libtcod.console_print(console, x, y + print_height, 'Spell Resist: ' + str(self.spell_resist_bonus))
            print_height += 1
        if self.break_chance > 0:
            libtcod.console_print(console, x, y + print_height, 'It has a ' + str(self.break_chance) + '%%' + ' chance to break when used.')
            print_height += 1
        if self.ctrl_attack_desc:
            libtcod.console_set_default_foreground(console, libtcod.azure)
            text = 'Ctrl+attack: ' + self.ctrl_attack_desc
            h = libtcod.console_get_height_rect(console, x, y + print_height, width, consts.SCREEN_HEIGHT, text)
            libtcod.console_print_rect(console, x, y + print_height + 1, width, h, text)
            print_height += h + 1
            libtcod.console_set_default_foreground(console, libtcod.white)
        if hasattr(self, 'spell_list') and self.spell_list is not None:
            libtcod.console_set_default_foreground(console, libtcod.azure)
            libtcod.console_print(console, x, y + print_height,'Spells:')
            libtcod.console_set_default_foreground(console, libtcod.white)
            for spell in self.flat_spell_list:
                level = self.spell_list[spell] #dictionaries don't preserve order - flat lists do
                spell_data = spells.library[spell]
                if level == 0:
                    libtcod.console_set_default_foreground(console, libtcod.gray)
                libtcod.console_print(console, x, y + print_height, "- " + spell_data.name.title() + " " + str(level) + "/" + str(spell_data.max_level))
                libtcod.console_set_default_foreground(console, libtcod.white)
                print_height += 1

        return print_height

    def get_active_spells(self):
        return {s: l for (s, l) in self.spell_list.items() if l > 0}

    def can_cast(self, spell_name, actor):
        sl = self.spell_list[spell_name]
        if actor is player.instance:
            if player.instance.player_stats.int < spells.library[spell_name].int_requirement:
                ui.message("This spell is too difficult for you to understand.", libtcod.blue)
                return False
        level = spells.library[spell_name].levels[sl-1]

        if spell_name not in self.spell_list:
            ui.message("You don't have that spell.")
            return False
        elif sl <= 0:
            ui.message('That spell has not been learned!', libtcod.blue)
            return False
        elif self.spell_charges[spell_name] <= 0:
            ui.message('That spell is out of charges.', libtcod.blue)
            return False
        elif actor.fighter.stamina < level['stamina_cost']:
            ui.message("You don't have the stamina to cast that spell.", libtcod.light_yellow)
            return False
        return True


        #return self.spell_list.has_key(spell_name) and sl > 0 and \
        #       actor.fighter.stamina >= level['stamina_cost'] and \
        #        self.spell_charges[spell_name] > 0

    def level_up(self, force = False):
        if self.level >= self.max_level:
            ui.message('{} is already max level!'.format(self.owner.name))

        if self.essence not in player.instance.essence and not force:
            ui.message("You don't have any " + self.essence + " essence.", libtcod.blue)
            return 'didnt-take-turn'

        cost = self.level_costs[self.level] #next level cost, no level-1

        if collections.Counter(player.instance.essence)[self.essence] < cost and not force:
            ui.message("You don't have enough " + self.essence + " essence.", libtcod.blue)
            return 'didnt-take-turn'

        if self.spell_list is not None:
            spell = self.level_progression[self.level]
            self.spell_list[spell] += 1
            #refill spell charges for that spell
            self.spell_charges[spell] = spells.library[spell].levels[self.spell_list[spell]-1]['charges']
            if self.spell_list[spell] == 1:
                ui.message('Learned spell ' + spells.library[spell].name.title(), libtcod.white)
            else:
                ui.message('Upgraded spell ' + spells.library[spell].name.title() + " to level " + str(self.spell_list[spell]), libtcod.white)
            ui.message('')
        for i in range(cost):
            if self.essence in player.instance.essence:
                player.instance.essence.remove(self.essence)
        self.level += 1
        return 'leveled-up'

    def refill_spell_charges(self):
        #on medidate, item create, and potions(?)
        for spell,level in self.get_active_spells().items():
            spell_level = spells.library[spell].levels[level-1]
            self.spell_charges[spell] = spell_level['charges']

class Item:
    def __init__(self, category, use_function=None, type='item', ability=None):
        self.category = category
        self.use_function = use_function
        self.type = type
        self.ability = ability
        
    def pick_up(self):
        if self.type == 'item':
            if len(player.instance.fighter.inventory) >= 26:
                ui.message('Your inventory is too full to pick up ' + self.owner.name)
            else:
                player.instance.fighter.inventory.append(self.owner)
                self.owner.destroy()
                ui.message('You picked up a ' + self.owner.name + '!', libtcod.light_grey)
                equipment = self.owner.equipment
                if equipment and get_equipped_in_slot(player.instance.fighter.inventory,equipment.slot) is None:
                    equipment.equip()
        elif self.type == 'spell':
            if len(memory) >= player.instance.player_stats.max_memory:
                ui.message('You cannot hold any more spells in your memory!', libtcod.purple)
            else:
                memory.append(self.owner)
                self.owner.destroy()
                ui.message(str(self.owner.name) + ' has been added to your memory.', libtcod.purple)
            
    def use(self):
        if self.owner.equipment:
            self.owner.equipment.toggle()
            return
        if self.use_function is not None:
            if self.use_function() != 'cancelled':
                if self.type == 'item' and self.category != 'charm':
                    player.instance.fighter.inventory.remove(self.owner)
                elif self.type == 'spell':
                    memory.remove(self.owner)
            else:
                return 'cancelled'
        else:
            ui.message('The ' + self.owner.name + ' cannot be used.')

                
    def drop(self):
        if self.owner.equipment:
            self.owner.equipment.dequip();
        current_map.add_object(self.owner)
        player.instance.fighter.inventory.remove(self.owner)
        self.owner.x = player.instance.x
        self.owner.y = player.instance.y
        ui.message('You dropped a ' + self.owner.name + '.', libtcod.white)

    def get_options_list(self):
        options = []
        if self.use_function is not None:
            options.append('Use')
        if self.owner.equipment:
            if self.owner.equipment.is_equipped:
                options.append('Unequip')
            else:
                options.append('Equip')
            if self.owner.equipment.level_progression:
                cost = self.owner.equipment.level_costs[self.owner.equipment.level]
                options.append('Imbue ' + ('*') * cost)
        options.append('Drop')
        return options

    def print_description(self, console, x, y, width):
        print_height = 0

        if self.owner.equipment:
            print_height += self.owner.equipment.print_description(console, x, y + print_height, width)

        return print_height

class GameObject:

    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, behavior=None, item=None, equipment=None,
                 player_stats=None, always_visible=False, interact=None, description=None, on_create=None,
                 update_speed=1.0, misc=None, blocks_sight=False, on_step=None, burns=False, on_tick=None,
                 elevation=None, background_color=None, movement_type=0, summon_time = None):
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
        self.behavior = behavior
        if self.behavior:
            self.behavior = ai.AI_General(behavior=self.behavior)
            self.behavior.owner = self
            self.behavior.behavior.owner = self
        self.item = item
        if self.item:
            self.item.owner = self
        self.equipment = equipment
        if self.equipment:
            self.equipment.owner = self
            self.item = Item(self.equipment.category)
            self.item.owner = self
        self.player_stats = player_stats
        if self.player_stats:
            self.player_stats.owner = self
        if on_create is not None:
            on_create(self)
        self.misc = misc
        if self.misc:
            self.misc.owner = self
        self.blocks_sight = blocks_sight
        self.on_step = on_step
        self.burns = burns
        self.on_tick_specified = on_tick
        if elevation is None:
            if current_map is not None and current_map.tiles is not None:
                self.elevation = current_map.tiles[self.x][self.y].elevation
            else:
                self.elevation = 0
        else:
            self.elevation = elevation
        self.background_color = background_color
        self.movement_type = movement_type
        self.summon_time = summon_time

    def print_description(self, console, x, y, width):
        height = libtcod.console_get_height_rect(console, x, y, width, consts.SCREEN_HEIGHT, self.description)
        draw_height = y
        libtcod.console_print_rect(console, x, draw_height, width, height, self.description.capitalize())
        draw_height += height
        if self.item:
            h = self.item.print_description(console, x, draw_height, width)
            draw_height += h
            height += h
        if self.fighter:
            h = self.fighter.print_description(console, x, draw_height, width)
            draw_height += h
            height += h
        return height

    def on_create(self):
        if self.blocks_sight:
            fov.set_fov_properties(self.x, self.y, self.blocks_sight, self.elevation)

    def set_position(self, x, y):

        old_x = self.x
        old_y = self.y

        # If the object is not moving, skip this function.
        if old_x == x and old_y == y:
            return

        # Update the object's position/elevation
        self.x = x
        self.y = y
        old_elev = self.elevation
        self.elevation = current_map.tiles[x][y].elevation

        # Update the tile we left for the renderer
        global changed_tiles
        changed_tiles.append((old_x, old_y))

        # Update fov maps (if this object affects fov)
        if self.blocks_sight:
            fov.set_fov_properties(old_x, old_y, current_map.tiles[old_x][old_y].blocks_sight, self.elevation)
            fov.set_fov_properties(x, y, True, self.elevation)

        # Update the pathfinding map - update our previous space and mark our new space as impassable
        if current_map.pathfinding and self.blocks:
            if is_blocked(old_x, old_y):
                current_map.pathfinding.mark_blocked((old_x, old_y))
            else:
                current_map.pathfinding.mark_unblocked((old_x, old_y))
            current_map.pathfinding.mark_blocked((x, y))

        # Check for objects with 'stepped_on' functions on our new space (xp, essence, traps, etc)
        stepped_on = get_objects(self.x, self.y, lambda o: o.on_step)
        if len(stepped_on) > 0:
            for obj in stepped_on:
                obj.on_step(obj, self)

        # Update 'in-mud' state
        if self.fighter and self.movement_type & pathfinding.FLYING != pathfinding.FLYING:
            if current_map.tiles[self.x][self.y].tile_type == 'mud' and not self.fighter.has_status('sluggish'):
                self.fighter.apply_status_effect(effects.StatusEffect('sluggish', color=libtcod.sepia))
            elif current_map.tiles[self.x][self.y].tile_type != 'mud' and self.fighter.has_status('sluggish'):
                self.fighter.remove_status('sluggish')

        # If the player moved, recalculate field of view, checking for elevation changes
        if self is player.instance:
            if old_elev != self.elevation:
                fov.set_view_elevation(self.elevation)
            fov.set_fov_recompute()

    def swap_positions(self, target):
        target_pos = target.x, target.y
        target.set_position(self.x, self.y)
        value = self.move(target_pos[0] - self.x, target_pos[1] - self.y)
        if not value:
            target.set_position(target_pos[0], target_pos[1])
        return value

    def move(self, dx, dy):

        x,y = self.x + dx, self.y + dy
        blocked = is_blocked(x,y, from_coord=(self.x, self.y), movement_type=self.movement_type)

        if not blocked:
            if self.fighter is not None:
                if self.fighter.has_status('immobilized'):
                    return True
                web = object_at_tile(self.x, self.y, 'spiderweb')
                if web is not None and not self.name == 'tunnel spider':
                    ui.message('%s %s against the web' % (
                                    syntax.name(self.name).capitalize(),
                                    syntax.conjugate(self is player.instance, ('struggle', 'struggles'))))
                    web.destroy()
                    return True
                door = object_at_tile(x,y, 'door')
                if door is not None and door.closed:
                    door_interact(door)
                    return True
                cost = current_map.tiles[self.x][self.y].stamina_cost
                if cost > 0 and self is player.instance\
                        and self.movement_type & pathfinding.FLYING != pathfinding.FLYING\
                        and self.movement_type & pathfinding.AQUATIC != pathfinding.AQUATIC:
                    if self.fighter.stamina >= cost:
                        self.fighter.adjust_stamina(-cost)
                    else:
                        ui.message("You don't have the stamina leave this space!", libtcod.light_yellow)
                        return False
                else:
                    self.fighter.adjust_stamina(consts.STAMINA_REGEN_MOVE)     # gain stamina for moving across normal terrain

                if current_map.tiles[x][y].on_step is not None:
                    current_map.tiles[x][y].on_step(x,y,self)

            self.set_position(x,y)

            return True
        return False

    def draw(self, console):
        if fov.player_can_see(self.x, self.y):
            if ui.selected_monster is self:
                libtcod.console_put_char_ex(console, self.x, self.y, self.char, libtcod.black, self.color)
            else:
                if self.background_color is None:
                    libtcod.console_set_default_foreground(console, self.color)
                    libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)
                else:
                    libtcod.console_put_char_ex(console, self.x, self.y, self.char, self.color, self.background_color)
        elif self.always_visible and current_map.tiles[self.x][self.y].explored:
            shaded_color = libtcod.Color(self.color[0], self.color[1], self.color[2])
            libtcod.color_scale_HSV(shaded_color, 0.1, 0.4)
            libtcod.console_set_default_foreground(console, shaded_color)
            if self.background_color is not None:
                shaded_bkgnd = libtcod.Color(self.background_color[0], self.background_color[1], self.background_color[2])
                libtcod.color_scale_HSV(shaded_bkgnd, 0.1, 0.4)
                libtcod.console_put_char_ex(console, self.x, self.y, self.char, shaded_color, shaded_bkgnd)
            else:
                libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def move_towards(self, target_x, target_y):
        if self.x == target_x and self.y == target_y:
            return

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def move_astar(self, target_x, target_y):
        if self.x == target_x and self.y == target_y:
            return 'already here'

        if not current_map.pathfinding:
            self.move_astar_old(target_x, target_y)
            return 'no map'
        else:
            if not current_map.pathfinding.is_accessible((target_x, target_y)):
                closest_adjacent = None
                closest = 10000
                for adj in adjacent_tiles_diagonal(target_x, target_y):
                    if is_blocked(adj[0], adj[1], from_coord=(target_x, target_y), movement_type=self.movement_type):
                        continue
                    dist = self.distance(adj[0], adj[1])
                    if dist < closest:
                        closest = dist
                        closest_adjacent = adj
                if closest_adjacent is None:
                    self.move_towards(target_x, target_y)
                    return 'no adjacent'
                else:
                    target_x = closest_adjacent[0]
                    target_y = closest_adjacent[1]

            path = current_map.pathfinding.a_star_search((self.x, self.y), (target_x, target_y), self.movement_type)

            if consts.DEBUG_DRAW_PATHS:
                pathfinding.draw_path(path)

            if path != 'failure' and 0 < len(path) < 25:
                # find the next coordinate in the computed full path
                x, y = path[1]
                if x or y:
                    if current_map.tiles[x][y].blocks:
                        current_map.pathfinding.mark_blocked((x, y))  # bandaid fix - hopefully paths will self-correct now
                    else:
                        self.move_towards(x, y)
            else:
                # Use the old(er) function instead
                self.move_towards(target_x, target_y)
                return 'failure'

    def move_astar_old(self, target_x, target_y):

        if self.x == target_x and self.y == target_y:
            return

        fov = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)
        
        # Scan the map and set all walls to unwalkable
        for y1 in range(consts.MAP_HEIGHT):
            for x1 in range(consts.MAP_WIDTH):
                terrain = current_map.tiles[x1][y1].blocks
                elev = self.elevation != current_map.tiles[x1][y1].elevation and not current_map.tiles[x1][y1].is_ramp
                blocks = terrain or elev
                libtcod.map_set_properties(fov, x1, y1, not current_map.tiles[x1][y1].blocks_sight, not blocks)
        
        # Scan all objects to see if there are objects that must be navigated around
        for obj in current_map.objects:
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
                self.move_towards(x, y)
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
        if self not in current_map.objects:
            return
        current_map.objects.remove(self)
        current_map.objects.insert(0, self)

    def on_tick(self, object=None):
        if self.summon_time:
            self.summon_time -= 1
            if self.summon_time <= 0:
                if fov.player_can_see(self.x, self.y):
                    ui.message('%s fades away as %s returns to the world from whence %s came.' %
                               (syntax.name(self.name).capitalize(),
                                syntax.pronoun(self.name),
                                syntax.pronoun(self.name)), libtcod.gray)
                self.destroy()
                return
        if self.on_tick_specified:
            self.on_tick_specified(object)
        if self.fighter:
            self.fighter.on_tick()
        if self.misc and hasattr(self.misc, 'on_tick'):
            self.misc.on_tick(object)

    def destroy(self):
        global changed_tiles
        if self.blocks_sight:
            fov.set_fov_properties(self.x, self.y, current_map.tiles[self.x][self.y].blocks_sight, self.elevation)
        if self.blocks and current_map.pathfinding:
            current_map.pathfinding.mark_unblocked((self.x, self.y))
        changed_tiles.append((self.x, self.y))
        if self in current_map.fighters:
            current_map.fighters.remove(self)
        current_map.objects.remove(self)
        if self is ui.selected_monster:
            ui.target_next_monster()


class Tile:
    
    def __init__(self, tile_type='stone floor'):
        self.explored = False
        self.tile_type = tile_type
        self.no_overwrite = False
        self.elevation = 0
        self.flags = 0

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

    @property
    def flammable(self):
        return terrain.data[self.tile_type].flammable

    @property
    def diggable(self):
        if self.flags & terrain.FLAG_NO_DIG == terrain.FLAG_NO_DIG:
            return False
        return terrain.data[self.tile_type].diggable

    @property
    def is_wall(self):
        return terrain.data[self.tile_type].isWall

    @property
    def is_floor(self):
        return terrain.data[self.tile_type].isFloor

    @property
    def is_water(self):
        return terrain.data[self.tile_type].isWater

    @property
    def is_ramp(self):
        return terrain.data[self.tile_type].isRamp

    @property
    def is_pit(self):
        return terrain.data[self.tile_type].isPit

    @property
    def on_step(self):
        return terrain.data[self.tile_type].on_step

                
#############################################
# General Functions
#############################################


def has_skill(name):
    if name == 'Adrien':
        return False  # OOH, BURN!
    for skill in learned_skills:
        if skill.name == name:
            return True
    return False


def expire_out_of_vision(obj):
    if not fov.player_can_see(obj.x, obj.y):
        obj.destroy()


def step_on_reed(reed, obj):
    reed.destroy()


def step_on_blightweed(weed, obj):
    if obj.fighter:
        obj.fighter.time_since_last_damaged = 0
        if obj.fighter.armor > 0:
            obj.fighter.shred += 1
            if fov.player_can_see(obj.x, obj.y):
                ui.message('The blightweed thorns shred %s armor!' % syntax.name(obj.name, possesive=True), libtcod.desaturated_red)

def step_on_snow_drift(x,y,obj):
    current_map.tiles[x][y].tile_type = 'snowy ground'

def adjacent_tiles_orthogonal(x, y):
    adjacent = []
    if x > 0:
        adjacent.append((x - 1, y))
    if x < consts.MAP_WIDTH - 1:
        adjacent.append((x + 1, y))
    if y > 0:
        adjacent.append((x, y - 1))
    if y < consts.MAP_WIDTH - 1:
        adjacent.append((x, y + 1))
    return adjacent


def adjacent_tiles_diagonal(x, y):
    adjacent = []
    for i_y in range(y - 1, y + 2):
        for i_x in range(x - 1, x + 2):
            if 0 <= i_x < consts.MAP_WIDTH and 0 <= i_y < consts.MAP_HEIGHT and not (i_x == x and i_y == y):
                adjacent.append((i_x, i_y))
    return adjacent


def is_adjacent_orthogonal(a_x, a_y, b_x, b_y):
    return (abs(a_x - b_x) <= 1 and a_y == b_y) or (abs(a_y - b_y) <= 1 and a_x == b_x)


def is_adjacent_diagonal(a_x, a_y, b_x, b_y):
    return abs(a_x - b_x) <= 1 and abs(a_y - b_y) <= 1


def blastcap_explode(blastcap):
    global changed_tiles

    blastcap.fighter = None
    current_map.fighters.remove(blastcap)
    ui.message('The blastcap explodes with a BANG, stunning nearby creatures!', libtcod.gold)
    for obj in current_map.fighters:
        if is_adjacent_orthogonal(blastcap.x, blastcap.y, obj.x, obj.y):
            if obj.fighter.apply_status_effect(effects.StatusEffect('stunned', consts.BLASTCAP_STUN_DURATION, libtcod.light_yellow)):
                ui.message('%s %s stunned!' % (
                                syntax.name(obj.name).capitalize(),
                                syntax.conjugate(obj is player.instance, ('are', 'is'))), libtcod.gold)

    if ui.selected_monster is blastcap:
        changed_tiles.append((blastcap.x, blastcap.y))
        ui.selected_monster = None
        ui.auto_target_monster()

    blastcap.destroy()
    return


def centipede_on_hit(attacker, target):
    target.fighter.apply_status_effect(effects.StatusEffect('stung', consts.CENTIPEDE_STING_DURATION, libtcod.flame))


def zombie_on_hit(attacker, target):
    if libtcod.random_get_int(0, 0, 100) < consts.ZOMBIE_IMMOBILIZE_CHANCE:
        ui.message('%s grabs %s! %s cannot move!' % (
                        syntax.name(attacker.name).capitalize(),
                        syntax.name(target.name),
                        syntax.pronoun(target.name).capitalize()), libtcod.yellow)
        target.fighter.apply_status_effect(effects.immobilized(3))


def clamp(value, min_value, max_value):
    if value < min_value:
        value = min_value
    if value > max_value:
        value = max_value
    return value


def random_position_in_circle(radius):
    r = libtcod.random_get_float(0, 0.0, float(radius))
    theta = libtcod.random_get_float(0, 0.0, 2.0 * math.pi)
    return int(round(r * math.cos(theta))), int(round(r * math.sin(theta)))


def object_at_tile(x, y, name):
    for obj in current_map.objects:
        if obj.x == x and obj.y == y and obj.name == name:
            return obj
    return None


def water_elemental_tick(elemental):
    for obj in current_map.fighters:
        if obj.fighter.team != elemental.fighter.team and is_adjacent_diagonal(obj.x, obj.y, elemental.x, elemental.y):
            obj.fighter.apply_status_effect(effects.sluggish(duration=3))
            obj.fighter.apply_status_effect(effects.slowed(duration=3))


# on_create function of tunnel spiders. Creates a web at the spiders location and several random adjacent spaces
def tunnel_spider_spawn_web(obj):
    adjacent = adjacent_tiles_diagonal(obj.x, obj.y)
    webs = [(obj.x, obj.y)]
    for a in adjacent:
        if libtcod.random_get_int(0, 0, 2) == 0 and not current_map.tiles[a[0]][a[1]].blocks:
            webs.append(a)
    for w in webs:
        make_spiderweb(w[0], w[1])


# creates a spiderweb at the target location
def make_spiderweb(x, y):
    web = GameObject(x, y, '*', 'spiderweb', libtcod.lightest_gray,
                     description='a web of spider silk. Stepping into a web will impede movement for a turn.',
                     burns=True)
    current_map.add_object(web)
    web.send_to_back()


def get_all_equipped(equipped_list):
    result = []
    for item in equipped_list:
        if item.equipment and item.equipment.is_equipped:
            result.append(item.equipment)
    return result


def get_equipped_in_slot(equipped_list,slot):
    for obj in equipped_list:
        if obj.equipment and obj.equipment.is_equipped:
            if obj.equipment.slot == slot or (obj.equipment.slot == 'both hands' and
                                                      (slot == 'right hand' or slot == 'left hand')):
                return obj.equipment
    return None


def from_dungeon_level(table):
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

#expects a value between 0.0 and 1.0 for factor
def normalized_choice(choices_list,factor):
    size = len(choices_list)
    if size < 1:
        return None
    return choices_list[int((size - 1) * clamp(factor,0,1))]

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

def next_level():
    global dungeon_level, changed_tiles

    ui.message('You descend...', libtcod.white)
    dungeon_level += 1
    generate_level()
    #initialize_fov()

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))

def bomb_beetle_corpse_tick(object=None):
    if object is None:
        return
    object.bomb_timer -= 1
    if object.bomb_timer > 2:
        object.color = libtcod.black
    elif object.bomb_timer > 1:
        object.color = libtcod.darkest_red
    elif object.bomb_timer > 0:
        object.color = libtcod.red
    elif object.bomb_timer <= 0:
        ui.message('The bomb beetle corpse explodes!', libtcod.orange)
        create_fire(object.x, object.y, 10)
        for tile in adjacent_tiles_diagonal(object.x, object.y):
            if libtcod.random_get_int(0, 0, 3) != 0:
                create_fire(tile[0], tile[1], 10)
            monster = get_monster_at_tile(tile[0], tile[1])
            if monster is not None:
                monster.fighter.take_damage(consts.BOMB_BEETLE_DAMAGE)
                if monster.fighter is not None:
                    monster.fighter.apply_status_effect(effects.burning())
        object.destroy()


def bomb_beetle_death(beetle):

    ui.message('%s is dead!' % syntax.name(beetle.name).capitalize(), libtcod.red)
    beetle.char = 149
    beetle.color = libtcod.black
    beetle.blocks = True
    beetle.fighter = None
    beetle.behavior = None
    beetle.name = 'beetle bomb'
    beetle.description = 'The explosive carapace of a blast beetle. In a few turns, it will explode!'
    beetle.bomb_timer = 3
    beetle.on_tick = bomb_beetle_corpse_tick
    current_map.fighters.remove(beetle)

    if ui.selected_monster is beetle:
        changed_tiles.append((beetle.x, beetle.y))
        ui.selected_monster = None
        ui.auto_target_monster()


def monster_death(monster):
    global changed_tiles

    if hasattr(monster.fighter,'inventory') and len(monster.fighter.inventory) > 0:
        for item in monster.fighter.inventory:
            item.x = monster.x
            item.y = monster.y
            current_map.add_object(item)
            item.send_to_back()

    ui.message('%s is dead!' % syntax.name(monster.name).capitalize(), libtcod.red)

    if monster.fighter.monster_flags & monsters.NO_CORPSE == monsters.NO_CORPSE:
        monster.destroy()
    elif monster.summon_time is not None:
        monster.destroy()
        ui.message('%s corpse fades into the world from whence it came.' %
                   syntax.pronoun(monster.name, possesive=True).capitalize(), libtcod.gray)
    else:
        monster.char = '%'
        monster.color = libtcod.darker_red
        monster.blocks = False
        if current_map.pathfinding:
            current_map.pathfinding.mark_unblocked((monster.x, monster.y))
        monster.behavior = None
        monster.name = 'remains of ' + monster.name
        monster.send_to_back()
        current_map.fighters.remove(monster)
    monster.fighter = None

    if ui.selected_monster is monster:
        changed_tiles.append((monster.x, monster.y))
        ui.selected_monster = None
        ui.auto_target_monster()


def target_monster(max_range=None):
    while True:
        (x, y) = ui.target_tile(max_range)
        if x is None:
            return None
        for obj in current_map.fighters:
            if obj.x == x and obj.y == y and obj is not player.instance:
                return obj
        return None


def get_monster_at_tile(x, y):
    for obj in current_map.fighters:
        if obj.x == x and obj.y == y and obj is not player.instance:
            return obj
    return None


def object_at_coords(x, y):

    ops = [t for t in current_map.objects if (t.x == x and t.y == y)]
    if len(ops) > 1:
        menu_choice = ui.menu("Which object?", [o.name for o in ops], 40)
        if menu_choice is not None:
            return ops[menu_choice]
        else:
            return None
    elif len(ops) == 0:
        return current_map.tiles[x][y]
    else:
        return ops[0]

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

    for object in current_map.fighters:
        if object is not player.instance and fov.player_can_see(object.x, object.y):
            dist = player.instance.distance_to(object)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy = object
    return closest_enemy


def in_bounds(x, y):
    return 0 <= x < consts.MAP_WIDTH and 0 <= y < consts.MAP_HEIGHT


def is_blocked(x, y, from_coord=None, movement_type=None):

    tile = current_map.tiles[x][y]

    from_tile = None
    elevation = None
    if from_coord is not None:
        from_tile = current_map.tiles[from_coord[0]][from_coord[1]]
        elevation = from_tile.elevation

    if movement_type is None:
        if elevation is not None and tile.elevation != elevation and not tile.is_ramp and not from_tile.is_ramp:
            return True
        if tile.blocks or tile.is_pit:
            return True
    else:
        if tile.blocks:
            if movement_type & pathfinding.TUNNELING != pathfinding.TUNNELING:
                # If this is a solid block and we do not have the TUNNELING flag...
                return True
        elif tile.is_pit:
            if movement_type & pathfinding.FLYING != pathfinding.FLYING:
                # If this is a pit and we do not have the FLYING flag...
                return True
        elif elevation is not None and tile.elevation != elevation and not tile.is_ramp and not from_tile.is_ramp:
            if movement_type & pathfinding.CLIMBING != pathfinding.CLIMBING and \
                                    movement_type & pathfinding.FLYING != pathfinding.FLYING:
                # If there is a cliff separating these tiles and we do not have the CLIMBING/FLYING flags...
                return True
        elif not tile.is_water:
            if movement_type & pathfinding.NORMAL != pathfinding.NORMAL and \
                                    movement_type & pathfinding.FLYING != pathfinding.FLYING:
                # If this is not water and we do not have the NORMAL/FLYING flags...
                return True

    # If we did not find a blockage in terrain, check for blocking objects
    for object in current_map.objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    # No obstructions were found
    return False


def get_room_spawns(room):
    return [[k, libtcod.random_get_int(0, v[0], v[1])] for (k, v) in room['spawns'].items()]


def spawn_monster(name, x, y, team='enemy'):
    if consts.DEBUG_NO_MONSTERS:
        return None
    if not is_blocked(x, y):
        p = monsters.proto[name]

        modifier = {}
        mod_tag = ""
        if(p.get('modifier_category',None) is not None):
            mod_tag = random_choice(monsters.modifier_categories[p['modifier_category']])
            modifier = monsters.modifiers[mod_tag]
            mod_tag = mod_tag + " " #for monster description

        death = monster_death
        if p.get('death_function'):
            death = p.get('death_function')
        fighter_component = combat.Fighter( hp=int(p['hp'] * modifier.get('hp_bonus',1)),
                                            armor=int(p['armor'] * modifier.get('armor_bonus',1)), evasion=int(p['evasion'] * modifier.get('evasion_bonus',1)),
                                            accuracy=int(p['accuracy'] * modifier.get('accuracy_bonus',1)), xp=0,
                                            death_function=death, spell_power=p.get('spell_power', 0) * modifier.get('spell_power_bonus',1),
                                            can_breath_underwater=True, resistances=p.get('resistances',[]) + modifier.get('resistances',[]),
                                            weaknesses=p.get('weaknesses',[]) + modifier.get('weaknesses', []),
                                            inventory=spawn_monster_inventory(p.get('equipment')), on_hit=p.get('on_hit'),
                                            base_shred=p.get('shred', 0) * modifier.get('shred_bonus',1),
                                            base_guaranteed_shred=p.get('guaranteed_shred', 0),
                                            base_pierce=p.get('pierce', 0) * modifier.get('pierce_bonus',1), hit_table=p.get('body_type'),
                                            monster_flags=p.get('flags', 0),subtype=p.get('subtype'),damage_bonus=p.get('attack_bonus', 0),
                                            monster_str_dice=p.get('strength_dice'), team=p.get('team', team))

        if p.get('attributes'):
            fighter_component.abilities = [create_ability(a) for a in p['attributes'] if a.startswith('ability_')]
        behavior = None
        if p.get('ai'):
            behavior = p.get('ai')()

        monster = GameObject(x, y, p['char'], mod_tag + p['name'], p['color'], blocks=True, fighter=fighter_component,
                             behavior=behavior, description=p['description'], on_create=p.get('on_create'),
                             movement_type=p.get('movement_type', pathfinding.NORMAL), on_tick=p.get('on_tick'))

        if monster.behavior:
            monster.behavior.attack_speed = 1.0 / p.get('attack_speed', 1.0 * modifier.get('speed_bonus', 1.0))
            monster.behavior.move_speed = 1.0 / p.get('move_speed', 1.0 * modifier.get('speed_bonus', 1.0))

        if p.get('essence'):
            monster.essence = p.get('essence')
        monster.elevation = current_map.tiles[x][y].elevation
        current_map.add_object(monster)
        return monster
    return None


def spawn_monster_inventory(proto):
    result = []
    if proto:
        for slot in proto:
            equip = random_choice(slot)
            if equip != 'none':
                result.append(create_item(equip, material=loot.choose_material(-10), quality=loot.choose_quality(-10)))
    return result


def create_ability(name):
    if name in abilities.data:
        a = abilities.data[name]
        return abilities.Ability(a.get('name'), a.get('description'), a['function'], a.get('cooldown'))
    else:
        return None


def create_item(name, material=None, quality=None):
    p = loot.proto[name]
    ability = None
    if p.get('ability') is not None and p.get('ability') in abilities.data:
        ability = create_ability(p.get('ability'))
    item_component = Item(category=p['category'], use_function=p.get('on_use'), type=p['type'], ability=ability)
    equipment_component = None
    if p['category'] == 'weapon' or p['category'] == 'armor' or p['category'] == 'book':
        equipment_component = Equipment(
            slot=p['slot'],
            category=p['category'],
            attack_damage_bonus=p.get('attack_damage_bonus', 0),
            armor_bonus=p.get('armor_bonus', 0),
            max_hp_bonus=p.get('max_hp_bonus', 0),
            evasion_bonus=p.get('evasion_bonus', 0),
            spell_power_bonus=p.get('spell_power_bonus', 0),
            stamina_cost=p.get('stamina_cost', 0),
            str_requirement=p.get('str_requirement', 0),
            shred_bonus=p.get('shred', 0),
            guaranteed_shred_bonus=p.get('guaranteed_shred', 0),
            pierce=p.get('pierce', 0),
            accuracy=p.get('accuracy', 0),
            ctrl_attack=p.get('ctrl_attack'),
            ctrl_attack_desc=p.get('ctrl_attack_desc'),
            break_chance=p.get('break', 0),
            weapon_dice=p.get('weapon_dice'),
            str_dice=p.get('str_dice', 0),
            on_hit=p.get('on_hit',[]),
            damage_type=p.get('damage_type'),
            attack_speed_bonus=p.get('attack_speed_bonus', 0),
            attack_delay=p.get('attack_delay', 0),
            essence=p.get('essence'),
            spell_list=p.get('spells'),
            level_progression=p.get('levels'),
            level_costs=p.get('level_costs'),
            crit_bonus=p.get('crit_bonus',1.0),
            resistances=p.get('resistances',[]),
            subtype=p.get('subtype'),
            starting_level=p.get('level',0)
        )

        if equipment_component.category == 'weapon':
            equipment_component.base_id = name
            # Material/Quality
            if material is None:
                material = random_choice(
                    {
                        'wooden' : 10,
                        'bronze' : 15,
                        'iron' : 65,
                        'steel' : 10,
                        'crystal' : 1,
                        'meteor' : 1,
                        'blightstone' : 1,
                     }
                )
            equipment_component.material = material
            equipment_component.attack_damage_bonus += loot.weapon_materials[material]['dmg']
            equipment_component.accuracy_bonus += loot.weapon_materials[material]['acc']
            equipment_component.shred_bonus += loot.weapon_materials[material].get('shred', 0)
            equipment_component.pierce_bonus += loot.weapon_materials[material].get('pierce', 0)
            equipment_component.guaranteed_shred_bonus += loot.weapon_materials[material].get('autoshred', 0)
            equipment_component.break_chance += loot.weapon_materials[material].get('break', 0.0)
            if quality is None:
                quality = random_choice(
                    {
                        'broken' : 5,
                        'crude' : 5,
                        '' : 75,
                        'military' : 10,
                        'fine' : 10,
                        'masterwork' : 5,
                        'artifact' : 1,
                     }
                )
            equipment_component.quality = quality
            equipment_component.attack_damage_bonus += loot.weapon_qualities[quality]['dmg']
            equipment_component.accuracy_bonus += loot.weapon_qualities[quality]['acc']
            equipment_component.shred_bonus += loot.weapon_qualities[quality].get('shred', 0)
            equipment_component.pierce_bonus += loot.weapon_qualities[quality].get('pierce', 0)
            equipment_component.guaranteed_shred_bonus += loot.weapon_qualities[quality].get('autoshred', 0)
            equipment_component.break_chance += loot.weapon_qualities[quality].get('break', 0.0)

    go = GameObject(0, 0, p['char'], p['name'], p.get('color', libtcod.white), item=item_component,
                      equipment=equipment_component, always_visible=True, description=p.get('description'))
    if ability is not None:
        go.item.ability = ability
    if hasattr(equipment_component, 'material'):
        go.name = equipment_component.material + ' ' + go.name
    if hasattr(equipment_component, 'quality') and equipment_component.quality != '':
        go.name = equipment_component.quality + ' ' + go.name
    go.name = go.name.title()
    return go


def spawn_item(name, x, y, material=None, quality=None):
        item = create_item(name, material, quality)
        item.x = x
        item.y = y
        current_map.add_object(item)
        item.send_to_back()


def set_quality(equipment, quality):
    # set to default
    p = loot.proto[equipment.base_id]
    equipment.attack_damage_bonus = p.get('attack_damage_bonus', 0)
    equipment.accuracy_bonus = p.get('accuracy', 0)
    equipment.shred_bonus = p.get('shred', 0)
    equipment.pierce_bonus = p.get('pierce', 0)
    equipment.guaranteed_shred_bonus = p.get('guaranteed_shred', 0)
    equipment.break_chance = p.get('break', 0)
    equipment.owner.name = p['name']
    # assign quality
    equipment.quality = quality
    equipment.attack_damage_bonus += loot.weapon_qualities[quality]['dmg']
    equipment.accuracy_bonus += loot.weapon_qualities[quality]['acc']
    equipment.shred_bonus += loot.weapon_qualities[quality].get('shred', 0)
    equipment.pierce_bonus += loot.weapon_qualities[quality].get('pierce', 0)
    equipment.guaranteed_shred_bonus += loot.weapon_qualities[quality].get('autoshred', 0)
    equipment.break_chance = loot.weapon_qualities[quality].get('break', 0.0)
    # update name
    go = equipment.owner
    if hasattr(equipment, 'material'):
        go.name = equipment.material + ' ' + go.name
    if hasattr(equipment, 'quality') and equipment.quality != '':
        go.name = equipment.quality + ' ' + go.name
    go.name = go.name.title()


def check_breakage(equipment):
    if equipment.break_chance and equipment.break_chance > 0.0:
        roll = libtcod.random_get_double(0, 0, 1.0)
        roll *= 100.0
        if roll < equipment.break_chance:
            # broken!
            ui.message('The ' + equipment.owner.name + ' breaks!', libtcod.white)
            set_quality(equipment, 'broken')
            return True
        else:
            return False
    else:
        return False

def create_fire(x,y,temp):
    global changed_tiles

    tile = current_map.tiles[x][y]
    if tile.is_water or (tile.blocks and not tile.flammable):
        return
    component = ai.FireBehavior(temp)
    obj = GameObject(x,y,libtcod.CHAR_ARROW2_N,'Fire',libtcod.red,misc=component)
    current_map.add_object(obj)
    if temp > 4:
        if tile.is_ramp:
            scorch = 'scorched ramp'
        else:
            scorch = 'scorched floor'
        if tile.blocks:
            fov.set_fov_properties(x, y, False)
        current_map.tiles[x][y].tile_type = scorch
    for obj in get_objects(x, y, condition=lambda o: o.burns):
        obj.destroy()
    changed_tiles.append((x, y))

def door_interact(door):
    if not is_blocked(door.x, door.y):
        if door.closed:
            door.closed = False
            door.blocks_sight = False
            door.background_color = None
        else:
            door.closed = True
            door.blocks_sight = True
            door.background_color = libtcod.sepia
        changed_tiles.append((door.x, door.y))
        fov.set_fov_properties(door.x, door.y, door.blocks_sight, door.elevation)
        return 'interacted-door'
    ui.message('Something is blocking the door.')
    return 'didnt-take-turn'


def unpack_dice(dice, normalize_size=None):
    c = 0
    if '+' in dice:
        dice, c = dice.split('+')

    a, b = dice.split('d')
    flat_bonus = int(c)

    if normalize_size is None:
        dice_count = int(a)
        dice_size = int(b)
        remainder = 0
    else:
        dice_count = int(a) * (int(b) / normalize_size)
        dice_size = normalize_size
        remainder = int(b) % normalize_size
    return dice_count, dice_size, remainder, flat_bonus


def roll_dice(dice, normalize_size=None):
    dice_count, dice_size, remainder, flat_bonus = unpack_dice(dice, normalize_size)

    r = 0
    for i in range(dice_count):
        r += libtcod.random_get_int(0,1,dice_size)
    if remainder > 0:
        r += libtcod.random_get_int(0, 1, remainder)
    return r + flat_bonus


def dice_range(dice, normalize_size=None):
    dice_count, dice_size, remainder, flat_bonus = unpack_dice(dice, normalize_size)

    remainder_min = 0
    if remainder > 0:
        remainder_min = 1

    return dice_count + remainder_min + flat_bonus, dice_count * dice_size + remainder + flat_bonus


def find_closest_open_tile(x, y, exclude=[]):
    if in_bounds(x, y) and not is_blocked(x, y) and len(exclude) == 0:
        return x, y
    explored = [(x, y)]
    neighbors = [(x, y)]
    for tile in adjacent_tiles_diagonal(x, y):
        neighbors.append(tile)
    while len(neighbors) > 0:
        tile = neighbors[0]
        if in_bounds(tile[0], tile[1]) and not is_blocked(tile[0], tile[1]) and tile not in exclude:
            return tile  # we found an open tile
        neighbors.remove(tile)
        explored.append(tile)
        for n in adjacent_tiles_diagonal(tile[0], tile[1]):
            if n not in explored and n not in neighbors:
                neighbors.append(n)
    return None  # failure

def place_objects(tiles,encounter_count=1, loot_count=1, xp_count=1):
    if len(tiles) == 0:
        return

    branch = dungeon.branches[current_map.branch]
    monsters_set = branch.get('monsters')
    if monsters_set is not None:
        for i in range(encounter_count):
            encounter_roll = roll_dice('1d' + str(branch['encounter_range'] + current_map.difficulty))
            if roll_dice('1d10') == 10:  # Crit the encounter table, roll to confirm
                encounter_roll = libtcod.random_get_int(0, encounter_roll, len(monsters_set)) - 1
            encounter_roll = min(encounter_roll, len(monsters_set) - 1)
            encounter = monsters_set[encounter_roll]
            size = 1
            random_pos = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]

            if encounter.get('party') is not None:
                size = roll_dice(encounter['party'])

            for i in range(size):
                loc = find_closest_open_tile(random_pos[0],random_pos[1])
                if loc is not None and loc in tiles:
                    spawn_monster(encounter['encounter'][libtcod.random_get_int(0,0,len(encounter['encounter'])-1)], loc[0], loc[1])
                    tiles.remove(loc)
                    if len(tiles) == 0:
                        return


    for i in range(loot_count):
        random_pos = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]

        if not is_blocked(random_pos[0], random_pos[1]):
            item = loot.item_from_table(current_map.branch)
            if item is not None:
                item.x = random_pos[0]
                item.y = random_pos[1]
                current_map.add_object(item)
                item.send_to_back()
                tiles.remove(random_pos)
                if len(tiles) == 0:
                    return

    for x in range(xp_count):
        for i in range(2):
            random_pos = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]
            current_map.add_object(GameObject(random_pos[0], random_pos[1], 7, 'xp', libtcod.lightest_blue, always_visible=True,
                                      description='xp', on_step= player.pick_up_xp))
            tiles.remove(random_pos)
            if len(tiles) == 0:
                return


def check_boss(level):
    global spawned_bosses

    #for (k, v) in dungeon.bosses.items():
    #    chance = v.get(level)
    #    if chance is not None and spawned_bosses.get(k) is None:
    #        if chance >= libtcod.random_get_int(0, 0, 100):
    #            spawned_bosses[k] = True
    #            return k
    return None


def get_dungeon_level():
    global dungeon_level
    return "dungeon_{}".format(dungeon_level)

def get_loot(monster):
    loot_table = monster.loot_table
    drop = loot_table[libtcod.random_get_int(0,0,len(loot_table) - 1)]
    if drop:
        proto = loot.proto[drop]
        item = Item(category=proto['category'], use_function=proto['on_use'], type=proto['type'])
        return GameObject(monster.owner.x, monster.owner.y, proto['char'], proto['name'], proto['color'], item=item)

def get_objects(x, y, condition=None, distance=0):
    found = []
    for obj in current_map.objects:
        if max(abs(obj.x - x), abs(obj.y - y)) <= distance:
            if condition is not None:
                if condition(obj):
                    found.append(obj)
            else:
                found.append(obj)
    return found

def get_description(obj):
    if obj and hasattr(obj, 'description') and obj.description is not None:
        return obj.description.capitalize()
    else:
        return ""


def land_next_to_target(target_x, target_y, source_x, source_y):
    if abs(target_x - source_x) <= 1 and abs(target_y - source_y) <= 1:
        return source_x, source_y  # trivial case - if we are adjacent we don't need to move
    b = beam(source_x, source_y, target_x, target_y)
    land_x = b[len(b) - 2][0]
    land_y = b[len(b) - 2][1]
    if not is_blocked(land_x, land_y):
        return land_x, land_y
    return None

def clear_map():
    libtcod.console_set_default_background(map_con, libtcod.black)
    libtcod.console_set_default_foreground(map_con, libtcod.black)
    libtcod.console_clear(map_con)


def render_map():
    global changed_tiles, visible_tiles

    if fov.fov_recompute:
        fov.fov_recompute = False
        libtcod.map_compute_fov(fov.fov_player, player.instance.x, player.instance.y, consts.TORCH_RADIUS, consts.FOV_LIGHT_WALLS, consts.FOV_ALGO)
        fov.player_fov_calculated = True
        new_visible = []
        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):
                if libtcod.map_is_in_fov(fov.fov_player, x, y):
                    new_visible.append((x, y))
        for tile in new_visible:
            if tile not in visible_tiles:
                changed_tiles.append(tile)
        for tile in visible_tiles:
            if tile not in new_visible:
                changed_tiles.append(tile)
        visible_tiles = new_visible

    for tile in changed_tiles:
        x = tile[0]
        y = tile[1]
        visible = libtcod.map_is_in_fov(fov.fov_player, x, y)
        color_fg = libtcod.Color(current_map.tiles[x][y].color_fg[0], current_map.tiles[x][y].color_fg[1],
                                 current_map.tiles[x][y].color_fg[2])
        color_bg = libtcod.Color(current_map.tiles[x][y].color_bg[0], current_map.tiles[x][y].color_bg[1],
                                 current_map.tiles[x][y].color_bg[2])
        tint = clamp(1.0 + 0.25 * float(current_map.tiles[x][y].elevation), 0.1, 2.0)
        libtcod.color_scale_HSV(color_fg, 1.0, tint)
        libtcod.color_scale_HSV(color_bg, 1.0, tint)
        if not visible:
            if current_map.tiles[x][y].explored:
                libtcod.color_scale_HSV(color_fg, 0.1, 0.4)
                libtcod.color_scale_HSV(color_bg, 0.1, 0.4)
                libtcod.console_put_char_ex(map_con, x, y, current_map.tiles[x][y].tile_char, color_fg, color_bg)
            else:
                libtcod.console_put_char_ex(map_con, x, y, ' ', libtcod.black, libtcod.black)
        else:
            libtcod.console_put_char_ex(map_con, x, y, current_map.tiles[x][y].tile_char, color_fg, color_bg)
            current_map.tiles[x][y].explored = True

    changed_tiles = []

    for obj in current_map.objects:
        if obj is not player.instance:
            obj.draw(map_con)
    player.instance.draw(map_con)

    libtcod.console_blit(map_con, player.instance.x - consts.MAP_VIEWPORT_WIDTH / 2, player.instance.y - consts.MAP_VIEWPORT_HEIGHT / 2,
                consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT, 0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y)
    ui.draw_border(0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT)


def render_all():

    if not in_game:
        render_main_menu_splash()
        return

    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_clear(0)

    render_map()

    ui.render_side_panel()

    ui.render_message_panel()

    ui.render_action_panel()

    ui.render_ui_overlay()


def render_main_menu_splash():
    img = libtcod.image_load('menu_background.png')
    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_clear(0)
    libtcod.image_blit_2x(img, 0, 0, 0)
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT / 2 - 8, libtcod.BKGND_NONE,
                             libtcod.CENTER,
                             'MAGIC-ROGUELIKE')
    libtcod.console_print_ex(0, consts.SCREEN_WIDTH / 2, consts.SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, libtcod.CENTER,
                             'by Tyler Soberanis and Adrien Young')


def use_stairs(stairs):
    import world
    next_map = stairs.link[1]
    current_map.pathfinding = None
    enter_map(next_map, world.opposite(stairs.link[0]))


def enter_map(world_map, direction=None):
    global current_map

    if current_map is not None:
        clear_map()
        libtcod.console_blit(map_con, 0, 0, consts.MAP_WIDTH, consts.MAP_HEIGHT, 0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y)
        libtcod.console_blit(map_con, 0, 0, consts.MAP_WIDTH, consts.MAP_HEIGHT, 0, consts.SCREEN_WIDTH - consts.MAP_WIDTH, consts.MAP_VIEWPORT_Y)
        libtcod.console_set_default_foreground(map_con, libtcod.white)
        if world_map.tiles is None:
            load_string = 'Generating...'
        else:
            load_string = 'Loading...'
        libtcod.console_print(map_con, 0, 0, load_string)
        libtcod.console_blit(map_con, 0, 0, len(load_string), 1, 0, consts.MAP_VIEWPORT_X + 4, consts.MAP_VIEWPORT_Y + 4)
        ui.draw_border(0, consts.MAP_VIEWPORT_X, consts.MAP_VIEWPORT_Y, consts.MAP_VIEWPORT_WIDTH, consts.MAP_VIEWPORT_HEIGHT)

        libtcod.console_flush()

    current_map = world_map

    if world_map.tiles is None:
        generate_level(world_map)

    current_map.pathfinding = pathfinding.Graph()
    current_map.pathfinding.initialize()

    if direction is not None:
        for obj in current_map.objects:
            if hasattr(obj, 'link') and obj.link[0] == direction:
                player.instance.x = obj.x
                player.instance.y = obj.y
                player.instance.elevation = current_map.tiles[obj.x][obj.y].elevation

    fov.initialize_fov()

    ui.display_fading_text(dungeon.branches[current_map.branch]['name'].title(), 60, 20)


def generate_level(world_map):
    global spawned_bosses
    mapgen.make_map(world_map)


#############################################
# Initialization & Main Loop
#############################################

def main_menu():
    mapgen.load_features_from_file('features.txt')

    while not libtcod.console_is_window_closed():
        render_main_menu_splash()

        choice = ui.menu('', ['NEW GAME', 'CONTINUE', 'QUIT'], 24, x_center=consts.SCREEN_WIDTH / 2)
        
        if choice == 0: #new game
            if new_game() != 'cancelled':
                play_game()
        elif choice == 1:
            try:
                load_game()
            except:
                ui.msgbox('\n No saved game to load.\n', 24)
                continue
            play_game()
        elif choice == 2:
            print('Quitting game...')
            return


def new_game():
    global game_state, dungeon_level, memory, in_game, changed_tiles, learned_skills, current_map

    confirm = False
    loadout = None
    current_map = None

    while not confirm:
        options = list(player.loadouts.keys())
        choice = ui.menu('Select your starting class',options,36,x_center=consts.SCREEN_WIDTH / 2)
        if choice is None:
            return 'cancelled'
        loadout = options[choice]
        confirm = ui.menu('Confirm starting as ' + loadout.title() + ":\n\n" + player.loadouts[loadout]['description'],
                          ['Start','Back'],36,x_center=consts.SCREEN_WIDTH / 2) == 0

    in_game = True
    player.create(loadout)
    ui.selected_monster = None

    import world
    world.initialize_world()
    
    # generate map
    dungeon_level = 1

    if consts.DEBUG_STARTING_MAP is not None:
        enter_map(world.world_maps[consts.DEBUG_STARTING_MAP])
    else:
        enter_map(world.world_maps['beach'])

    # initialize_fov()
    game_state = 'playing'

    memory = []
    learned_skills = []

    ui.message('Welcome to the dungeon...', libtcod.gold)

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))


def save_game():
    pass
    #file = shelve.open('savegame', 'n')
    #file['map'] = dungeon_map
    #file['objects'] = objects
    #file['player_index'] = objects.index(player)
    #file['stairs_index'] = objects.index(stairs)
    #file['memory'] = memory
    #file['game_msgs'] = ui.game_msgs
    #file['game_state'] = game_state
    #file['dungeon_level'] = dungeon_level
    #file['learned_skills'] = learned_skills
    #file.close()


def load_game():
    pass
    #global dungeon_map, objects, player, memory, game_state, dungeon_level, stairs, in_game, selected_monster, learned_skills

    #in_game = True

    #file = shelve.open('savegame', 'r')
    #dungeon_map = file['map']
    #objects = file['objects']
    #player = objects[file['player_index']]
    #stairs = objects[file['stairs_index']]
    #memory = file['memory']
    #ui.game_msgs = file['game_msgs']
    #game_state = file['game_state']
    #dungeon_level = file['dungeon_level']
    #selected_monster = None
    #learned_skills = file['learned_skills']
    #file.close()

    #current_map.pathfinding.initialize(dungeon_map)
    #fov.initialize_fov()

    #for y in range(consts.MAP_HEIGHT):
    #    for x in range(consts.MAP_WIDTH):
    #        changed_tiles.append((x, y))


def play_game():
    global key, mouse, game_state, in_game
    
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():

        # render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
        render_all()
        libtcod.console_flush()

        # handle keys and exit game if needed
        player_action = player.handle_keys()
        if player_action == 'exit':
            save_game()
            in_game = False
            break

        if consts.RENDER_EVERY_TURN:
            render_all()
            libtcod.console_flush()

        # Let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            player.instance.on_tick(object=player.instance)
            for object in current_map.objects:
                if object.behavior:
                    object.behavior.take_turn()
                if object is not player.instance:
                    object.on_tick(object=object)

        # Handle auto-targeting
        ui.auto_target_monster()


# my modules
import actions
import loot
import spells
import monsters
import dungeon
import mapgen
import abilities
import effects
import pathfinding
import fov
import ui
import ai
import player
import combat
import terrain

# Globals

# Libtcod initialization
libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT, 'Magic Roguelike', False)
libtcod.sys_set_fps(consts.LIMIT_FPS)

# Consoles
con = libtcod.console_new(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
map_con = libtcod.console_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)

# Flags
in_game = False

# Graphics
changed_tiles = []
visible_tiles = []

# Level
current_map = None
