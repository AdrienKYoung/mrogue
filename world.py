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
        self.visited = consts.DEBUG_ALL_EXPLORED

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

def get_map(map_name):
    if map_name not in world_maps.keys():
        raise Exception('Map not found: %s' % map_name)
    return world_maps[map_name]

def get_branch_scaling():
    import dungeon
    scaling = {}
    for branch in dungeon.branches.keys():
        scaling[branch] = dungeon.branches[branch]['scaling']
    return scaling

def set_branch_scaling(scaling):
    import dungeon
    for branch in scaling.keys():
        dungeon.branches[branch]['scaling'] = scaling[branch]

def initialize_world():
    import dungeon
    import npc
    global world_maps

    for branch in dungeon.branches.values():
        branch['scaling'] = 0
    npc.npcs = {}

    world_maps = {}

    world_maps['beach'] = Map('beach')

    # Make Pilgrim's Grotto and connect to beach
    if dungeon.branches['grotto'].get('enabled', False):
        new_map = Map('grotto')
        world_maps['grotto'] = new_map
        world_maps['beach'].add_link(new_map, 'north')

    # Add marsh maps and link back to beach
    if dungeon.branches['marsh'].get('enabled', False):
        for y in range(2):
            for x in range(2):
                new_map = Map('marsh', coord=(x, y))
                if x > 0:
                    new_map.add_link(world_maps['marsh_' + str(x - 1) + '_' + str(y)], 'west')
                if y > 0:
                    new_map.add_link(world_maps['marsh_' + str(x) + '_' + str(y - 1)], 'north')
                world_maps[new_map.name] = new_map
        world_maps['marsh_1_1'].add_link(world_maps['beach'], 'east')

        # Make bog at a random marsh room and link back to the marsh
        if dungeon.branches['bog'].get('enabled', False):
            new_map = Map('bog')
            world_maps['marsh_0_%d' % libtcod.random_get_int(0, 0, 1)].add_link(new_map, 'down')
            world_maps[new_map.name] = new_map

    # Add badlands maps and link back to beach
    if dungeon.branches['badlands'].get('enabled', False):
        for y in range(2):
            for x in range(2):
                new_map = Map('badlands', coord=(x, y))
                if x > 0:
                    new_map.add_link(world_maps['badlands_' + str(x - 1) + '_' + str(y)], 'west')
                if y > 0:
                    new_map.add_link(world_maps['badlands_' + str(x) + '_' + str(y - 1)], 'north')
                world_maps[new_map.name] = new_map
        world_maps['badlands_0_1'].add_link(world_maps['beach'], 'west')

        # Make crypt at a random badlands room and link back to the badlands
        if dungeon.branches['crypt'].get('enabled', False):
            new_map = Map('crypt')
            world_maps['badlands_%d_1' % libtcod.random_get_int(0, 0, 1)].add_link(new_map, 'down')
            world_maps[new_map.name] = new_map

    # Make lines of goblin tunnels and link them below the badlands and marshes
    if dungeon.branches['gtunnels'].get('enabled', False):
        for x in range(3):
            y = 2
            new_map = Map('gtunnels', coord=(x, y))
            if x > 0:
                new_map.add_link(world_maps['gtunnels_' + str(x - 1) + '_' + str(y)], 'west')
            world_maps[new_map.name] = new_map
        for y in range(2):
            x = 1
            new_map = Map('gtunnels', coord=(x, y))
            if y > 0:
                new_map.add_link(world_maps['gtunnels_' + str(x) + '_' + str(y - 1)], 'north')
            world_maps[new_map.name] = new_map
        world_maps['gtunnels_1_1'].add_link(world_maps['gtunnels_1_2'], 'south')

        new_map = Map('gtunnels', coord=(0, 1))
        new_map.add_link(world_maps['gtunnels_1_1'], 'east')
        world_maps[new_map.name] = new_map
        new_map = Map('gtunnels', coord=(0, 3))
        new_map.add_link(world_maps['gtunnels_0_2'], 'north')
        if dungeon.branches['marsh'].get('enabled', False):
            new_map.add_link(world_maps['marsh_1_0'], 'up')
        world_maps[new_map.name] = new_map
        new_map = Map('gtunnels', coord=(2, 3))
        new_map.add_link(world_maps['gtunnels_2_2'], 'north')
        if dungeon.branches['badlands'].get('enabled', False):
            new_map.add_link(world_maps['badlands_0_0'], 'up')
        world_maps[new_map.name] = new_map

    # Make river
    if dungeon.branches['river'].get('enabled', False):
        new_map = Map('river', depth=0)
        if dungeon.branches['marsh'].get('enabled', False):
            new_map.add_link(world_maps['marsh_1_0'], 'south')
        world_maps[new_map.name] = new_map
        new_map = Map('river', depth=1)
        if dungeon.branches['badlands'].get('enabled', False):
            new_map.add_link(world_maps['badlands_0_0'], 'south')
        world_maps[new_map.name] = new_map
        if dungeon.branches['crossing'].get('enabled', False):
            new_map = Map('crossing')
            new_map.add_link(world_maps['river_0'], 'west')
            new_map.add_link(world_maps['river_1'], 'east')
            world_maps[new_map.name] = new_map

    # Add Frozen Forest maps and link back to river/goblin tunnels
    if dungeon.branches['forest'].get('enabled', False):
        for y in range(2):
            for x in range(2):
                new_map = Map('forest', coord=(x, y))
                if x > 0:
                    new_map.add_link(world_maps['forest_' + str(x - 1) + '_' + str(y)], 'west')
                if y > 0:
                    new_map.add_link(world_maps['forest_' + str(x) + '_' + str(y - 1)], 'north')
                world_maps[new_map.name] = new_map
        if dungeon.branches['river'].get('enabled', False):
            world_maps['forest_1_1'].add_link(world_maps['river_1'], 'south')
        if dungeon.branches['gtunnels'].get('enabled', False):
            world_maps['forest_0_1'].add_link(world_maps['gtunnels_1_1'], 'down')

        # Make eolith caverns at a random forest room and link back to the forest
        if dungeon.branches['eolith'].get('enabled', False):
            new_map = Map('eolith')
            world_maps['forest_%d_%d' % (libtcod.random_get_int(0, 0, 1), libtcod.random_get_int(0, 0, 1))].add_link(new_map, 'down')
            world_maps[new_map.name] = new_map

    # Add Garden maps and link back to river/goblin tunnels
    if dungeon.branches['garden'].get('enabled', False):
        for y in range(3):
            x = 1
            new_map = Map('garden', coord=(x, y))
            if y > 0:
                new_map.add_link(world_maps['garden_' + str(x) + '_' + str(y - 1)], 'north')
            world_maps[new_map.name] = new_map
        new_map = Map('garden', coord=(0, 1))
        new_map.add_link(world_maps['garden_1_1'], 'east')
        world_maps[new_map.name] = new_map
        if dungeon.branches['river'].get('enabled', False):
            world_maps['garden_1_2'].add_link(world_maps['river_0'], 'south')
        if dungeon.branches['gtunnels'].get('enabled', False):
            world_maps['garden_1_2'].add_link(world_maps['gtunnels_0_1'], 'down')

    if dungeon.branches['garden'].get('enabled', False) and dungeon.branches['forest'].get('enabled', False):
        # Link gardens and forest
        world_maps['garden_1_1'].add_link(world_maps['forest_0_0'], 'east')

    # Add catacombs map and link back to gtunnels
    if dungeon.branches['catacombs'].get('enabled', False):
        for x in range(4):
            new_map = Map('catacombs', coord=(x, 0))
            world_maps[new_map.name] = new_map
            if x > 0:
                new_map.add_link(world_maps['catacombs_' + str(x - 1) + '_0'], 'west')
        if dungeon.branches['gtunnels'].get('enabled', False):
            world_maps['catacombs_3_0'].add_link(world_maps['gtunnels_1_0'], 'up')

    if dungeon.branches['bone'].get('enabled', False):
        for x in range(4):
            new_map = Map('bone', coord=(x, 0))
            world_maps[new_map.name] = new_map
            if x > 0:
                new_map.add_link(world_maps['bone_' + str(x - 1) + '_0'], 'west')
        if dungeon.branches['catacombs'].get('enabled', False):
            world_maps['bone_3_0'].add_link(world_maps['catacombs_3_0'], 'up')

    # Add unnamed tomb
    if dungeon.branches['tomb'].get('enabled', False):
        new_map = Map('tomb')
        world_maps['tomb'] = new_map
        world_maps['catacombs_0_0'].add_link(new_map, 'up')

    # Add tower of mages and link back to forest
    if dungeon.branches['tower'].get('enabled', False):
        for z in range(4):
            new_map = Map('tower', depth=z)
            if z > 0:
                new_map.add_link(world_maps['tower_' + str(z - 1)], 'down')
            world_maps[new_map.name] = new_map
        if dungeon.branches['forest'].get('enabled', False):
            world_maps['tower_0'].add_link(world_maps['forest_1_1'], 'west')

    # Add lava lake
    if dungeon.branches['lavalake'].get('enabled', False):
        new_map = Map('lavalake')
        world_maps['lavalake'] = new_map
        if dungeon.branches['badlands'].get('enabled', False):
            world_maps['badlands_1_0'].add_link(new_map, 'north')

    # Add slagfields maps and link back to lava/tower
    if dungeon.branches['slagfields'].get('enabled', False):
        for y in range(2):
            for x in range(2):
                new_map = Map('slagfields', coord=(x, y))
                if x > 0:
                    new_map.add_link(world_maps['slagfields_' + str(x - 1) + '_' + str(y)], 'west')
                if y > 0:
                    new_map.add_link(world_maps['slagfields_' + str(x) + '_' + str(y - 1)], 'north')
                world_maps[new_map.name] = new_map
        if dungeon.branches['tower'].get('enabled', False):
            world_maps['slagfields_0_0'].add_link(world_maps['tower_0'], 'west')
        if dungeon.branches['lavalake'].get('enabled', False):
            world_maps['slagfields_0_1'].add_link(world_maps['lavalake'], 'west')

    # Add foundry of war maps and link back to slagfields
    if dungeon.branches['foundry'].get('enabled', False):
        for y in range(2):
            for x in range(2):
                new_map = Map('foundry', coord=(x, y), depth=0)
                if x > 0:
                    new_map.add_link(world_maps['foundry_' + str(x - 1) + '_' + str(y) + '_0'], 'west')
                if y > 0:
                    new_map.add_link(world_maps['foundry_' + str(x) + '_' + str(y - 1) + '_0'], 'north')
                world_maps[new_map.name] = new_map
        new_map = Map('foundry', coord=(1, 0), depth=1)
        new_map.add_link(world_maps['foundry_1_0_0'], 'down')
        world_maps[new_map.name] = new_map
        if dungeon.branches['slagfields'].get('enabled', False):
            world_maps['foundry_0_1_0'].add_link(world_maps['slagfields_1_0'], 'west')

    # Add giant woods/canopy maps and link back to gardens
    if dungeon.branches['giantwoods'].get('enabled', False):
        for y in range(2):
            for x in range(2):
                new_map = Map('giantwoods', coord=(x, y))
                if x > 0:
                    new_map.add_link(world_maps['giantwoods_' + str(x - 1) + '_' + str(y)], 'west')
                if y > 0:
                    new_map.add_link(world_maps['giantwoods_' + str(x) + '_' + str(y - 1)], 'north')
                world_maps[new_map.name] = new_map
        if dungeon.branches['garden'].get('enabled', False):
            world_maps['giantwoods_1_0'].add_link(world_maps['garden_0_1'], 'north')

    if dungeon.branches['canopy'].get('enabled', False):
        for y in range(2):
            for x in range(2):
                new_map = Map('canopy', coord=(x, y))
                if x > 0:
                    new_map.add_link(world_maps['canopy_' + str(x - 1) + '_' + str(y)], 'west')
                if y > 0:
                    new_map.add_link(world_maps['canopy_' + str(x) + '_' + str(y - 1)], 'north')
                if dungeon.branches['giantwoods'].get('enabled', False):
                    new_map.add_link(world_maps['giantwoods_' + str(x) + '_' + str(y)], 'down')
                world_maps[new_map.name] = new_map

    # Add sunken temple and link back to tomb/giant woods
    if dungeon.branches['temple'].get('enabled', False):
        for x in range(2):
            for z in range(2):
                new_map = Map('temple', coord=(x, 1), depth=z)
                if x > 0:
                    new_map.add_link(world_maps['temple_' + str(x - 1) + '_1_' + str(z)], 'west')
                if z > 0:
                    new_map.add_link(world_maps['temple_' + str(x) + '_1_' + str(z - 1)], 'up')
                world_maps[new_map.name] = new_map
        new_map = Map('temple', coord=(0, 0), depth=1)
        new_map.add_link(world_maps['temple_0_1_1'], 'south')
        world_maps[new_map.name] = new_map
        if dungeon.branches['giantwoods'].get('enabled', False):
            world_maps['temple_1_1_0'].add_link(world_maps['giantwoods_0_0'], 'up')
        if dungeon.branches['tomb'].get('enabled', False):
            world_maps['temple_1_1_0'].add_link(world_maps['tomb'], 'north')

    # Add mines maps and link back to gtunnels/bone pits
    if dungeon.branches['mines'].get('enabled', False):
        for z in range(3):
            new_map = Map('mines', coord=(0, 1), depth=z)
            if z > 0:
                new_map.add_link(world_maps['mines_0_1_' + str(z - 1)], 'up')
            world_maps[new_map.name] = new_map
        new_map = Map('mines', coord=(0, 0), depth=1)
        new_map.add_link(world_maps['mines_0_1_1'], 'south')
        if dungeon.branches['bone'].get('enabled', False):
            new_map.add_link(world_maps['bone_3_0'], 'north')
        world_maps[new_map.name] = new_map
        if dungeon.branches['gtunnels'].get('enabled', False):
            world_maps['mines_0_1_0'].add_link(world_maps['gtunnels_1_2'], 'up')

    # Add depths maps and link back to mines
    if dungeon.branches['depths'].get('enabled', False):
        for y in range(2):
            for x in range(2):
                new_map = Map('depths', coord=(x, y))
                if x > 0:
                    new_map.add_link(world_maps['depths_' + str(x - 1) + '_' + str(y)], 'west')
                if y > 0 and x == 0:
                    new_map.add_link(world_maps['depths_' + str(x) + '_' + str(y - 1)], 'north')
                world_maps[new_map.name] = new_map
        if dungeon.branches['mines'].get('enabled', False):
            world_maps['depths_1_1'].add_link(world_maps['mines_0_1_2'], 'up')

    # Add menagerie
    if dungeon.branches['menagerie'].get('enabled', False):
        new_map = Map('menagerie')
        world_maps['menagerie'] = new_map
        if dungeon.branches['garden'].get('enabled', False):
            world_maps['garden_1_0'].add_link(new_map, 'west')

    # Add gatehouse
    if dungeon.branches['gatehouse'].get('enabled', False):
        new_map = Map('gatehouse')
        world_maps['gatehouse'] = new_map
        if dungeon.branches['garden'].get('enabled', False):
            world_maps['garden_1_0'].add_link(new_map, 'east')
        if dungeon.branches['forest'].get('enabled', False):
            world_maps['forest_0_0'].add_link(new_map, 'north')

    # Add battlements maps and link back to gatehouse
    if dungeon.branches['battlements'].get('enabled', False):
        for x in range(3):
            new_map = Map('battlements', coord=(x, 0))
            world_maps[new_map.name] = new_map
            if x > 0:
                new_map.add_link(world_maps['battlements_' + str(x - 1) + '_0'], 'west')
        new_map = Map('battlements', coord=(2, 1))
        new_map.add_link(world_maps['battlements_2_0'], 'north')
        if dungeon.branches['gatehouse'].get('enabled', False):
            new_map.add_link(world_maps['gatehouse'], 'west')
        world_maps[new_map.name] = new_map

    # Add city maps and link back to the battlements
    if dungeon.branches['city'].get('enabled', False):
        for x in range(3):
            new_map = Map('city', coord=(x, 1))
            world_maps[new_map.name] = new_map
            if x > 0:
                new_map.add_link(world_maps['city_' + str(x - 1) + '_1'], 'west')
        new_map = Map('city', coord=(1, 0))
        new_map.add_link(world_maps['city_1_1'], 'south')
        world_maps[new_map.name] = new_map
        new_map = Map('city', coord=(1, 2))
        new_map.add_link(world_maps['city_1_1'], 'north')
        if dungeon.branches['battlements'].get('enabled', False):
            new_map.add_link(world_maps['battlements_0_0'], 'south')
        world_maps[new_map.name] = new_map

    # Add cathedral
    if dungeon.branches['cathedral'].get('enabled', False):
        new_map = Map('cathedral')
        world_maps['cathedral'] = new_map
        if dungeon.branches['city'].get('enabled', False):
            world_maps['city_1_2'].add_link(new_map, 'west')

    # Add cursed path maps and link back to the citadel/tomb
    if dungeon.branches['cursed'].get('enabled', False):
        for y in range(2):
            new_map = Map('cursed', coord=(1, y))
            world_maps[new_map.name] = new_map
            if y > 0:
                new_map.add_link(world_maps['cursed_1_' + str(y - 1)], 'north')
        for y in range(1, 3):
            new_map = Map('cursed', coord=(0, y))
            world_maps[new_map.name] = new_map
            if y > 1:
                new_map.add_link(world_maps['cursed_0_' + str(y - 1)], 'north')
        world_maps['cursed_1_1'].add_link(world_maps['cursed_0_1'], 'west')
        if dungeon.branches['cathedral'].get('enabled', False):
            world_maps['cursed_1_0'].add_link(world_maps['cathedral'], 'up')
        if dungeon.branches['tomb'].get('enabled', False):
            world_maps['tomb'].add_link(world_maps['cursed_0_2'], 'north')

    # Make test map
    world_maps['test'] = Map('test')

world_maps = None
