import game as main
import consts
import Queue
import math
import libtcodpy as libtcod

class Graph:
    def __init__(self):
        self.edges = {}

    def neighbors(self, id):
        return self.edges[id]

    def initialize(self, dungeon_map):

        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):
                source_tile = dungeon_map[x][y]
                for tile in main.adjacent_tiles_diagonal(x, y):
                    neighbor_tile = dungeon_map[tile[0]][tile[1]]
                    if not neighbor_tile.blocks:
                        if neighbor_tile.elevation == source_tile.elevation or \
                                        neighbor_tile.tile_type == 'ramp' or source_tile.tile_type == 'ramp':
                            if (x, y) in self.edges.keys():
                                self.edges[(x, y)].append((tile[0], tile[1]))
                            else:
                                self.edges[(x, y)] = [(tile[0], tile[1])]
        for obj in main.objects:
            if obj.blocks:
                self.mark_impassable((obj.x, obj.y))

    def add_edge(self, source, neighbor):

        source_tile = main.dungeon_map[source[0]][source[1]]
        neighbor_tile = main.dungeon_map[neighbor[0]][neighbor[1]]

        if source_tile.elevation != neighbor_tile.elevation:
            if not (source_tile.tile_type == 'ramp' or neighbor_tile.tile_type == 'ramp'):
                return

        if source in self.edges.keys():
            self.edges[source].append(neighbor)
        else:
            self.edges[source] = [neighbor]

    def mark_impassable(self, coord):
        for tile in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            if tile in self.edges and coord in self.edges[tile]:
                self.edges[tile].remove(coord)
        #if coord in self.edges:
        #    self.edges[coord] = []

    def mark_passable(self, coord):
        for tile in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            self.add_edge(tile, coord)

            #if coord in self.edges and tile not in self.edges[coord]:
            #    self.add_edge(coord, tile)


    def is_accessible(self, coord):
        for tile in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            if tile in self.edges:
                edge = self.edges[tile]

            if tile in self.edges and coord in self.edges[tile]:
                return True
        return False

    def a_star_search(self, start, goal):
        closed_set = []
        open_set = [start]
        came_from = {}
        g_score = {}
        f_score = {}
        for x in range(consts.MAP_WIDTH):
            for y in range(consts.MAP_HEIGHT):
                g_score[(x, y)] = float('inf')
                f_score[(x, y)] = float('inf')

        g_score[start] = 0
        f_score[start] = heuristic(start, goal)

        while len(open_set) > 0:
            shortest = float('inf')
            for open in open_set:
                if f_score[open] < shortest:
                    current = open
                    shortest = f_score[open]

            if current == goal:
                return reconstruct_path(came_from, current)

            open_set.remove(current)
            closed_set.append(current)

            if current in self.edges.keys():
                for neighbor in self.edges[current]:
                    if neighbor in closed_set:
                        continue
                    tentative_g_score = g_score[current] + dist_between(current, neighbor)
                    if neighbor not in open_set:
                        open_set.append(neighbor)
                    elif tentative_g_score >= g_score[neighbor]:
                        continue

                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)

        return 'failure'

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    total_path.reverse()
    return total_path

def dist_between(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def draw_path(path):
    oldpaths = []
    for obj in main.objects:
        if obj.name == 'path':
            oldpaths.append(obj)
    for obj in oldpaths:
        obj.destroy()

    if path != 'failure':
        for t in path:
            main.objects.append(
                main.GameObject(t[0], t[1], '*', 'path', libtcod.yellow, always_visible=True, description=''))

map = Graph()