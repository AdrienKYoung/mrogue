import game as main

class Map:
    def __init__(self, branch, coord=None, depth=None, difficulty=0):
        self.links = []
        self.branch = branch
        self.name = branch
        if coord is not None:
            self.name += '_%d_%d' % (coord[0], coord[1])
        if depth is not None:
            self.name += '_%d' % depth
        self.tiles = None
        self.objects = None
        self.fighters = None
        self.tickers = []
        self.difficulty = difficulty
        self.pathfinding = None

    def add_link(self, cell, direction):
        self.links.append((direction, cell))
        cell.links.append((opposite(direction), self))

    def add_object(self, object):
        if not isinstance(object, main.GameObject):
            raise ValueError("{} is not a game object!".format(object))
        self.objects.append(object)
        if object.fighter:
            self.fighters.append(object)


def opposite(direction):
    if direction == 'north':
        return 'south'
    elif direction == 'south':
        return 'north'
    elif direction == 'east':
        return 'west'
    elif direction == 'west':
        return 'east'
    elif direction == 'up':
        return 'down'
    elif direction == 'down':
        return 'up'
    else:
        return None

def initialize_world():
    global world_maps

    world_maps = {}

    world_maps['beach'] = Map('beach')
    world_maps['forest'] = Map('forest')
    world_maps['garden'] = Map('garden')

    for y in range(2):
        for x in range(3):
            new_map = Map('marsh', coord=(x, y))
            if x > 0:
                new_map.add_link(world_maps['marsh_' + str(x - 1) + '_' + str(y)], 'west')
            if y > 0:
                new_map.add_link(world_maps['marsh_' + str(x) + '_' + str(y - 1)], 'north')
            world_maps[new_map.name] = new_map
    world_maps['marsh_2_1'].add_link(world_maps['beach'], 'east')

    for y in range(3):
        for x in range(2):
            new_map = Map('badlands', coord=(x, y))
            if x > 0:
                new_map.add_link(world_maps['badlands_' + str(x - 1) + '_' + str(y)], 'west')
            if y > 0:
                new_map.add_link(world_maps['badlands_' + str(x) + '_' + str(y - 1)], 'north')
            world_maps[new_map.name] = new_map
    world_maps['badlands_0_2'].add_link(world_maps['beach'], 'west')

world_maps = None