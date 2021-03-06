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

import game as main
import consts
import libtcodpy as libtcod
import random
import math
import terrain
import Queue
import copy
import player
import dungeon
import loot
import log
from collections import deque

angles = [0,
          0.5 * math.pi,
          math.pi,
          1.5 * math.pi]

NOROTATE = 1
NOREFLECT = 2
NOSPAWNS = 4
NOELEV = 8
SPECIAL = 16
map = None
default_wall = 'stone wall'
default_floor = 'stone floor'
default_ramp = 'stone ramp'

class BSP_Leaf:

    def __init__(self, x, y, w, h, min_size=6):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.left = None
        self.right = None
        self.min_size = min_size

    def split(self):
        if self.left is not None or self.right is not None:
            return False
        # determine split direction
        if self.w > self.h and self.w / self.h > 1.25:
            split_horizontal = False
        elif self.h > self.w and self.h / self.w > 1.25:
            split_horizontal = True
        else:
            split_horizontal = libtcod.random_get_int(0, 0, 1) == 0

        if split_horizontal:
            max_size = self.h - self.min_size
        else:
            max_size = self.w - self.min_size
        if max_size <= self.min_size:
            return False

        split_value = libtcod.random_get_int(0, self.min_size, max_size)

        if split_horizontal:
            self.left = BSP_Leaf(self.x, self.y, self.w, split_value, min_size=self.min_size)
            self.right = BSP_Leaf(self.x, self.y + split_value, self.w, self.h - split_value, min_size=self.min_size)
        else:
            self.left = BSP_Leaf(self.x, self.y, split_value, self.h, min_size=self.min_size)
            self.right = BSP_Leaf(self.x + split_value, self.y, self.w - split_value, self.h, min_size=self.min_size)
        return True

    def split_recursive(self):
        if self.split():
            self.left.split_recursive()
            self.right.split_recursive()


# It's not a bug, it's a
class Feature:
    def __init__(self):
        self.room = None
        self.flags = 0
        self.scripts = []
        self.name = ''

    def set_flag(self, flag):
        self.flags = self.flags | flag

    def has_flag(self, flag):
        return self.flags & flag != 0

class Room:
    def __init__(self):
        self.tiles = {}
        self.data = {}
        self.key_points = {}
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None
        self.pos = 0, 0
        self.no_overwrite = False
        self.link_points = []

    @property
    def bounds(self):
        if self.max_x is None or self.min_x is None or self.max_y is None or self.min_y is None:
            return 0, 0
        else:
            return self.max_x - self.min_x + 1, self.max_y - self.min_y + 1

    @property
    def rect(self):
        bounds = self.bounds
        return Rect(self.min_x, self.min_y, bounds[0] - 1, bounds[1] - 1)

    @property
    def width(self):
        return self.max_x - self.min_x + 1

    @property
    def height(self):
        return self.max_y - self.min_y + 1

    # define the world-space position of the upper-left-hand corner of this room. Adjust all tile positions
    def set_pos(self, x, y):
        if self.pos[0] == x and self.pos[1] == y:
            return  # No translation
        new_tiles = {}
        new_data = {}
        new_key_points = {}
        new_min_x = new_min_y = 10000
        new_max_x = new_max_y = -10000
        for tile in self.tiles.keys():
            new_x = tile[0] + x - self.min_x - self.width / 2
            new_y = tile[1] + y - self.min_y - self.height / 2
            if new_x < new_min_x:
                new_min_x = new_x
            if new_y < new_min_y:
                new_min_y = new_y
            if new_x > new_max_x:
                new_max_x = new_x
            if new_y > new_max_y:
                new_max_y = new_y
            new_tiles[new_x, new_y] = self.tiles[tile]
            if tile in self.data.keys():
                new_data[new_x, new_y] = self.data[tile]
            for key_point in self.key_points.items():
                if key_point[1] == (tile[0], tile[1]):
                    new_key_points[key_point[0]] = (new_x, new_y)
        self.min_x = new_min_x
        self.min_y = new_min_y
        self.max_x = new_max_x
        self.max_y = new_max_y
        self.tiles = new_tiles
        self.data = new_data
        self.key_points = new_key_points
        self.pos = x, y

    # Orient to the origin, then rotate about the top-left corner, then reorient to the origin again.
    def rotate(self, angle):
        if angle == 0.0 or angle == 2 * math.pi:
            return  # No rotation
        self.set_pos(0, 0)
        self.min_x = None
        self.min_y = None
        self.max_x = None
        self.max_y = None
        new_tiles = {}
        new_data = {}
        new_key_points = {}
        for tile in self.tiles.keys():
            new_x = int(round(float(tile[0]) * math.cos(angle) - float(tile[1]) * math.sin(angle)))
            new_y = int(round(float(tile[0]) * math.sin(angle) + float(tile[1]) * math.cos(angle)))
            new_tiles[new_x, new_y] = self.tiles[tile]
            if tile in self.data.keys():
                new_data[new_x, new_y] = self.data[tile]
            if self.min_x is None or new_x < self.min_x:
                self.min_x = new_x
            if self.min_y is None or new_y < self.min_y:
                self.min_y = new_y
            if self.max_x is None or new_x > self.max_x:
                self.max_x = new_x
            if self.max_y is None or new_y > self.max_y:
                self.max_y = new_y
            for key_point in self.key_points.items():
                if key_point[1] == (tile[0], tile[1]):
                    new_key_points[key_point[0]] = (new_x, new_y)
        self.tiles = new_tiles
        self.data = new_data
        self.pos = self.min_x, self.min_y
        self.key_points = new_key_points
        self.set_pos(0, 0)

    # Orient to the origin, then reflect across one or both axes
    def reflect(self, reflect_x=False, reflect_y=False):
        if not reflect_x and not reflect_y:
            return  # No reflection
        self.set_pos(0, 0)
        new_tiles = {}
        new_data = {}
        new_key_points = {}
        for tile in self.tiles.keys():
            if reflect_x:
                new_x = -tile[0] + self.max_x
            else:
                new_x = tile[0]
            if reflect_y:
                new_y = -tile[1] + self.max_y
            else:
                new_y = tile[1]
            new_tiles[(new_x, new_y)] = self.tiles[tile]
            if tile in self.data.keys():
                new_data[new_x, new_y] = self.data[tile]
            for key_point in self.key_points.items():
                if key_point[1] == (tile[0], tile[1]):
                    new_key_points[key_point[0]] = (new_x, new_y)
        self.tiles = new_tiles
        self.data = new_data
        self.key_points = new_key_points


    def set_tile(self, x, y, tile_type, elevation=None):
        if self.min_x is None or self.min_x > x:
            self.min_x = x
        if self.max_x is None or self.max_x < x:
            self.max_x = x
        if self.min_y is None or self.min_y > y:
            self.min_y = y
        if self.max_y is None or self.max_y < y:
            self.max_y = y
        self.tiles[(x, y)] = tile_type
        if elevation is not None:
            self.data[(x, y)] = []
            self.data[(x, y)].append('ELEVATION')
            self.data[(x, y)].append(str(elevation))
            #ele_str = 'ELEVATION ' + str(elevation)
            #if (x, y) not in self.data.keys():
            #    self.data[(x, y)] = ele_str
            #else:
            #    self.data[(x, y)] += (' ' + ele_str)

    def remove_tile(self, x, y):
        if not (x, y) in self.tiles.keys():
            return
        del self.tiles[(x, y)]
        if (x, y) in self.data.keys():
            del self.data[(x, y)]
        to_remove = []
        for key_point in self.key_points:
            if key_point[1] == (x, y):
                to_remove.append(key_point[0])
        for key in to_remove:
            del self.key_points[key]
        if x == self.min_x or x == self.max_x or y == self.min_y or y == self.max_y:
            self.max_x = None
            self.min_x = None
            self.max_y = None
            self.min_y = None
            for t in self.tiles:
                if self.min_x is None or self.min_x > t[0]:
                    self.min_x = t[0]
                if self.max_x is None or self.max_x < t[0]:
                    self.max_x = t[0]
                if self.min_y is None or self.min_y > t[1]:
                    self.min_y = t[1]
                if self.max_y is None or self.max_y < t[1]:
                    self.max_y = t[1]

    def get_open_tiles(self):
        return_tiles = []
        for tile in self.tiles.keys():
            tile_type = self.tiles[tile]
            if tile_type == 'open' or tile_type == 'floor':
                tile_type = default_floor
            elif tile_type == 'wall':
                tile_type = default_wall
            elif tile_type == 'ramp':
                tile_type = default_ramp
            if tile in self.data.keys():
                if self.data[tile] == '>' or self.data[tile] == 'X':
                    return_tiles.append(tile)
                    continue
            if not terrain.data[tile_type].blocks and not terrain.data[tile_type].isPit and tile not in self.data.keys():
                return_tiles.append(tile)
        return return_tiles

    def get_blocked_tiles(self):
        return_tiles = []
        for tile in self.tiles.keys():
            tile_type = self.tiles[tile]
            if tile_type == 'open' or tile_type == 'floor':
                tile_type = default_floor
            elif tile_type == 'wall':
                tile_type = default_wall
            elif tile_type == 'ramp':
                tile_type = default_ramp
            if terrain.data[tile_type].blocks or terrain.data[tile_type].isPit or tile in self.data.keys():
                return_tiles.append(tile)
        return return_tiles

    def add_rectangle(self, x0=0, y0=0, width=None, height=None, tile_type=default_floor):
        if width is None:
            width = libtcod.random_get_int(0, consts.MG_ROOM_MIN_SIZE, consts.MG_ROOM_MAX_SIZE)
        if height is None:
            height = libtcod.random_get_int(0, consts.MG_ROOM_MIN_SIZE, consts.MG_ROOM_MAX_SIZE)
        for x in range(width):
            for y in range(height):
                self.set_tile(x0 + x, y0 + y, tile_type)

    def add_circle(self, x0=0, y0=0, r=None, tile_type=default_floor):
        if r is None:
            r = libtcod.random_get_int(0, consts.MG_CIRCLE_ROOM_MIN_RADIUS, consts.MG_CIRCLE_ROOM_MAX_RADIUS)
        d = 2 * r + 1
        for x in range(d):
            for y in range(d):
                distsqrd = (x - r) ** 2 + (y - r) ** 2
                if distsqrd <= r ** 2:
                    self.set_tile(x0 + x - r, y0 + y - r, tile_type)

    def center(self):
        center = (self.min_x + self.bounds[0] / 2, self.min_y + self.bounds[1] / 2)
        if center in self.tiles.keys():
            return center
        else:
            return None

    def distance_to(self,other):
        c = self.center()
        co = other.center()
        size = (self.bounds[0] + self.bounds[1]) / 2
        other_size = size = (other.bounds[0] + other.bounds[1]) / 2
        return abs(c[0] - co[0]) + abs(c[1] - co[1]) - size - other_size

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

    @property
    def w(self):
        return self.x2 - self.x1

    @property
    def h(self):
        return self.y2 - self.y1


def create_room_random(terrain_options=None):
    choice = libtcod.random_get_int(0, 0, 1)

    if choice == 0:
        return create_room_cloud(random_terrain(terrain_options))
    elif choice == 1:
        return create_room_circle(terrain_options)
    #elif choice == 2: #pretty sure this one was causing connectivity issues
    #     return create_room_cellular_automata(10, 10)


def random_terrain(options=None):
    if options is None:
        options = ['shallow water','grass floor',default_floor]
    dice = libtcod.random_get_int(0, 0, len(options)-1)
    return options[dice]

def create_room_cellular_automata(width, height):
    room = Room()
    #Step 1: fill room with random walls/floor
    for y in range(height):
        for x in range(width):
            if libtcod.random_get_int(0, 0, 100) < 60:
                room.set_tile(x, y, default_floor)
            else:
                room.set_tile(x, y, default_wall)
    #Step 2: iterate over each tile in the room using the 4-5 rule:
    # For each tile, if it is a wall and four or more of its neighbors are walls, it is a wall, else it becomes a floor
    # if it is not a wall and five or more of its neighbors are walls, it becomes a wall, else it stays floor
    for i in range(2):  # 2 iterations
        for tile in room.tiles.keys():
            wall_count = get_adjacent_walls(room, tile[0], tile[1])
            if room.tiles[tile] == default_wall:
                if wall_count >= 4:
                    continue
                else:
                    room.tiles[tile] = default_floor
            else:
                if wall_count >= 5:
                    room.tiles[tile] = default_wall
                else:
                    continue
    #Step 3: fill all connected tiles. Replace tiles not connected to the largest section with wall
    fill_pockets(room=room)

    return room


def fill_pockets(room=None):
    if room is None:
        tiles = {}
        for x in range(consts.MAP_WIDTH):
            for y in range(consts.MAP_HEIGHT):
                tiles[(x, y)] = map.tiles[x][y].tile_type
    else:
        tiles = room.tiles

    done = False
    filled_lists = []
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            if (x, y) in tiles.keys() and tiles[(x, y)] != default_wall:
                if len(filled_lists) > 0:
                    for list in filled_lists:
                        if (x, y) in list:
                            continue
                new_list = flood_fill(tiles, filled_lists, x, y)
                filled_lists.append(new_list)
    longest = 0
    longest_list = None
    for list in filled_lists:
        if len(list) > longest:
            longest = len(list)
            longest_list = list
    for list in filled_lists:
        if list is not longest_list:
            for tile in list:
                if room is None:
                    change_map_tile(tile[0], tile[1], default_wall)
                else:
                    room.tiles[tile] = default_wall

def flood_fill(tiles, filled_lists, x, y):
    new_list = []
    Q = Queue.Queue()
    Q.put((x, y))
    while not Q.empty():
        n = Q.get()
        if tiles[n] == default_wall or n in new_list:
            continue
        already_filled = False
        for list in filled_lists:
            if n in list:
                already_filled = True
                break
        if not already_filled:
            new_list.append(n)
            if (n[0] - 1, n[1]) in tiles:
                Q.put((n[0] - 1, n[1]))
            if (n[0] + 1, n[1]) in tiles:
                Q.put((n[0] + 1, n[1]))
            if (n[0], n[1] - 1) in tiles:
                Q.put((n[0], n[1] - 1))
            if (n[0], n[1] + 1) in tiles:
                Q.put((n[0], n[1] + 1))
            if (n[0] - 1, n[1] - 1) in tiles:
                Q.put((n[0] - 1, n[1] - 1))
            if (n[0] - 1, n[1] + 1) in tiles:
                Q.put((n[0] - 1, n[1] + 1))
            if (n[0] + 1, n[1] + 1) in tiles:
                Q.put((n[0] + 1, n[1] + 1))
            if (n[0] + 1, n[1] - 1) in tiles:
                Q.put((n[0] + 1, n[1] - 1))
    return new_list

def get_adjacent_walls(room, x, y):
    wall_count = 0
    startx = x - 1
    starty = y - 1
    endx = x + 1
    endy = y + 1
    bounds = room.bounds
    for i_y in range(starty, endy + 1):
        for i_x in range(startx, endx + 1):
            if i_x < 0 or i_x >= bounds[0] or i_y < 0 or i_y >= bounds[1] or terrain.data[room.tiles[(i_x, i_y)]].isWall:
                wall_count += 1
    return wall_count


# Wander randomly from start point. Return a list of tiles visited
def drunken_walk(start_x, start_y, walls_block=True, water_blocks=True, min_length=10, max_length=10):
    max_length = min_length + libtcod.random_get_int(0, 0, max_length - min_length)
    current_length = 0
    current_pos = (start_x, start_y)
    return_tiles = [current_pos]
    while current_length < max_length:
        possible_moves = []
        for adj in main.adjacent_tiles_orthogonal(current_pos[0], current_pos[1]):
            adj_tile = map.tiles[adj[0]][adj[1]]
            if (adj_tile.is_water and water_blocks) or (adj_tile.blocks and walls_block):
                continue
            possible_moves.append(adj)
        if len(possible_moves) == 0:
            # nowhere to go - return the tiles we've visited so far
            return return_tiles
        current_pos = possible_moves[libtcod.random_get_int(0, 0, len(possible_moves) - 1)]
        return_tiles.append(current_pos)
        current_length += 1
    return return_tiles


def random_from_list(list):
    if list is None or len(list) == 0:
        return None
    i = libtcod.random_get_int(0, 0, len(list) - 1)
    return list[i]

def create_room_rectangle(terrain_options=None):
    room = Room()
    room.add_rectangle(tile_type=random_terrain(terrain_options))
    return room


def create_room_circle(terrain_options=None):
    room = Room()
    room.add_circle(tile_type=random_terrain(terrain_options))
    return room

def create_room_cloud(tile_type = None, min_radius=2, max_radius=5):
    room = Room()
    r = libtcod.random_get_int(0, min_radius, max_radius)
    if tile_type is None:
        room.add_circle(r=r,tile_type=random_terrain())
    else:
        room.add_circle(r=r, tile_type=tile_type)
    nodes = libtcod.random_get_int(0, 2 + r, 6 + r)
    for i in range(nodes):
        angle = (2 * math.pi / nodes) * (float(i) + 1.0)
        coord = int(round(float(r) * math.cos(angle))), int(round(float(r) * math.sin(angle)))
        nodesize = libtcod.random_get_int(0, min_radius / 2, max_radius / 2)

        if tile_type is None:
            room.add_circle(r=nodesize, x0=coord[0], y0=coord[1], tile_type=random_terrain())
        else:
            room.add_circle(r=nodesize, x0=coord[0], y0=coord[1], tile_type=tile_type)
    return room

def create_room(room):
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            dice = libtcod.random_get_int(0, 0, 3)
            if dice == 0:
                change_map_tile(x, y, 'shallow water')
            elif dice == 1:
                change_map_tile(x, y, 'grass floor')
            else:
                change_map_tile(x, y, default_floor)


def apply_room(room, clear_objects=False, hard_override=False, avg_elevation=False):

    elevations = {}

    for tile in room.tiles.keys():

        if tile[0] < 0 or tile[1] < 0 or tile[0] >= consts.MAP_WIDTH or tile[1] >= consts.MAP_HEIGHT:
            raise IndexError('Tile index out of range: ' + str(tile[0]) + ', ' + str(tile[1]))

        old_tile = map.tiles[tile[0]][tile[1]]
        if avg_elevation:
            if old_tile.elevation not in elevations:
                elevations[old_tile.elevation] = 1
            else:
                elevations[old_tile.elevation] += 1

        if not old_tile.no_overwrite or hard_override:

            new_tile_type = room.tiles[tile[0], tile[1]]
            if new_tile_type == 'wall':
                new_tile_type = default_wall
            elif new_tile_type == 'floor':
                new_tile_type = default_floor
            elif new_tile_type == 'ramp':
                new_tile_type = default_ramp

            change_map_tile(tile[0], tile[1], new_tile_type, room.no_overwrite, hard_override)
            #if new_tile_type == 'open':
            #    if old_tile.blocks:
            #        old_tile.tile_type = default_floor
            #else:
            #    old_tile.tile_type = room.tiles[tile[0], tile[1]]
            #old_tile.no_overwrite = room.no_overwrite
            if clear_objects or old_tile.blocks or old_tile.is_pit:
                for o in map.objects:
                    if o.x == tile[0] and o.y == tile[1] and o is not player.instance:
                        o.destroy()
            if tile in room.data.keys():
                line = room.data[tile]
                if len(line) == 0:
                    pass
                else:
                    apply_data(tile[0], tile[1], line)
                    if room.data[tile][0] == 'X':
                        room.link_points.append(tile)


    # Find most common elevation. Set all tiles to that elevation
    if avg_elevation:
        most_common_elevation = 0
        max_count = 0
        for elev in elevations.keys():
            if elevations[elev] >= max_count:
                most_common_elevation = elev
        for tile in room.tiles.keys():
            map.tiles[tile[0]][tile[1]].elevation = most_common_elevation
            for obj in main.get_objects(tile[0], tile[1]):
                obj.elevation = most_common_elevation

def apply_data(x, y, data):

    skip = 0
    for i in range(len(data)):
        if skip > 0:
            skip -= 1
            continue
        if data[i] == 'ELEVATION':
            map.tiles[x][y].elevation = int(data[i + 1])
            for obj in main.get_objects(x, y):
                obj.elevation = int(data[i + 1])
            skip = 1
        elif data[i].isdigit():
            apply_object(x, y, data[i:])
            break
        elif data[i] == '$':
            apply_item(x, y, data[i:])
            break
        elif data[i] == '>':
            for o in main.get_objects(x, y):
                o.destroy()
            map.objects.append(main.GameObject(x, y, '>', 'stairs', libtcod.white, always_visible=True))
        elif data[i] == '+' or data[i] == '*':
            door = create_door(x, y, locked=data[i] == '*')
            if door is not None:
                map.objects.append(door)
                door.send_to_back()

def apply_object(x, y, data):
    # Don't apply objects on the map's edge
    if x <= 0 or y <= 0 or x >= consts.MAP_WIDTH - 1 or y >= consts.MAP_HEIGHT - 1:
        return
    monster_id = None
    npc_id = None
    go_name = None
    go_description = None
    go_blocks = None
    go_char = None
    go_color= None
    for i in range(1, len(data)):
        if data[i] == 'MONSTER_ID':
            monster_id = data[i + 1]
            i += 1
        elif data[i] == 'NPC_ID':
            npc_id = data[i + 1]
            i += 1
        elif data[i] == 'GO_NAME':
            go_name = data[i + 1]
            i += 1
        elif data[i] == 'GO_BLOCKS':
            go_blocks = data[i + 1]
            i += 1
        elif data[i] == 'GO_CHAR':
            go_char = data[i + 1]
            i += 1
        elif data[i] == 'GO_COLOR':
            r = int(data[i + 1])
            g = int(data[i + 2])
            b = int(data[i + 3])
            go_color = libtcod.Color(r, g, b)
            i += 3
        elif data[i] == 'GO_DESCRIPTION':
            i += 1
            go_description = ''
            while not data[i].startswith('GO_'):
                go_description += data[i] + ' '
                i += 1
        elif data[i] == 'ELEVATION':
            map.tiles[x][y].elevation = data[i + 1]
            i += 1

    if monster_id is not None:
        main.spawn_monster(monster_id, x, y)
    elif npc_id is not None:
        main.spawn_npc(npc_id, x, y, map.name)
    elif go_name is not None:
        new_obj = main.GameObject(x, y, go_char, go_name, go_color, blocks=go_blocks, description=go_description)
        map.add_object(new_obj)

def apply_item(x, y, data):
    loot_level = None
    category = None
    item_id = None
    quality = None
    material = None
    loot_table = None
    if len(data) > 1:
        for i in range(1, len(data)):
            if data[i] == 'CHEST':
                chest = create_chest(x, y)
                if chest is not None:
                    map.add_object(chest)
                return
            if data[i] == 'LOOT_LEVEL':
                loot_level = int(data[i + 1])
            elif data[i] == 'CATEGORY':
                category = data[i + 1]
            elif data[i] == 'ITEM_ID':
                item_id = data[i + 1]
            elif data[i] == 'QUALITY':
                quality = data[i + 1]
            elif data[i] == 'MATERIAL':
                material = data[i + 1]
            elif data[i] == "LOOT_TABLE":
                loot_table = data[i + 1]
    if item_id:
        main.spawn_item(item_id, x, y, material=material, quality=quality)
    elif loot_table:
        item = loot.item_from_table_ex(loot_table, (loot_level if(loot_level is not None) else 1))
        if item is not None:
            item.x = x
            item.y = y
            map.add_object(item)
            item.send_to_back()
    else:
        item = create_random_loot(category=category, loot_level=loot_level)
        if item is not None:
            item.x = x
            item.y = y
            map.add_object(item)
            item.send_to_back()

def create_random_loot(category=None, loot_level=None):
    table = None
    tables = dungeon.branches[map.branch]['loot']
    if tables is not None:
        if category is None and loot_level is None:
            # choose a random loot table for this branch
            table = tables.keys()[libtcod.random_get_int(0, 0, len(tables.keys()) - 1)]
        elif category is not None and loot_level is None:
            # choose the first table matching this category
            for t in tables:
                if t.startswith(category):
                    table = t
                    break
            if table is None:
                for t in loot.table.keys():
                    if t.startswith(category):
                        table = t
                        break
        elif category is None and loot_level is not None:
            # choose a random table. Set its loot level to match.
            table = tables.keys()[libtcod.random_get_int(0, 0, len(tables.keys()) - 1)]
            table = table.split('_')[0]
            table += '_%d' % loot_level
        else:
            # we have both a category and a loot level
            table = category + '_' + str(loot_level)

    if table is not None:
        item = loot.item_from_table(map.branch, table)
        if item is not None:
            return item
        else:
            return None

def change_map_tile(x, y, tile_type, no_overwrite=False, hard_override=False):
    if not main.in_bounds(x, y):
        return 'out of range'
    if not map.tiles[x][y].no_overwrite or hard_override:
        if tile_type == 'open':
            if map.tiles[x][y].blocks:
                map.tiles[x][y].tile_type = default_floor
        else:
            map.tiles[x][y].tile_type = tile_type
        map.tiles[x][y].no_overwrite = no_overwrite


def create_perlin_tunnel(x1, y1, x2, y2, tile_type=None, min_width=1, max_width=1):
    changed = []
    if tile_type is None:
        tile_type = default_floor
    #determine longest axis
    if abs(x2 - x1) > abs(y2 - y1):
        # longest axis: X
        if x1 <= x2:
            start_x, end_x, start_y, end_y = x1, x2, y1, y2
        else:
            start_x, end_x, start_y, end_y = x2, x1, y2, y1
        noise = perlin_interpolate(start_x, end_x, start_y, end_y, 8, y_bounds=(1, consts.MAP_HEIGHT - 2))

        for i in range(len(noise) - 1):
            x = noise[i][0]
            y0 = int(noise[i][1])
            y1 = int(noise[min(i + 1, len(noise) - 1)][1])
            for y in range(min(y0, y1), max(y0, y1) + 1):
                w = libtcod.random_get_int(0, min_width, max_width)
                for i_x in range(w):
                    for i_y in range(w):
                        change_map_tile(x + i_x, y + i_y, tile_type)
                        changed.append((x + i_x, y + i_y))
    else:
        # longest axis: Y
        if y1 <= y2:
            start_x, end_x, start_y, end_y = x1, x2, y1, y2
        else:
            start_x, end_x, start_y, end_y = x2, x1, y2, y1
        noise = perlin_interpolate(start_y, end_y, start_x, end_x, 8, y_bounds=(1, consts.MAP_WIDTH - 2))

        for i in range(len(noise) - 1):
            y = noise[i][0]
            x0 = int(noise[i][1])
            x1 = int(noise[min(i + 1, len(noise) - 1)][1])
            for x in range(min(x0, x1), max(x0, x1) + 1):
                w = libtcod.random_get_int(0, min_width, max_width)
                for i_x in range(w):
                    for i_y in range(w):
                        change_map_tile(x + i_x, y + i_y, tile_type)
                        changed.append((x + i_x, y + i_y))
    return changed


def perlin_interpolate(x0, x1, y0, y1, height=None, y_bounds=None):
    if height is None:
        height = y1 - y0
    return _perlin_interpolate(x0, x1, y0, y1, max(height, abs(y1 - y0)), y_bounds=y_bounds) + [(x1, float(y1))]

def _perlin_interpolate(start_x, end_x, start_y, end_y, height, octave=1, y_bounds=None):
    if end_x - start_x > 4:
        v_half = start_x + int(math.floor((end_x - start_x) / 2))
        range_half = (end_y + start_y) / 2
        rand_range = height * (0.75 ** (octave - 1))
        rand_min = range_half - 0.5 * rand_range
        rand_max = range_half + 0.5 * rand_range
        if y_bounds is not None:
            if rand_min < y_bounds[0]:
                adjustment = y_bounds[0] - rand_min
                rand_min += adjustment
                rand_max += adjustment
            elif rand_max > y_bounds[1]:
                adjustment = rand_max - y_bounds[1]
                rand_min -= adjustment
                rand_max -= adjustment
        midpoint = libtcod.random_get_float(0, rand_min, rand_max)
        return _perlin_interpolate(start_x, v_half, start_y, midpoint, height, octave=octave + 1, y_bounds=y_bounds) + \
               _perlin_interpolate(v_half, end_x, midpoint, end_y, height, octave=octave + 1, y_bounds=y_bounds)
    else:
        values = []
        for i in range(start_x, end_x):
            g = float(i - start_x) / float(end_x - start_x)
            values.append((i, start_y + (end_y - start_y) * g))
        return values

def create_wandering_tunnel(x1, y1, x2, y2, tile_type=None, wide=True, hardoverride=False):
    if tile_type is None:
        tile_type = default_floor
    current_x = x1
    current_y = y1
    xdir = 0
    if x2 - x1 > 0:
        xdir = 1
    elif x2 - x1 < 0:
        xdir = -1
    ydir = 0
    if y2 - y1 > 0:
        ydir = 1
    elif y2 - y1 < 0:
        ydir = -1
    while not (current_x == x2 and current_y == y2):
        # determine what moves are legal from this position
        moves = []
        if current_x != x2:
            moves.append('x')
        if current_y != y2:
            moves.append('y')
        if current_x != x2 and current_y != y2:
            moves.append('xy')
        # choose a legal move at random
        move = moves[libtcod.random_get_int(0, 0, len(moves) - 1)]
        # move the current tile
        if move == 'x' or move == 'xy':
            current_x += xdir
        if move == 'y' or move == 'xy':
            current_y += ydir
        # replace terrain at current tile with floor
        change_map_tile(current_x, current_y, tile_type)
        if wide and (libtcod.random_get_int(0, 0, 1) == 0 or move == 'xy'):
            change_map_tile(current_x - 1, current_y, tile_type, hard_override=hardoverride)
            change_map_tile(current_x + 1, current_y, tile_type, hard_override=hardoverride)
            change_map_tile(current_x, current_y - 1, tile_type, hard_override=hardoverride)
            change_map_tile(current_x, current_y + 1, tile_type, hard_override=hardoverride)


def create_h_tunnel(x1, x2, y, tile_type=default_floor):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        change_map_tile(x, y, tile_type)


def create_v_tunnel(y1, y2, x, tile_type=default_floor):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        change_map_tile(x, y, tile_type)


def create_hv_tunnel(x1, y1, x2, y2, tile_type=default_floor):
    if libtcod.random_get_float(0,0,1) < 0.5:
        create_v_tunnel(y1,y2,x1,tile_type)
        create_h_tunnel(x1, x2, y2, tile_type)
    else:
        create_h_tunnel(x1, x2, y1, tile_type)
        create_v_tunnel(y1, y2, x2, tile_type)

def scatter_reeds(tiles, probability=20):
    for tile in tiles:
        if libtcod.random_get_int(0, 1, 100) < probability and not map.tiles[tile[0]][tile[1]].blocks:
            create_reed(tile[0], tile[1])


def scatter_blightweed(start_tile):
    tiles = drunken_walk(start_tile[0], start_tile[1], walls_block=True, water_blocks=False, min_length=8, max_length=24)
    for tile in tiles:
        create_blightweed(tile[0], tile[1])


def fill_blightweed(tiles):
    for tile in tiles:
        if map.tiles[tile[0]][tile[1]].tile_type == 'dry grass':
            create_blightweed(tile[0], tile[1])


def create_terrain_patch(start, terrain_type, min_patch=20, max_patch=400, cross_elevation=False, overwrite=False):
    patch_limit = min_patch + libtcod.random_get_int(0, 0, max_patch - min_patch)
    patch_count = 0
    Q = Queue.Queue()
    Q.put(start)
    changed_tiles = []
    while not Q.empty() and patch_count < patch_limit:
        tile = Q.get()
        map.tiles[tile[0]][tile[1]].tile_type = terrain_type
        changed_tiles.append(tile)
        patch_count += 1
        adjacent = []

        for adj in main.adjacent_tiles_diagonal(tile[0], tile[1]):
            adj_tile = map.tiles[adj[0]][adj[1]]
            if overwrite or (not adj_tile.blocks and not adj_tile.is_water and not adj_tile.is_ramp and
                    (cross_elevation or adj_tile.elevation == map.tiles[tile[0]][tile[1]].elevation)):
                adjacent.append(adj)

        for i in range(3):
            if len(adjacent) > 0:
                index = libtcod.random_get_int(0, 0, len(adjacent) - 1)
                Q.put(adjacent[index])
                adjacent.remove(adjacent[index])
    return changed_tiles


def create_reed(x, y):
    import actions.on_step_actions
    obj = main.get_objects(x, y)
    if len(obj) > 0:
        return  # object in the way
    type_here = map.tiles[x][y].tile_type
    if type_here == 'deep water':
        map.tiles[x][y].tile_type = 'shallow water'
    elif type_here != 'shallow water' and type_here != 'mud':
        map.tiles[x][y].tile_type = 'grass floor'
    reed = main.GameObject(x, y, 244, 'reeds', libtcod.darker_green, always_visible=True, description='A thicket of '
                           'reeds so tall they obstruct your vision. They are easily crushed underfoot.'
                           , blocks_sight=True, on_step=actions.on_step_actions.step_on_reed, burns=True)
    map.add_object(reed)


def create_blightweed(x, y):
    import actions.on_step_actions
    obj = main.get_objects(x, y)
    if len(obj) > 0:
        return None # object in the way
    tile_here = map.tiles[x][y]
    if tile_here.tile_type == 'deep water' or tile_here.blocks:
        return None # blocked
    weed = main.GameObject(x, y, 244, 'blightweed', libtcod.desaturated_red, always_visible=True, description=
                           'A cursed, twisted plant bristling with menacing, blood-red thorns. It catches and shreds the'
                           ' armor of those who attempt to pass through it.', on_step=actions.on_step_actions.step_on_blightweed, burns=True)
    map.add_object(weed)


def create_chest(x, y):
    obj = main.get_objects(x, y)
    if len(obj) > 0:
        return None # object in the way
    chest = main.GameObject(x, y, '$', 'locked chest', libtcod.yellow, always_visible=True,
                            description='A sturdy wooden chest, secured by a lock. What loot might be inside?',
                            blocks_sight=False, blocks=True, burns=False, interact=main.chest_interact,
                            background_color=libtcod.dark_sepia)
    return chest


def create_door(x, y, locked=False):
    obj = main.get_objects(x, y)
    if len(obj) > 0:
        return None # object in the way
    type_here = map.tiles[x][y].tile_type
    if terrain.data[type_here].isFloor:
        change_map_tile(x, y, default_floor)
    if locked:
        name = 'locked door'
        color = libtcod.darkest_flame
        description = 'A heavy stone door with a keyhole in the center. It is locked.'
    else:
        name = 'door'
        color = libtcod.dark_sepia
        description = 'A sturdy wooden door'
    door = main.GameObject(x, y, '+', name, libtcod.brass, always_visible=True, description=description,
                           blocks_sight=True, blocks=False, burns=True, interact=main.door_interact,
                           background_color=color)
    door.locked = locked
    door.closed = True
    return door

def create_gate_switch(gatex,gatey,switchx,switchy):
    obj = main.get_objects(gatex, gatey)
    if len(obj) > 0:
        return None,None  # object in the way

    type_here = map.tiles[gatex][gatey].tile_type
    if terrain.data[type_here].isFloor:
        change_map_tile(gatex, gatey, default_floor)
    description = 'A heavy iron gate, locked by some unknown mechanism.'
    door = main.GameObject(gatex, gatey, '=', 'iron gate', libtcod.brass, always_visible=True, description=description,
                           blocks_sight=True, blocks=False, burns=False, background_color=libtcod.darkest_flame,
                           interact=main.door_interact)
    door.locked = True
    door.closed = True

    switch = main.GameObject(switchx, switchy, '!', 'hanging chain', libtcod.dark_gray, always_visible=True,
                             description='A hanging chain. Enticingly pullable.', blocks_sight=False, blocks=False,
                             burns=False, interact=lambda o,a: main.switch_interact(door), background_color=libtcod.darkest_flame)

    return door, switch

def initialize_features():
    global feature_categories, features
    feature_categories = {}
    features = {}
    load_features_from_file('features.txt')

def load_features_from_file(filename):
    global feature_categories, features
    feature_file = open(filename, 'r')
    lines = feature_file.read().split('\n')
    while len(lines) > 0:
        current_line = lines[0]
        lines.remove(lines[0])
        if current_line.startswith('//'):
            continue
        if current_line.startswith('IMPORT'):
            load_features_from_file(current_line.split(' ')[1])
            continue

        if current_line.startswith('FEATURE'):
            name = current_line.split(' ')[1]

            feature_lines = []
            categories = []
            while lines[0] != 'ENDFEATURE':
                if not lines[0].startswith('//') and not lines[0].startswith('CATEGORY'):
                    feature_lines.append(lines[0])
                if lines[0].startswith('CATEGORY'):
                    cat_line = lines[0].split()
                    for i in range(1, len(cat_line)):
                        categories.append(cat_line[i])
                lines.remove(lines[0])
            new_feature = load_feature(feature_lines)
            new_feature.name = name

            if len(categories) == 0:
                categories.append('default')
            for category in categories:
                if category in feature_categories.keys():
                    feature_categories[category].append(new_feature)
                else:
                    feature_categories[category] = [new_feature]
            features[name] = new_feature


file_key = {
    ' ' : None,
    '.' : 'floor',
    ',' : 'grass floor',
    '#' : 'wall',
    '-' : 'shallow water',
    '~' : 'deep water',
    ':' : 'chasm',
    '_' : 'open',
    '/' : 'ramp',
}
def load_feature(lines=[]):
    try:
        #stuff
        new_feature = Feature()
        feature_room = Room()
        feature_room.no_overwrite = True
        default_ground = '.'
        loot_string = '$'
        data_strings = {}
        script_strings = []
        redefined = {}
        height = None
        y_index = 0
        for i_y in range(len(lines)):
            if lines[i_y].startswith('FLAGS'):
                f = lines[i_y].split(' ')
                for flag in f[1:]:
                    if flag == 'NOROTATE':
                        new_feature.set_flag(NOROTATE)
                    elif flag == 'NOREFLECT':
                        new_feature.set_flag(NOREFLECT)
                    elif flag == 'NOSPAWNS':
                        new_feature.set_flag(NOSPAWNS)
                    elif flag == 'NOELEV':
                        new_feature.set_flag(NOELEV)
                    elif flag == 'SPECIAL':
                        new_feature.set_flag(SPECIAL)
            elif lines[i_y].startswith('DEFAULT'):
                default_ground = lines[i_y].split(' ')[1]
            elif lines[i_y].startswith('DEFINE'):
                line = lines[i_y].split(' ')[1:]
                if line[0] == '$':
                    loot_string = line
                elif line[0].isdigit():
                    digit = int(line[0])
                    data_strings[digit] = line
                elif line[0] in file_key.keys():
                    redefined[line[0]] = ' '.join(line[1:])
            elif lines[i_y].startswith('SCRIPT'):
                for script in lines[i_y].split(' ')[1:]:
                    script_strings.append(script)
            elif lines[i_y].startswith('HEIGHT'):
                height = int(lines[i_y].split(' ')[1])
                y_index = 0
            elif lines[i_y].startswith('ENDHEIGHT'):
                height = None
            elif lines[i_y].startswith('CATEGORY'):
                pass
            else:
                for i_x in range(len(lines[i_y])):
                    c = lines[i_y][i_x]

                    if c in redefined.keys():
                        tile_type = redefined[c]
                    elif c in file_key.keys():
                        tile_type = file_key[c]
                    else:
                        if default_ground in redefined.keys():
                            tile_type = redefined[default_ground]
                        else:
                            tile_type = file_key[default_ground]

                    if tile_type is not None:
                        feature_room.set_tile(i_x, y_index, tile_type, height)

                    if c == '$':
                        if (i_x, y_index) in feature_room.data.keys():
                            for s in loot_string:
                                feature_room.data[(i_x, y_index)].append(s)
                        else:
                            feature_room.data[(i_x, y_index)] = loot_string
                    elif c == '>' or c == '+' or c == '*' or c == 'X':
                        if (i_x, y_index) in feature_room.data.keys():
                            feature_room.data[(i_x, y_index)].append(c)
                        else:
                            feature_room.data[(i_x, y_index)] = c
                    elif 65 <= ord(c) <= 90 or 97 <= ord(c) <= 122:
                        feature_room.key_points[c] = (i_x, y_index)
                    elif c.isdigit():
                        if (i_x, y_index) in feature_room.data.keys():
                            for s in data_strings[int(c)]:
                                feature_room.data[(i_x, y_index)].append(s)
                        else:
                            feature_room.data[(i_x, y_index)] = data_strings[int(c)]
                y_index += 1

        new_feature.room = feature_room
        for script in script_strings:
            new_feature.scripts.append(script)
        return new_feature
    except:
        raise IOError('Input could not be parsed.')


def create_feature(x, y, feature_name, open_tiles=None, hard_override=False, rotation=None):
    if feature_name not in features.keys():
        return 'feature not found'
    else:
        feature = features[feature_name]
        template = copy.copy(feature.room)

        if feature.has_flag(SPECIAL):
            if map.has_special:
                return 'failed'
            else:
                map.has_special = True

        if not feature.has_flag(NOREFLECT):
            template.reflect(reflect_x=libtcod.random_get_int(0, 0, 1) == 1, reflect_y=libtcod.random_get_int(0, 0, 1) == 1)

        if rotation is not None:
            template.rotate(rotation)
        elif not feature.has_flag(NOROTATE):
            rotation = angles[libtcod.random_get_int(0, 0, 3)]
            template.rotate(rotation)
        else:
            rotation = 0


        template.set_pos(x, y)
        adj_x = adj_y = 0
        if template.min_x < 1:
            adj_x = -template.min_x
        if template.max_x >= consts.MAP_WIDTH - 1:
            adj_x = consts.MAP_WIDTH - template.max_x - 1
        if template.min_y < 1:
            adj_y = -template.min_y
        if template.max_y >= consts.MAP_WIDTH - 1:
            adj_y = consts.MAP_WIDTH - template.max_y - 1
        template.set_pos(x + adj_x, y + adj_y)

        # Check to see if our new feature collides with any existing features
        if not hard_override:
            new_rect = Rect(template.pos[0] - template.width / 2, template.pos[1] - template.height / 2, template.bounds[0], template.bounds[1])
            for rect in feature_rects:
                if rect.intersect(new_rect):
                    return 'failed'
            feature_rects.append(new_rect)

        apply_room(template, feature.has_flag(NOSPAWNS), hard_override=hard_override, avg_elevation=feature.has_flag(NOELEV))

        if open_tiles is not None:
            # If feature has NOSPAWNS flag, remove all tiles from 'open_tiles' list
            if feature.has_flag(NOSPAWNS):
                for tile in template.tiles.keys():
                    if tile in open_tiles:
                        open_tiles.remove(tile)
            else:  # Otherwise remove only the tiles that are now blocking and add the tiles that are now open
                for tile in template.get_blocked_tiles():
                    if tile in open_tiles:
                        open_tiles.remove(tile)
                for tile in template.get_open_tiles():
                    if tile not in open_tiles:
                        open_tiles.append(tile)

        apply_scripts(feature, room=template)

        return template

def apply_scripts(feature, room=None):
    for script in feature.scripts:
        if script == 'scatter_reeds':
            scatter_reeds(room.get_open_tiles())
        elif script == 'fill_blightweed':
            fill_blightweed(room.get_open_tiles())
        elif script == 'create_slopes':
            create_slopes(room.get_open_tiles())
        elif script == 'your script here':
            pass

def clear_borders_from_open_set(open_tiles):
    for x in range(consts.MAP_WIDTH):
        if (x, 0) in open_tiles:
            open_tiles.remove((x, 0))
        if (x, consts.MAP_HEIGHT - 1) in open_tiles:
            open_tiles.remove((x, consts.MAP_HEIGHT - 1))
    for y in range(consts.MAP_WIDTH):
        if (0, y) in open_tiles:
            open_tiles.remove((0, y))
        if (consts.MAP_WIDTH - 1, y) in open_tiles:
            open_tiles.remove((consts.MAP_WIDTH - 1, y))

def choose_random_tile(tile_list, exclusive=True):
    chosen_tile = tile_list[libtcod.random_get_int(0, 0, len(tile_list) - 1)]
    if exclusive:
        tile_list.remove(chosen_tile)
    return chosen_tile

def create_voronoi(h,w,m,n,features=[], max_dist=8.0, border=4):
    result = [[0 for x in range(w)] for y in range(h)]
    # create random feature points
    f = [(random.randint(border,w - (1 + border)),random.randint(border,h - (1 + border))) for i in range(m)] + features
    for x in range(w):
        for y in range(h):
            # Build a list of distances to each feature. little optimization here, don't sqrt values until they're needed
            dist = [math.fabs((x-x2) ** 2 + (y-y2) ** 2) for (x2,y2) in f]
            dist.sort()
            dist = [math.sqrt(a) for a in dist[:n]]
            # Sum the n closest features
            result[x][y] = math.ceil(math.fsum(dist)/n)
            # Scale result to a 0.0 to 1.0 scale where 1.0 is 0 dist from feature point and 0.0 is max_dist or greater
            # distance from a feature point
            result[x][y] = main.clamp((float(max_dist - result[x][y]) / max_dist), 0.0, 1.0)
    return result, f

def create_coastline(height):
    shore_noise = libtcod.noise_new(1)
    shore_y = height
    for x in range(consts.MAP_WIDTH):
        shore = libtcod.noise_get_fbm(shore_noise, [float(x) / 10.0, float(x) / 10.0 + 1.0], libtcod.NOISE_PERLIN)
        this_shore = shore_y + int(shore * 10)
        for y in range(consts.MAP_HEIGHT - 1, this_shore, -1):
            change_map_tile(x, y, 'shallow seawater')
        for y in range(consts.MAP_HEIGHT - 1, shore_y + 6 + int(shore * 8), -1):
            change_map_tile(x, y, 'deep seawater')


def erode_map(floor_type=default_floor, iterations=1):
    for i in range(iterations):
        eroded = []
        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):
                if not map.tiles[x][y].is_wall:
                    continue
                open_count = 0
                adjacent = main.adjacent_tiles_diagonal(x, y)
                for tile in adjacent:
                    if not map.tiles[tile[0]][tile[1]].is_wall:
                        open_count += 1
                if libtcod.random_get_int(0, 0, 4) < open_count:
                    eroded.append((x, y))
        for tile in eroded:
            change_map_tile(tile[0], tile[1], floor_type)


def create_slopes(tiles=None):

    if tiles is None:
        tiles = []
        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):
                tiles.append((x, y))

    for tile in tiles:
        this_tile = map.tiles[tile[0]][tile[1]]
        if this_tile.is_wall:
            continue
        for adj in main.adjacent_tiles_diagonal(tile[0], tile[1]):
            adj_tile = map.tiles[adj[0]][adj[1]]
            if adj_tile.elevation < this_tile.elevation:
                change_map_tile(tile[0], tile[1], default_ramp, hard_override=True)
                break

def create_hills(perlin_scaling=4.0, height_scaling=4.0):
    height_noise = libtcod.noise_new(2)
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            elevation = libtcod.noise_get(height_noise, [perlin_scaling * (float(x) / float(consts.MAP_WIDTH)),
                                                         perlin_scaling * (float(y) / float(consts.MAP_HEIGHT))],
                                          libtcod.NOISE_PERLIN)
            elevation += 0.5
            elevation = int(elevation * height_scaling)
            if elevation > 0:
                change_map_tile(x, y, default_floor)
                map.tiles[x][y].elevation = elevation - 1

def make_rooms_and_corridors():

    rooms = []
    num_rooms = 0

    for r in range(consts.MG_MAX_ROOMS):

        room_array = create_room_random()
        dimensions = room_array.bounds

        x = libtcod.random_get_int(0, 1, consts.MAP_WIDTH - dimensions[0] - 1)
        y = libtcod.random_get_int(0, 1, consts.MAP_HEIGHT - dimensions[1] - 1)

        room_bounds = Rect(x, y, dimensions[0], dimensions[1])

        failed = False
        for other_room in rooms:
            if room_bounds.intersect(other_room):
                failed = True
                break

        if not failed:
            # create_room(new_room)
            room_array.set_pos(room_bounds.x1, room_bounds.y1)
            apply_room(room_array)
            (new_x, new_y) = room_array.center()

            if num_rooms == 0:
                player.instance.x = new_x
                player.instance.y = new_y
            else:
                (prev_x, prev_y) = rooms[num_rooms - 1].center()
                create_wandering_tunnel(prev_x, prev_y, new_x, new_y)
                # if libtcod.random_get_int(0, 0, 1) == 0:
                #    create_h_tunnel(prev_x, new_x, prev_y)
                #    create_v_tunnel(prev_y, new_y, new_x)
                # else:
                #    create_v_tunnel(prev_y, new_y, prev_x)
                #    create_h_tunnel(prev_x, new_x, new_y)
            #main.place_objects(room_array.get_open_tiles())
            if libtcod.random_get_int(0, 0, 5) == 0:
                scatter_reeds(room_array.get_open_tiles())
            rooms.append(room_bounds)
            num_rooms += 1

    # Generate every-floor random features
    sample = random.sample(rooms, 2)
    #x, y = sample[0].center()
    #main.stairs = main.GameObject(x, y, '<', 'stairs downward', libtcod.white, always_visible=True)
    #map.objects.append(main.stairs)
    #main.stairs.send_to_back()
    #x, y = sample[len(sample) - 1].center()
    #level_shrine = main.GameObject(x, y, '=', 'shrine of power', libtcod.white, always_visible=True, interact=None)
    #map.add_object(level_shrine)
    #level_shrine.send_to_back()

def mirror_map():
    for x in range(consts.MAP_WIDTH / 2):
        for y in range(consts.MAP_HEIGHT):
            change_map_tile(consts.MAP_WIDTH - 1 - x, y, map.tiles[x - 1][y].tile_type)

def make_garden_connections(room, direction):
    other = room.connections[direction]
    if other is None: return
    if other.connections[main.opposite_direction(direction)] == room:
        other.connections[main.opposite_direction(direction)] = None
    if direction == 'right' or direction == 'left':
        if direction == 'right':
            x_r = (room.max_x, other.min_x)
        else:
            x_r = (other.max_x, room.min_x)
        if other.height < room.height:
            if other.height % 2 == 0:
                y_r = (other.center()[1] - 1, other.center()[1])
            else:
                y_r = (other.center()[1], other.center()[1])
        else:
            if room.height % 2 == 0:
                y_r = (room.center()[1] - 1, room.center()[1])
            else:
                y_r = (room.center()[1], room.center()[1])
            if abs(y_r[0] - other.max_y) < 1 or abs(y_r[0] - other.min_y) < 2:
                return
    else:
        if direction == 'bottom':
            y_r = (room.max_y, other.min_y)
        else:
            y_r = (other.max_y, room.min_y)
        if other.width < room.width:
            if other.width % 2 == 0:
                x_r = (other.center()[0] - 1, other.center()[0])
            else:
                x_r = (other.center()[0], other.center()[0])
        else:
            if room.width % 2 == 0:
                x_r = (room.center()[0] - 1, room.center()[0])
            else:
                x_r = (room.center()[0], room.center()[0])
            if abs(x_r[0] - other.max_x) < 1 or abs(x_r[0] - other.min_x) < 2:
                return
    tiles = []
    for y in range(y_r[0], y_r[1] + 1):
        for x in range(x_r[0], x_r[1] + 1):
            if map.tiles[x][y].tile_type == default_wall:
                change_map_tile(x, y, 'marble path', no_overwrite=True)
                tiles.append((x, y))
            if (x, y) in room.tiles.keys():
                room.data[(x, y)] = 'nowall'
            if (x, y) in other.tiles.keys():
                other.data[(x, y)] = 'nowall'
    if len(tiles) > 0:
        decorate_garden_connection(tiles, direction == 'top' or direction == 'bottom')
    else:
        pass

def decorate_garden_connection(tiles, horizontal, tile_type=None):
    if tile_type is None:
        options = ['cypress tree', 'hedge']
        tile_type = options[libtcod.random_get_int(0, 0, len(options) - 1)]
    if horizontal:
        left = min(tiles[0][0], tiles[len(tiles) - 1][0])
        right = max(tiles[0][0], tiles[len(tiles) - 1][0])
        change_map_tile(left - 1, tiles[0][1], tile_type, no_overwrite=True)
        change_map_tile(right + 1, tiles[0][1], tile_type, no_overwrite=True)
    else:
        top = min(tiles[0][1], tiles[len(tiles) - 1][1])
        bottom = max(tiles[0][1], tiles[len(tiles) - 1][1])
        change_map_tile(tiles[0][0], top - 1, tile_type, no_overwrite=True)
        change_map_tile(tiles[0][0], bottom + 1, tile_type, no_overwrite=True)

def make_garden_rooms(leaf):
    if leaf.left is None or leaf.right is None:
        room = Room()
        for x in range(leaf.w):
            room.set_tile(x, 0, default_wall)
            room.set_tile(x, leaf.h, default_wall)
        for y in range(leaf.h):
            room.set_tile(0, y, default_wall)
            room.set_tile(leaf.w, y, default_wall)
        room.set_pos(leaf.x + room.width / 2, leaf.y + room.height / 2)
        apply_room(room)
    else:
        make_garden_rooms(leaf.left)
        make_garden_rooms(leaf.right)

def decorate_garden_room(room):
    w = room.width
    h = room.height
    shortest = min(w, h)
    # Set default ground
    garden_set_default_ground(room)
    # Border
    border_decorations = [garden_corners, garden_small_corners, garden_passable_border]
    if shortest >= 7:
        border_decorations.append(garden_border)
        border_decorations.append(garden_large_corners)
        if w % 2 == 1 and h % 2 == 1:
            border_decorations.append(garden_border_staggered_1)
    if h >= 7:
        border_decorations.append(garden_border_h)
    if w >= 7:
        border_decorations.append(garden_border_v)
    border_decorations.append(None)
    choice = border_decorations[libtcod.random_get_int(0, 0, len(border_decorations) - 1)]
    if choice is not None:
        choice(room)
    garden_fill_center(room)
    if len(room.tiles) > 0:
        garden_center_features(room)

def garden_set_default_ground(room, type=None):
    if type is None:
        types=['grass floor', 'marble path']
        type = types[libtcod.random_get_int(0, 0, len(types) - 1)]
    if room.min_x is None:
        return
    room.default_floor = type
    for y in range(room.min_y, room.max_y + 1):
        for x in range(room.min_x, room.max_x + 1):
            change_map_tile(x, y, type)

def garden_fill_center(room, type=None):
    if type is None:
        if room.default_floor == 'grass floor':
            type = 'marble path'
        else:
            type = 'grass floor'
    to_remove = []
    for tile in room.tiles:
        if (tile[0], tile[1] + 1) in room.tiles.keys() and \
                        (tile[0], tile[1] - 1) in room.tiles.keys() and \
                        (tile[0] + 1, tile[1]) in room.tiles.keys() and \
                        (tile[0] - 1, tile[1]) in room.tiles.keys() and \
                        (tile[0] - 1, tile[1] + 1) in room.tiles.keys() and \
                        (tile[0] - 1, tile[1] - 1) in room.tiles.keys() and \
                        (tile[0] + 1, tile[1] + 1) in room.tiles.keys() and \
                        (tile[0] + 1, tile[1] - 1) in room.tiles.keys():
            change_map_tile(tile[0], tile[1], type)
        else:
            to_remove.append(tile)
    for tile in to_remove:
        room.remove_tile(tile[0], tile[1])

def garden_passable_border(room):
    w = room.width
    h = room.height
    types=['grass floor', 'shallow water']
    fncs = [garden_border, garden_border_h, garden_border_v, garden_corners, garden_large_corners]
    if w % 2 == 1 and h % 2 == 1:
        fncs.append(garden_border_staggered_1)
    fncs[libtcod.random_get_int(0, 0, len(fncs) - 1)](room, types[libtcod.random_get_int(0, 0, len(types) - 1)])

def garden_border(room, terrain_type='hedge'):
    min_x = room.min_x
    max_x = room.max_x
    min_y = room.min_y
    max_y = room.max_y
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if x == min_x or x == max_x or y == min_y or y == max_y:
                if (x, y) not in room.data.keys():
                    change_map_tile(x, y, terrain_type)
                    room.remove_tile(x, y)

def garden_border_h(room, terrain_type=None):
    if terrain_type is None:
        types=['hedge', 'cypress tree']
        terrain_type = types[libtcod.random_get_int(0, 0, len(types) - 1)]

    for x in range(room.min_x, room.max_x + 1):
        if (x, room.min_y) not in room.data.keys():
            change_map_tile(x, room.min_y, terrain_type)
            room.remove_tile(x, room.min_y)
        if (x, room.max_y) not in room.data.keys():
            change_map_tile(x, room.max_y, terrain_type)
            room.remove_tile(x, room.max_y)

def garden_border_v(room, terrain_type=None):
    if terrain_type is None:
        types=['hedge', 'cypress tree']
        terrain_type = types[libtcod.random_get_int(0, 0, len(types) - 1)]
    for y in range(room.min_y, room.max_y + 1):
        if (room.min_x, y) not in room.data.keys():
            change_map_tile(room.min_x, y, terrain_type)
            room.remove_tile(room.min_x, y)
        if (room.max_x, y) not in room.data.keys():
            change_map_tile(room.max_x, y, terrain_type)
            room.remove_tile(room.max_x, y)

def garden_border_staggered_1(room, terrain_type='cypress tree'):
    min_x = room.min_x
    max_x = room.max_x
    min_y = room.min_y
    max_y = room.max_y
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if x == min_x or x == max_x or y == min_y or y == max_y:
                room.remove_tile(x, y)
                if (x - min_x) % 2 == 0 and (y - min_y) % 2 == 0 and (x, y) not in room.data.keys():
                    change_map_tile(x, y, terrain_type)

def garden_small_corners(room, tile_type='cypress tree'):
    corners = [
        (room.min_x, room.min_y),
        (room.max_x, room.min_y),
        (room.min_x, room.max_y),
        (room.max_x, room.max_y),
    ]
    for corner in corners:
        change_map_tile(corner[0], corner[1], tile_type)
        room.remove_tile(corner[0], corner[1])

def garden_corners(room, tile_type='hedge'):
    corners = [
        (room.min_x, room.min_y),
        (room.min_x + 1, room.min_y),
        (room.min_x, room.min_y + 1),
        (room.max_x, room.min_y),
        (room.max_x - 1, room.min_y),
        (room.max_x, room.min_y + 1),
        (room.min_x, room.max_y),
        (room.min_x + 1, room.max_y),
        (room.min_x, room.max_y - 1),
        (room.max_x, room.max_y),
        (room.max_x - 1, room.max_y),
        (room.max_x, room.max_y - 1),
    ]
    for corner in corners:
        change_map_tile(corner[0], corner[1], tile_type)
        room.remove_tile(corner[0], corner[1])

def garden_large_corners(room, tile_type='marble wall', size=2):
    s = size - 1
    min_x = room.min_x
    max_x = room.max_x
    min_y = room.min_y
    max_y = room.max_y
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if (abs(x - min_x) <= s and abs(y - min_y) <= 1) or \
                    (abs(x - max_x) <= s and abs(y - min_y) <= s) or \
                    (abs(x - min_x) <= s and abs(y - max_y) <= s) or \
                    (abs(x - max_x) <= s and abs(y - max_y) <= s):
                change_map_tile(x, y, tile_type)
                room.remove_tile(x, y)

def garden_center_features(room):
    w = room.width
    h = room.height
    choices = []
    legal_features = [feature.name for feature in feature_categories['garden'] if
                      ((feature.room.width <= w and feature.room.height <= h and feature.room.width % 2 == w % 2 and feature.room.height % 2 == h % 2) or
                       (feature.room.height <= w and feature.room.width <= h and feature.room.height % 2 == w % 2 and feature.room.width % 2 == h % 2))]
    if len(legal_features) > 0:
        choices.append((garden_make_feature, legal_features[libtcod.random_get_int(0, 0, len(legal_features) - 1)]))
    if w % 2 == 1 and h % 2 == 1:
        choices.append((garden_cross_small, None))
        if w > 5 and h > 5:
            choices.append((garden_cross_large, None))
    if w >= 5 and h >= 5:
        choices.append((garden_inner_walls, None))
    #choices.append(None)
    if len(choices) > 0 and main.roll_dice('1d1') == 1:
        choice = choices[libtcod.random_get_int(0, 0, len(choices) - 1)]
        if choice is not None:
            choice[0](room, choice[1])

def garden_make_feature(room, feature):
    c = room.center()
    f = features[feature]
    H = False
    V = False
    if room.width >= f.room.width and room.width % 2 == f.room.width % 2:
        H = True
    if room.height >= f.room.width and room.height % 2 == f.room.width % 2:
        V = True
    if H and not V:
        rotation = angles[0]
    elif V and not H:
        rotation = angles[1]
    elif V and H:
        opts = [angles[0], angles[1], angles[2], angles[3]]
        rotation = opts[libtcod.random_get_int(0, 0, 1)]
    else:
        return
    create_feature(c[0], c[1], feature, rotation=rotation)

def garden_cross_small(room, tile_type=None):
    c = room.center()
    if tile_type is None:
        types = ['hedge', 'cypress tree', 'marble wall', 'chasm', 'shallow water', 'deep water']
        tile_type = types[libtcod.random_get_int(0, 0, len(types) - 1)]
    change_map_tile(c[0], c[1], tile_type)
    change_map_tile(c[0] + 1, c[1], tile_type)
    change_map_tile(c[0] - 1, c[1], tile_type)
    change_map_tile(c[0], c[1] + 1, tile_type)
    change_map_tile(c[0], c[1] - 1, tile_type)

def garden_cross_large(room, tile_type=None):
    c = room.center()
    if tile_type is None:
        types = ['hedge', 'cypress tree', 'marble wall', 'chasm', 'shallow water', 'deep water']
        tile_type = types[libtcod.random_get_int(0, 0, len(types) - 1)]
    for x in range(c[0] - 2, c[0] + 3):
        change_map_tile(x, c[1], tile_type)
    for y in range(c[1] - 2, c[1] + 3):
        change_map_tile(c[0], y, tile_type)

def garden_inner_walls(room, tile_type=None):
    center_x = [room.center()[0]]
    center_y = [room.center()[1]]
    if room.width % 2 == 0:
        center_x.append(room.center()[0] - 1)
    if room.height % 2 == 0:
        center_y.append(room.center()[1] - 1)
    if tile_type is None:
        types = ['hedge', 'marble wall']
        tile_type = types[libtcod.random_get_int(0, 0, len(types) - 1)]
    for tile in room.tiles.keys():
        if (tile[0], tile[1] + 1) in room.tiles.keys() and \
                        (tile[0], tile[1] - 1) in room.tiles.keys() and \
                        (tile[0] + 1, tile[1]) in room.tiles.keys() and \
                        (tile[0] - 1, tile[1]) in room.tiles.keys() and \
                        (tile[0] - 1, tile[1] + 1) in room.tiles.keys() and \
                        (tile[0] - 1, tile[1] - 1) in room.tiles.keys() and \
                        (tile[0] + 1, tile[1] + 1) in room.tiles.keys() and \
                        (tile[0] + 1, tile[1] - 1) in room.tiles.keys():
            continue
        if tile[0] not in center_x and tile[1] not in center_y:
            change_map_tile(tile[0], tile[1], tile_type)

def make_map_garden():
    import random

    for x in range(consts.MAP_WIDTH):
        for y in range(consts.MAP_HEIGHT):
            change_map_tile(x, y, default_floor)
    root = BSP_Leaf(0, 0, consts.MAP_WIDTH / 2 + 1, consts.MAP_HEIGHT - 1)
    root.split_recursive()
    make_garden_rooms(root)
    mirror_map()

    # arrange the cells into new Room objects
    garden_cells = []
    filled_lists = []
    tiles = {}
    for x in range(consts.MAP_WIDTH):
        for y in range(consts.MAP_HEIGHT):
            tiles[(x, y)] = map.tiles[x][y].tile_type
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            if (x, y) in tiles.keys() and tiles[(x, y)] != default_wall:
                if len(filled_lists) > 0:
                    for filled in filled_lists:
                        if (x, y) in filled:
                            continue
                new_list = flood_fill(tiles, filled_lists, x, y)
                if len(new_list) > 0:
                    filled_lists.append(new_list)

    for filled in filled_lists[1:]:
        new_cell = Room()
        for tile in filled:
            new_cell.set_tile(tile[0], tile[1], map.tiles[tile[0]][tile[1]].tile_type)
        garden_cells.append(new_cell)

    # Make connections
    for cell in garden_cells:
        cell.connections = {
            'left' : None,
            'right' : None,
            'top' : None,
            'bottom' : None,
        }
    for cell in garden_cells:
        left = cell.min_x - 2
        right = cell.max_x + 2
        top = cell.min_y - 2
        bottom = cell.max_y + 2
        c = cell.center()
        for other in garden_cells:
            if cell.connections['left'] is None and left > 0 and (left, c[1]) in other.tiles.keys():
                cell.connections['left'] = other
                other.connections['right'] = cell
            if cell.connections['right'] is None and right < consts.MAP_WIDTH - 2 and (right, c[1]) in other.tiles.keys():
                cell.connections['right'] = other
                other.connections['left'] = cell
            if cell.connections['top'] is None and top > 0 and (c[0], top) in other.tiles.keys():
                cell.connections['top'] = other
                other.connections['bottom'] = cell
            if cell.connections['bottom'] is None and bottom < consts.MAP_HEIGHT - 1 and (c[0], bottom) in other.tiles.keys():
                cell.connections['bottom'] = other
                other.connections['top'] = cell

    # TODO: Prim's algorithm to ensure connectivity of garden cells
    root = garden_cells[libtcod.random_get_int(0, 0, len(garden_cells) - 1)]
    open_set = [root]
    closed_set = []
    while len(open_set) > 0:
        cell = open_set[libtcod.random_get_int(0, 0, len(open_set) - 1)]
        open_set.remove(cell)
        closed_set.append(cell)
        keys = [key for key in cell.connections.keys() if cell.connections[key] is not None and not cell.connections[key] in closed_set]
        if len(keys) == 0:
            continue
        link_count = libtcod.random_get_int(0, 1, len(keys))
        random.shuffle(keys)
        for i in range(link_count):
            make_garden_connections(cell, keys[i])
            open_set.append(cell.connections[keys[i]])

    if len(closed_set) < len(garden_cells):
        # If we didn't make enough connections, try again
        return make_map_garden()

    # Decorate rooms
    for cell in garden_cells:
        decorate_garden_room(cell)
    to_be_removed = []
    for cell in garden_cells:
        if len(cell.tiles) == 0:
            to_be_removed.append(cell)
    for cell in to_be_removed:
        garden_cells.remove(cell)

    open_tiles = []
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            if not map.tiles[x][y].blocks:
                open_tiles.append((x, y))

    active_branch = dungeon.branches[map.branch]

    clear_borders_from_open_set(open_tiles)

    main.place_objects(open_tiles,
                       main.roll_dice(active_branch['encounter_dice']) + main.roll_dice('1d' + str(map.difficulty + 1)),
                       main.roll_dice(active_branch['loot_dice']),
                       active_branch['xp_amount'])

    # Map links
    for link in map.links:
        hlink = True
        c = '>'
        if link[0] == 'north':
            x = consts.MAP_WIDTH / 2
            y = 1
            r = angles[0]
            c = chr(24)
        elif link[0] == 'south':
            x = consts.MAP_WIDTH / 2
            y = consts.MAP_HEIGHT - 2
            r = angles[2]
            c = chr(25)
        elif link[0] == 'east':
            x = consts.MAP_WIDTH - 3
            y = consts.MAP_HEIGHT / 2
            r = angles[1]
            c = chr(26)
        elif link[0] == 'west':
            x = 1
            y = consts.MAP_WIDTH / 2
            r = angles[3]
            c = chr(27)
        else:
            x = libtcod.random_get_int(0, consts.MAP_WIDTH / 3, consts.MAP_WIDTH * 2 / 3)
            y = libtcod.random_get_int(0, consts.MAP_HEIGHT / 3, consts.MAP_HEIGHT * 2 / 3)
            r = None
            if link[0] == 'up':
                c = '>'
            elif link[0] == 'down':
                c = '<'
            hlink = False
        if hlink:
            link_feature_category = link[1].branch + '_hlink'
        else:
            link_feature_category = link[1].branch + '_vlink'
        if link_feature_category in feature_categories and len(feature_categories[link_feature_category]) > 0:
            link_feature = random_from_list(feature_categories[link_feature_category]).name
        else:
            link_feature = feature_categories['default_gate'][0].name
        # find map cell closest to this location:
        garden_cells.sort(key=lambda cell: main.distance(cell.center()[0], cell.center()[1], x, y))
        if link[0] == 'east' or link[0] == 'west' or not hlink:
            y = garden_cells[0].center()[1]
        if link[0] =='north' or link[0] == 'south' or not hlink:
            x = garden_cells[0].center()[0]
        create_feature(x, y, link_feature, hard_override=True, rotation=r)
        stairs = None
        for i in range(len(map.objects) - 1, 0, -1):
            if map.objects[i].name == 'stairs':
                stairs = map.objects[i]
                break
        if stairs is not None:
            stairs.name = 'Path to ' + dungeon.branches[link[1].branch]['name']
            stairs.description = 'A winding path leading to ' + dungeon.branches[link[1].branch]['name']
            stairs.link = link
            stairs.interact = main.use_stairs
            stairs.char = c


def make_map_forest():

    sizex,sizey = consts.MAP_WIDTH - 1,consts.MAP_HEIGHT - 1
    link_locations = [(consts.MAP_WIDTH/2,1),(1,consts.MAP_HEIGHT/2),(consts.MAP_WIDTH/2,consts.MAP_HEIGHT-1),(consts.MAP_WIDTH-1,consts.MAP_HEIGHT/2)]
    noise = create_voronoi(sizex,sizey,10,1,link_locations, max_dist=12.0)
    room = Room()
    room.set_pos(1,1)
    for x in range(sizex):
        for y in range(sizey):
            #elevation = abs(int(math.ceil(4 - noise[x][y] / 2)))
            chance = noise[0][x][y]
            if libtcod.random_get_float(0, 0.0, 1.0) < chance:
                if libtcod.random_get_float(0, 0.0, 1.0) > chance:
                    tile = 'snow drift'
                else:
                    tile = 'snowy ground'
            else:
                tile = 'pine tree'
            room.set_tile(x, y, tile)

            #tile = 'snowy ground'
            #if elevation == 0:
            #    tile = 'snow drift'
            #room.set_tile(x,y,tile,elevation)

    apply_room(room)

    # create tunnels to connect feature points to closet two neighbors
    connected = []
    for f in noise[1]:
        connected.append(f)
        dist = [(math.fabs((f[0] - x2) ** 2 + (f[1] - y2) ** 2), (x2, y2)) for (x2, y2) in noise[1]]
        dist.sort(key=lambda o: o[0])
        links = 0
        for neighbor in dist:
            if neighbor[1] not in connected and neighbor[1] != f:
                create_perlin_tunnel(f[0], f[1], neighbor[1][0], neighbor[1][1], tile_type=default_floor, max_width=2)
                connected.append(neighbor[1])
                links += 1
                if links >= 2:
                    break
        # if no connection was made
        if links == 0:
            neighbor = dist[1]
            create_perlin_tunnel(f[0], f[1], neighbor[1][0], neighbor[1][1], tile_type=default_floor, max_width=2)
            connected.append(neighbor[1])

    # flood fill to remove isolated pockets
    fill_pockets()

    #for f in noise[1]:
    #    change_map_tile(f[0], f[1], 'deep water')

    #for i in range(0, 10 + libtcod.random_get_int(0, 0, 10)):
    #    start = (libtcod.random_get_int(0, 3, consts.MAP_WIDTH - 3),
    #             libtcod.random_get_int(0, 3, consts.MAP_HEIGHT - 3))
    #    create_terrain_patch(start, default_wall, 40, 80)

    open_tiles = []
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            if not map.tiles[x][y].blocks:
                open_tiles.append((x, y))

    feature_count = libtcod.random_get_int(0, 5, 10)
    for i in range(feature_count):
        tile = choose_random_tile(open_tiles)
        feature_index = libtcod.random_get_int(0, 0, len(feature_categories['forest']) - 1)
        feature_name = feature_categories['forest'][feature_index].name
        create_feature(tile[0], tile[1], feature_name, open_tiles)

    active_branch = dungeon.branches[map.branch]

    clear_borders_from_open_set(open_tiles)

    main.place_objects(open_tiles,
                       main.roll_dice(active_branch['encounter_dice']) + main.roll_dice('1d' + str(map.difficulty + 1)),
                       main.roll_dice(active_branch['loot_dice']),
                       active_branch['xp_amount'])

    make_basic_map_links()

def make_map_slag_fields():
    sizex,sizey = consts.MAP_WIDTH - 1,consts.MAP_HEIGHT - 1
    link_locations = []
    number_features = libtcod.random_get_int(0, 5, 12)
    if number_features < 9:
        link_locations = [(consts.MAP_WIDTH/2,1),(1,consts.MAP_HEIGHT/2),(consts.MAP_WIDTH/2,consts.MAP_HEIGHT-1),(consts.MAP_WIDTH-1,consts.MAP_HEIGHT/2)]
    noise = create_voronoi(sizex,sizey, number_features, 2, link_locations, max_dist=20.0)
    room = Room()
    room.set_pos(1,1)
    for x in range(sizex):
        for y in range(sizey):
            elevation = abs(int(5 - math.ceil(noise[0][x][y] * 4)))

            if elevation <= 2:
                elevation = 1
                if libtcod.random_get_float(0, 0.0, 1.0) < .1:
                    tile = 'shale'
                else:
                    tile = 'lava'
            elif elevation > 3:
                tile = 'dark shale wall'
            else:
                tile = 'shale'

            room.set_tile(x, y, tile, elevation)
    apply_room(room)
    erode_map('shale', libtcod.random_get_int(0, 2, 10))

    tree_count = libtcod.random_get_int(0, 0, 5)
    for i in range(tree_count):
        doodad_pos = ( libtcod.random_get_int(0, 1, consts.MAP_WIDTH - 2),
                     libtcod.random_get_int(0, 1, consts.MAP_HEIGHT - 2))
        if not map.tiles[doodad_pos[0]][doodad_pos[1]].is_water:
            change_map_tile(doodad_pos[0], doodad_pos[1], 'rusted skeleton')

    boulder_count = libtcod.random_get_int(0, 4, 8)
    for i in range(boulder_count):
        boulder = create_room_cloud(tile_type='dark shale wall', min_radius=1, max_radius=2)
        boulder.set_pos(libtcod.random_get_int(0, 10, consts.MAP_WIDTH - 10),
                        libtcod.random_get_int(0, 10, consts.MAP_HEIGHT - 10))
        apply_room(boulder)

    ash_count = libtcod.random_get_int(0, 0, 8)
    for i in range(ash_count):
        create_terrain_patch((libtcod.random_get_int(0, 10, consts.MAP_WIDTH - 10),
                              libtcod.random_get_int(0, 10, consts.MAP_HEIGHT - 10)), 'ash')

    create_slopes()

    open_tiles = []
    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            tile = map.tiles[x][y]
            if not tile.blocks and not tile.is_dangerous:
                open_tiles.append((x, y))

    feature_count = libtcod.random_get_int(0, 5, 10)
    for i in range(feature_count):
        tile = choose_random_tile(open_tiles)
        feature_index = libtcod.random_get_int(0, 0, len(feature_categories['slagfields']) - 1)
        feature_name = feature_categories['slagfields'][feature_index].name
        create_feature(tile[0], tile[1], feature_name, open_tiles)

    make_basic_map_links()

    active_branch = dungeon.branches[map.branch]
    main.place_objects(open_tiles,
                       main.roll_dice(active_branch['encounter_dice']) + main.roll_dice('1d' + str(map.difficulty + 1)),
                       main.roll_dice(active_branch['loot_dice']),
                       active_branch['xp_amount'])

def make_map_marsh():

    rooms = []
    num_rooms = 0

    room = create_room_cellular_automata(consts.MAP_WIDTH - 2, consts.MAP_HEIGHT - 2)
    room.set_pos(consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2)
    apply_room(room)
    open_tiles = room.get_open_tiles()
    grass_count = libtcod.random_get_int(0, 5, 15)
    for i in range(grass_count):
        grass = create_terrain_patch(choose_random_tile(open_tiles, exclusive=False), 'grass floor')
        if libtcod.random_get_int(0, 0, 100) < 30:
            scatter_reeds(grass)

    pond_count = libtcod.random_get_int(0, 5, 15)
    for i in range(pond_count):
        pond = create_terrain_patch(choose_random_tile(open_tiles, exclusive=False), 'shallow water', max_patch=150)
        if libtcod.random_get_int(0, 0, 100) < 10:
            scatter_reeds(pond)

    blastcap_count = libtcod.random_get_int(0, 0, 20)
    for i in range(blastcap_count):
        tile = choose_random_tile(open_tiles)
        main.spawn_monster('monster_blastcap', tile[0], tile[1])

    feature_count = libtcod.random_get_int(0, 0, 10)
    for i in range(feature_count):
        tile = choose_random_tile(open_tiles)
        feature_index = libtcod.random_get_int(0, 0, len(feature_categories['marsh']) - 1)
        feature_name = feature_categories['marsh'][feature_index].name
        create_feature(tile[0], tile[1], feature_name, open_tiles)

    active_branch = dungeon.branches[map.branch]
    clear_borders_from_open_set(open_tiles)
    main.place_objects(open_tiles,
                       main.roll_dice(active_branch['encounter_dice']) + main.roll_dice('1d'+str(map.difficulty + 1)),
                       main.roll_dice(active_branch['loot_dice']),
                       active_branch['xp_amount'])
    #stair_tile = choose_random_tile(open_tiles)
    #main.stairs = main.GameObject(stair_tile[0], stair_tile[1], '<', 'stairs downward', libtcod.white, always_visible=True)
    #map.objects.append(main.stairs)
    #main.stairs.send_to_back()

    make_basic_map_links()


def make_map_beach():

    for y in range(6, consts.MAP_HEIGHT - 6):
        for x in range(6, consts.MAP_WIDTH - 6):
            map.tiles[x][y].tile_type = default_floor

    for i in range(0, 6 + libtcod.random_get_int(0, 0, 8)):
        start = (libtcod.random_get_int(0, 10, consts.MAP_WIDTH - 10),
                 libtcod.random_get_int(0, 10, consts.MAP_HEIGHT * 2 / 3))
        create_terrain_patch(start, default_wall, 40, 80)

    erode_map(default_floor, 2)

    create_coastline(2 * consts.MAP_HEIGHT / 3)

    # Determine player spawn
    player_x = consts.MAP_WIDTH / 2
    player_y = consts.MAP_HEIGHT / 2
    for y in range(consts.MAP_HEIGHT - 1, 1, -1):
        if map.tiles[player_x][y].tile_type == default_floor:
            player_y = y
            break
    player.instance.x = player_x
    player.instance.y = player_y

    for link in map.links:
        if link[0] != 'north':
            make_basic_map_link(link)
        else:
            # Make grotto entrance
            stairs = None
            create_feature(consts.MAP_WIDTH / 2, 1, 'grotto_entrance')
            for i in range(len(map.objects) - 1, 0, -1):
                if map.objects[i].name == 'stairs':
                    stairs = map.objects[i]
                    break
            if stairs is not None:
                stairs.name = "Gate to the Pilgrim's Grotto"
                stairs.description = 'A tall basalt doorway, covered with engravings worn dull by the salty winds.'
                stairs.link = link
                stairs.interact = main.use_stairs
                stairs.char = chr(24)


def make_map_grotto():
    import npc
    open_tiles = []
    create_feature(consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2, 'grotto', open_tiles=open_tiles)
    stairs = None
    for i in range(len(map.objects) - 1, 0, -1):
        if map.objects[i].name == 'stairs':
            stairs = map.objects[i]
            break
    if stairs is not None:
        stairs.name = "Gate to the shore"
        stairs.description = 'A tall basalt doorway, covered with engravings worn dull by the salty winds.'
        stairs.link = map.links[0]
        stairs.interact = main.use_stairs
        stairs.char = chr(25)
        stairs.event = npc.event_leave_grotto

def make_map_lava_lake():
    open_tiles = []
    create_feature(consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2, 'lava_lake', open_tiles=open_tiles)
    stairs = []
    for i in range(len(map.objects)):
        if map.objects[i].name == 'stairs':
            stairs.append(map.objects[i])
    if len(stairs) > 0:
        stairs.sort(key=lambda s: s.y)
        stairs[0].name = 'Gate to the slagfields'
        stairs[0].description = 'A winding path leading to the slagfields.'
        stairs[0].link = map.links[1]
        stairs[0].char = chr(26)
        stairs[1].name = 'Gate to the badlands'
        stairs[1].description = 'A winding path leading to the badlands.'
        stairs[1].link = map.links[0]
        stairs[1].char = chr(25)
        for stair in stairs:
            stair.interact = main.use_stairs


def make_map_crypt():
    open_tiles = []
    create_feature(consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2, 'crypt', open_tiles=open_tiles)
    for tile in open_tiles:
        if main.roll_dice('1d4') == 1:
            main.make_spiderweb(tile[0], tile[1])
    stairs = None
    for i in range(len(map.objects) - 1, 0, -1):
        if map.objects[i].name == 'stairs':
            stairs = map.objects[i]
            break
    if stairs is not None:
        stairs.name = "Staircase to the badlands"
        stairs.description = 'A narrow stone stairway leading up to the badlands.'
        stairs.link = map.links[0]
        stairs.interact = main.use_stairs
        stairs.char = '>'

def make_map_bog():
    open_tiles = []
    create_feature(consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2, 'bog', open_tiles=open_tiles)
    stairs = None
    for i in range(len(map.objects) - 1, 0, -1):
        if map.objects[i].name == 'stairs':
            stairs = map.objects[i]
            break
    if stairs is not None:
        stairs.name = "Staircase to the marsh"
        stairs.description = 'A narrow stone stairway leading up to the marsh.'
        stairs.link = map.links[0]
        stairs.interact = main.use_stairs
        stairs.char = '>'

def make_map_eolith():
    open_tiles = []
    key_points = create_feature(consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2, 'eolith_cavern', open_tiles=open_tiles).key_points
    treasure_point = key_points.values()[libtcod.random_get_int(0, 0, len(key_points.values()) - 1)]
    main.spawn_item('weapon_longsword', treasure_point[0], treasure_point[1], quality='')
    main.spawn_item('equipment_leather_armor', treasure_point[0], treasure_point[1], quality='')
    change_map_tile(treasure_point[0], treasure_point[1],'ice wall', hard_override=True)
    stairs = None
    for i in range(len(map.objects) - 1, 0, -1):
        if map.objects[i].name == 'stairs':
            stairs = map.objects[i]
            break
    if stairs is not None:
        stairs.name = "Staircase to the Frozen Forest"
        stairs.description = 'A narrow stone stairway leading up to the frozen forest.'
        stairs.link = map.links[0]
        stairs.interact = main.use_stairs
        stairs.char = '>'

def make_map_river():
    for y in range(2, consts.MAP_HEIGHT - 2):
        for x in range(2, consts.MAP_WIDTH - 2):
            map.tiles[x][y].tile_type = default_floor

    bank_noise = libtcod.noise_new(1)
    width_noise = libtcod.noise_new(1)
    shallows_noise = libtcod.noise_new(1)
    north_bank = 20
    for x in range(consts.MAP_WIDTH):
        shore = libtcod.noise_get_fbm(bank_noise, [float(x) / 10.0, float(x) / 10.0 + 1.0], libtcod.NOISE_PERLIN)
        this_shore = north_bank + int(shore * 10)
        width = libtcod.noise_get_fbm(width_noise, [float(x) / 10.0, float(x) / 10.0 + 1.0], libtcod.NOISE_PERLIN)
        this_width = 15 + int(width * 10)
        shallows = libtcod.noise_get_fbm(shallows_noise, [float(x) / 10.0, float(x) / 10.0 + 1.0], libtcod.NOISE_PERLIN)
        this_shallows = 2 + abs(int(shallows * 10))
        min_y = this_shore
        max_y = this_shore + this_width
        for y in range(min_y - this_shallows - 1):
            change_map_tile(x, y, 'cypress tree')
        for y in range(min_y - this_shallows, min_y):
            change_map_tile(x, y, 'shallow water')
        for y in range(min_y, max_y):
            change_map_tile(x, y, 'deep water')
        for y in range(max_y, max_y + this_shallows):
            change_map_tile(x, y, 'shallow water')
        for y in range(max_y + this_shallows + 1, consts.MAP_HEIGHT - 1):
            change_map_tile(x, y, 'cypress tree')
    erode_map('grass floor', iterations=4)

    make_river_map_links()

def make_map_crossing():
    open_tiles = []
    create_feature(consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2, 'stonewater_crossing', open_tiles=open_tiles)
    make_river_map_links()

def make_map_badlands():

    for y in range(consts.MAP_HEIGHT):
        for x in range(consts.MAP_WIDTH):
            change_map_tile(x, y, 'mud')

    create_hills()

    tree_count = libtcod.random_get_int(0, 15, 100)
    for i in range(tree_count):
        tree_pos = (libtcod.random_get_int(0, 1, consts.MAP_WIDTH - 2), libtcod.random_get_int(0, 1, consts.MAP_HEIGHT - 2))
        if not map.tiles[tree_pos[0]][tree_pos[1]].is_water:
            change_map_tile(tree_pos[0], tree_pos[1], 'gnarled tree')

    left_noise = libtcod.noise_new(1)
    right_noise = libtcod.noise_new(1)
    top_noise = libtcod.noise_new(1)
    bottom_noise = libtcod.noise_new(1)
    for x in range(consts.MAP_WIDTH):
        top_depth = int(5.0 * libtcod.noise_get(top_noise, [20.0 * float(x) / float(consts.MAP_WIDTH)], libtcod.NOISE_PERLIN))
        top_depth += 3
        for y in range(top_depth):
            change_map_tile(x, y, default_wall)
        bottom_depth = int(5.0 * libtcod.noise_get(bottom_noise, [20.0 * float(x) / float(consts.MAP_WIDTH)], libtcod.NOISE_PERLIN))
        bottom_depth += 3
        for y in range(bottom_depth):
            change_map_tile(x, consts.MAP_HEIGHT - y, default_wall)
    for y in range(consts.MAP_HEIGHT):
        left_depth = int(
            5.0 * libtcod.noise_get(left_noise, [20.0 * float(y) / float(consts.MAP_HEIGHT)], libtcod.NOISE_PERLIN))
        left_depth += 3
        for x in range(left_depth):
            change_map_tile(x, y, default_wall)
        right_depth = int(
            5.0 * libtcod.noise_get(right_noise, [20.0 * float(y) / float(consts.MAP_HEIGHT)], libtcod.NOISE_PERLIN))
        right_depth += 3
        for x in range(right_depth):
            change_map_tile(consts.MAP_WIDTH - x, y, default_wall)

    # scatter boulders
    boulder_count = libtcod.random_get_int(0, 4, 8)
    for i in range(boulder_count):
        boulder = create_room_cloud(tile_type=default_wall, min_radius=1, max_radius=2)
        boulder.set_pos(libtcod.random_get_int(0, 10, consts.MAP_WIDTH - 10), libtcod.random_get_int(0, 10, consts.MAP_HEIGHT - 10))
        apply_room(boulder)
    grass_count = libtcod.random_get_int(0, 0, 8)
    for i in range(grass_count):
        create_terrain_patch((libtcod.random_get_int(0, 10, consts.MAP_WIDTH - 10), libtcod.random_get_int(0, 10, consts.MAP_HEIGHT - 10)), 'dry grass')

    create_slopes()

    open_tiles = []
    for x in range(consts.MAP_WIDTH):
        for y in range(consts.MAP_HEIGHT):
            if not map.tiles[x][y].blocks:
                open_tiles.append((x, y))

    feature_count = libtcod.random_get_int(0, 0, 3)
    for i in range(feature_count):
        tile = choose_random_tile(open_tiles)
        feature_index = libtcod.random_get_int(0, 0, len(feature_categories['badlands']) - 1)
        feature_name = feature_categories['badlands'][feature_index].name
        create_feature(tile[0], tile[1], feature_name, open_tiles)

    blightweed_count = libtcod.random_get_int(0, 0, 6)
    for i in range(blightweed_count):
        blight_tile = open_tiles[libtcod.random_get_int(0, 0, len(open_tiles) - 1)]
        scatter_blightweed(blight_tile)

    active_branch = dungeon.branches[map.branch]
    clear_borders_from_open_set(open_tiles)
    main.place_objects(open_tiles,
                       main.roll_dice(active_branch['encounter_dice']) + main.roll_dice('1d'+str(map.difficulty + 1)),
                       main.roll_dice(active_branch['loot_dice']),
                       active_branch['xp_amount'])
    make_basic_map_links()

def make_map_gtunnels():
    active_branch = dungeon.branches[map.branch]

    #Step 1: scatter key points:
    key_points = []
    for i in range(20):
        key_points.append((libtcod.random_get_int(0, 3, consts.MAP_WIDTH - 4),
                           libtcod.random_get_int(0, 3, consts.MAP_HEIGHT - 4)))
    #Step 2: link key points with perlin tunnels
    for i in range(len(key_points) - 2):
        create_perlin_tunnel(key_points[i][0], key_points[i][1], key_points[i + 1][0], key_points[i + 1][1])
    open_tiles = []
    for x in range(consts.MAP_WIDTH):
        for y in range(consts.MAP_HEIGHT):
            if not map.tiles[x][y].blocks:
                open_tiles.append((x, y))
    #Step 3: create rooms. Link them from their centers to nearest open points.
    room_rects = []
    room_count = 10 + libtcod.random_get_int(0, 0, 10)
    num_rooms = 0
    for i in range(room_count / 2):
        room = create_room_random(active_branch['terrain_types'])
        dimensions = room.bounds

        x = libtcod.random_get_int(0, 2 + (dimensions[0] / 2), consts.MAP_WIDTH - (dimensions[0] / 2) - 3)
        y = libtcod.random_get_int(0, 2 + (dimensions[1] / 2), consts.MAP_HEIGHT - (dimensions[1] / 2) - 3)

        room_bounds = Rect(x - dimensions[0] / 2, y - dimensions[0] / 2, dimensions[0], dimensions[1])

        failed = False
        for other_room in room_rects:
            if room_bounds.intersect(other_room):
                failed = True
                break

        if not failed:
            # create_room(new_room)
            room.set_pos(room_bounds.center()[0], room_bounds.center()[1])
            apply_room(room)
            (new_x, new_y) = room.center()
            if num_rooms > 0:
                (prev_x, prev_y) = room_rects[num_rooms - 1].center()
                create_perlin_tunnel(prev_x, prev_y, new_x, new_y, min_width=1, max_width=2)
                #create_wandering_tunnel(prev_x, prev_y, new_x, new_y)
            num_rooms += 1
            room_rects.append(room_bounds)

    #Step 4: scatter features. Link them from their link points to nearest open points.
    room_count = 10 + libtcod.random_get_int(0, 0, 10)
    connectors = []
    for i in range(room_count / 2):
        tile = (libtcod.random_get_int(0, 3, consts.MAP_WIDTH - 4),
                           libtcod.random_get_int(0, 3, consts.MAP_HEIGHT - 4))
        feature_index = libtcod.random_get_int(0, 0, len(feature_categories['gtunnels']) - 1)
        feature_name = feature_categories['gtunnels'][feature_index].name
        result = create_feature(tile[0], tile[1], feature_name, open_tiles)
        if isinstance(result, Room):
            # A feature was created
            if len(result.link_points) > 0:
                inner_bounds = Rect(result.min_x + 1, result.min_y + 1, result.width - 2, result.height - 2)
                for link in result.link_points:
                    closest = main.find_closest_open_tile(link[0], link[1], result.tiles.keys())
                    path_rect = Rect(min(link[0], closest[0]),
                                     min(link[1], closest[1]),
                                     abs(link[0] - closest[0]),
                                     abs(link[1] - closest[1]))
                    connectors += create_perlin_tunnel(link[0], link[1], closest[0], closest[1], tile_type='open')
            else:
                center = (result.min_x + result.max_x) / 2, (result.min_y + result.max_y) / 2
                closest = main.find_closest_open_tile(center[0], center[1], result.tiles.keys())
                if closest is not None:
                    connectors += create_perlin_tunnel(center[0], center[1], closest[0], closest[1], tile_type='open')

    for t in connectors:
        change_map_tile(t[0], t[1], 'open', hard_override=True)
        if t not in open_tiles:
            open_tiles.append(t)

    clear_borders_from_open_set(open_tiles)
    main.place_objects(open_tiles,
                       main.roll_dice(active_branch['encounter_dice']) + main.roll_dice('1d' + str(map.difficulty + 1)),
                       main.roll_dice(active_branch['loot_dice']),
                       active_branch['xp_amount'])

    make_basic_map_links()

def make_map_catacombs():
    rooms = []
    rects = []
    num_rooms = 0

    #Create chasms
    chasm_count = main.roll_dice('1d8') + 6
    for i in range(chasm_count):
        create_terrain_patch((libtcod.random_get_int(0, 3, consts.MAP_WIDTH - 4),
                           libtcod.random_get_int(0, 3, consts.MAP_HEIGHT - 4)), 'chasm', overwrite=True, min_patch=200, max_patch=1200)


    #for i in range(libtcod.random_get_int(0,2,18)):
    #    change_map_tile(libtcod.random_get_int(0, 3, consts.MAP_WIDTH - 4),
    #                       libtcod.random_get_int(0, 3, consts.MAP_HEIGHT - 4), 'chasm')
    #    if main.roll_dice('1d2') == 1:
    #        erode_map('chasm',1)
    #erode_map('chasm',libtcod.random_get_int(0,5,8))

    #First, create the entrance
    entrance = create_room_rectangle(['snowy ground'])
    dimensions = entrance.bounds
    x = libtcod.random_get_int(0, 1 + dimensions[0] / 2, consts.MAP_WIDTH - dimensions[0] / 2 - 1)
    y = consts.MAP_HEIGHT - dimensions[1] / 2 - 1
    room_bounds = Rect(x, y, dimensions[0], dimensions[1])
    entrance.set_pos(room_bounds.x1, room_bounds.y1)
    apply_room(entrance)
    rooms.append(entrance)
    rects.append(room_bounds)
    num_rooms += 1

    exit = Room()
    exit.add_rectangle(width=3,height=3,tile_type='snowy ground')
    dimensions = exit.bounds
    x = libtcod.random_get_int(0, 1 + dimensions[0] / 2, consts.MAP_WIDTH - dimensions[0] / 2 - 1)
    y = 1 + dimensions[1] / 2
    room_bounds = Rect(x, y, dimensions[0], dimensions[1])
    exit.set_pos(room_bounds.x1, room_bounds.y1)
    #apply_room(exit)
    #rooms.append(exit)
    rects.append(room_bounds)
    num_rooms += 1

    #Create other rooms
    for r in range(consts.MG_MAX_ROOMS):

        room = create_room_rectangle(['stone floor'])
        dimensions = room.bounds

        x = libtcod.random_get_int(0, 1 + dimensions[0] / 2, consts.MAP_WIDTH - dimensions[0] / 2 - 1)
        y = libtcod.random_get_int(0, 1 + dimensions[1] / 2, consts.MAP_HEIGHT - dimensions[1] / 2 - 1)
        room_bounds = Rect(x-1, y-1, dimensions[0]+2, dimensions[1]+2)

        failed = False
        for other_room in rects:
            if room_bounds.intersect(other_room):
               failed = True

        if not failed:
            room.set_pos(room_bounds.x1, room_bounds.y1)
            apply_room(room)
            rooms.append(room)
            rects.append(room_bounds)
            num_rooms += 1

    #make_basic_map_links()

    connection_threshold_step = 8
    open = deque()
    open.append(entrance)
    closed = []
    tcount = 0

    nodes = []
    nodes.append({'nr':0, 'room':entrance,'parent':None,'connections':[]})

    #Create room connections
    while len(open) > 0:
        curr = open.popleft()
        closed.append(curr)
        connections = []
        node = [n for n in nodes if n['room'] is curr][0]
        threshold = connection_threshold_step
        while len(connections) == 0 and threshold < consts.MAP_WIDTH * 2:
            connections = [r for r in rooms if (r is not curr) and (curr.distance_to(r) < threshold) \
                           and (r not in open) and (r not in closed)]
            threshold += connection_threshold_step

        for con in connections:
            if con not in open and con not in closed:
                tcount += 1
                open.append(con)
                center_old = con.center()
                center_new = curr.center()
                tunnel = catacombs_hv_tunnel(center_old[0], center_old[1], center_new[0], center_new[1], con.rect, curr.rect)
                tmp = {'nr':tcount,'parent':node, 'room': con, 'connections': []}
                node['connections'].append({'tunnel':tunnel, 'connection':tmp})
                nodes.append(tmp)
                #for tn in tunnel:
                #    main.current_map.add_object(main.GameObject(tn[0],tn[1],chr(ord('0') + tcount % 10),'blah',libtcod.white, always_visible=True))

    #Connect the exit
    apply_room(exit)
    exit_connector = sorted(rooms,key= lambda r: exit.distance_to(r))[1]
    node = [n for n in nodes if n['room'] is exit_connector][0]
    rooms.append(exit)
    center_old = exit.center()
    center_new = exit_connector.center()
    tunnel = catacombs_hv_tunnel(center_old[0], center_old[1], center_new[0], center_new[1], exit.rect, exit_connector.rect)
    tmp = {'nr': tcount, 'parent': node, 'room': exit, 'connections': []}
    node['connections'].append({'tunnel': tunnel, 'connection': tmp})
    nodes.append(tmp)

    # Create switch-door puzzles
    segments = deque()
    exit_node = [n for n in nodes if n['room'] is exit][0]
    segments.append((nodes[0],exit_node))
    blacklist = [nodes[0],exit_node]

    iterations = 0
    while len(segments) > 0 and iterations < consts.MG_PUZZLE_MAX_COUNT:
        start,end = segments.popleft()
        length = get_back_path_length(start,end)
        if length < 2:
            continue
        print("Processing segment {}:{} (length {})".format(start['nr'],end['nr'],length))

        prev = None
        pivot = end
        for i in range(libtcod.random_get_int(0,1,length)):
            prev = pivot
            pivot = pivot['parent']
        blacklist.append(pivot)
        connected_nodes = get_connected_nodes(nodes, start, blacklist)
        print("Connected nodes: {}",[(n[0]['nr'],n[1]) for n in connected_nodes])
        switch = connected_nodes[-1][0]
        print("Selected node {} at distance {} for switch (of {} options)".format(switch['nr'],connected_nodes[-1][1],len(connected_nodes)))
        if switch not in blacklist:
            blacklist.append(switch)
            tunnel = [p for p in pivot['connections'] if p['connection']][0]['tunnel']
            door_location = None
            for loc in tunnel:
                adjacent_walls = [tile for tile in main.adjacent_tiles_orthogonal(*loc) \
                                  if is_wall_or_pit(main.current_map.tiles[tile[0]][tile[1]])]
                if len(adjacent_walls) == 2:
                    door_location = loc
                    break
            center = switch['room'].center()
            if door_location is not None:
                d, s = create_gate_switch(door_location[0],door_location[1],center[0],center[1])
                if d is not None:
                    print("Successfully created switch-gate pair")
                    main.current_map.add_object(d)
                    main.current_map.add_object(s)
                    segments.append((start, switch))
        segments.append((start,pivot))
        segments.append((prev,end))

def build_edge(corner1, corner2):
    if corner1[0] == corner2[0]:
        step = (corner2[1] - corner1[1]) / abs(corner2[1] - corner1[1])
        for y in range(corner1[1], corner2[1] + step, step):
            change_map_tile(corner1[0], y, default_wall)
    elif corner1[1] == corner2[1]:
        step = (corner2[0] - corner1[0]) / abs(corner2[0] - corner1[0])
        for x in range(corner1[0], corner2[0] + step, step):
            change_map_tile(x, corner1[1], default_wall)


def is_wall_or_pit(tile):
    return tile.is_wall or tile.is_pit

def get_back_path_length(a,b):
    c = b
    length = 0
    while c is not a:
        length += 1
        c = c['parent']
    return length

def get_connected_nodes(nodes,n,blacklist):
    open = [(n,0)]
    closed = []
    while len(open) > 0:
        curr = open.pop()
        closed.append(curr)
        for c in curr[0]['connections']:
            if c['connection'] not in blacklist:
                open.append((c['connection'],curr[1]+1))
    closed.sort(key=lambda o: o[1])
    return closed

def catacombs_h_tunnel(x1, x2, y, tile_type=default_floor):
    if x1 == x2:
        return []
    changed = []
    started = False
    step = (x2 - x1) / abs(x2 - x1)
    for x in range(x1, x2 + step, step):
        if is_wall_or_pit(map.tiles[x][y]):
            started = True
            change_map_tile(x, y, tile_type)
            changed.append((x,y))
        elif started:
            break
    return changed


def catacombs_v_tunnel(y1, y2, x, tile_type=default_floor):
    if y1 == y2:
        return []
    changed = []
    started = False
    step = (y2 - y1) / abs(y2 - y1)
    for y in range(y1, y2 + step, step):
        if is_wall_or_pit(map.tiles[x][y]):
            started = True
            change_map_tile(x, y, tile_type)
            changed.append((x,y))
        elif started:
            break
    return changed


def catacombs_hv_tunnel(x1, y1, x2, y2, rect1, rect2, tile_type=default_floor):

    if libtcod.random_get_float(0,0,1) < 0.5:
        if x1 == rect2.x1 - 1:
            build_edge((rect2.x1, rect2.y1), (rect2.x1, rect2.y2))
        if x1 == rect2.x2 + 1:
            build_edge((rect2.x2, rect2.y1), (rect2.x2, rect2.y2))
        if y2 == rect1.y1 - 1:
            build_edge((rect1.x1, rect1.y1), (rect1.x2, rect1.y1))
        if y2 == rect1.y2 + 1:
            build_edge((rect1.x1, rect1.y2), (rect1.x2, rect1.y2))
        tunnel = catacombs_v_tunnel(y1, y2, x1, tile_type)
        if len(tunnel) == 0 or tunnel[len(tunnel) - 1] == (x1, y2):
            tunnel += catacombs_h_tunnel(x1, x2, y2, tile_type)
    else:
        if y1 == rect2.y1 - 1:
            build_edge((rect2.x1, rect2.y1), (rect2.x2, rect2.y1))
        if y1 == rect2.y2 + 1:
            build_edge((rect2.x1, rect2.y2), (rect2.x2, rect2.y2))
        if x2 == rect1.x1 - 1:
            build_edge((rect1.x1, rect1.y1), (rect1.x1, rect1.y2))
        if x2 == rect1.x2 + 1:
            build_edge((rect1.x2, rect1.y1), (rect1.x2, rect1.y2))
        tunnel = catacombs_h_tunnel(x1, x2, y1, tile_type)
        if len(tunnel) == 0 or tunnel[len(tunnel) - 1] == (x2, y1):
            tunnel += catacombs_v_tunnel(y1, y2, x2, tile_type)
    return tunnel

def make_test_space():
    for y in range(2, consts.MAP_HEIGHT - 2):
        for x in range(2, consts.MAP_WIDTH - 2):
            map.tiles[x][y].tile_type = default_floor

    #map.branch = 'marsh'
    player_tile = (consts.MAP_WIDTH / 2, consts.MAP_HEIGHT - 4)

    if consts.DEBUG_TEST_FEATURE is not None:
        create_feature(consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2, consts.DEBUG_TEST_FEATURE, None)

    player.instance.x = player_tile[0]
    player.instance.y = player_tile[1]

    if consts.DEBUG_TEST_MONSTER is not None:
        if isinstance(consts.DEBUG_TEST_MONSTER, dict):
            main.spawn_encounter(map.tiles, consts.DEBUG_TEST_MONSTER,(player_tile[0], player_tile[1] - 20))
        else:
            main.spawn_monster(consts.DEBUG_TEST_MONSTER, player_tile[0], player_tile[1] - 20)

    make_basic_map_links()

    #stair_tile = (player_tile[0], player_tile[1] + 3)
    #main.stairs = main.GameObject(stair_tile[0], stair_tile[1], '<', 'stairs downward', libtcod.white,
    #                              always_visible=True)
    #map.objects.append(main.stairs)
    #main.stairs.send_to_back()

def make_river_map_links():
    northwest = None
    southwest = None
    northeast = None
    southeast = None
    for y in range(0, consts.MAP_HEIGHT - 1):
        if northwest is None and map.tiles[1][y].tile_type == 'shallow water':
            northwest = (1, y - 2)
        if northeast is None and map.tiles[consts.MAP_WIDTH - 2][y].tile_type == 'shallow water':
            northeast = (consts.MAP_WIDTH - 2, y - 2)
        if map.tiles[1][y].tile_type == 'shallow water':
            if southwest is None or y > southwest[1] - 2:
                southwest = (1, y + 2)
        if map.tiles[consts.MAP_WIDTH - 2][y].tile_type == 'shallow water':
            if southeast is None or y > southeast[1] - 2:
                southeast = (consts.MAP_WIDTH - 2, y + 2)

    for link in map.links:
        if link[1].branch == 'river' or link[1].branch == 'crossing':
            if link[0] == 'east':
                link_pos = northeast, southeast
                link_id = 'northeast', 'southeast'
                link_destination_id = 'northwest', 'southwest'
                link_char = chr(26)
            elif link[0] == 'west':
                link_pos = northwest, southwest
                link_id = 'northwest', 'southwest'
                link_destination_id = 'northeast', 'southeast'
                link_char = chr(27)
            else:
                continue
            for i in range(2):
                stairs = main.GameObject(link_pos[i][0], link_pos[i][1], '>', 'stairs', libtcod.white,
                                         always_visible=True)
                stairs.name = "Gate to %s" % dungeon.branches[link[1].branch]['name']
                stairs.description = 'A winding path leading to %s.' % dungeon.branches[link[1].branch]['name']
                stairs.link = link
                stairs.interact = main.use_stairs
                stairs.char = link_char
                stairs.link_id = link_id[i]
                stairs.destination_id = link_destination_id[i]
                map.add_object(stairs)
        else:
            make_basic_map_link(link)

def make_basic_map_links():
    # make map links
    for link in map.links:
        make_basic_map_link(link)

def make_basic_map_link(link, connect_with_tunnels=True):
    hlink = True
    r = 0
    c = '>'
    if link[0] == 'north':
        x = libtcod.random_get_int(0, consts.MAP_WIDTH / 3, consts.MAP_WIDTH * 2 / 3)
        y = 2
        r = angles[0]
        c = chr(24)
    elif link[0] == 'south':
        x = libtcod.random_get_int(0, consts.MAP_WIDTH / 3, consts.MAP_WIDTH * 2 / 3)
        y = consts.MAP_HEIGHT - 3
        r = angles[2]
        c = chr(25)
    elif link[0] == 'east':
        x = consts.MAP_WIDTH - 3
        y = libtcod.random_get_int(0, consts.MAP_HEIGHT / 3, consts.MAP_HEIGHT * 2 / 3)
        r = angles[1]
        c = chr(26)
    elif link[0] == 'west':
        x = 2
        y = libtcod.random_get_int(0, consts.MAP_HEIGHT / 3, consts.MAP_HEIGHT * 2 / 3)
        r = angles[3]
        c = chr(27)
    else:
        x = libtcod.random_get_int(0, consts.MAP_WIDTH / 3, consts.MAP_WIDTH * 2 / 3)
        y = libtcod.random_get_int(0, consts.MAP_HEIGHT / 3, consts.MAP_HEIGHT * 2 / 3)
        if link[0] == 'up':
            c = '>'
        elif link[0] == 'down':
            c = '<'
        hlink = False
    if hlink:
        link_feature_category = link[1].branch + '_hlink'
        if link_feature_category in feature_categories and len(feature_categories[link_feature_category]) > 0:
            link_feature = random_from_list(feature_categories[link_feature_category]).name
        else:
            link_feature = feature_categories['default_gate'][0].name
        exclude = []
        create_feature(x, y, link_feature, hard_override=True, rotation=r, open_tiles=exclude)
        if connect_with_tunnels:
            closest = main.find_closest_open_tile(x, y, exclude=exclude)
            create_wandering_tunnel(closest[0], closest[1], x, y, tile_type='open', hardoverride=True)
    else:
        link_feature_category = link[1].branch + '_vlink'
        if link_feature_category in feature_categories and len(feature_categories[link_feature_category]) > 0:
            link_feature = random_from_list(feature_categories[link_feature_category]).name
        else:
            link_feature = feature_categories['default_gate'][0].name
        exclude = []
        create_feature(x, y, link_feature, hard_override=True, open_tiles=exclude)
        if connect_with_tunnels:
            closest = main.find_closest_open_tile(x, y, exclude=exclude)
            create_wandering_tunnel(closest[0], closest[1], x, y, tile_type='open', hardoverride=True)
    # find the stairs that we just placed
    stairs = None
    for i in range(len(map.objects) - 1, 0, -1):
        if map.objects[i].name == 'stairs':
            stairs = map.objects[i]
            break
    if stairs is not None:
        stairs.name = 'Path to ' + dungeon.branches[link[1].branch]['name']
        stairs.description = 'A winding path leading to ' + dungeon.branches[link[1].branch]['name']
        stairs.link = link
        stairs.interact = main.use_stairs
        stairs.char = c

def make_map(_map):
    global feature_rects, map, default_floor, default_wall, default_ramp

    feature_rects = []
    map = _map
    map.has_special = False

    map.objects = [player.instance]
    map.fighters = [player.instance]

    default_floor = dungeon.branches[map.branch]['default_floor']
    default_wall = dungeon.branches[map.branch]['default_wall']
    default_ramp = dungeon.branches[map.branch]['default_ramp']

    map.tiles = [[main.Tile(default_wall)
                         for y in range(consts.MAP_HEIGHT)]
                        for x in range(consts.MAP_WIDTH)]

    map.difficulty = dungeon.branches[map.branch]['scaling']
    dungeon.branches[map.branch]['scaling'] += 1

    main.spawned_bosses = {}

    # choose generation type
    dungeon.branches[map.branch]['generate']()

    open_tile = main.find_closest_open_tile(25, 23)
    if open_tile is not None:
        player.instance.x = open_tile[0]
        player.instance.y = open_tile[1]

    # make sure the edges are undiggable walls
    for i in range(consts.MAP_WIDTH):
        map.tiles[i][0].tile_type = default_wall
        map.tiles[i][0].flags |= terrain.FLAG_NO_DIG
        map.tiles[i][consts.MAP_HEIGHT - 1].tile_type = default_wall
        map.tiles[i][consts.MAP_HEIGHT - 1].flags |= terrain.FLAG_NO_DIG
    for i in range(consts.MAP_HEIGHT):
        map.tiles[0][i].tile_type = default_wall
        map.tiles[0][i].flags |= terrain.FLAG_NO_DIG
        map.tiles[consts.MAP_WIDTH - 1][i].tile_type = default_wall
        map.tiles[consts.MAP_WIDTH - 1][i].flags |= terrain.FLAG_NO_DIG
