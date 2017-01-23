import game as main
import consts
import libtcodpy as libtcod
import random
import math
import terrain
import loot
import Queue
import pathfinding
import world
import player

angles = [0,
          0.5 * math.pi,
          math.pi,
          1.5 * math.pi]

NOROTATE = 1
NOREFLECT = 2
NOSPAWNS = 4
map = None

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
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None
        self.pos = 0, 0
        self.no_overwrite = False

    # define the world-space position of the upper-left-hand corner of this room. Adjust all tile positions
    def set_pos(self, x, y):
        if self.pos[0] == x and self.pos[1] == y:
            return  # No translation
        new_tiles = {}
        new_data = {}
        for tile in self.tiles.keys():
            new_x = tile[0] + x - self.min_x
            new_y = tile[1] + y - self.min_y
            new_tiles[new_x, new_y] = self.tiles[tile]
            if tile in self.data.keys():
                new_data[new_x, new_y] = self.data[tile]
        w = self.bounds[0] - 1
        h = self.bounds[1] - 1
        self.min_x = x
        self.min_y = y
        self.max_x = self.min_x + w
        self.max_y = self.min_y + h
        self.tiles = new_tiles
        self.data = new_data
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
        self.tiles = new_tiles
        self.data = new_data
        self.pos = self.min_x, self.min_y
        self.set_pos(0, 0)

    # Orient to the origin, then reflect across one or both axes
    def reflect(self, reflect_x=False, reflect_y=False):
        if not reflect_x and not reflect_y:
            return  # No reflection
        self.set_pos(0, 0)
        new_tiles = {}
        new_data = {}
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
        self.tiles = new_tiles
        self.data = new_data


    def set_tile(self, x, y, tile_type, elevation=0):
        if self.min_x is None or self.min_x > x:
            self.min_x = x
        if self.max_x is None or self.max_x < x:
            self.max_x = x
        if self.min_y is None or self.min_y > y:
            self.min_y = y
        if self.max_y is None or self.max_y < y:
            self.max_y = y
        self.tiles[(x, y)] = tile_type
        if elevation != 0:
            self.data[(x, y)] = []
            self.data[(x, y)].append('ELEVATION')
            self.data[(x, y)].append(str(elevation))
            #ele_str = 'ELEVATION ' + str(elevation)
            #if (x, y) not in self.data.keys():
            #    self.data[(x, y)] = ele_str
            #else:
            #    self.data[(x, y)] += (' ' + ele_str)


    def get_open_tiles(self):
        return_tiles = []
        for tile in self.tiles.keys():
            if self.tiles[tile] == 'default ground' or (not terrain.data[self.tiles[tile]].blocks and tile not in self.data.keys()):
                return_tiles.append(tile)
            if tile in self.data.keys() and self.data[tile] == '>':
                return_tiles.append(tile)
        return return_tiles

    def get_blocked_tiles(self):
        return_tiles = []
        for tile in self.tiles.keys():
            if not self.tiles[tile] == 'default ground' and (terrain.data[self.tiles[tile]].blocks or tile in self.data.keys()):
                return_tiles.append(tile)
        return return_tiles

    @property
    def bounds(self):
        if self.max_x is None or self.min_x is None or self.max_y is None or self.min_y is None:
            return 0, 0
        else:
            return self.max_x - self.min_x + 1, self.max_y - self.min_y + 1

    def add_rectangle(self, x0=0, y0=0, width=None, height=None, tile_type='stone floor'):
        if width is None:
            width = libtcod.random_get_int(0, consts.MG_ROOM_MIN_SIZE, consts.MG_ROOM_MAX_SIZE)
        if height is None:
            height = libtcod.random_get_int(0, consts.MG_ROOM_MIN_SIZE, consts.MG_ROOM_MAX_SIZE)
        for x in range(width):
            for y in range(height):
                self.set_tile(x0 + x, y0 + y, tile_type)

    def add_circle(self, x0=0, y0=0, r=None, tile_type='stone floor'):
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


def create_room_random():
    choice = libtcod.random_get_int(0, 0, 2)

    choice = 2
    if choice == 0:
        return create_room_rectangle()
    elif choice == 1:
        return create_room_circle()
    elif choice == 2:
        return create_room_cloud()
    elif choice == 3:
        return create_room_cellular_automata(10, 10)
    else:
        # Default
        return create_room_rectangle()


#TODO: This should look at branch type
def random_terrain():
    dice = libtcod.random_get_int(0, 0, 3)
    if dice == 0:
        return 'shallow water'
    elif dice == 1:
        return 'grass floor'
    else:
        return 'stone floor'

def create_room_cellular_automata(width, height):
    room = Room()
    #Step 1: fill room with random walls/floor
    for y in range(height):
        for x in range(width):
            if libtcod.random_get_int(0, 0, 100) < 60:
                room.set_tile(x, y, 'stone floor')
            else:
                room.set_tile(x, y, 'stone wall')
    #Step 2: iterate over each tile in the room using the 4-5 rule:
    # For each tile, if it is a wall and four or more of its neighbors are walls, it is a wall, else it becomes a floor
    # if it is not a wall and five or more of its neighbors are walls, it becomes a wall, else it stays floor
    for i in range(2):  # 2 iterations
        for tile in room.tiles.keys():
            wall_count = get_adjacent_walls(room, tile[0], tile[1])
            if room.tiles[tile] == 'stone wall':
                if wall_count >= 4:
                    continue
                else:
                    room.tiles[tile] = 'stone floor'
            else:
                if wall_count >= 5:
                    room.tiles[tile] = 'stone wall'
                else:
                    continue
    #Step 3: fill all connected tiles. Replace tiles not connected to the largest section with wall
    done = False
    filled_lists = []
    for y in range(height):
        for x in range(width):
            if room.tiles[(x, y)] == 'stone floor':
                if len(filled_lists) > 0:
                    for list in filled_lists:
                        if (x, y) in list:
                            continue
                new_list = flood_fill(room, filled_lists, x, y)
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
                room.tiles[tile] = 'stone wall'

    return room


def flood_fill(room, filled_lists, x, y):
    new_list = []
    Q = Queue.Queue()
    Q.put((x, y))
    while not Q.empty():
        n = Q.get()
        if room.tiles[n] == 'stone wall' or n in new_list:
            continue
        already_filled = False
        for list in filled_lists:
            if n in list:
                already_filled = True
                break
        if not already_filled:
            new_list.append(n)
            if (n[0] - 1, n[1]) in room.tiles:
                Q.put((n[0] - 1, n[1]))
            if (n[0] + 1, n[1]) in room.tiles:
                Q.put((n[0] + 1, n[1]))
            if (n[0], n[1] - 1) in room.tiles:
                Q.put((n[0], n[1] - 1))
            if (n[0], n[1] + 1) in room.tiles:
                Q.put((n[0], n[1] + 1))
            if (n[0] - 1, n[1] - 1) in room.tiles:
                Q.put((n[0] - 1, n[1] - 1))
            if (n[0] - 1, n[1] + 1) in room.tiles:
                Q.put((n[0] - 1, n[1] + 1))
            if (n[0] + 1, n[1] + 1) in room.tiles:
                Q.put((n[0] + 1, n[1] + 1))
            if (n[0] + 1, n[1] - 1) in room.tiles:
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
            if i_x < 0 or i_x >= bounds[0] or i_y < 0 or i_y >= bounds[1] or room.tiles[(i_x, i_y)] == 'stone wall':
                wall_count += 1
    return wall_count


def random_from_list(list):
    if list is None or len(list) == 0:
        return None
    i = libtcod.random_get_int(0, 0, len(list) - 1)
    return list[i]


def find_closest_open_tile(x, y, exclude=[]):
    explored = [(x, y)]
    neighbors = [(x, y)]
    for tile in main.adjacent_tiles_diagonal(x, y):
        neighbors.append(tile)
    while len(neighbors) > 0:
        tile = neighbors[0]
        if main.in_bounds(tile[0], tile[1]) and not main.is_blocked(tile[0], tile[1], 0) and tile not in exclude:
            return tile  # we found an open tile
        neighbors.remove(tile)
        explored.append(tile)
        for n in main.adjacent_tiles_diagonal(tile[0], tile[1]):
            if n not in explored and n not in neighbors:
                neighbors.append(n)
    return None  # failure


def create_room_rectangle():
    room = Room()
    room.add_rectangle(tile_type=random_terrain())
    return room


def create_room_circle():
    room = Room()
    room.add_circle(tile_type=random_terrain())
    return room

def create_room_cloud():
    room = Room()
    r = libtcod.random_get_int(0, 2, 5)
    room.add_circle(r=r,tile_type=random_terrain())
    nodes = libtcod.random_get_int(0, 2 + r, 6 + r)
    for i in range(nodes):
        angle = (2 * math.pi / nodes) * (float(i) + 1.0)
        coord = int(round(float(r) * math.cos(angle))), int(round(float(r) * math.sin(angle)))
        nodesize = libtcod.random_get_int(0, 1, 2)
        room.add_circle(r=nodesize, x0=coord[0], y0=coord[1])
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
                change_map_tile(x, y, 'stone floor')


def apply_room(room, clear_objects=False, hard_override=False):
    for tile in room.tiles.keys():

        if tile[0] < 0 or tile[1] < 0 or tile[0] >= consts.MAP_WIDTH or tile[1] >= consts.MAP_HEIGHT:
            raise IndexError('Tile index out of range: ' + str(tile[0]) + ', ' + str(tile[1]))

        old_tile = map.tiles[tile[0]][tile[1]]

        if not old_tile.no_overwrite or hard_override:

            change_map_tile(tile[0], tile[1], room.tiles[tile[0], tile[1]])
            if room.tiles[tile[0], tile[1]] == 'default ground':
                if old_tile.blocks:
                    old_tile.tile_type = 'stone floor'
            else:
                old_tile.tile_type = room.tiles[tile[0], tile[1]]
            old_tile.no_overwrite = room.no_overwrite
            if clear_objects or old_tile.blocks:
                for o in map.objects:
                    if o.x == tile[0] and o.y == tile[1] and o is not player.instance:
                        o.destroy()
            if tile in room.data.keys():
                line = room.data[tile]
                if len(line) == 0:
                    pass
                else:
                    apply_data(tile[0], tile[1], line)


def apply_data(x, y, data):

    for i in range(len(data)):
        if data[i] == 'ELEVATION':
            map.tiles[x][y].elevation = int(data[i + 1])
            for obj in main.get_objects(x, y):
                obj.elevation = int(data[i + 1])
            i += 1
        elif data[i].isdigit():
            apply_object(x, y, data[i:])
            break
        elif data[i] == '$':
            apply_item(x, y, data[i:])
            break
        elif data[i] == '>':
            map.objects.append(main.GameObject(x, y, '>', 'stairs', libtcod.white, always_visible=True))
        elif data[i] == '+':
            door = create_door(x, y)
            map.objects.append(door)
            door.send_to_back()


def apply_object(x, y, data):
    monster_id = None
    go_name = None
    go_description = None
    go_blocks = None
    go_char = None
    go_color= None
    for i in range(1, len(data)):
        if data[i] == 'MONSTER_ID':
            monster_id = data[i + 1]
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
    elif go_name is not None:
        new_obj = main.GameObject(x, y, go_char, go_name, go_color, blocks=go_blocks, description=go_description)
        map.add_object(new_obj)

def apply_item(x, y, data):
    loot_level = main.dungeon_level * 5
    category = None
    item_id = None
    quality = None
    material = None
    if len(data) > 1:
        for i in range(1, len(data)):
            if data[i] == 'LOOT_LEVEL':
                loot_level = int(data[i + 1])
                i += 1
            elif data[i] == 'CATEGORY':
                category = data[i + 1]
                i += 1
            elif data[i] == 'ITEM_ID':
                item_id = data[i + 1]
                i += 1
            elif data[i] == 'QUALITY':
                quality = data[i + 1]
                i += 1
            elif data[i] == 'MATERIAL':
                material = data[i + 1]
                i += 1
    if item_id:
        main.spawn_item(item_id, x, y, material=material, quality=quality)
    else:
        item = loot.item_from_table(loot_level=loot_level, category=category)
        item.x = x
        item.y = y
        map.add_object(item)
        item.send_to_back()


def change_map_tile(x, y, tile_type, no_overwrite=False):
    if not main.in_bounds(x, y):
        return 'out of range'
    if not map.tiles[x][y].no_overwrite:
        if tile_type == 'default ground':
            if map.tiles[x][y].blocks:
                map.tiles[x][y].tile_type = 'stone floor'
        else:
            map.tiles[x][y].tile_type = tile_type
        map.tiles[x][y].no_overwrite = no_overwrite


def create_wandering_tunnel(x1, y1, x2, y2, tile_type='stone floor'):
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
        if libtcod.random_get_int(0, 0, 1) == 0 or move == 'xy':
            change_map_tile(current_x - 1, current_y, tile_type)
            change_map_tile(current_x + 1, current_y, tile_type)
            change_map_tile(current_x, current_y - 1, tile_type)
            change_map_tile(current_x, current_y + 1, tile_type)


def create_h_tunnel(x1, x2, y, tile_type='stone floor'):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        change_map_tile(x, y, tile_type)


def create_v_tunnel(y1, y2, x, tile_type='stone floor'):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        change_map_tile(x, y, tile_type)


def scatter_reeds(tiles):
    for tile in tiles:
        if libtcod.random_get_int(0, 0, 4) == 0 and not map.tiles[tile[0]][tile[1]].blocks:
            create_reed(tile[0], tile[1])


def create_terrain_patch(start, terrain_type, min_patch=20, max_patch=400):
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
        for y in range(tile[1] - 1, tile[1] + 2):
            for x in range(tile[0] - 1, tile[0] + 2):
                if x < 0 or y < 0 or x >= consts.MAP_WIDTH or y >= consts.MAP_HEIGHT:
                    continue
                if not map.tiles[x][y].blocks and map.tiles[x][y].tile_type != terrain_type:
                    adjacent.append((x, y))
        for i in range(3):
            if len(adjacent) > 0:
                index = libtcod.random_get_int(0, 0, len(adjacent) - 1)
                Q.put(adjacent[index])
                adjacent.remove(adjacent[index])
    return changed_tiles


def create_reed(x, y):
    obj = main.get_objects(x, y)
    if len(obj) > 0:
        return  # object in the way
    type_here = map.tiles[x][y].tile_type
    if type_here == 'deep water':
        map.tiles[x][y].tile_type = 'shallow water'
    elif type_here != 'shallow water':
        map.tiles[x][y].tile_type = 'grass floor'
    reed = main.GameObject(x, y, 244, 'reeds', libtcod.darker_green, always_visible=True, description='A thicket of '
                           'reeds so tall they obstruct your vision. They are easily crushed underfoot.'
                           , blocks_sight=True, on_step=main.step_on_reed, burns=True)
    map.add_object(reed)

def create_door(x, y):
    obj = main.get_objects(x, y)
    if len(obj) > 0:
        return  # object in the way
    type_here = map.tiles[x][y].tile_type
    if terrain.data[type_here].isFloor:
        map.tiles[x][y].tile_type = "stone floor"
    door = main.GameObject(x, y, '+', 'door', libtcod.brass, always_visible=True, description='A sturdy wooden door',
                           blocks_sight=True, blocks=False, burns=True, interact=main.door_interact,
                           background_color=libtcod.sepia)
    door.closed = True
    return door

def load_features_from_file(filename):
    global feature_categories, features
    feature_categories = {}
    features = {}
    feature_file = open(filename, 'r')
    lines = feature_file.read().split('\n')
    while len(lines) > 0:
        current_line = lines[0]
        lines.remove(lines[0])
        if current_line.startswith('//'):
            continue
        if current_line.startswith('FEATURE'):
            name = current_line.split(' ')[1]

            #do stuff
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
    '.' : 'stone floor',
    ',' : 'grass floor',
    '#' : 'stone wall',
    '-' : 'shallow water',
    '~' : 'deep water',
    ':' : 'chasm',
    '_' : 'default ground',
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
        height = 0
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
            elif lines[i_y].startswith('DEFAULT'):
                default_ground = lines[i_y].split(' ')[1]
            elif lines[i_y].startswith('DEFINE'):
                line = lines[i_y].split(' ')[1:]
                if line[0] == '$':
                    loot_string = line
                elif line[0].isdigit():
                    digit = int(line[0])
                    data_strings[digit] = line
            elif lines[i_y].startswith('SCRIPT'):
                for script in lines[i_y].split(' ')[1:]:
                    script_strings.append(script)
            elif lines[i_y].startswith('HEIGHT'):
                height = int(lines[i_y].split(' ')[1])
                y_index = 0
            elif lines[i_y].startswith('ENDHEIGHT'):
                height = 0
            elif lines[i_y].startswith('CATEGORY'):
                pass
            else:
                for i_x in range(len(lines[i_y])):
                    c = lines[i_y][i_x]
                    try:
                        type = file_key[c]
                    except KeyError:
                        type = file_key[default_ground]

                    if type is not None:
                        feature_room.set_tile(i_x, y_index, type, height)

                    if c == '$':
                        if (i_x, y_index) in feature_room.data.keys():
                            for s in loot_string:
                                feature_room.data[(i_x, y_index)].append(s)
                        else:
                            feature_room.data[(i_x, y_index)] = loot_string
                    elif c == '>':
                        if (i_x, y_index) in feature_room.data.keys():
                            feature_room.data[(i_x, y_index)].append('>')
                        else:
                            feature_room.data[(i_x, y_index)] = '>'
                    elif c == '+':
                        if (i_x, y_index) in feature_room.data.keys():
                            feature_room.data[(i_x, y_index)].append('+')
                        else:
                            feature_room.data[(i_x, y_index)] = '+'
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
        template = feature.room

        if not feature.has_flag(NOREFLECT):
            template.reflect(reflect_x=libtcod.random_get_int(0, 0, 1) == 1, reflect_y=libtcod.random_get_int(0, 0, 1) == 1)

        if rotation is not None:
            template.rotate(rotation)
        elif not feature.has_flag(NOROTATE):
            rotation = angles[libtcod.random_get_int(0, 0, 3)]
            template.rotate(rotation)
        else:
            rotation = 0

        if template.bounds[0] + x > consts.MAP_WIDTH - 1:
            x = consts.MAP_WIDTH - 1 - template.bounds[0]
        if template.bounds[1] + y > consts.MAP_HEIGHT - 1:
            y = consts.MAP_HEIGHT - 1 - template.bounds[1]
        template.set_pos(x, y)

        # Check to see if our new feature collides with any existing features
        if not hard_override:
            new_rect = Rect(template.pos[0], template.pos[1], template.bounds[0], template.bounds[1])
            for rect in feature_rects:
                if rect.intersect(new_rect):
                    return 'failed'
            feature_rects.append(new_rect)

        apply_room(template, feature.has_flag(NOSPAWNS), hard_override=hard_override)

        if open_tiles is not None:
            # If feature has NOSPAWNS flag, remove all tiles from 'open_tiles' list
            if feature.has_flag(NOSPAWNS):
                for tile in template.tiles.keys():
                    if tile in open_tiles:
                        open_tiles.remove(tile)
            else:  # Otherwise remvove only the tiles that are now blocking and add the tiles that are now open
                for tile in template.get_blocked_tiles():
                    if tile in open_tiles:
                        open_tiles.remove(tile)
                for tile in template.get_open_tiles():
                    if tile not in open_tiles:
                        open_tiles.append(tile)

        # reorient the template for next placement
        template.rotate(2 * math.pi - rotation)

        apply_scripts(feature)
        return 'success'

def apply_scripts(feature):
    for script in feature.scripts:
        if script == 'scatter_reeds':
            scatter_reeds(feature.room.get_open_tiles())
        elif script == 'your script here':
            pass


def choose_random_tile(tile_list, exclusive=True):
    chosen_tile = tile_list[libtcod.random_get_int(0, 0, len(tile_list) - 1)]
    if exclusive:
        tile_list.remove(chosen_tile)
    return chosen_tile


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
            main.place_objects(room_array.get_open_tiles())
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
    boss = main.check_boss(main.get_dungeon_level())
    if boss is not None:
        main.spawn_monster(boss, sample[1].center()[0], sample[1].center()[1])


def make_map_marsh():

    rooms = []
    num_rooms = 0

    room = create_room_cellular_automata(consts.MAP_WIDTH - 2, consts.MAP_HEIGHT - 2)
    room.set_pos(1, 1)
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

    if consts.DEBUG_TEST_FEATURE is not None:
        tile = choose_random_tile(open_tiles)
        create_feature(tile[0], tile[1], consts.DEBUG_TEST_FEATURE, open_tiles)

    feature_count = libtcod.random_get_int(0, 0, 10)
    for i in range(feature_count):
        tile = choose_random_tile(open_tiles)
        feature_index = libtcod.random_get_int(0, 0, len(feature_categories['default']) - 1)
        feature_name = feature_categories['default'][feature_index].name
        create_feature(tile[0], tile[1], feature_name, open_tiles)

    player_tile = choose_random_tile(open_tiles)

    player.instance.x = player_tile[0]
    player.instance.y = player_tile[1]
    for i in range(7):
        main.place_objects(open_tiles)
    #stair_tile = choose_random_tile(open_tiles)
    #main.stairs = main.GameObject(stair_tile[0], stair_tile[1], '<', 'stairs downward', libtcod.white, always_visible=True)
    #map.objects.append(main.stairs)
    #main.stairs.send_to_back()
    boss = main.check_boss(main.get_dungeon_level())
    if boss is not None:
        boss_tile = choose_random_tile(open_tiles)
        main.spawn_monster(boss, boss_tile[0], boss_tile[1])


def make_test_space():
    for y in range(2, consts.MAP_HEIGHT - 2):
        for x in range(2, consts.MAP_WIDTH - 2):
            map.tiles[x][y].tile_type = 'stone floor'

    player_tile = (consts.MAP_WIDTH / 2, consts.MAP_HEIGHT / 2)

    if consts.DEBUG_TEST_FEATURE is not None:
        create_feature(player_tile[0] - 3, player_tile[1] - 16, consts.DEBUG_TEST_FEATURE, None)

    player.instance.x = player_tile[0]
    player.instance.y = player_tile[1]

    main.spawn_monster('monster_reeker', player_tile[0], player_tile[1] - 20)

    #stair_tile = (player_tile[0], player_tile[1] + 3)
    #main.stairs = main.GameObject(stair_tile[0], stair_tile[1], '<', 'stairs downward', libtcod.white,
    #                              always_visible=True)
    #map.objects.append(main.stairs)
    #main.stairs.send_to_back()


def make_map_links():
    # make map links
    for link in map.links:
        hlink = True
        r = 0
        c = '>'
        if link[0] == 'north':
            x = libtcod.random_get_int(0, consts.MAP_WIDTH / 3, consts.MAP_WIDTH * 2 / 3)
            y = 1
            r = angles[0]
            c = chr(24)
        elif link[0] == 'south':
            x = libtcod.random_get_int(0, consts.MAP_WIDTH / 3, consts.MAP_WIDTH * 2 / 3)
            y = consts.MAP_HEIGHT - 1
            r = angles[2]
            c = chr(25)
        elif link[0] == 'east':
            x = consts.MAP_WIDTH - 1
            y = libtcod.random_get_int(0, consts.MAP_HEIGHT / 3, consts.MAP_HEIGHT * 2 / 3)
            r = angles[1]
            c = chr(26)
        elif link[0] == 'west':
            x = 1
            y = libtcod.random_get_int(0, consts.MAP_HEIGHT / 3, consts.MAP_HEIGHT * 2 / 3)
            r = angles[3]
            c = chr(27)
        else:
            x = libtcod.random_get_int(0, consts.MAP_WIDTH / 3, consts.MAP_WIDTH * 2 / 3)
            y = libtcod.random_get_int(0, consts.MAP_HEIGHT / 3, consts.MAP_HEIGHT * 2 / 3)
            hlink = False
        if hlink:
            link_feature = random_from_list(feature_categories[link[1].branch + '_hlink']).name
            exclude = []
            create_feature(x, y, link_feature, hard_override=True, rotation=r, open_tiles=exclude)
            closest = find_closest_open_tile(x + 1, y + 1, exclude=exclude)
            create_wandering_tunnel(closest[0], closest[1], x, y, tile_type='default ground')
        else:
            pass  # TODO: Vertical passages
        # find the stairs that we just placed
        stairs = None
        for i in range(len(map.objects) - 1, 0, -1):
            if map.objects[i].name == 'stairs':
                stairs = map.objects[i]
                break
        if stairs is not None:
            stairs.name = 'Path to ' + world.full_names[link[1].branch]
            stairs.description = 'A winding path leading to ' + world.full_names[link[1].branch]
            stairs.link = link
            stairs.interact = main.use_stairs
            stairs.char = c

def make_map(_map):
    global feature_rects, map

    feature_rects = []
    map = _map

    map.objects = [player.instance]

    map.tiles = [[main.Tile('stone wall')
                         for y in range(consts.MAP_HEIGHT)]
                        for x in range(consts.MAP_WIDTH)]
    main.spawned_bosses = {}

    # choose generation type
    if consts.DEBUG_TEST_MAP:
        make_test_space()
    elif map.branch == 'marsh':
        make_map_marsh()
    elif map.branch == 'goblin':
        make_rooms_and_corridors()
    else:
        # make_rooms_and_corridors()
        make_map_marsh()

    make_map_links()

    # make sure the edges are undiggable walls
    for i in range(consts.MAP_WIDTH):
        map.tiles[i][0].tile_type = 'hard stone wall'
        map.tiles[i][consts.MAP_HEIGHT - 1].tile_type = 'hard stone wall'
    for i in range(consts.MAP_HEIGHT):
        map.tiles[0][i].tile_type = 'hard stone wall'
        map.tiles[consts.MAP_WIDTH - 1][i].tile_type = 'hard stone wall'

    pathfinding.map.initialize(map.tiles)
