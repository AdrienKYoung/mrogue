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

import consts
import libtcodpy as libtcod
import game as main

# FOV-related globals
player_fov_calculated = False  # indicates whether the most recent fov_compute was with respect to the player
fov_player = None              # a pointer to an item in fov_height. Set to the player's elevation
fov_height = {}                # a dictionary of fov maps, indexed by elevation
fov_recompute = False          # signals to the renderer whether the set of visible tiles has changed

# FOV initialization - computes fov maps for all elevations found in the map.
# Called once when a new map is generated or loaded.
def initialize_fov():
    import player
    global fov_height, fov_player

    # arrays to track elevations that need to be/have already been computed
    elevations = [0]
    finished_elevations = []

    # for every elevation found in the map...
    while len(elevations) > 0:
        elevation = elevations[0]
        elevations.remove(elevation)
        finished_elevations.append(elevation)

        # create a new fov map at this elevation
        fov_height[elevation] = libtcod.map_new(consts.MAP_WIDTH, consts.MAP_HEIGHT)

        # for every tile in the map...
        for y in range(consts.MAP_HEIGHT):
            for x in range(consts.MAP_WIDTH):

                this_elevation = main.current_map.tiles[x][y].elevation
                main.changed_tiles.append((x, y))

                if this_elevation != elevation:
                    # check if this tile is at an elevation we haven't discovered yet
                    if this_elevation not in elevations and this_elevation not in finished_elevations:
                        elevations.append(this_elevation)
                    # set properties for tile of different elevation
                    libtcod.map_set_properties(fov_height[elevation], x, y,
                                               this_elevation <= elevation and not main.current_map.tiles[x][y].blocks_sight_all_elevs, True)
                else:
                    # set properties for tile of same elevation
                    libtcod.map_set_properties(fov_height[elevation], x, y, not main.current_map.tiles[x][y].blocks_sight, True)

                # reveal all tiles if consts.DEBUG_ALL_EXPLORED is True
                if consts.DEBUG_ALL_EXPLORED:
                    main.current_map.tiles[x][y].explored = True

    # after computing fov maps for tiles, modify them for any object that blocks sight
    for obj in main.current_map.objects:
        if obj.blocks_sight:
            set_fov_properties(obj.x, obj.y, True, obj.elevation)

    # finally set the player's view elevation
    set_view_elevation(player.instance.elevation)
    set_fov_recompute()


# sets the fov properties of a tile. Use this instead of libtcod.map_set_properties!
# if elevation is not defined, the property is applied to all elevations. Use this for things like wall tiles.
def set_fov_properties(x, y, blocks_sight, elevation=None):
    global fov_height

    if elevation is None:
        for index in fov_height.keys():
            libtcod.map_set_properties(fov_height[index], x, y, not blocks_sight, True)
    else:
        for index in fov_height.keys():
            if index <= elevation:
                libtcod.map_set_properties(fov_height[index], x, y, not blocks_sight, True)

    set_fov_recompute()


# Checks if the given tile is in the player's line of sight. If the last fov calculation was not with respect to the
# player, it recalculates it without signaling an fov recompute to the renderer
def player_can_see(x, y):
    import player
    global fov_recompute, player_fov_calculated

    if not player_fov_calculated:
        libtcod.map_compute_fov(fov_player, player.instance.x, player.instance.y, consts.TORCH_RADIUS, consts.FOV_LIGHT_WALLS,
                                consts.FOV_ALGO)
        player_fov_calculated = True

    return libtcod.map_is_in_fov(fov_player, x, y)


# Checks if the given monster can see the given target, where target is a GameObject. In the very common case of
# checking vision of the player at the same elevation, defaults to checking player's vision to save time
def monster_can_see_object(monster, target):
    import player
    if monster.elevation == target.elevation and target is player.instance:
        if monster.fighter is None or monster.fighter.stealth == player.instance.fighter.stealth:
            return player_can_see(monster.x, monster.y)
        else:
            return monster.distance_to(player.instance) <= player.instance.fighter.stealth and \
                   monster_can_see_tile(monster, target.x, target.y)

    return monster_can_see_tile(monster, target.x, target.y)


# Checks if the given monster can see the given tile. Recalculates fov using the monster's point of view and elevation.
# Signals for the player's fov to be recalculated.
def monster_can_see_tile(monster, x, y):
    global player_fov_calculated

    if monster.elevation in fov_height.keys():
        libtcod.map_compute_fov(fov_height[monster.elevation], monster.x, monster.y, consts.TORCH_RADIUS,
                                consts.FOV_LIGHT_WALLS, consts.FOV_ALGO)
        player_fov_calculated = False

        set_fov_recompute()
        return libtcod.map_is_in_fov(fov_height[monster.elevation], x, y)
    else:
        return False  # TODO: alternative here


# Sets the fov map of the player to the elevation indicated. Called whenever the player changes elevations.
def set_view_elevation(elevation):
    global fov_player, fov_recompute

    if elevation in fov_height.keys():
        fov_player = fov_height[elevation]
    else:
        pass  # TODO: alternative here
    fov_recompute = True


# Indicate that the set of visible tiles has changed so the renderer can redraw them appropriately
def set_fov_recompute():
    global fov_recompute
    fov_recompute = True