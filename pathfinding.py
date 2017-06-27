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
import Queue
import math
import libtcodpy as libtcod
import log

MAX_EDGES_DISCOVERED = 100
# Movement type flags:
NORMAL = 1
FLYING = 2
AQUATIC = 4
CLIMBING = 8
TUNNELING = 16
LAVA = 32

class Edge:
    def __init__(self, coord):
        self.coord = coord
        self.weights = {
            NORMAL : None,
            FLYING : None,
            AQUATIC : None,
            CLIMBING : None,
            TUNNELING : None,
            LAVA : None,
        }

class Graph:
    def __init__(self):
        self.edges = { }

    def initialize(self):

        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):
                self.edges[(x, y)] = []
                for tile in main.adjacent_tiles_diagonal(x, y):
                    self.edge_to((x, y), tile)

        for obj in main.current_map.objects:
            if obj.blocks:
                self.mark_blocked((obj.x, obj.y))

    def edge_to(self, source, neighbor, mod=1.0):
        if not source in self.edges:
            self.edges[source] = []
        edge = None
        for e in self.edges[source]:
            if e.coord == neighbor:
                edge = e
                break
        if edge is None:
            edge = Edge(neighbor)
            self.edges[source].append(edge)

        if source[0] != neighbor[0] and source[1] != neighbor[1]:
            mod *= 1.2

        source_tile = main.current_map.tiles[source[0]][source[1]]
        neighbor_tile = main.current_map.tiles[neighbor[0]][neighbor[1]]
        if not neighbor_tile.blocks:
            # If the tile is not blocked, that's all we care about for flying movement.
            edge.weights[FLYING] = 1.0 * mod
            if neighbor_tile.tile_type == 'lava':
                edge.weights[LAVA] = 1.0 * mod
            elif neighbor_tile.elevation == source_tile.elevation or neighbor_tile.is_ramp or source_tile.is_ramp:
                # If these tiles are on the same elevation, or one of them is a ramp, we have normal connectivity
                if neighbor_tile.is_water:
                    # If this tile is a water space, it has normal movement costs for aquatic movement
                    edge.weights[AQUATIC] = 1.0 * mod
                    if not neighbor_tile.jumpable:
                        # If this is deep water, it is very costly for normal movement
                        edge.weights[NORMAL] = 5.0 * mod
                    else:
                        # If this is shallow water, it is slightly more costly than normal movement
                        edge.weights[NORMAL] = 1.05 * mod
                elif not neighbor_tile.is_pit:
                    edge.weights[NORMAL] = 1.0 * mod
            elif not neighbor_tile.is_pit:
                # These tiles are separated by elevation. Climbing movement can cross, though a bit costly
                edge.weights[CLIMBING] = 2.0 * mod
        else:
            # Tunneling can move through solid walls, slightly more costly than normal movement
            edge.weights[TUNNELING] = 1.05 * mod

    def mark_blocked(self, coord):
        for adj in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            if adj in self.edges:
                for e in self.edges[adj]:
                    if e.coord == coord:
                        for weight in e.weights.keys():
                            e.weights[weight] = None
                        break

    def mark_unblocked(self, coord):
        for adj in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            self.edge_to(adj, coord)

    # Returns true if there is at least one adjacent tile with an edge leading to this tile (following valid movement)
    def is_accessible(self, coord, movement_type=NORMAL):
        for adj in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            if adj in self.edges:
                for e in self.edges[adj]:
                    if e.coord == coord:
                        for weight in e.weights.keys():
                            if weight & movement_type == weight and e.weights[weight] is not None:
                                return True
        return False


    def a_star_search(self, start, goal, movement_type=NORMAL):
        log.info("PATH","Getting {} path from {} to {}",[movement_type,start,goal])
        discovered = 0
        closed_set = []
        open_set = [start]  # TODO: Use Priority Queue
        came_from = {}
        g_score = {}
        f_score = {}
        for x in range(consts.MAP_WIDTH):
            for y in range(consts.MAP_HEIGHT):
                g_score[(x, y)] = float('inf')
                f_score[(x, y)] = float('inf')

        g_score[start] = 0
        f_score[start] = Graph.heuristic(start, goal)

        while len(open_set) > 0:
            discovered += 1
            if discovered > MAX_EDGES_DISCOVERED:
                break
            shortest = float('inf')
            for open in open_set:
                if f_score[open] < shortest:
                    current = open
                    shortest = f_score[open]

            if current == goal:
                result = Graph.reconstruct_path(came_from, current)
                log.info('PATH',"Generated path: {}",[result])
                return result

            open_set.remove(current)
            closed_set.append(current)

            if current in self.edges.keys():
                for neighbor in self.edges[current]:  # 'neighbor' is an Edge
                    w = None
                    for weight in neighbor.weights.keys():
                        if weight == LAVA and neighbor.weights[weight] is not None:
                            pass
                        if weight & movement_type == weight and neighbor.weights[weight] is not None:
                            if w is None:
                                w = neighbor.weights[weight]
                            elif neighbor.weights[weight] < w:
                                w = neighbor.weights[weight]
                    if w is None:
                        # no edge to this tile following valid movement
                        continue

                    if neighbor.coord in closed_set:
                        continue
                    tentative_g_score = g_score[current] + Graph.dist_between(current, neighbor.coord)
                    if neighbor.coord not in open_set:
                        open_set.append(neighbor.coord)
                    elif tentative_g_score >= g_score[neighbor.coord]:
                        continue

                    came_from[neighbor.coord] = current
                    g_score[neighbor.coord] = tentative_g_score + w
                    f_score[neighbor.coord] = g_score[neighbor.coord] + Graph.dist_between(neighbor.coord, goal)

        log.warn("PATH","No path from {} to {}",[start,goal])
        return 'failure'

    @staticmethod
    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()
        return total_path

    @staticmethod
    def dist_between(a, b):
        (x1, y1) = a
        (x2, y2) = b
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @staticmethod
    def heuristic(a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)


# Used for debugging (consts.DEBUG_DRAW_PATHS must be true)
def draw_path(path):
    oldpaths = []
    for obj in main.current_map.objects:
        if obj.name == 'path':
            oldpaths.append(obj)
    for obj in oldpaths:
        obj.destroy()

    if path != 'failure':
        for t in path:
            main.current_map.add_object(
                main.GameObject(t[0], t[1], '*', 'path', libtcod.yellow, always_visible=True, description=''))
