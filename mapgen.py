import game as main
import consts
import libtcodpy as libtcod
import random
import math


class Room:
    def __init__(self):
        self.tiles = {}
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None

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


def create_room_random():
    choice = libtcod.random_get_int(0, 0, 2)

    choice = 2
    if choice == 0:
        return create_room_rectangle()
    elif choice == 1:
        return create_room_circle()
    elif choice == 2:
        return create_room_cloud()
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


def apply_room(room, x0, y0):
    dimensions = room.bounds
    for x in range(dimensions[0]):
        for y in range(dimensions[1]):
            key = x + room.min_x, y + room.min_y
            if key in room.tiles:
                main.dungeon_map[x0 + x][y0 + y].tile_type = room.tiles[key]

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
        if libtcod.random_get_int(0, 0, 1) == 0:
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

def make_map():

    main.objects = [main.player]

    main.dungeon_map = [[main.Tile('stone wall')
                    for y in range(consts.MAP_HEIGHT)]
                   for x in range(consts.MAP_WIDTH)]

    rooms = []
    main.spawned_bosses = {}
    num_rooms = 0

    for r in range(consts.MG_MAX_ROOMS):

        room_array = create_room_random()
        dimensions = room_array.bounds
        #dimensions = len(room_array), len(room_array[0])

        #w = libtcod.random_get_int(0, consts.MG_ROOM_MIN_SIZE, consts.MG_ROOM_MAX_SIZE)
        #h = libtcod.random_get_int(0, consts.MG_ROOM_MIN_SIZE, consts.MG_ROOM_MAX_SIZE)
        #x = libtcod.random_get_int(0, 0, consts.MAP_WIDTH - w - 1)
        #y = libtcod.random_get_int(0, 0, consts.MAP_HEIGHT - h - 1)
        x = libtcod.random_get_int(0, 1, consts.MAP_WIDTH - dimensions[0] - 1)
        y = libtcod.random_get_int(0, 1, consts.MAP_HEIGHT - dimensions[1] - 1)


        #new_room = Rect(x, y, w, h)
        new_room = Rect(x, y, dimensions[0], dimensions[1])

        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #create_room(new_room)
            apply_room(room_array, new_room.x1, new_room.y1)
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                main.player.x = new_x
                main.player.y = new_y
            else:
                (prev_x, prev_y) = rooms[num_rooms - 1].center()
                create_wandering_tunnel(prev_x, prev_y, new_x, new_y)
                #if libtcod.random_get_int(0, 0, 1) == 0:
                #    create_h_tunnel(prev_x, new_x, prev_y)
                #    create_v_tunnel(prev_y, new_y, new_x)
                #else:
                #    create_v_tunnel(prev_y, new_y, prev_x)
                #    create_h_tunnel(prev_x, new_x, new_y)
            main.place_objects(new_room)
            rooms.append(new_room)
            num_rooms += 1

    # Generate every-floor random features
    sample = random.sample(rooms, 2)
    x, y = sample[0].center()
    main.stairs = main.GameObject(x, y, '<', 'stairs downward', libtcod.white, always_visible=True)
    main.objects.append(main.stairs)
    main.stairs.send_to_back()
    x, y = sample[1].center()
    level_shrine = main.GameObject(x, y, '=', 'shrine of power', libtcod.white, always_visible=True, interact=main.level_up)
    main.objects.append(level_shrine)
    level_shrine.send_to_back()
    boss = main.check_boss(main.get_dungeon_level())
    if boss is not None:
        main.spawn_monster(boss, sample[1])
