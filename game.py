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

import math
import string
import sys

import consts
import libtcodpy as libtcod
import log
import syntax
import shelve
import traceback
from collections import deque

#############################################
# Classes
#############################################

class Light:
    def __init__(self, color, power, radius):
        self.color = color
        self.power = power
        self.radius = radius

class Item:
    def __init__(self, category, use_function=None, type='item', ability=None, holder=None, charges=None):
        self.category = category
        self.use_function = use_function
        self.type = type
        self.ability = ability
        self.holder = holder
        self.charges = charges
        self.inventory_index = None

    def pick_up(self, actor, no_message=False):
        if self.type == 'item':
            if len(actor.fighter.inventory) >= 26:
                if actor is player.instance:
                    ui.message('Your inventory is too full to pick up the ' + self.owner.name)
            else:
                index = ord('a')
                while chr(index) in [i.item.inventory_index for i in actor.fighter.inventory]:
                    index += 1
                self.inventory_index = chr(index)
                self.holder = actor
                actor.fighter.inventory.append(self.owner)
                self.owner.destroy()
                if actor is player.instance and not no_message:
                    ui.message('You picked up a ' + string.capwords(self.owner.name) + '.', libtcod.light_grey)
                eq = self.owner.equipment
                if eq and (get_equipped_in_slot(actor.fighter.inventory,eq.slot) is None or
                          eq.slot == 'ring' and len(get_equipped_in_slot(actor.fighter.inventory, 'ring')) < 2):
                    eq.equip(no_message)

    def use(self):
        if self.owner.equipment:
            return self.owner.equipment.toggle()
        elif self.use_function is not None:
            if self.use_function() != 'cancelled':
                if self.type == 'item' and not(self.category == 'gem' and consts.DEBUG_INFINITE_GEMS):
                    if self.category == 'charm':
                        if self.charges is not None and not consts.DEBUG_INFINITE_GEMS:
                            self.charges -= 1
                            if self.charges <= 0:
                                self.holder.fighter.inventory.remove(self.owner)
                                ui.message('The %s crumbles to dust, its energy spent.' % self.owner.name, libtcod.gray)
                    else:
                        self.holder.fighter.inventory.remove(self.owner)
            else:
                return 'cancelled'
        elif self.holder is player.instance:
            ui.message('The ' + self.owner.name + ' cannot be used.')


    def drop(self, no_message=False):
        if self.holder is None:
            return
        if self.owner not in self.holder.fighter.inventory:
            return
        if self.owner.equipment:
            if self.owner.equipment.dequip(no_message=no_message) == 'cancelled':
                return 'cancelled'
        current_map.add_object(self.owner)
        self.holder.fighter.inventory.remove(self.owner)
        self.owner.x = self.holder.x
        self.owner.y = self.holder.y
        self.inventory_index = None
        if not no_message and self.holder is player.instance:
            ui.message('You dropped a ' + string.capwords(self.owner.name) + '.', libtcod.white)
        self.holder = None

    def get_options_list(self):
        options = []
        if self.use_function is not None:
            options.append('Use')
        if self.owner.equipment:
            if self.owner.equipment.is_equipped:
                options.append('Unequip')
            else:
                options.append('Equip')
            if self.owner.equipment.level_progression and self.owner.equipment.level < len(self.owner.equipment.level_costs):
                cost = self.owner.equipment.level_costs[self.owner.equipment.level]
                options.append('Imbue ' + ('*') * cost)
        options.append('Drop')
        return options

    def print_description(self, console, x, y, width):
        print_height = 0

        if self.owner.equipment:
            print_height += self.owner.equipment.print_description(console, x, y + print_height, width)
        if self.category == 'charm':
            print_height += charms.print_charm_description(self, console, x, y + print_height, width)

        return print_height

class Zone:
    def __init__(self,radius,on_enter = None,on_tick = None):
        self.radius = radius
        self.on_enter = on_enter
        self.on_tick = on_tick
        self.influence = []
        self.owner = None

    def tick(self):
        current = []
        for f in current_map.fighters:
            if f is self.owner:
                continue
            deltax = abs(f.x - self.owner.x)
            deltay = abs(f.y - self.owner.y)
            if deltax <= self.radius and deltay <= self.radius:
                if f not in self.influence and self.on_enter is not None:
                    self.on_enter(self.owner,f)
                current.append(f)
                if self.on_tick is not None:
                    self.on_tick(self.owner,f)
        self.influence = [f for f in self.influence if f in current]

class Ticker:
    def __init__(self,max_ticks,on_tick):
        self.ticks = 0
        self.on_tick = on_tick
        self.max_ticks = max_ticks

class GameObject:

    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, behavior=None, item=None, equipment=None,
                 player_stats=None, always_visible=False, interact=None, description="", on_create=None,
                 update_speed=1.0, misc=None, blocks_sight=False, on_step=None, burns=False, on_tick=None,
                 elevation=None, background_color=None, movement_type=0, summon_time = None, zones=[], is_corpse=False,
                 zombie_type=None, npc=None, light=None, stealth=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.always_visible = always_visible
        self.interact = interact
        self.player_adjacent = False
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
        self._movement_type = movement_type
        self.summon_time = summon_time
        self.zones = []
        for z in zones:
            self.add_zone(z)
        self.is_corpse = is_corpse
        self.zombie_type = zombie_type
        self.npc = npc
        if self.npc:
            self.npc.owner = self
        self.light = light
        self.stealth = stealth

    @property
    def movement_type(self):
        if self.fighter is not None and self.fighter.has_status('levitating'):
            return pathfinding.FLYING
        return self._movement_type

    def change_behavior(self,behavior):
        self.behavior.behavior = behavior
        self.behavior.owner = self
        self.behavior.behavior.owner = self

    def print_description(self, console, x, y, width):
        height = libtcod.console_get_height_rect(console, x, y, width, SCREEN_HEIGHT(), self.description)
        draw_height = y
        if self.description is None:
            self.description = ''
        libtcod.console_print_rect(console, x, draw_height, width, height, self.description)
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
        #if old_x == x and old_y == y:
        #    return

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

        # Check terrain
        if self.fighter and self.movement_type & pathfinding.FLYING != pathfinding.FLYING:
            if current_map.tiles[self.x][self.y].tile_type == 'mud' and not self.fighter.has_status('sluggish'):
                self.fighter.apply_status_effect(effects.sluggish(None), dc=None, supress_message=True)
            elif current_map.tiles[self.x][self.y].tile_type != 'mud' and self.fighter.has_status('sluggish'):
                self.fighter.remove_status('sluggish')

        if self is player.instance and has_skill('aquatic'):
            if current_map.tiles[self.x][self.y].is_water and not self.fighter.has_status('agile'):
                self.fighter.apply_status_effect(effects.agile(None))
            elif not current_map.tiles[self.x][self.y].is_water and self.fighter.has_status('agile'):
                self.fighter.remove_status('agile')

        if self.movement_type & pathfinding.FLYING != pathfinding.FLYING:
            if current_map.tiles[self.x][self.y].is_pit:
                fall_in_pit(self)

        # If the player moved, recalculate field of view, checking for elevation changes
        if self is player.instance:
            if old_elev != self.elevation:
                fov.set_view_elevation(self.elevation)
            fov.set_fov_recompute()
        else:
            #if it's a monster, track if it was next to the player last turn and check perks
            if is_adjacent_diagonal(self.x,self.y,player.instance.x,player.instance.y):
                if has_skill('vanguard') and not self.player_adjacent:
                    player.instance.fighter.attack(self)
                self.player_adjacent = True
            else:
                self.player_adjacent = False

    def swap_positions(self, target):
        target_pos = target.x, target.y
        target.set_position(self.x, self.y)
        value = self.move(target_pos[0] - self.x, target_pos[1] - self.y)
        if not value:
            target.set_position(target_pos[0], target_pos[1])
        return value

    def move(self, dx, dy):

        if dx == 0 and dy == 0:
            return False

        x,y = self.x + dx, self.y + dy
        blocked = is_blocked(x,y, from_coord=(self.x, self.y), movement_type=self.movement_type, is_player=self is player.instance)

        if not blocked:
            if self.fighter is not None:
                if self.fighter.has_status('immobilized'):
                    if self is player.instance:
                        ui.message('You cannot move!', libtcod.yellow)
                        return False
                    else:
                        return True
                web = object_at_tile(self.x, self.y, 'spiderweb')
                if web is not None and not (self.fighter and (self.fighter.has_flag(monsters.WEB_IMMUNE) or
                                                  self.fighter.has_item_with_attribute('web_immune'))):
                    ui.message('%s %s against the web' % (
                                    syntax.name(self).capitalize(),
                                    syntax.conjugate(self is player.instance, ('struggle', 'struggles'))))
                    web.destroy()
                    return True

                door = object_at_tile(x,y, 'door')
                if door is None: door = object_at_tile(x, y, 'locked door')
                if door is not None and door.closed:
                    door_interact(door, self)
                    return True

                if self is player.instance:
                    if current_map.tiles[x][y].tile_type == 'lava' and \
                            not 'fire' in self.fighter.immunities and \
                            current_map.tiles[self.x][self.y].tile_type != 'lava':
                        if not ui.menu_y_n('Really walk into lava?'):
                            return False

                    fire = object_at_tile(x, y, 'Fire')
                    if fire is not None and not 'fire' in self.fighter.immunities and not has_skill('pyromaniac'):
                        old_fire = object_at_tile(self.x, self.y, 'Fire')
                        if old_fire is None:
                            if not ui.menu_y_n('Really walk into flame?'):
                                return False

                cost = current_map.tiles[self.x][self.y].stamina_cost
                swim = current_map.tiles[self.x][self.y].is_water \
                        and (self.movement_type & pathfinding.AQUATIC == pathfinding.AQUATIC)

                if cost > 0 and self is player.instance\
                        and self.movement_type & pathfinding.FLYING != pathfinding.FLYING \
                        and not swim:
                    if self.fighter.stamina >= cost:
                        self.fighter.adjust_stamina(-cost)
                    else:
                        ui.message("You don't have the stamina leave this space!", libtcod.light_yellow)
                        return False
                else:
                    self.fighter.adjust_stamina(consts.STAMINA_REGEN_MOVE)     # gain stamina for moving across normal terrain

                if current_map.tiles[x][y].on_step is not None:
                    current_map.tiles[x][y].on_step(x,y,self)

                # grab ammo
                if self.fighter and self is player.instance:
                    ammo_objs = get_objects(x, y, lambda o: o.name == 'ammo')
                    for ammo_obj in ammo_objs:
                        ammo_obj.recoverable_ammo -= self.fighter.adjust_ammo(ammo_obj.recoverable_ammo, True)
                        if ammo_obj.recoverable_ammo == 0:
                            ammo_obj.destroy()

                if self.light is not None:
                    for _x in range(max(0, self.x - self.light.radius), min(consts.MAP_WIDTH, self.x + self.light.radius + 1)):
                        for _y in range(max(0, self.y - self.light.radius),
                                       min(consts.MAP_WIDTH, self.y + self.light.radius + 1)):
                            changed_tiles.append((_x,_y))

            self.set_position(x,y)

            return True
        else:
            interactables = get_objects(x, y, lambda o: hasattr(o, 'interact') and o.interact and o.blocks)
            if len(interactables) > 0:
                interactables[0].interact(interactables[0], self)
                return True
            return False

    def player_can_see(self):
        if self.fighter is not None:
            s = self.fighter.stealth
        else:
            s = self.stealth
        if s is not None and player.instance.distance_to(self) >= s:
            return False
        else:
            return fov.player_can_see(self.x, self.y)

    def draw(self, console):
        if self.player_can_see():
            if ui.selected_monster is self:
                libtcod.console_put_char_ex(console, self.x, self.y, self.char, libtcod.black, self.color)
            else:
                if self.background_color is None:
                    libtcod.console_set_default_foreground(console, self.color)
                    libtcod.console_put_char(console, self.x, self.y, self.char, libtcod.BKGND_NONE)
                else:
                    libtcod.console_put_char_ex(console, self.x, self.y, self.char, self.color, self.background_color)
        elif self.always_visible and current_map.tiles[self.x][self.y].explored and self.stealth is None:
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
        log.info('PATH',"{} moving to space ({},{})",[self.name,self.x + dx, self.y + dy])
        self.move(dx, dy)

    def move_astar(self, target_x, target_y):
        if self.x == target_x and self.y == target_y:
            return 'already here'

        if not current_map.pathfinding:
            self.move_astar_old(target_x, target_y)
            return 'no map'
        else:
            movement_type = self.movement_type
            if self.fighter and 'fire' in self.fighter.immunities:
                movement_type |= pathfinding.LAVA

            if not current_map.pathfinding.is_accessible((target_x, target_y)):
                closest_adjacent = None
                closest = 10000
                for adj in adjacent_tiles_diagonal(target_x, target_y):
                    if is_blocked(adj[0], adj[1], from_coord=(target_x, target_y),
                                  movement_type=movement_type, is_player=self is player.instance):
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

            path = current_map.pathfinding.a_star_search((self.x, self.y), (target_x, target_y), movement_type)

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
        return distance(self.x, self.y, other.x, other.y)

    def distance(self, x, y):
        return distance(self.x,self.y,x,y)
        
    def send_to_back(self):
        if self not in current_map.objects:
            return
        current_map.objects.remove(self)
        current_map.objects.insert(0, self)

    def add_zone(self,z):
        self.zones.append(z)
        z.owner = self

    def on_tick(self, object=None):
        if self.summon_time:
            self.summon_time -= 1
            if self.summon_time <= 0:
                if fov.player_can_see(self.x, self.y):
                    ui.message('%s fades away as %s returns to the world from whence %s came.' %
                               (syntax.name(self).capitalize(),
                                syntax.pronoun(self),
                                syntax.pronoun(self)), libtcod.gray)
                self.destroy()
                return
        if self.on_tick_specified:
            self.on_tick_specified(object)
        if self.fighter:
            self.fighter.on_tick()
        if self.misc and hasattr(self.misc, 'on_tick'):
            self.misc.on_tick(object)
        for z in self.zones:
            z.tick()

    def destroy(self):
        global changed_tiles
        if current_map is None:
            return
        if self.blocks_sight:
            fov.set_fov_properties(self.x, self.y, current_map.tiles[self.x][self.y].blocks_sight, self.elevation)
        if self.blocks and current_map.pathfinding:
            current_map.pathfinding.mark_unblocked((self.x, self.y))
        changed_tiles.append((self.x, self.y))
        if self in current_map.fighters:
            current_map.fighters.remove(self)
        if self in current_map.objects:
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
        if self.flags & terrain.FLAG_NO_DIG == terrain.FLAG_NO_DIG:
            return 0
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
    def is_ice(self):
        return terrain.data[self.tile_type].isIce

    @property
    def on_step(self):
        return terrain.data[self.tile_type].on_step

    @property
    def is_dangerous(self):
        return terrain.data[self.tile_type].dangerous

    @property
    def blocks_sight_all_elevs(self):
        return terrain.data[self.tile_type].blocks_sight_all_elevs

                
#############################################
# General Functions
#############################################

def get_path_to_point(start, end, movement_type=0, max_edges=-1):
    if current_map is None or current_map.pathfinding is None:
        return None
    if max_edges == -1:
        path = current_map.pathfinding.a_star_search(start, end, movement_type=movement_type)
    else:
        path = current_map.pathfinding.a_star_search(start, end, movement_type=movement_type, max_edges=max_edges)
    if path == 'failure' or len(path) == 0:
        return None
    return path

def has_skill(name):
    for skill in learned_skills.keys():
        if skill == name:
            if learned_skills[skill] > 0:
                return learned_skills[skill]
            else:
                return 1
    return 0

def skill_value(name):
    import perks
    v = has_skill(name)
    if v > 0:
        return perks.perk_list[name]['values'][v - 1]
    else:
        return 0

def expire_out_of_vision(obj):
    if not fov.player_can_see(obj.x, obj.y):
        obj.destroy()

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

def adjacent_inclusive(x,y):
    result = adjacent_tiles_diagonal(x,y)
    result.append((x,y))
    return result

def is_adjacent_orthogonal(a_x, a_y, b_x, b_y):
    return (abs(a_x - b_x) <= 1 and a_y == b_y) or (abs(a_y - b_y) <= 1 and a_x == b_x)


def is_adjacent_diagonal(a_x, a_y, b_x, b_y):
    return abs(a_x - b_x) <= 1 and abs(a_y - b_y) <= 1

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


def scum_glob_tick(glob):
    tile = current_map.tiles[glob.x][glob.y]
    if not tile.is_water and not tile.tile_type == 'oil' and not tile.is_ramp and not tile.is_pit:
        tile.tile_type = 'oil'
        changed_tiles.append((glob.x, glob.y))


def scum_glob_on_create(obj):
    obj.fighter.apply_status_effect(effects.oiled(duration=None))

def lifeplant_pulse(self):
    for obj in current_map.fighters:
        if is_adjacent_diagonal(obj.x, obj.y, self.x, self.y):
            obj.fighter.heal(roll_dice('1d3'))

def bloodfly_on_create(obj):
    obj.fighter.hp = obj.fighter.max_hp / 2


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
    old_web = get_objects(x, y, lambda o: o.name == 'spiderweb')
    if len(old_web) > 0:
        return
    web = GameObject(x, y, 'x', 'spiderweb', libtcod.lightest_gray,
                     description='a web of spider silk. Stepping into a web will impede movement for a turn.',
                     burns=True)
    current_map.add_object(web)
    web.send_to_back()


def raise_dead(actor,target, duration=None):
    if target.fighter is None and target.is_corpse:
        spawn_tile = find_closest_open_tile(target.x, target.y)
        monster = target.zombie_type if target.zombie_type is not None else 'monster_rotting_zombie'
        zombie = spawn_monster(monster, spawn_tile[0], spawn_tile[1])
        zombie.fighter.team = actor.fighter.team
        zombie.behavior.follow_target = actor
        if duration is not None:
            zombie.summon_time = duration
        target.destroy()
        ui.message('A corpse walks again...', libtcod.dark_violet)


def create_temp_terrain(type, tiles, duration, save_old_terrain=False):
    terrain_data = terrain.data[type]
    ticker = Ticker(duration, _temp_terrain_on_tick)
    ticker.restore = []
    ticker.map = current_map

    for (x, y) in tiles:
        # Don't place walls over game objects
        if terrain_data.blocks and len(get_objects(x, y)) > 0:
            continue
        tile = current_map.tiles[x][y]
        if tile.diggable or not tile.is_wall:
            if save_old_terrain:
                ticker.restore.append((x,y,tile.tile_type))
            else:
                ticker.restore.append((x,y,dungeon.branches[current_map.branch]['default_floor']))
            tile.tile_type = type
            changed_tiles.append((x, y))
            if terrain_data.blocks:
                current_map.pathfinding.mark_blocked((x, y))
            else:
                current_map.pathfinding.mark_unblocked((x, y))
            fov.set_fov_properties(x, y, terrain_data.blocks_sight)

    current_map.tickers.append(ticker)


def _temp_terrain_on_tick(ticker):
    if ticker.max_ticks <= ticker.ticks:
        ticker.dead = True
        for x,y,type in ticker.restore:
            terrain_data = terrain.data[type]
            ticker.map.tiles[x][y].tile_type = type
            changed_tiles.append((x, y))
            if terrain_data.blocks:
                current_map.pathfinding.mark_blocked((x, y))
            else:
                current_map.pathfinding.mark_unblocked((x, y))
            fov.set_fov_properties(x, y, terrain_data.blocks_sight)


def get_all_equipped(equipped_list):
    result = []
    for item in equipped_list:
        if item.equipment and item.equipment.is_equipped:
            result.append(item.equipment)
    return result


def get_equipped_in_slot(equipped_list,slot):
    if slot == 'both hands':
        slot = 'right hand'

    if slot == 'ring':
        return [r for r in equipped_list if r.equipment is not None and r.equipment.is_equipped and r.equipment.slot == 'ring']

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


def random_entry(options):
    return options[libtcod.random_get_int(0,0,len(options)-1)]


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

def monster_death(monster, context):
    global changed_tiles

    if hasattr(monster.fighter,'inventory') and len(monster.fighter.inventory) > 0 and monster.summon_time is None:
        for item in monster.fighter.inventory:
            if item.equipment:
                item.equipment.dequip()
            item.x = monster.x
            item.y = monster.y
            current_map.add_object(item)
            item.send_to_back()

    if context.get('suppress_messages', False):
        ui.message('%s is dead!' % syntax.name(monster).capitalize(), libtcod.red)

    # drop ammo
    if hasattr(monster, 'recoverable_ammo'):
        drop_ammo(monster.x, monster.y, monster.recoverable_ammo)
        del monster.recoverable_ammo

    if monster.fighter.has_flag(monsters.NO_CORPSE):
        monster.destroy()
    elif monster.summon_time is not None:
        monster.destroy()
        if context.get('suppress_messages', False):
            ui.message('%s corpse fades back to the world from whence it came.' %
                       syntax.pronoun(monster, possesive=True).capitalize(), libtcod.gray)
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


def drop_ammo(x, y, amount):
    ammo_obj = object_at_tile(x, y, 'ammo')
    if ammo_obj is None:
        ammo_obj = GameObject(x, y, '\\', 'ammo', libtcod.white, stealth=2)
        ammo_obj.recoverable_ammo = amount
        current_map.add_object(ammo_obj)
    else:
        ammo_obj.recoverable_ammo += amount


def target_monster(max_range=None):
    while True:
        (x, y) = ui.target_tile(max_range)
        if x is None:
            return None
        for obj in current_map.fighters:
            if obj.x == x and obj.y == y and obj is not player.instance and obj.player_can_see():
                return obj
        return None


def get_monster_at_tile(x, y):
    for obj in current_map.fighters:
        if obj.x == x and obj.y == y and obj is not player.instance:
            return obj
    return None

def get_fighters_in_burst(x, y, radius, fov_source=None, condition=None):
    return [obj for obj in current_map.fighters if distance(x,y,obj.x,obj.y) < radius + 1 and \
            fov.monster_can_see_object(fov_source,obj) and (condition is None or condition(obj))]

def get_tiles_in_burst(x, y, radius):
    tiles = []
    for _x in range(max(0, x - radius), min(x + radius + 1, consts.MAP_WIDTH)):
        for _y in range(max(0, y - radius), min(y + radius + 1, consts.MAP_HEIGHT)):
            tiles.append((_x,_y))
    return tiles

def get_tiles_in_circular_burst(x, y, radius):
    return [ tile for tile in get_tiles_in_burst(x,y,radius) \
             if distance(tile[0], tile[1], x, y) ]

def opposite_team(team):
    if team == 'ally':
        return 'enemy'
    elif team == 'enemy':
        return 'ally'
    return 'neutral'

def opposite_direction(dir):
    if dir == 'left':
        return 'right'
    elif dir == 'right':
        return 'left'
    elif dir == 'top':
        return 'bottom'
    elif dir == 'bottom':
        return 'top'
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


def beam_interrupt(sourcex, sourcey, destx, desty, ignore_fighters=False, movement_type=2): #movement_type = flying
    libtcod.line_init(sourcex, sourcey, destx, desty)
    line_x, line_y = libtcod.line_step()
    while line_x is not None:
        if is_blocked(line_x, line_y, movement_type=movement_type, ignore_fighters=ignore_fighters):  # beam interrupt scans until it hits something
            return line_x, line_y
        line_x, line_y = libtcod.line_step()
    return destx, desty


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def cone(sourcex,sourcey,destx,desty,max_range):
    affected_tiles = []
    selected_angle = math.atan2(-(desty - sourcey), destx - sourcex)
    if selected_angle < 0: selected_angle += math.pi * 2
    for draw_x in range(max(sourcex - max_range, 0),
                        min(sourcex + max_range, consts.MAP_WIDTH - 1) + 1):
        for draw_y in range(max(sourcey - max_range, 0),
                            min(sourcey + max_range, consts.MAP_HEIGHT - 1) + 1):
            if draw_x == sourcex and draw_y == sourcey:
                continue
            #if not fov.player_can_see(draw_x, draw_y):
            #    continue
            this_angle = math.atan2(-(draw_y - sourcey), draw_x - sourcex)
            if this_angle < 0: this_angle += math.pi * 2
            phi = abs(this_angle - selected_angle)
            if phi > math.pi:
                phi = 2 * math.pi - phi

            if phi <= math.pi / 4 and round(distance(sourcex,sourcey,draw_x, draw_y)) <= max_range:
                affected_tiles.append((draw_x, draw_y))
    return affected_tiles


def closest_monster(max_range):
    closest_enemy = None
    low_priority_enemy = None
    low_priority_dist = max_range + 1
    closest_dist = max_range + 1

    for object in current_map.fighters:
        if object is not player.instance and object.player_can_see() and not (object.npc and object.npc.active):
            dist = player.instance.distance_to(object)
            if object.fighter.has_flag(monsters.LOW_PRIORITY) or object.fighter.team == 'ally':
                if dist < low_priority_dist:
                    low_priority_dist = dist
                    low_priority_enemy = object
            else:
                if dist < closest_dist:
                    closest_dist = dist
                    closest_enemy = object
    if closest_enemy is not None:
        return closest_enemy
    else:
        return low_priority_enemy

def closest_unexplored_tile():
    open = deque()
    open.append((player.instance.x, player.instance.y))
    closed = []
    while len(open) > 0:
        curr = open.popleft()
        for t in adjacent_tiles_diagonal(curr[0], curr[1]):
            if t not in open and t not in closed and is_explorable(curr):
                if current_map.tiles[t[0]][t[1]].explored:
                    open.append(t)
                else:
                    return t
        closed.append(curr)
    return None

def is_explorable(pos):
    blockers = get_objects(pos[0],pos[1], lambda o: (o is not player.instance and o.blocks) or (hasattr(o,'locked') and o.locked))
    tile = current_map.tiles[pos[0]][pos[1]]
    return len(blockers) < 1 and not tile.is_dangerous and not tile.blocks

def in_bounds(x, y):
    return 0 <= x < consts.MAP_WIDTH and 0 <= y < consts.MAP_HEIGHT


def is_blocked(x, y, from_coord=None, movement_type=None, ignore_fighters=False, is_player=False):

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
        elif tile.tile_type == 'lava':
            if not is_player:
                if movement_type & pathfinding.FLYING != pathfinding.FLYING and \
                        movement_type & pathfinding.LAVA != pathfinding.LAVA:
                    # If this is lava and we do not have the FLYING flag or the LAVA flag...
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
    if not ignore_fighters:
        for object in current_map.objects:
            if object.blocks and object.x == x and object.y == y:
                return True

    # No obstructions were found
    return False


def get_room_spawns(room):
    return [[k, libtcod.random_get_int(0, v[0], v[1])] for (k, v) in room['spawns'].items()]


def apply_attribute(attribute,monster):
    return attribute


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
            if mod_tag != '':
                mod_tag = mod_tag + " " #for monster description

        death = {'function': 'default'}
        if p.get('death_function'):
            death = p.get('death_function')
        fighter_component = combat.Fighter(
                    hp=int(p['hp'] * modifier.get('hp_bonus',1)),
                    armor=int(p['armor'] * modifier.get('armor_bonus',1)),
                    evasion=int(p['evasion'] * modifier.get('evasion_bonus',1)),
                    accuracy=int(p['accuracy'] * modifier.get('accuracy_bonus',1)),
                    death_function=death,
                    spell_power=p.get('spell_power', 0) * modifier.get('spell_power_bonus',1),
                    can_breath_underwater=p.get('can_breathe_underwater', True),
                    resistances=dict(p.get('resistances',{}).items() + modifier.get('resistances',{}).items()),
                    inventory=spawn_monster_inventory(p.get('equipment'),
                    loot_level=p.get('loot_level',-1)),
                    on_hit=p.get('on_hit'),
                    base_shred=p.get('shred', 0) + modifier.get('shred_bonus',1),
                    base_guaranteed_shred=p.get('guaranteed_shred', 0),
                    on_get_hit=p.get('on_get_hit'),
                    base_pierce=p.get('pierce', 0) * modifier.get('pierce_bonus',1),
                    hit_table=p.get('body_type'),
                    monster_flags=p.get('flags', 0),
                    subtype=p.get('subtype'),
                    damage_bonus=p.get('attack_bonus', 0),
                    monster_str_dice=p.get('strength_dice'),
                    team=p.get('team', team),
                    _range=p.get('range',1),
                    will=int(p.get('will', 5) * modifier.get('will_bonus',1)),
                    fortitude=int(p.get('fortitude', 5) * modifier.get('fortitude_bonus',1))
        )

        attributes = roll_monster_abilities(p.get('attributes'))
        if len(attributes) > 0:
            fighter_component._abilities = ([create_ability(a) for a in attributes if a.startswith('ability_')])
            fighter_component.attributes = [a for a in attributes if a.startswith('attribute_')]

        behavior = None
        if p.get('ai'):
            behavior = p.get('ai')()

        zombie_type = p.get('zombie')
        if zombie_type is None:
            name = "monster_zombie_{}".format(p.get('subtype'))
            if name in monsters.proto:
                zombie_type = name

        monster = GameObject(x, y, p['char'], mod_tag + p['name'], p['color'], blocks=True, fighter=fighter_component,
                             behavior=behavior, description=p['description'], on_create=p.get('on_create'),
                             movement_type=p.get('movement_type', pathfinding.NORMAL), on_tick=p.get('on_tick'),
                             zombie_type=zombie_type, stealth=p.get('stealth'))

        monster.light = Light(libtcod.flame, 1, 2)

        for i in monster.fighter.inventory:
            i.item.holder = monster
            if i.equipment:
                i.equipment.equip()

        if monster.behavior:
            monster.behavior.base_attack_speed = 1.0 / p.get('attack_speed', 1.0 * modifier.get('speed_bonus', 1.0))
            monster.behavior.base_move_speed = 1.0 / p.get('move_speed', 1.0 * modifier.get('speed_bonus', 1.0))

        if p.get('essence'):
            monster.essence = p.get('essence')
        monster.elevation = current_map.tiles[x][y].elevation
        if not 'attribute_ambush' in fighter_component.attributes:
            current_map.add_object(monster)
        else:
            monster.blocks = False
            monster.blocks_sight = False
            current_map.objects.append(monster)
        return monster
    return None


def spawn_monster_inventory(proto,loot_level=-1):
    result = []
    if proto:
        for slot in proto:
            equip = random_choice(slot)
            if equip != 'none':
                p = items.table()[equip]
                if p.get('slot') == 'left hand':
                    allowed = True
                    for item in result:
                        if item.equipment.slot == 'both hands':
                            allowed = False
                            break
                    if not allowed:
                        continue
                if p.get('allowed_materials') is not None:
                    material = p.get('allowed_materials')[libtcod.random_get_int(0, 0, len(p.get('allowed_materials')) - 1)]
                elif 'weapon' in equip:
                    material = loot.choose_weapon_material(loot_level)
                elif 'equipment' in equip:
                    material = loot.choose_armor_material(loot_level)
                else:
                    result.append(create_item(equip))
                    continue
                result.append(create_item(equip, material=material, quality=loot.choose_quality(loot_level)))

    return result

def roll_monster_abilities(proto):
    result = []
    if proto:
        for slot in proto:
            if isinstance(slot,dict):
                result.append(random_choice(slot))
            else:
                result.append(slot)

    return result

def spawn_npc(name, x, y, map_name):
    import npc
    if name in npc.npcs.keys():
        result = npc.npcs[name]
    else:
        p = npc.data[name]
        npc_component = npc.NPC(name, p['root'])
        fighter = None
        behavior = None
        attack_speed = 1.0
        move_speed = 1.0
        movement_type = pathfinding.NORMAL
        if name in npc.fighters.keys():
            f = npc.fighters[name]
            death = {'function': 'default'}
            if p.get('death_function'):
                death = p.get('death_function')
            fighter = combat.Fighter(
                hp=int(f['hp']),
                armor=int(f['armor']),
                evasion=int(f['evasion']),
                accuracy=int(f['accuracy']),
                death_function=death,
                spell_power=f.get('spell_power', 0),
                can_breath_underwater=p.get('can_breathe_underwater', True),
                resistances=dict(f.get('resistances', {}).items()),
                inventory=spawn_monster_inventory(f.get('equipment'), loot_level=f.get('loot_level', -1)),
                on_hit=f.get('on_hit'),
                base_shred=f.get('shred', 0),
                base_guaranteed_shred=f.get('guaranteed_shred', 0),
                on_get_hit=f.get('on_get_hit'),
                base_pierce=f.get('pierce', 0),
                hit_table=f.get('body_type'),
                monster_flags=f.get('flags', 0),
                subtype=f.get('subtype'),
                damage_bonus=f.get('attack_bonus', 0),
                monster_str_dice=f.get('strength_dice'),
                team=f.get('team', 'neutral'),
                _range=f.get('range', 1),
                will=int(f.get('will', 10)),
                fortitude=int(f.get('fortitude', 10))
            )
            attack_speed = 1.0 / f.get('attack_speed', 1.0)
            move_speed = 1.0 / f.get('move_speed', 1.0)
            movement_type = f.get('movement_type', pathfinding.NORMAL)
            if f.get('ai'):
                behavior = f.get('ai')()

        result = GameObject(x, y, p['char'], p['name'], p['color'], blocks=True, interact=npc.start_conversation,
                             description=p['description'], on_create=p.get('on_create'), npc=npc_component,
                             fighter=fighter, behavior=behavior, movement_type=movement_type, on_tick=p.get('on_tick'),
                             stealth=p.get(stealth))
        result.syntax_data = {
            'proper': p.get('proper_noun', True),
            'gender': p.get('gender', 'neutral')
        }

        if result.fighter:
            for i in result.fighter.inventory:
                i.item.holder = result
                if i.equipment:
                    i.equipment.equip()

        if result.behavior:
            result.behavior.base_attack_speed = attack_speed
            result.behavior.base_move_speed = move_speed

        result.elevation = current_map.tiles[x][y].elevation

        npc.npcs[name] = result

    if result.npc.location == map_name:
        result.set_position(x, y)
        current_map.add_object(result)
        return result
    return None


def create_ability(name, range_override = None):
    from actions import abilities
    if name in abilities.data:
        a = abilities.data[name]
        return abilities.Ability(name, a.get('name'), a.get('description'), a.get('cooldown'),
                                 intent=a.get('intent', 'aggressive'), range = range_override)
    else:
        return None

def opposite_essence(essence):
    if essence == 'water':
        return 'fire'
    elif essence == 'fire':
        return 'water'
    elif essence == 'earth':
        return 'air'
    elif essence == 'air':
        return 'earth'
    elif essence == 'life':
        return 'death'
    elif essence == 'death':
        return 'life'
    else:
        return essence

def spawn_essence(x,y,type):
    essence_pickup = create_essence(type)
    essence_pickup.set_position(x, y)
    current_map.add_object(essence_pickup)
    return essence_pickup


def create_essence(essence_type):
    essence_pickup = GameObject(0, 0, '*', 'mote of ' + essence_type + ' essence',
                                spells.essence_colors[essence_type],
                                description='A colored orb that glows with elemental potential.',
                                on_step=player.pick_up_essence, always_visible=True)
    essence_pickup.essence_type = essence_type
    return essence_pickup

def create_item(name, material=None, quality=''):
    from actions import abilities
    p = items.table()[name]

    if p['category'] == 'essence':
        return create_essence(p['essence_type'])

    ability = None
    if p.get('ability') is not None and p.get('ability') in abilities.data:
        ability = create_ability(p.get('ability'), p.get('range'))
    item_component = Item(category=p['category'], use_function=p.get('on_use'), type=p['type'], ability=ability, charges=p.get('charges'))
    equipment_component = None
    if p['category'] == 'weapon' or p['category'] == 'armor' or p['category'] == 'book' or p['category'] == 'accessory' or p['category'] == 'quiver':
        if consts.DEBUG_UNLOCK_TOMES and 'level' in p.keys():
            level = 10
        else:
            level = p.get('level', 0)
        equipment_component = equipment.Equipment(
            slot=p['slot'],
            category=p['category'],
            base_id=name,
            strength_dice_bonus=p.get('strength_dice_bonus', 0),
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
            damage_types=p.get('damage_types'),
            attack_speed_bonus=p.get('attack_speed_bonus', 0),
            attack_delay=p.get('attack_delay', 0),
            essence=p.get('essence'),
            spell_list=p.get('spells'),
            level_progression=p.get('levels'),
            level_costs=p.get('level_costs'),
            crit_bonus=p.get('crit_bonus',1.0),
            resistances=p.get('resistances',{}),
            subtype=p.get('subtype'),
            starting_level=level,
            weight=p.get('weight',0),
            range_=p.get('range',1),
            sh_max=p.get('sh_max', 0),
            sh_raise_cost=p.get('sh_raise_cost', 0),
            sh_recovery=p.get('sh_recovery', 0),
            stamina_regen=p.get('stamina_regen', 0),
            status_effect=p.get('status_effect'),
            will_bonus=p.get('will', 0),
            fortitude_bonus=p.get('fortitude', 0),
            attributes=p.get('attributes', []),
            stealth=p.get('stealth'),
            max_ammo=p.get('max_ammo', 0),
        )



        if material is None:
            material = 'iron' if equipment_component.category == 'weapon' else ''
            allowed = p.get('allowed_materials')
            if allowed is not None and material not in allowed:
                # choose random allowed material
                material = allowed[libtcod.random_get_int(0, 0, len(allowed) - 1)]

        if equipment_component.category == 'weapon':
            equipment_component.modifiers[quality] = loot.qualities[quality]['weapon']
            equipment_component.modifiers[material] = loot.weapon_materials[material]
            equipment_component.quality = quality
            equipment_component.material = material
        if equipment_component.category == 'armor':
            equipment_component.modifiers[quality] = loot.qualities[quality]['armor']
            equipment_component.modifiers[material] = loot.armor_materials[material]
            equipment_component.quality = quality
            equipment_component.material = material
            if equipment_component.sh_max > 0:
                equipment_component.sh_points = equipment_component.sh_max

    go = GameObject(0, 0, p['char'], p['name'], p.get('color', libtcod.white), item=item_component,
                      equipment=equipment_component, always_visible=True, description=p.get('description'))

    if ability is not None:
        go.item.ability = ability
    if hasattr(equipment_component, 'material') and equipment_component.material != '':
        go.name = equipment_component.material + ' ' + go.name
    if hasattr(equipment_component, 'quality') and equipment_component.quality != '':
        go.name = equipment_component.quality + ' ' + go.name
    go.name = string.capwords(go.name)
    return go


def spawn_item(name, x, y, material=None, quality=None):
        item = create_item(name, material, quality)
        item.x = x
        item.y = y
        current_map.add_object(item)
        item.send_to_back()


def set_quality(equipment, quality):
    #remove all quality modifiers from the item
    for k in loot.qualities.keys():
        if k in equipment.modifiers:
            del equipment.modifiers[k]
    equipment.quality = quality
    equipment.modifiers[equipment.quality] = loot.qualities[equipment.quality][equipment.category]

    # update name
    go = equipment.owner
    go.name = items.table()[equipment.base_id]['name']
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


def melt_ice(x, y):
    if x < 0 or y < 0 or x >= consts.MAP_WIDTH or y >= consts.MAP_WIDTH:
        return
    if not current_map.tiles[x][y].is_ice:
        return
    if current_map.tiles[x][y].tile_type == 'ice' or current_map.tiles[x][y].tile_type == 'ice wall':
        current_map.tiles[x][y].tile_type = 'shallow water'
    elif current_map.tiles[x][y].tile_type == 'deep_ice':
        current_map.tiles[x][y].tile_type = 'deep water'
    changed_tiles.append((x, y))

def freeze_water(x, y, permanent=False):
    if x < 0 or y < 0 or x >= consts.MAP_WIDTH or y >= consts.MAP_WIDTH:
        return
    if not current_map.tiles[x][y].is_water:
        return
    if current_map.tiles[x][y].jumpable:
        ice_type = 'ice'
    else:
        ice_type = 'deep_ice'
    if permanent:
        current_map.tiles[x][y].tile_type = ice_type
        changed_tiles.append((x, y))
    else:
        create_temp_terrain(ice_type, [(x, y)], 30 + roll_dice('1d30'), save_old_terrain=True)

def create_fire(x ,y, temp):

    tile = current_map.tiles[x][y]
    if tile.is_water or (tile.blocks and tile.flammable == 0) or tile.is_pit:
        return
    elif tile.is_ice:
        melt_ice(x, y)
        return
    current = object_at_tile(x,y,'Fire')
    if current is not None:
        if current.misc.temperature < temp:
            current.misc.temperature = temp
        return

    component = ai.FireBehavior(temp)
    obj = GameObject(x,y,libtcod.CHAR_ARROW2_N,'Fire',libtcod.red,misc=component, description='A column of roaring flames')
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

def create_frostfire(x, y):
    tile = current_map.tiles[x][y]
    if tile.is_water:
        freeze_water(x, y)
    elif tile.tile_type == 'lava':
        tile.tile_type = 'scorched floor'
        changed_tiles.append((x, y))
    current = object_at_tile(x, y, 'Frostfire')
    if current is not None:
        if current.misc.temperature < 10:
            current.misc.temperature = 10
        return
    component = ai.FrostfireBehavior(10)
    obj = GameObject(x, y, libtcod.CHAR_ARROW2_N, 'Frostfire', libtcod.light_sky, misc=component,
                     description='An eerie blue flame of pure cold, freezing anything it touches')
    current_map.add_object(obj)
    changed_tiles.append((x, y))

def create_reeker_gas(x, y, duration=consts.REEKER_PUFF_DURATION):
    if not current_map.tiles[x][y].blocks and \
                    len(get_objects(x, y, lambda o: o.name == 'reeker gas' or o.name == 'reeker')) == 0:
        puff = GameObject(x, y, libtcod.CHAR_BLOCK3, 'reeker gas', libtcod.dark_fuchsia,
                          description='a puff of reeker gas', misc=ai.ReekerGasBehavior(duration=duration))
        current_map.add_object(puff)


def chest_interact(chest, actor):
    if actor is player.instance:
        if lock_interact(actor, 'chest'):
            #loot_drop = mapgen.create_random_loot(loot_level=dungeon.branches[current_map.branch]['loot_level'] + 2)
            loot_drop = loot.item_from_table(current_map.branch, 'chest_0')
            if loot_drop is not None:
                loot_drop.x = chest.x
                loot_drop.y = chest.y
                current_map.add_object(loot_drop)
                loot_drop.send_to_back()
            chest.destroy()


def lock_interact(actor=None, object_name='object'):
    if actor is not None and actor is not player.instance:
        return False
    key = player.get_key()
    if key is not None:
        if ui.menu_y_n('This %s is locked. Use your glass key?' % object_name):
            ui.message('The glass key fits into the lock and you hear a click. The key dissolves into sand.',
                       libtcod.yellow)
            player.instance.fighter.inventory.remove(key)
            return True
    else:
        ui.menu('This %s is locked.' % object_name, ['Back'])
    return False


def door_interact(door, actor):
    #Band-aid solution to auto-explore door soft-lock
    #TODO - Fix A*
    if actor is player.instance:
        player.flush_queued_actions()

    if not is_blocked(door.x, door.y):
        if door.closed:
            do_open = False
            if door.locked:
                do_open = lock_interact(actor, 'door')
            else:
                do_open = True
            if do_open:
                door.closed = False
                door.blocks_sight = False
                door.background_color = None
                if door.locked:
                    door.locked = False
                    door.name = 'door'
                    door.description = 'A heavy stone door with a keyhole in the center. It is unlocked.'
            else:
                return 'blocked'
        else:
            door.closed = True
            door.blocks_sight = True
            door.background_color = libtcod.dark_sepia
        changed_tiles.append((door.x, door.y))
        fov.set_fov_properties(door.x, door.y, door.blocks_sight, door.elevation)
        return 'interacted-door'
    ui.message('Something is blocking the door.')
    return 'didnt-take-turn'

def switch_interact(switch, actor):
    door = switch.door
    ui.message('You hear the rattling of iron chains as a gate opens somewhere.')
    door.locked = False
    door.closed = False
    door.char = '.'

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

#TODO: add movement_type parameter
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


def find_random_open_tile():
    open = []
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            if not is_blocked(x, y):
                open.append((x, y))
    return open[libtcod.random_get_int(0, 0, len(open) - 1)]


def spawn_encounter(tiles,encounter,position,count=None, leader=None):
    if leader is not None:
        for l in leader:
            loc = find_closest_open_tile(position[0], position[1])
            if loc is not None and loc in tiles:
                spawn_monster(l, loc[0], loc[1])
                tiles.remove(loc)
                if len(tiles) == 0:
                    return
    if count is not None:
        for i in range(count):
            loc = find_closest_open_tile(position[0], position[1])
            if loc is not None and loc in tiles:
                spawn_monster(encounter['encounter'][libtcod.random_get_int(0, 0, len(encounter['encounter']) - 1)], loc[0],
                              loc[1])
                tiles.remove(loc)
                if len(tiles) == 0:
                    return
    else:
        for m in encounter['encounter']:
            loc = find_closest_open_tile(position[0], position[1])
            if loc is not None:
                spawn_monster(m, loc[0], loc[1])
                tiles.remove(loc)
                if len(tiles) == 0:
                    return

def place_objects(tiles,encounter_count=1, loot_count=1, xp_count=1):
    if len(tiles) == 0:
        return

    branch = dungeon.branches[current_map.branch]
    monsters_set = branch.get('monsters')
    if monsters_set is not None:
        current_set = []
        for e in monsters_set:
            min_depth = e.get('min_depth')
            max_depth = e.get('max_depth')
            if min_depth <= current_map.difficulty and (max_depth is None or max_depth >= current_map.difficulty):
                current_set.append(e)
        if len(current_set) > 0:
            for i in range(encounter_count):
                #encounter_roll = roll_dice('1d' + str(branch['encounter_range'] + current_map.difficulty))
                #if roll_dice('1d10') == 10:  # Crit the encounter table, roll to confirm
                #    encounter_roll = libtcod.random_get_int(0, encounter_roll, len(monsters_set)) - 1
                #encounter_roll = min(encounter_roll, len(monsters_set) - 1)
                #encounter = monsters_set[encounter_roll]
                encounter = current_set[libtcod.random_get_int(0, 0, len(current_set) - 1)]
                size = 1
                random_pos = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]

                if encounter.get('party') is not None:
                    size = roll_dice(encounter['party'])

                spawn_encounter(tiles,encounter,random_pos,size,leader=encounter.get('leader'))

    for i in range(loot_count):
        random_pos = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]

        if not is_blocked(random_pos[0], random_pos[1]):
            special = loot.check_special_drop()
            if special is not None:
                item = create_item(special)
            else:
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


def get_loot(monster):
    loot_table = monster.loot_table
    drop = loot_table[libtcod.random_get_int(0,0,len(loot_table) - 1)]
    if drop:
        proto = items.table()[drop]
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


def get_visible_units():
    return [f for f in current_map.fighters if f.player_can_see()]


def get_visible_units_ex(predicate):
    return [f for f in current_map.fighters if f.player_can_see() and predicate(f)]


def land_next_to_target(target_x, target_y, source_x, source_y):
    if abs(target_x - source_x) <= 1 and abs(target_y - source_y) <= 1:
        return source_x, source_y  # trivial case - if we are adjacent we don't need to move
    b = beam(source_x, source_y, target_x, target_y)
    land_x = b[len(b) - 2][0]
    land_y = b[len(b) - 2][1]
    if not is_blocked(land_x, land_y):
        return land_x, land_y
    return None

def fall_in_pit(object):
    ui.message('%s %s into the pit!' % (syntax.name(object).capitalize(), syntax.conjugate(object is player.instance, ('fall', 'falls'))), libtcod.white)
    if not hasattr(object, 'fighter') or object.fighter is None:
        object.destroy()
        return

    object.fighter.take_damage(roll_dice('2d10', normalize_size=4))
    if object.fighter is None: # Died in fall
        object.destroy()
        return
    pit_ticker = Ticker(5, _pit_ticker)
    pit_ticker.obj = object
    pit_ticker.old_stealth = object.stealth
    object.stealth = -1
    object.fighter.apply_status_effect(effects.stunned(duration=5))
    current_map.tickers.append(pit_ticker)

def _pit_ticker(ticker):
    if ticker.ticks >= ticker.max_ticks:
        ticker.dead = True
        if ticker.obj is player.instance:
            tile = None
            ui.message('Climb out where?')
            while tile is None or tile[0] is None:
                tile = ui.target_tile(max_range=1)
            destination = find_closest_open_tile(tile[0], tile[1])
        else:
            destination = find_closest_open_tile(ticker.obj.x, ticker.obj.y)
        ticker.obj.stealth = ticker.old_stealth
        ticker.obj.set_position(destination[0], destination[1])

def clear_map():
    libtcod.console_set_default_background(map_con, libtcod.black)
    libtcod.console_set_default_foreground(map_con, libtcod.black)
    libtcod.console_clear(map_con)


lighting = [[libtcod.black for x in range(consts.MAP_WIDTH)] for y in range(consts.MAP_HEIGHT)]

def render_map():
    global changed_tiles, visible_tiles, lighting

    if consts.ENABLE_LIGHTING:
        for x in range(0,consts.MAP_WIDTH):
            for y in range(0,consts.MAP_HEIGHT):
                lighting[x][y] = libtcod.dark_gray #global illumination
        lights = [obj for obj in current_map.objects if obj.light is not None]
        for ll in lights:
            for x in range(max(0,ll.x - ll.light.radius), min(consts.MAP_WIDTH, ll.x + ll.light.radius + 1)):
                for y in range(max(0, ll.y - ll.light.radius), min(consts.MAP_WIDTH, ll.y + ll.light.radius + 1)):
                    if fov.monster_can_see_tile(ll,x,y):
                        val = libtcod.color_lerp(ll.light.color, ll.light.color * lighting[x][y],
                                                 clamp(distance(x,y,ll.x,ll.y) / ll.light.radius, 0, 1))
                        lighting[x][y] += val

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
        light = libtcod.white
        if consts.ENABLE_LIGHTING:
            light = lighting[x][y]
        color_fg = libtcod.Color(current_map.tiles[x][y].color_fg[0], current_map.tiles[x][y].color_fg[1],
                                 current_map.tiles[x][y].color_fg[2]) * light
        color_bg = libtcod.Color(current_map.tiles[x][y].color_bg[0], current_map.tiles[x][y].color_bg[1],
                                 current_map.tiles[x][y].color_bg[2]) * light
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

    #for x in range(consts.MAP_WIDTH):
    #    for y in range(consts.MAP_HEIGHT):
    #        if not current_map.pathfinding.is_accessible((x, y)):
    #            libtcod.console_put_char_ex(map_con, x, y, 'X', libtcod.yellow, libtcod.darker_yellow)

    for obj in current_map.objects:
        if obj is not player.instance:
            obj.draw(map_con)

    player.instance.draw(map_con)

    vw = ui.MAP_VIEWPORT_WIDTH()
    vh = ui.MAP_VIEWPORT_HEIGHT()

    libtcod.console_blit(map_con, player.instance.x - vw / 2, player.instance.y - vh / 2,
                ui.MAP_VIEWPORT_WIDTH(), ui.MAP_VIEWPORT_HEIGHT(), 0, ui.MAP_VIEWPORT_X, ui.MAP_VIEWPORT_Y)
    ui.draw_border(0, ui.MAP_VIEWPORT_X, ui.MAP_VIEWPORT_Y, vw, vh)


def render_all():

    if not in_game:
        render_main_menu_splash()
        return

    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_clear(0)

    render_map()

    ui.render_message_panel()

    ui.render_action_panel()

    ui.render_side_panel()

    ui.render_ui_overlay()


def render_main_menu_splash():
    #img = libtcod.image_load('menu_background.png')
    libtcod.console_set_default_background(0, libtcod.black)
    libtcod.console_clear(0)
    #libtcod.image_blit_2x(img, 0, 0, 0)
    libtcod.console_set_default_foreground(0, libtcod.light_yellow)
    libtcod.console_print_ex(0, SCREEN_WIDTH() / 2, SCREEN_HEIGHT() / 2 - 8, libtcod.BKGND_NONE,
                             libtcod.CENTER,
                             'MAGIC-ROGUELIKE')
    libtcod.console_print_ex(0, SCREEN_WIDTH() / 2, SCREEN_HEIGHT() - 2, libtcod.BKGND_NONE, libtcod.CENTER,
                             'by Tyler Soberanis and Adrien Young')


def use_stairs(stairs, actor):
    import world

    if hasattr(stairs, 'event') and callable(stairs.event):
        if stairs.event() == 'one-off':
            stairs.event = None

    next_map = stairs.link[1]
    current_map.pathfinding = None
    if hasattr(stairs, 'destination_id'):
        destination_id = stairs.destination_id
    else:
        destination_id = None
    enter_map(next_map, world.opposite(stairs.link[0]), destination_id=destination_id)


def enter_map(world_map, direction=None, destination_id=None):
    import npc
    global current_map
    world_map.visited = True
    following = []

    if current_map is not None:
        for fighter in current_map.fighters:
            if fighter.fighter.permanent_ally:
                following.append(fighter)
        for fighter in following:
            fighter.destroy()
        clear_map()
        libtcod.console_clear(ui.overlay)
        libtcod.console_blit(ui.overlay, 0, 0, ui.MAP_VIEWPORT_WIDTH(), ui.MAP_VIEWPORT_HEIGHT(), 0, ui.MAP_VIEWPORT_X, ui.MAP_VIEWPORT_Y)
        libtcod.console_set_default_foreground(map_con, libtcod.white)
        if world_map.tiles is None:
            load_string = 'Generating...'
        else:
            load_string = 'Loading...'
        libtcod.console_print(map_con, 0, 0, load_string)
        libtcod.console_blit(map_con, 0, 0, len(load_string), 1, 0, ui.MAP_VIEWPORT_X + 4, ui.MAP_VIEWPORT_Y + 4)
        ui.draw_border(0, ui.MAP_VIEWPORT_X, ui.MAP_VIEWPORT_Y, ui.MAP_VIEWPORT_WIDTH(), ui.MAP_VIEWPORT_HEIGHT())

        libtcod.console_flush()

    current_map = world_map

    if current_map.objects is not None:
        for obj in current_map.objects:
            if obj in npc.npcs.values():
                if obj.npc.location != current_map.name:
                    # We found an NPC who's not supposed to be here any more.
                    obj.destroy()

    if world_map.tiles is None:
        generate_level(world_map)

    current_map.pathfinding = pathfinding.Graph()
    current_map.pathfinding.initialize()

    if direction is not None:
        for obj in current_map.objects:
            if hasattr(obj, 'link') and obj.link[0] == direction:
                if destination_id is not None:
                    if not hasattr(obj, 'link_id') or obj.link_id != destination_id:
                        continue
                player.instance.x = obj.x
                player.instance.y = obj.y
                player.instance.elevation = current_map.tiles[obj.x][obj.y].elevation

    if player.instance not in current_map.objects or player.instance not in current_map.fighters:
        current_map.add_object(player.instance)

    for follower in following:
        pos = find_closest_open_tile(player.instance.x, player.instance.y)
        follower.set_position(pos[0], pos[1])
        current_map.add_object(follower)

    fov.initialize_fov()

    ui.display_fading_text(string.capwords(dungeon.branches[current_map.branch]['name']), 60, 20)
    save_game()

def generate_level(world_map):
    mapgen.make_map(world_map)


#############################################
# Initialization & Main Loop
#############################################

def main_menu():
    global windowx, windowy, tilex, tiley, in_game

    mapgen.initialize_features()

    while not libtcod.console_is_window_closed():
        render_main_menu_splash()

        choice = ui.menu('', ['NEW GAME', 'LOAD', 'QUIT'], 24, x_center=SCREEN_WIDTH() / 2)
        
        if choice == 0: #new game
            if new_game() != 'cancelled':
                play_game()
        elif choice == 1:
            try:
                load_game()
            except:
                in_game = False
                ui.menu('\n No saved game to load.\n', [], 30, x_center=SCREEN_WIDTH() / 2)
                continue
            play_game()
        elif choice == 2:
            print('Quitting game...')
            return

def new_game():
    global game_state, dungeon_level, in_game, changed_tiles, learned_skills, current_map

    confirm = False
    loadout = None
    current_map = None

    while not confirm:
        options = list(player.loadouts.keys())
        choice = ui.menu('Select your starting class',options,36,x_center=SCREEN_WIDTH() / 2)
        if choice is None:
            return 'cancelled'
        loadout = options[choice]
        confirm = ui.menu('Confirm starting as ' + loadout.title() + ":\n\n" + player.loadouts[loadout]['description'],
                          ['Start','Back'],36,x_center=SCREEN_WIDTH() / 2) == 0

    learned_skills = {}
    player.create(loadout)
    in_game = True
    ui.selected_monster = None

    import world
    world.initialize_world()
    
    # generate map
    dungeon_level = 1

    game_state = 'playing'

    if consts.DEBUG_STARTING_MAP is not None:
        enter_map(world.world_maps[consts.DEBUG_STARTING_MAP])
    else:
        enter_map(world.world_maps['beach'])

    player.instance.memory = equipment.Equipment(None,'tome',spell_list=[])

    ui.game_msgs = []
    ui.message('You wake up on a beach...', libtcod.gold)

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))


def save_game():
    import world
    try:
        f = shelve.open('savegame', 'n')
        f['map'] = world.world_maps
        f['current_map'] = current_map.name
        f['player_index'] = current_map.objects.index(player.instance)
        f['learned_skills'] = learned_skills
        f['game_msgs'] = ui.game_msgs
        f['game_state'] = game_state
        f['branch_scaling'] = world.get_branch_scaling()
        f.close()
    except:
        print("Unexpected error saving game: ", sys.exc_info()[0])


def load_game():
    import world
    global game_state, current_map, in_game, learned_skills

    in_game = True

    f = shelve.open('savegame', 'r')
    world.world_maps = f['map']
    current_map = world.get_map(f['current_map'])
    player.instance = current_map.objects[f['player_index']]
    learned_skills = f['learned_skills']
    ui.game_msgs = f['game_msgs']
    game_state = f['game_state']
    world.set_branch_scaling(f['branch_scaling'])
    f.close()

    fov.initialize_fov()

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            changed_tiles.append((x, y))

def SCREEN_WIDTH():
    return windowx / tilex

def SCREEN_HEIGHT():
    return (windowy / tiley) - 4 #TODO: filthy hack to deal with the header-bar

def play_game():
    global key, mouse, game_state, windowx, windowy, shift
    
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():

        if consts.DEBUG_SAFE_CRASH:
            try:
                if step() == 'exit':
                    break
            except:
                print("Unexpected error: %s" % sys.exc_info()[0])
                traceback.print_tb(sys.exc_traceback)
        else:
            if step() == 'exit':
                break

        # Handle auto-targeting
        ui.auto_target_monster()

def step():

    global in_game, shift

    # Render the screen
    libtcod.sys_check_for_event(
        libtcod.EVENT_KEY_PRESS |
        libtcod.EVENT_KEY_RELEASE |
        libtcod.EVENT_MOUSE, key, mouse)

    # handle shift on mac, because its treated as a key press instead of a modifier for some reason
    if key.vk == libtcod.KEY_SHIFT:
        shift = key.pressed

    render_all()
    libtcod.console_flush()

    # Handle keys and exit game if needed
    player_action = player.handle_keys(shift)
    if player_action == 'exit':
        save_game()
        in_game = False
        return 'exit'

    if consts.RENDER_EVERY_TURN:
        render_all()
        libtcod.console_flush()

    # Let monsters take their turn
    if game_state == 'playing' and player_action != 'didnt-take-turn':
        dead_tickers = []
        player.instance.on_tick(object=player.instance)
        for object in current_map.objects:
            if object.behavior:
                object.behavior.take_turn()
            if object is not player.instance:
                object.on_tick(object=object)
        for ticker in current_map.tickers:
            if hasattr(ticker, 'ticks'):
                ticker.ticks += 1
            if hasattr(ticker, 'on_tick'):
                ticker.on_tick(ticker)
            if hasattr(ticker, 'dead') and ticker.dead:
                dead_tickers.append(ticker)
        for ticker in dead_tickers:
            if ticker in current_map.tickers:
                current_map.tickers.remove(ticker)

    return

# Globals

# Libtcod initialization
libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
windowx,windowy = libtcod.sys_get_current_resolution()
tilex, tiley = 16,16
libtcod.console_init_root(SCREEN_WIDTH(), SCREEN_HEIGHT(), 'mrogue', False)
libtcod.sys_set_fps(consts.LIMIT_FPS)
shift = False

# Consoles
con = libtcod.console_new(SCREEN_WIDTH(), SCREEN_HEIGHT())
map_con = libtcod.console_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)

# Flags
in_game = False

# Graphics
changed_tiles = []
visible_tiles = []

# Level
current_map = None

# my modules
import loot
import spells
import monsters
import dungeon
import mapgen
import effects
import pathfinding
import fov
import ui
import ai
import player
import combat
import terrain
import equipment
import charms
import items
