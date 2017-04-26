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
        self.visited = consts.DEBUG_REVEAL_MAP

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

    # Make Pilgrim's Grotto and connect to beach
    new_map = Map('grotto')
    world_maps['grotto'] = new_map
    world_maps['beach'].add_link(new_map, 'north')

    # Add marsh maps and link back to beach
    for y in range(2):
        for x in range(3):
            new_map = Map('marsh', coord=(x, y))
            if x > 0:
                new_map.add_link(world_maps['marsh_' + str(x - 1) + '_' + str(y)], 'west')
            if y > 0:
                new_map.add_link(world_maps['marsh_' + str(x) + '_' + str(y - 1)], 'north')
            world_maps[new_map.name] = new_map
    world_maps['marsh_2_1'].add_link(world_maps['beach'], 'east')

    # Add badlands maps and link back to beach
    for y in range(3):
        for x in range(2):
            new_map = Map('badlands', coord=(x, y))
            if x > 0:
                new_map.add_link(world_maps['badlands_' + str(x - 1) + '_' + str(y)], 'west')
            if y > 0:
                new_map.add_link(world_maps['badlands_' + str(x) + '_' + str(y - 1)], 'north')
            world_maps[new_map.name] = new_map
    world_maps['badlands_0_2'].add_link(world_maps['beach'], 'west')

    # Make lines of goblin tunnels and link them below the badlands and marshes
    for x in range(1, 4):
        y = 2
        new_map = Map('gtunnels', coord=(x, y))
        if x > 1:
            new_map.add_link(world_maps['gtunnels_' + str(x - 1) + '_' + str(y)], 'west')

        world_maps[new_map.name] = new_map
    for y in range(2):
        x = 2
        new_map = Map('gtunnels', coord=(x, y))
        if y > 0:
            new_map.add_link(world_maps['gtunnels_' + str(x) + '_' + str(y - 1)], 'north')
        world_maps[new_map.name] = new_map
    for x in range(2):
        y = 1
        new_map = Map('gtunnels', coord=(x, y))
        if x > 0:
            new_map.add_link(world_maps['gtunnels_' + str(x - 1) + '_' + str(y)], 'west')
        world_maps[new_map.name] = new_map
    new_map = Map('gtunnels', coord=(3, 0))
    new_map.add_link(world_maps['gtunnels_2_0'], 'west')
    world_maps[new_map.name] = new_map
    world_maps['gtunnels_2_2'].add_link(world_maps['gtunnels_2_1'], 'north')
    world_maps['gtunnels_2_1'].add_link(world_maps['gtunnels_1_1'], 'west')
    world_maps['gtunnels_1_2'].add_link(world_maps['marsh_2_0'], 'up')
    world_maps['gtunnels_3_2'].add_link(world_maps['badlands_0_1'], 'up')

    # Add Frozen Forest maps and link back to badlands/goblin tunnels
    for y in range(2):
        for x in range(3):
            new_map = Map('forest', coord=(x, y))
            if x > 0:
                new_map.add_link(world_maps['forest_' + str(x - 1) + '_' + str(y)], 'west')
            if y > 0:
                new_map.add_link(world_maps['forest_' + str(x) + '_' + str(y - 1)], 'north')
            world_maps[new_map.name] = new_map
    world_maps['forest_2_1'].add_link(world_maps['badlands_1_0'], 'south')
    world_maps['forest_1_1'].add_link(world_maps['gtunnels_3_0'], 'down')

    # Add Garden maps and link back to marsh/goblin tunnels
    for y in range(3):
        for x in range(2):
            new_map = Map('garden', coord=(x, y))
            if x > 0:
                new_map.add_link(world_maps['garden_' + str(x - 1) + '_' + str(y)], 'west')
            if y > 0:
                new_map.add_link(world_maps['garden_' + str(x) + '_' + str(y - 1)], 'north')
            world_maps[new_map.name] = new_map
    world_maps['garden_0_2'].add_link(world_maps['marsh_1_0'], 'south')
    world_maps['garden_1_2'].add_link(world_maps['gtunnels_0_1'], 'down')

    # Link gardens and forest
    world_maps['garden_1_0'].add_link(world_maps['forest_0_0'], 'east')

world_maps = None
