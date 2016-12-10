import game as main
import consts
import libtcodpy as libtcod
import random
import math
import terrain
import Queue

class Room:
    def __init__(self):
        self.tiles = {}
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None
        self.pos = 0, 0

    # define the world-space position of the upper-left-hand corner of this room. Adjust all tile positions
    def set_pos(self, x, y):
        new_tiles = {}
        for tile in self.tiles.keys():
            new_x = tile[0] - self.pos[0] + x - self.min_x
            new_y = tile[1] - self.pos[1] + y - self.min_y
            new_tiles[new_x, new_y] = self.tiles[(tile[0], tile[1])]
        w = self.bounds[0] - 1
        h = self.bounds[1] - 1
        self.min_x = x
        self.min_y = y
        self.max_x = self.min_x + w
        self.max_y = self.min_y + h
        self.tiles = new_tiles
        self.pos = x, y

    def set_tile(self, x, y, tile_type):
        if self.min_x is None or self.min_x > x:
            self.min_x = x
        if self.max_x is None or self.max_x < x:
            self.max_x = x
        if self.min_y is None or self.min_y > y:
            self.min_y = y
        if self.max_y is None or self.max_y < y:
            self.max_y = y
        self.tiles[(x, y)] = tile_type

    def get_open_tiles(self):
        return_tiles = []
        for tile in self.tiles.keys():
            if not terrain.data[self.tiles[tile]].blocks:
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
                main.dungeon_map[x][y].tile_type = 'shallow water'
            elif dice == 1:
                main.dungeon_map[x][y].tile_type = 'grass floor'
            else:
                main.dungeon_map[x][y].tile_type = 'stone floor'


def apply_room(room):
    for tile in room.tiles.keys():
        main.dungeon_map[tile[0]][tile[1]].tile_type = room.tiles[tile[0], tile[1]]

def create_wandering_tunnel(x1, y1, x2, y2):
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
        main.dungeon_map[current_x][current_y].tile_type = 'stone floor'
        if libtcod.random_get_int(0, 0, 1) == 0 or move == 'xy':
            main.dungeon_map[current_x - 1][current_y].tile_type = 'stone floor'
            main.dungeon_map[current_x + 1][current_y].tile_type = 'stone floor'
            main.dungeon_map[current_x][current_y - 1].tile_type = 'stone floor'
            main.dungeon_map[current_x][current_y + 1].tile_type = 'stone floor'


def create_h_tunnel(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        main.dungeon_map[x][y].tile_type = 'stone floor'


def create_v_tunnel(y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        main.dungeon_map[x][y].tile_type = 'stone floor'


def scatter_reeds(tiles):
    for tile in tiles:
        if libtcod.random_get_int(0, 0, 4) == 0 and not main.dungeon_map[tile[0]][tile[1]].blocks:
            create_reed(tile[0], tile[1])

    #for y in range(room.w - 1):
    #    for x in range(room.h - 1):
    #        if libtcod.random_get_int(0, 0, 3) == 0 and not main.dungeon_map[x + room.x1][y + room.y1].blocks:
    #            create_reed(room.x1 + x, room.y1 + y)


def create_terrain_patch(start, terrain_type, min_patch=20, max_patch=400):
    patch_limit = min_patch + libtcod.random_get_int(0, 0, max_patch - min_patch)
    patch_count = 0
    Q = Queue.Queue()
    Q.put(start)
    changed_tiles = []
    while not Q.empty() and patch_count < patch_limit:
        tile = Q.get()
        main.dungeon_map[tile[0]][tile[1]].tile_type = terrain_type
        changed_tiles.append(tile)
        patch_count += 1
        adjacent = []
        for y in range(tile[1] - 1, tile[1] + 2):
            for x in range(tile[0] - 1, tile[0] + 2):
                if x < 0 or y < 0 or x >= consts.MAP_WIDTH or y >= consts.MAP_HEIGHT:
                    continue
                if not main.dungeon_map[x][y].blocks and main.dungeon_map[x][y].tile_type != terrain_type:
                    adjacent.append((x, y))
        for i in range(3):
            if len(adjacent) > 0:
                index = libtcod.random_get_int(0, 0, len(adjacent) - 1)
                Q.put(adjacent[index])
                adjacent.remove(adjacent[index])
    return changed_tiles


def create_reed(x, y):
    type_here = main.dungeon_map[x][y].tile_type
    if type_here == 'deep water':
        main.dungeon_map[x][y].tile_type = 'shallow water'
    elif type_here != 'shallow water':
        main.dungeon_map[x][y].tile_type = 'grass floor'
    reed = main.GameObject(x, y, 244, 'reeds', libtcod.darker_green, always_visible=True, description='A thicket of '
                           'reeds so tall they obstruct your vision. They are easily crushed underfoot.'
                           , blocks_sight=True, on_step=main.step_on_reed, burns=True)
    main.objects.append(reed)


def create_feature_from_file(filename, x, y):
    feature_file = open(filename, 'r')
    feature_lines = []
    for line in feature_file:
        feature_lines.append(line)
    for i_y in range(len(feature_lines)):
        for i_x in range(len(feature_lines[i_y])):
            pos = x + i_x, y + i_y
            if pos[0] < 0 or pos[1] < 0 or pos[0] >= consts.MAP_WIDTH or pos[1] >= consts.MAP_HEIGHT:
                continue
            type = None
            if feature_lines[i_y][i_x] == '.':
                type = 'stone floor'
            elif feature_lines[i_y][i_x] == '#':
                type = 'stone wall'
            if type is not None:
                main.dungeon_map[pos[0]][pos[1]].tile_type = type

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
                main.player.x = new_x
                main.player.y = new_y
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
    x, y = sample[0].center()
    main.stairs = main.GameObject(x, y, '<', 'stairs downward', libtcod.white, always_visible=True)
    main.objects.append(main.stairs)
    main.stairs.send_to_back()
    x, y = sample[len(sample) - 1].center()
    level_shrine = main.GameObject(x, y, '=', 'shrine of power', libtcod.white, always_visible=True, interact=None)
    main.objects.append(level_shrine)
    level_shrine.send_to_back()
    boss = main.check_boss(main.get_dungeon_level())
    if boss is not None:
        main.spawn_monster(boss, sample[1].center()[0], sample[1].center()[1])


def make_one_big_room():

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

    #tile = choose_random_tile(open_tiles)
    #create_feature_from_file('features.txt', tile[0], tile[1])

    player_tile = choose_random_tile(open_tiles)

    main.player.x = player_tile[0]
    main.player.y = player_tile[1]
    for i in range(10):
        main.place_objects(open_tiles)
    stair_tile = choose_random_tile(open_tiles)
    main.stairs = main.GameObject(stair_tile[0], stair_tile[1], '<', 'stairs downward', libtcod.white, always_visible=True)
    main.objects.append(main.stairs)
    main.stairs.send_to_back()
    boss = main.check_boss(main.get_dungeon_level())
    if boss is not None:
        boss_tile = choose_random_tile(open_tiles)
        main.spawn_monster(boss, boss_tile[0], boss_tile[1])

def choose_random_tile(tile_list, exclusive=True):
    chosen_tile = tile_list[libtcod.random_get_int(0, 0, len(tile_list) - 1)]
    if exclusive:
        tile_list.remove(chosen_tile)
    return chosen_tile

def make_map():

    main.objects = [main.player]

    main.dungeon_map = [[main.Tile('stone wall')
                         for y in range(consts.MAP_HEIGHT)]
                        for x in range(consts.MAP_WIDTH)]
    main.spawned_bosses = {}

    # choose generation type
    if libtcod.random_get_int(0, 0, 1) == 0 and False:
        make_rooms_and_corridors()
    else:
        make_one_big_room()
