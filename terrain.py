import consts
import libtcodpy as libtcod

class TileData:

    def __init__(self, blocks, blocks_sight, name, char,
                 foreground_color, background_color, description='unremarkable terrain', stamina_cost=0, jumpable=True,
                 burnTemp=0, flammable=False, diggable=False, isWall = False, isFloor = False, isWater = False):
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

data = {
    'stone floor': TileData(False, False, 'stone floor', '.', (128, 96, 0), (64, 48, 0),
                             'the cold, cobblestone dungeon floor', isFloor=True),
    'sand': TileData(False, False, 'sand', '.', (158, 134, 100), (127, 101, 63),
                             'fine, damp sand', isFloor=True),
    'stone wall': TileData(True, True, 'stone wall', '#', (255, 191, 0), (191, 143, 0),
                             'the sturdy masonry of the dungeon walls', diggable=True, isWall=True),
    'hard stone wall': TileData(True, True, 'stone wall', '#', (255, 191, 0), (191, 143, 0), # used for edge of map
                             'the sturdy masonry of the dungeon walls', diggable=False, isWall=True),
    'shallow water': TileData(False, False, 'shallow water', 247, (0, 95, 191), (0, 64, 128),
                             'a shallow pool of grimy water', consts.SHALLOW_WATER_COST, isWater=True),
    'deep water': TileData(False, False, 'deep water', 247, (0, 64, 128), (0, 32, 64),
                             'a deep pool of grimy water', consts.DEEP_WATER_COST, False, isWater=True),
    'chasm': TileData(True, False, 'chasm', libtcod.CHAR_BLOCK1, (16, 16, 32), (0, 0, 16),
                             'a pit descending into darkness'),
    'grass floor': TileData(False, False, 'grass floor', ',', (4, 140, 13), (29, 71, 10),
                             'a stone floor covered with cave grass', flammable=True, isFloor=True),
    'scorched floor': TileData(False, False, 'scorched floor', '.', (94, 55, 55), (30, 30, 30),
                             'still-warm floor scorched by fire', isFloor=True),
    'ramp': TileData(False, False, 'ramp', '/', (128, 96, 0), (64, 48, 0),
                             'a ramp'),
}
