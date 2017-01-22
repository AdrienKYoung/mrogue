class WorldCell:
    def __init__(self, branch, coord=None, depth=None):
        self.links = []
        self.branch = branch
        self.name = branch
        if coord is not None:
            self.name += '_%d_%d' % (coord[0], coord[1])
        if depth is not None:
            self.name += '_%d' % depth
        self.map = None
        self.objects = None

    def add_link(self, cell, direction):
        self.links.append((direction, cell))
        cell.links.append((opposite(direction), self))


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
    global world_cells

    world_cells = {}
    for y in range(3):
        for x in range(2):
            new_cell = WorldCell('marsh', coord=(x, y))
            if x > 0:
                new_cell.add_link(world_cells['marsh_' + str(x - 1) + '_' + str(y)], 'west')
            if y > 0:
                new_cell.add_link(world_cells['marsh_' + str(x) + '_' + str(y - 1)], 'north')
            world_cells[new_cell.name] = new_cell

world_cells = None