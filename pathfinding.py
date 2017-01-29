import game as main
import consts
import Queue
import math
import libtcodpy as libtcod

MAX_EDGES_DISCOVERED = 100

class Graph:
    def __init__(self):
        self.edges = {}


    def initialize(self, dungeon_map):

        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):
                source_tile = dungeon_map[x][y]
                for tile in main.adjacent_tiles_diagonal(x, y):
                    neighbor_tile = dungeon_map[tile[0]][tile[1]]
                    if not neighbor_tile.blocks:
                        if neighbor_tile.elevation == source_tile.elevation or \
                                        neighbor_tile.is_ramp or source_tile.is_ramp:
                            if (x, y) in self.edges.keys():
                                self.edges[(x, y)].append((tile[0], tile[1]))
                            else:
                                self.edges[(x, y)] = [(tile[0], tile[1])]
        for obj in main.current_map.objects:
            if obj.blocks:
                self.mark_impassable((obj.x, obj.y))


    # add an edge from the source tile to the neighbor tile (checking elevation rules). Assumes that 'neighbor' is passable
    def add_edge(self, source, neighbor):

        source_tile = main.current_map.tiles[source[0]][source[1]]
        neighbor_tile = main.current_map.tiles[neighbor[0]][neighbor[1]]

        if source_tile.elevation != neighbor_tile.elevation:
            if not (source_tile.is_ramp or neighbor_tile.is_ramp):
                return

        if source in self.edges.keys():
            self.edges[source].append(neighbor)
        else:
            self.edges[source] = [neighbor]


    # for every adjacent tile, make sure that tile does not point to the now impassable tile
    def mark_impassable(self, coord):
        for tile in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            if tile in self.edges and coord in self.edges[tile]:
                self.edges[tile].remove(coord)


    # for every adjacent tile, make an edge to the now passable tile (if it follows elevation rules)
    def mark_passable(self, coord):
        for tile in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            self.add_edge(tile, coord)


    # Returns true if there is at least one adjacent tile with an edge leading to this tile
    def is_accessible(self, coord):
        for tile in main.adjacent_tiles_diagonal(coord[0], coord[1]):
            if tile in self.edges and coord in self.edges[tile]:
                return True
        return False


    def a_star_search(self, start, goal):
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
                return Graph.reconstruct_path(came_from, current)

            open_set.remove(current)
            closed_set.append(current)

            if current in self.edges.keys():
                for neighbor in self.edges[current]:
                    if neighbor in closed_set:
                        continue
                    tentative_g_score = g_score[current] + Graph.dist_between(current, neighbor)
                    if neighbor not in open_set:
                        open_set.append(neighbor)
                    elif tentative_g_score >= g_score[neighbor]:
                        continue

                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + Graph.heuristic(neighbor, goal)

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
