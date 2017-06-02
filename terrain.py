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

class TileData:

    def __init__(self, blocks, blocks_sight, name, char,
                 foreground_color, background_color, description='unremarkable terrain', stamina_cost=0, jumpable=True,
                 burnTemp=0, flammable=0, diggable=False, isWall = False, isFloor = False, isWater = False,
                 isRamp=False, isPit=False, isIce=False, on_step=None, blocks_sight_all_elevs=True):
        self.blocks = blocks
        self.blocks_sight = blocks_sight
        self.name = name
        self.char = char
        self.foreground_color = foreground_color
        self.background_color = background_color
        self.description = description
        self.stamina_cost = stamina_cost
        self.jumpable = jumpable
        self.burnTemp = burnTemp
        self.flammable = flammable
        self.diggable = diggable
        self.isWall = isWall
        self.isFloor = isFloor
        self.isWater = isWater
        self.isRamp = isRamp
        self.isPit = isPit
        self.on_step = on_step
        self.isIce = isIce
        self.blocks_sight_all_elevs = blocks_sight and blocks_sight_all_elevs

data = {
    ###############################################
    #                  DEFAULT
    ###############################################

    'stone floor': TileData(False, False, 'stone floor', '.', (128, 96, 0), (64, 48, 0),
                             'the cold, damp stone cave floor', isFloor=True),
    'stone wall': TileData(True, True, 'stone wall', '#', (255, 191, 0), (191, 143, 0),
                             'solid limestone cave walls', diggable=True, isWall=True),
    'stone ramp': TileData(False, False, 'ramp', '/', (128, 96, 0), (64, 48, 0),
                             'a smooth ramp of stone', isRamp=True),

    ###############################################
    #                    MARSH
    ###############################################

    'damp soil': TileData(False, False, 'damp soil', '.', (128, 96, 0), (64, 48, 0),
                             'damp, loamy soil crawling with worms and insects', isFloor=True),
    'mossy stone wall': TileData(True, True, 'mossy stone wall', '#', (255, 191, 0), (191, 143, 0),
                             'a crumbling stone cliff overgrown with moss, ferns and vines', diggable=True, isWall=True),
    'grass floor': TileData(False, False, 'grass floor', ',', (4, 140, 13), (29, 71, 10),
                             'a grass consisting of strange mossy tufts. Though damp to the touch, this grass has been known to fuel wildfires with surprising vigor.', flammable=11, isFloor=True),

    ###############################################
    #                    BEACH
    ###############################################

    'sand': TileData(False, False, 'sand', '.', (158, 134, 100), (127, 101, 63),
                             'fine, damp sand', isFloor=True),
    'sea cliff': TileData(True, True, 'sea cliff', '#', (63, 50, 31), (31, 24, 15),
                             'a jagged outcropping of briny rock', diggable=True, isWall=True),
    'shallow seawater': TileData(False, False, 'shallow water', 247, (0, 95, 191), (0, 64, 128),
                             'foamy saltwater, rolled ashore by the gentle waves', consts.SHALLOW_WATER_COST, isWater=True),
    'deep seawater': TileData(False, False, 'deep water', 247, (0, 64, 128), (0, 32, 64),
                             'vast depths of seawater, rolling with the tide', consts.DEEP_WATER_COST, jumpable=False, isWater=True),

    ###############################################
    #                  BADLANDS
    ###############################################

    'shale': TileData(False, False, 'shale', '.', (48, 48, 48), (31, 31, 31),
                      'broken shingles of flat, smooth stone', isFloor=True),
    'dark shale wall': TileData(True, True, 'dark shale wall', '#', (96, 96, 96), (64, 64, 64),
                                'a sheer cliff of blackened stone', diggable=True, isWall=True),
    'wooden palisade': TileData(True, True, 'wooden palisade', '#', (94, 75, 47), (31, 24, 15),
                                'a barrier crafted from dry wooden posts lashed together with rope',
                                diggable=True, isWall=True, flammable=10),
    'gnarled tree': TileData(True, True, 'gnarled tree', chr(157), (94, 75, 47), (31, 31, 31),
                             'a twisted, leafless tree, worn down by the gritty winds of the badlands', flammable=7,
                             isWall=True),
    'shale slope': TileData(False, False, 'shale slope', '/', (48, 48, 48), (31, 31, 31),
                            'a smooth slope of shale', isRamp=True),
    'dry grass': TileData(False, False, 'dry grass', ',', (56, 49, 43), (38, 33, 29),
                             'dry stalks of grass that rustle in the wind. Might they burn?', flammable=15, isFloor=True),
    'barren tree': TileData(True, True, 'barren tree', chr(157), libtcod.sepia,libtcod.lightest_gray,
                             'a frozen, barren tree', flammable=11, isWall=True, blocks_sight_all_elevs=False),

    ###############################################
    #               GOBLIN TUNNELS
    ###############################################

    'tunnel wall' : TileData(True, True, 'tunnel wall', '#', (82, 91, 33), (54, 61, 22),
                            description='A roughly-carved tunnel wall, covered with stinking grime.', isWall=True, diggable=True),
    'tunnel floor' : TileData(False, False, 'tunnel floor', '.', (54, 61, 22), (29, 33, 12),
                            description='The muddy tunnel floor, its slimy surface cratered with footprints and stinking puddles', isFloor=True),
    'tunnel slope': TileData(False, False, 'tunnel slope', '/',(54, 61, 22), (29, 33, 12),
                            'a sloping tunnel floor', isRamp=True),
    'oil' : TileData(False, False, 'oil', '~', libtcod.darker_gray, libtcod.darkest_gray, 'A slick sheen of highly flammable oil.',
                            flammable=100, burnTemp=20, jumpable=False, isFloor=True),

    ###############################################
    #               FROZEN FOREST
    ###############################################

    'frozen soil': TileData(False, False,'frozen soil','.',(128, 96, 0), (20, 20, 20),'Soil packed hard by frost',
                            isFloor=True),
    'frozen slope': TileData(False, False,'frozen soil','/',(128, 96, 0), (20, 20, 20),'A slope of frosty earth',
                            isRamp=True),
    'snow drift': TileData(False, False, 'snow drift', '~', libtcod.lightest_gray, libtcod.light_gray,
                             'pristine, waist-deep powdered snow. It will be difficult to move through until it has been crushed down.',
                           consts.SNOW_COST, isFloor=True, on_step=main.step_on_snow_drift),
    'snowy ground': TileData(False, False, 'snowy ground', '.', libtcod.lightest_gray, libtcod.desaturated_amber,
                             'trampled snow, mixed with dirt', isFloor=True),
    'snowy slope': TileData(False, False, 'snowy slope', '/', libtcod.lightest_gray, libtcod.sepia,
                             'a slope covered in snow', isRamp=True),
    'pine tree': TileData(True, True, 'pine tree', libtcod.CHAR_ARROW2_N, libtcod.darkest_green,libtcod.lightest_gray,
                             'a pine tree, its needles ever green', flammable=2, isWall=True, blocks_sight_all_elevs=False),
    'ice': TileData(False, False, 'ice', '=', libtcod.lightest_blue, libtcod.light_blue,
                             'ground made of a thick sheet of ice', isFloor=True, isIce=True),
    'ice wall': TileData(True, False, 'ice wall', '#', libtcod.lightest_blue, libtcod.lighter_blue,
                             'ground made of a thick sheet of ice', isWall=True, isIce=True),
    'deep_ice': TileData(False, False, 'ice', '=', libtcod.white, libtcod.light_blue,
                             'ground made of a thick sheet of ice', isFloor=True, isIce=True),

    ###############################################
    #                   GARDENS
    ###############################################


    'marble path': TileData(False, False, 'marble path', '.', libtcod.light_gray, libtcod.gray,
                            'A path made of marble blocks. Tufts of grass push through the ancient cracks.', isFloor=True),

    'marble wall': TileData(True, True, 'marble wall', '#', libtcod.lightest_gray, libtcod.light_gray,
                            'A wall of polished marble, now overgrown with wild greenery', isWall=True, diggable=True),

    'hedge': TileData(True, True, 'hedge', '#', (21, 51, 7), (17, 40, 6),
                            'A thick hedge', isWall=True, diggable=False, flammable=5),

    'cypress tree': TileData(True, True, 'cypress tree', libtcod.CHAR_ARROW2_N, (17, 40, 6), (29, 71, 10),
                            'A tall, narrow tree.', isWall=True, diggable=False, flammable=5),

    ###############################################
    #                     MISC
    ###############################################

    'stone brick wall': TileData(True, True, 'stone brick wall', 254, libtcod.dark_gray, libtcod.darker_gray,
                                 description='A sturdy wall of great stone bricks. Its masonry is too thick and strong to dig through.',
                                 isWall=True, diggable=False),
    'shallow water': TileData(False, False, 'shallow water', 247, (0, 95, 191), (0, 64, 128),
                             'a shallow pool of grimy water', consts.SHALLOW_WATER_COST, isWater=True),
    'deep water': TileData(False, False, 'deep water', 247, (0, 64, 128), (0, 32, 64),
                             'a deep pool of grimy water', consts.DEEP_WATER_COST, jumpable=False, isWater=True),
    'mud': TileData(False, False, 'mud', 247, (94, 75, 47), (63, 50, 31),
                             'a thick puddle of mud that impedes movement - dodging attacks will be much more difficult here',
                            consts.MUD_COST, isWater=True),
    'lava': TileData(False,False,'lava',247,libtcod.yellow,libtcod.dark_red,'Bubbling molten rock',
                            consts.DEEP_WATER_COST,jumpable=True),
    'chasm': TileData(False, False, 'chasm', libtcod.CHAR_BLOCK1, (16, 16, 32), (0, 0, 16),
                             'a pit descending into darkness', isPit=True),
    'scorched floor': TileData(False, False, 'scorched floor', '.', (94, 55, 55), (30, 30, 30),
                             'embers linger on this still-warm floor scorched by flame', isFloor=True),
    'scorched ramp': TileData(False, False, 'scorched ramp', '/', (94, 55, 55), (30, 30, 30),
                             'embers linger on this still-warm floor scorched by flame', isRamp=True),
}

# flags
FLAG_NO_DIG = 1
